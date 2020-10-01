from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField


class ExtractForm(FlaskForm):
    total = StringField(label='Total_Found')
    current_page = IntegerField(label='Current_Page')
    total_pages = IntegerField(label='Total_Pages')
    first_url = StringField(label='first page')
    last_url = StringField(label='last page')
    next_url = StringField(label='next page')
    prev_url = StringField(label='previous page')
    extract_url = StringField(label='extract')
    close_url = StringField(label='close')
    action_type = HiddenField(label='action type')

    def populate_result(self, clauses, fields, query, action, show_fn, page_number):
        page = query.paginate(page=page_number, per_page=15)
        self.total.data = page.total
        self.current_page.data = page_number
        self.total_pages.data = page.pages
        self.first_url = url_for(show_fn, type=action, page=1, query_clauses=clauses, display_fields=fields)
        self.next_url = url_for(show_fn, type=action, page=page_number + 1, query_clauses=clauses,
                                display_fields=fields) if page.has_next else None
        self.prev_url = url_for(show_fn, type=action, page=page_number - 1, query_clauses=clauses,
                                display_fields=fields) if page.has_prev else None
        self.last_url = url_for(show_fn, type=action, page=page.pages, query_clauses=clauses, display_fields=fields)
        self.extract_url = url_for('extracts_extract', query_clauses=clauses,
                                   display_fields=fields)
        self.close_url = url_for('clear_actions', query_clauses=clauses, type=action,
                                 display_fields=fields) if action else None
        self.action_type.data = action
        return page
