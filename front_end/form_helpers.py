from flask import flash, url_for, current_app
from wtforms import SelectField
import os

from back_end.data_utilities import force_list, lookup
from globals import config


class MySelectField(SelectField):

    def pre_validate(self, form):
        if self.flags.required and self.data == 0:
            raise ValueError(self.gettext('Please choose an option'))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


def set_select_field(field, choices, item_name=None, default_selection=None):
    if len(choices) > 0 and isinstance(choices[0], tuple):
            items = choices
    else:
        items = [(c, c) for c in choices]
    if item_name:
        field.choices = [(0, '')] + items
    else:
        field.choices = items
    if default_selection:
        field.default = default_selection
        field.data = default_selection


def select_fields_to_query(select_fields, default_table):
    query_clauses = []
    c = ['ne', 'eq', 'gt', 'ge', 'lt', 'le', 'in']
    e = ['!=', '=', '>', '>=', '<', '<=', 'in']
    for field in select_fields:
        condition = '='
        if field.data:
            if field.type == 'MySelectField':
                value = field.data.value
            else:
                value = field.data
                if value[:2] in c:
                    condition = e[lookup(c, value[:2])]
                    value = value[2:]
            if isinstance(value, (int, float)) or len(value) > 0:
                field_name = field.label.text
                if '.' in field_name:
                    table, column = field_name.split('.')
                else:
                    table, column = default_table, field_name
                query_clauses.append((table, column, value, condition))
    return query_clauses


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
