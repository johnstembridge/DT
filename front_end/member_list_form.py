import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, HiddenField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Optional

from back_end.data_utilities import fmt_date
from back_end.interface import get_members_by_select
from front_end.form_helpers import set_select_field, MySelectField, select_fields_to_query
from globals.enumerations import MemberStatus, MembershipType


class MemberItemForm(FlaskForm):
    member_id = HiddenField(label='id')
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
    sel_number = StringField(label='number')
    sel_status = MySelectField(label='status', choices=MemberStatus.choices(), coerce=MemberStatus.coerce)
    sel_member_type = MySelectField(label='member_type', choices=MembershipType.choices(), coerce=MembershipType.coerce)
    sel_first_name = StringField(label='first_name')
    sel_last_name = StringField(label='last_name')
    sel_email = StringField(label='email')
    sel_post_code = StringField(label='Address.post_code')
    sel_country = StringField(label='Address.country')
    sel_start_date = StringField(label='start_date')  # DateField(validators=[Optional()])
    sel_end_date = StringField('end_date')  # DateField(validators=[Optional()])
    member_list = FieldList(FormField(MemberItemForm))
    add_member = SubmitField(label='Add member')

    def populate_member_list(self):
        select = []
        all_sels = [self.sel_number, self.sel_status, self.sel_member_type, self.sel_first_name, self.sel_last_name,
                    self.sel_email, self.sel_post_code, self.sel_country, self.sel_start_date, self.sel_end_date]
        set_select_field(self.sel_status, MemberStatus.choices(), extra_items=[(0, ''), (99, '<lapsed')])
        set_select_field(self.sel_member_type, MembershipType.choices(), extra_items=[(0, '')])
        q = get_members_by_select(select_fields_to_query(all_sels, 'Member'))
        for member in q:  # get_all_members(select) :
            item_form = MemberItemForm()
            item_form.member_id = member.id
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
