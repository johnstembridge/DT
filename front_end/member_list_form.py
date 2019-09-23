from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, HiddenField

from back_end.data_utilities import fmt_date
from back_end.interface import get_members_for_query
from front_end.form_helpers import MyStringField, MySelectField, select_fields_to_query
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
    sel_status = MySelectField(label='Status', choices=MemberStatus.choices(extra=[(99, '<lapsed (active)')], blank=True), coerce=MemberStatus.coerce, db_map='Member.status')
    sel_member_type = MySelectField(label='Member type', choices=MembershipType.choices(extra=[(99, '!=junior (adult)')], blank=True), coerce=MembershipType.coerce, db_map='Member.member_type')
    sel_first_name = MyStringField(label='First name', db_map='Member.first_name')
    sel_last_name = MyStringField(label='Last name', db_map='Member.last_name')
    sel_email = MyStringField(label='Email', db_map='Member.email')
    sel_post_code = MyStringField(label='Post code', db_map='Address.post_code')
    sel_country = MyStringField(label='Country', db_map='Address.country')
    sel_start_date = MyStringField(label='Start date', db_map='Member.start_date')  # DateField(validators=[Optional()])
    sel_end_date = MyStringField('End date', db_map='Member.end_date')  # DateField(validators=[Optional()])
    member_list = FieldList(FormField(MemberItemForm))
    add_member = SubmitField(label='Add member')

    def populate_member_list(self):
        all_sels = [self.sel_number, self.sel_status, self.sel_member_type, self.sel_first_name, self.sel_last_name,
                    self.sel_email, self.sel_post_code, self.sel_country, self.sel_start_date, self.sel_end_date]
        q = get_members_for_query(select_fields_to_query(all_sels, 'Member'), limit=20)
        for member in q:  # get_all_members(select) :
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
