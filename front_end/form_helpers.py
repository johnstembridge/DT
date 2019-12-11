from flask import flash, url_for, current_app
from flask_login import current_user
from wtforms import SelectField, StringField, ValidationError, SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from datetime import date, datetime
import os
import pickle
from collections import OrderedDict

from back_end.data_utilities import force_list, first_or_default, last_or_default, fmt_date, remove
from globals import config
from globals.enumerations import UserRole, MemberStatus


class MyStringField(StringField):
    def __init__(self, *args, db_map=None, **kwargs):
        super().__init__(*args, **kwargs)  # Initialize the super class
        self.db_map = db_map


class MySelectField(SelectField):
    def __init__(self, *args, db_map=None, **kwargs):
        super().__init__(*args, **kwargs)  # Initialize the super class
        self.db_map = db_map

    def pre_validate(self, form):
        if self.flags.required and self.data == 0:
            raise ValueError(self.gettext('Please choose an option'))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).name,
                error
            ), 'danger')


def status_choices():
    # set choices for membership status according to access rights
    if current_user.role.value >= UserRole.dt_board.value:
        choices = MemberStatus.choices(extra=[(99, 'all active (<lapsed)')], blank=True)
    else:
        choices = MemberStatus.choices(blank=True)
    access = current_user.role.access
    if access != 'all':
        limit = MemberStatus.lapsed.value if 'lapsed' in access else MemberStatus.current.value
        choices = [c for c in choices if c[0] <= limit or c[0] == 99]
    return choices


def limit_status_by_access(query_clauses):
    if current_user.role != UserRole.super:
        # limit inclusion of lapsed members according to current user's access rights
        access = current_user.role.access
        limit = MemberStatus.lapsed.value if 'lapsed' in access else MemberStatus.current.value
        sel_status = [c for c in query_clauses if c[0] == 'Member' and c[1] == 'status']
        if not sel_status:
            query_clauses.append(('Member', 'status', limit, '<=', None))
        if 'lapsed 1yr+' not in access:
            today = date.today()
            last_lapse_date = date(year=(today.year - 1 if today.month >= 8 else 2), month=8, day=1)
            query_clauses.append(('Member', 'end_date', fmt_date(last_lapse_date), '>=', None))
    return query_clauses


def select_fields_to_query(select_fields, default_table):
    query_clauses = []
    for field in select_fields:
        if field.data:
            if field.type == 'MySelectField':
                if field.data in [c[0].value for c in field.choices if not isinstance(c[0], int)]:
                    condition, value = '=', field.data
                else:
                    v = [c[1] for c in field.choices if c[0] == field.data][0]
                    condition, value = split_condition_and_value(v)
                    value = first_or_default([v[0] for v in field.choices if v[1] == value], None)
            else:
                condition, value = split_condition_and_value(field.data)
            func = None
            if isinstance(value, (int, float)) or len(value) > 0:
                field_name = field.db_map
                if '.' in field_name:
                    a = field_name.split('.')
                    if len(a) == 2:
                        table, column = a
                    if len(a) == 3:
                        table, column, func = a
                else:
                    table, column = default_table, field_name
                query_clauses.append((table, column, value, condition, func))
    query_clauses = limit_status_by_access(query_clauses)
    return query_clauses


def query_to_select_fields(select_fields, query_clauses):
    fields = {f.name: f for f in select_fields}
    for clause in query_clauses:
        table, column, value, condition, func = clause
        if condition == '=':
            condition = ''
        field = fields['sel_' + column]
        if field.type == 'MySelectField':
            choice = [f[1] for f in field.choices if f[0] == value][0]
            if condition != '':
                choice = '(' + condition + choice + ')'
            field.data = last_or_default([f[0] for f in field.choices if choice in f[1]], '')
        else:
            field.data = condition + value


def select_fields_to_update(select_fields, default_table):
    updates = {}
    for field in select_fields:
        if field.data:
            field_name = field.db_map
            if field.type == 'MySelectField':
                if field.data in [c[0].value for c in field.choices if not isinstance(c[0], int)]:
                    value = field.data
                else:
                    value = [c[1] for c in field.choices if c[0] == field.data][0]
                    if '(' in value:
                        value = value[:value.find('(') - 1]
                    value = first_or_default([v[0] for v in field.choices if v[1] == value], None)
            else:
                value = field.data
            func = None
            # if isinstance(value, (int, float)) or len(value) > 0:
            #     if '.' in field_name:
            #         a = field_name.split('.')
            #         if len(a) == 2:
            #             table, column = a
            #         if len(a) == 3:
            #             table, column, func = a
            #     else:
            #         table, column = default_table, field_name
            updates[field_name] = value
    return updates


