from flask import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FieldList, FormField, HiddenField

from back_end.data_utilities import fmt_date
from back_end.interface import get_members_for_query
from front_end.form_helpers import MyStringField, MySelectField, select_fields_to_query, query_to_select_fields, \
    status_choices, validate_date_format
from globals.enumerations import MemberStatus, MembershipType


class MemberItemForm(FlaskForm):
    member_number = HiddenField(label='id')
    number = StringField(label='number')
    status = StringField(label='status')
    member_type = StringField(label='type')
    first_name = StringField(label='first_name')
    last_name = StringField(label='last_name')
    email = StringField(label='email')
    post_code = StringField(label='post_code')
    country = StringField(label='country')
    start_date = StringField(label='start_date')
    end_date = StringField(label='end_date')


class MemberListForm(FlaskForm):
    sel_number = MyStringField(label='Number', db_map='Member.number')
    sel_status = MySelectField(label='Status', choices=[], coerce=MemberStatus.coerce,
                               db_map='Member.status')
    sel_member_type = MySelectField(label='Member type',
                                    choices=MembershipType.choices(extra=[(99, 'adult (!=junior)')], blank=True),
                                    coerce=MembershipType.coerce, db_map='Member.member_type')
    sel_first_name = MyStringField(label='First name', db_map='Member.first_name')
    sel_last_name = MyStringField(label='Last name', db_map='Member.last_name')
    sel_email = MyStringField(label='Email', db_map='Member.email')
    sel_post_code = MyStringField(label='Post code', db_map='Address.post_code')
    sel_country = MyStringField(label='Country', db_map='Address.country')
    sel_start_date = MyStringField(label='Start date', db_map='Member.start_date', validators=[validate_date_format])
    sel_end_date = MyStringField('End date', db_map='Member.end_date', validators=[validate_date_format])
    member_list = FieldList(FormField(MemberItemForm))
    total = StringField(label='Total_Found')
    current_page = IntegerField(label='Current_Page')
    total_pages = IntegerField(label='Total_Pages')
    first_url = StringField(label='first page')
    last_url = StringField(label='last page')
    next_url = StringField(label='next page')
    prev_url = StringField(label='previous page')

    def all_sels(self):
        return [self.sel_number, self.sel_status, self.sel_member_type, self.sel_first_name, self.sel_last_name,
                self.sel_email, self.sel_post_code, self.sel_country, self.sel_start_date, self.sel_end_date]

    def set_status_choices(self):
        # reset membership status choices. Has to be done after form declaration.
        self.sel_status.choices = status_choices()

    def set_initial_counts(self):
        self.total.data = self.total_pages.data = self.current_page.data = 0
        self.first_url = self.next_url = self.prev_url = self.last_url = None

    def populate_member_list(self, query_clauses, clauses, page_number=1):
        if not query_clauses:
            return
        query_to_select_fields(self.all_sels(), query_clauses)
        query = get_members_for_query(query_clauses)
        page = query.paginate(page=page_number, per_page=15)
        self.total.data = page.total
        self.current_page.data = page_number
        self.total_pages.data = page.pages
        self.first_url = url_for('members', page=1, query_clauses=clauses)
        self.next_url = url_for('members', page=page_number + 1, query_clauses=clauses) if page.has_next else None
        self.prev_url = url_for('members', page=page_number - 1, query_clauses=clauses) if page.has_prev else None
        self.last_url = url_for('members', page=page.pages, query_clauses=clauses)
        for member in page.items:  # get_all_members(select) :
            item_form = MemberItemForm()
            item_form.member_number = member.number
            item_form.number = member.dt_number()
            item_form.status = member.status.name
            item_form.member_type = member.member_type.name
            item_form.first_name = member.first_name
            item_form.last_name = member.last_name
            item_form.email = member.email or ''
            item_form.post_code = member.address.post_code
            item_form.country = member.address.country
            item_form.start_date = fmt_date(member.start_date)
            item_form.end_date = fmt_date(member.end_date)
            self.member_list.append_entry(item_form)

    def find_members(self):
        query_clauses = select_fields_to_query(self.all_sels(), 'Member')
        return query_clauses
