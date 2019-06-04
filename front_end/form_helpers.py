from flask import flash, url_for, current_app
from wtforms import SelectField, StringField
import os
import pickle

from back_end.data_utilities import force_list, lookup, first_or_default
from globals import config


class MyStringField(StringField):
    def __init__(self, *args, db_map=None, **kwargs):
        super().__init__(*args, **kwargs)       # Initialize the super class
        self.db_map = db_map


class MySelectField(SelectField):
    def __init__(self, *args, db_map=None, **kwargs):
        super().__init__(*args, **kwargs)       # Initialize the super class
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


def set_select_field(field, choices=None, extra_items=None, default_selection=None, db_map=None):
    if choices:
        if len(choices) > 0 and isinstance(choices[0], tuple):
                items = choices
        else:
            items = [(c, c) for c in choices]
        if extra_items:
            field.choices = extra_items + items
        else:
            field.choices = items
    if default_selection:
        field.default = default_selection
        field.data = default_selection
    if db_map:
        field.db_map = db_map


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
                    if '(' in value:
                        value = value[:value.find('(')-1]
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
    return query_clauses


def split_condition_and_value(value):
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