extract_fields_map = OrderedDict([
    ('number', 'dt_number()'),
    ('full name', 'full_name()'),
    ('first name', 'first_name'),
    ('last name', 'last_name'),
    ('sex', 'sex.name'),
    ('status', 'status.name'),
    ('type', 'member_type.name'),
    ('start', 'start_date'),
    ('end', 'end_date'),
    ('birth date', 'birth_date'),
    ('birth month', 'birth_month()'),
    ('age', 'age()'),
    ('age next bday', 'age_next_birthday()'),
    ('email', 'email'),
    ('home phone', 'home_phone'),
    ('mobile phone', 'mobile_phone'),
    ('comms', 'comms.name'),
    ('payment method', 'last_payment_method.name'),
    ('dues', 'dues()'),
    ('full address', 'address.full()'),
    ('address (line 1)', 'address.line_1'),
    ('address (line 2)', 'address.line_2'),
    ('address (line 3)', 'address.line_3'),
    ('city', 'address.city'),
    ('county', 'address.county'),
    ('state', 'address.state'),
    ('post code', 'address.post_code'),
    ('country', 'address.country'),
    ('country for post', 'address.country_for_mail()'),
    ('action', 'actions[].action.name'),
    ('action date', 'actions[].date'),
    ('action status', 'actions[].status.name'),
    ('action comment', 'actions[].comment'),
    ('upgrade', 'is_upgrade()'),
    ('use email', 'use_email()'),
    ('email bounced', 'email_bounced()'),
    ('junior email', 'junior.email'),
    ('AFCW access', 'afcw_has_access()'),
    ('3rd pty access', 'third_pty_access()'),
    ('recent new', 'is_recent_new()'),
    ('card start year', 'start_year_for_card()'),
    ('certificate date', '=encode_date_formal(datetime.date.today(), cert=True)'),
    ('next member type', 'future_membership_type().name'),
    ('volatile concession', 'volatile_concession()'),
    ('last updated', 'last_updated')
])


def validate_date_format(form, field):
    if field.data:
        try:
            date = split_condition_and_value(field.data)[1]
            datetime.strptime(date, '%d/%m/%Y').date()
        except:
            field.message = 'Date must be in format dd/mm/yyyy'
            raise ValidationError('Date must be in format dd/mm/yyyy')


def split_condition_and_value(value):
    if '(' in value:
        value = remove(value[value.find('('):], '() ')
    if len(value) > 0 and value[0] in [c[0] for c in ['!=', '=', '>', '>=', '<', '<=', '?']]:
        c = 1
        if value[1] == '=':
            c = 2
        condition = value[:c]
        value = value[c:]
    else:
        condition = '='
    return condition, value


def render_link(url, text="", image=None, icon=None, target=None):
    target = ' target="{}"'.format(target) if target else ''
    if image:
        return '<a href="{}"{}><img title="{}" src="{}"></a>'.format(url, target, text, image)
    if icon:
        if icon.startswith('glyphicon'):
            icon = '<i class="{}" style="font-size:20px;color:#6E1285"></i>'.format(icon)
        if icon == 'fa-link':
            icon = '<i class="fa fa-chevron-circle-right" style="font-size:20px;color:#6E1285"></i>'
        if icon.startswith('fa-'):
            icon = '<i class="fa {}" style="font-size:20px;color:#6E1285"></i>'.format(icon)
        return '<a href="{}"{} title="{}" class="icon-block">{}'.format(url, target, text, icon)
    if text:
        return '<a href="{}"{}>{}</a>'.format(url, target, text)


def url_pickle_dump(obj):
    return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL).decode("ISO-8859-1")


def url_pickle_load(obj):
    return pickle.loads(bytes(obj, 'ISO-8859-1'))


def render_html(template, **kwargs):
    import jinja2
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=config.get('locations')['templates']))
    template = env.get_template(template)
    return template.render(url_for=url_for, **kwargs)


def template_exists(template):
    return os.path.exists(os.path.join(current_app.jinja_loader.searchpath[0], template))


def update_html(html, pairs):
    for id, value in pairs.items():
        i = html.find(id)
        start = i + 1 + html[i:].find('>')
        length = html[start:].find('<')
        html = html[:start] + value + html[start + length:]
    return html


def get_elements_from_html(html, ids):
    result = {}
    for id in force_list(ids):
        i = html.find(id)
        if i >= 0:
            start = i + 1 + html[i:].find('>')
            length = html[start:].find('<')
            result[id] = html[start: start + length]
    return result


def line_break(text, line_break_character=None):
    br = '<br/>'
    if type(text) is list:
        res = br.join(text)
    else:
        res = text.replace(line_break_character, br)
    return res


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
