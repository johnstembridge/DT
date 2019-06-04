from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField


class ExtractForm(FlaskForm):
    fields = [
        ('DT number', 'dt_number()'),
        ('First Name', 'first_name'),
        ('Last Name', 'last_name'),
        ('Sex', 'sex.name'),
        ('Status', 'status.name'),
        ('Type', 'member_type.name'),
        ('Start', 'start_date'),
        ('End', 'end_date'),
        ('Birth', 'birth_date'),
        ('Address', 'address.full()'),
        ('Action', 'actions[].action.name'),
        ('Status', 'actions[].status.name')
    ]
    total = StringField(label='Total_Found')
    current_page = IntegerField(label='Current_Page')
    next_url = StringField(label='next page')
    prev_url = StringField(label='previous page')

    def populate_result(self, clauses, query, page_number=1):
        page = query.paginate(page=page_number)
        self.total.data = page.total
        self.current_page.data = page_number
        self.next_url = url_for('extracts_show', page=page_number + 1, query_clauses=clauses) if page.has_next else None
        self.prev_url = url_for('extracts_show', page=page_number - 1, query_clauses=clauses) if page.has_prev else None
        return self.fields, page
