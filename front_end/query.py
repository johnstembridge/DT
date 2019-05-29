from flask_wtf import FlaskForm
from wtforms import SubmitField
import calendar

from back_end.interface import get_members_by_select
from front_end.form_helpers import MyStringField, MySelectField, select_fields_to_query
from globals.enumerations import MemberStatus, MembershipType, PaymentMethod, CommsType, MemberAction, ActionStatus


class QueryForm(FlaskForm):
    months = [(m, calendar.month_name[m]) for m in range(1, 13)]

    number = MyStringField(label='number', db_map='Member.id')
    status = MySelectField(label='status', choices=MemberStatus.choices(extra=[(99, '<lapsed (active)')], blank=True),
                           coerce=MemberStatus.coerce, db_map='Member.status')
    member_type = MySelectField(label='member type', choices=MembershipType.choices(blank=True),
                                coerce=MembershipType.coerce, db_map='Member.member_type')
    start_date = MyStringField(label='start date', db_map='Member.start_date')
    end_date = MyStringField('end date', db_map='Member.end_date')
    payment_method = MySelectField(label='payment method', choices=PaymentMethod.choices(blank=True),
                                   coerce=PaymentMethod.coerce, db_map='Payment.method')
    comms = MySelectField(label='comms', choices=CommsType.choices(blank=True), coerce=CommsType.coerce,
                          db_map='Member.comms')
    current_action = MySelectField(label='current action', choices=MemberAction.choices(blank=True),
                                   coerce=MemberAction.coerce, db_map='Action.action')
    action_status = MySelectField(label='action status', choices=ActionStatus.choices(blank=True),
                                  coerce=ActionStatus.coerce, db_map='Action.status')
    first_name = MyStringField(label='first name', db_map='Member.first_name')
    last_name = MyStringField(label='last name', db_map='Member.larst_name')
    email = MyStringField(label='email', db_map='Member.email')
    post_code = MyStringField(label='post code', db_map='Address.post_code')
    country = MyStringField(label='country', db_map='Address.country')
    birth_month = MySelectField(label='birth month', choices=[(0, '')] + months, coerce=int,
                                db_map='Member.birth_date.month')
    age = MyStringField(label='age', db_map='Member.birth_date.age')
    submit = SubmitField(label='Submit')

    def populate_selections(self):
        pass

    def find_members(self):
        all_sels = [self.number, self.status, self.member_type, self.start_date, self.end_date,
                    self.payment_method, self.comms, self.current_action, self.action_status,
                    self.first_name, self.last_name, self.email, self.post_code, self.country,
                    self.birth_month, self.age]
        q = get_members_by_select(select_fields_to_query(all_sels, 'Member'))
        q
        pass
