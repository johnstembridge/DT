from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField
import calendar

from front_end.form_helpers import MyStringField, MySelectField, select_fields_to_query, select_fields_to_update, \
    status_choices, validate_date_format, MultiCheckboxField, extract_fields_map
from back_end.interface import country_choices
from globals.enumerations import MemberStatus, MembershipType, PaymentMethod, CommsType, CommsStatus, MemberAction, \
    ActionStatus, PaymentType


class QueryForm(FlaskForm):
    months = [(m, calendar.month_name[m]) for m in range(1, 13)]
    number = MyStringField(label='number', db_map='Member.number')
    last_updated = MyStringField(label='last updated', db_map='Member.last_updated', validators=[validate_date_format])
    status = MySelectField(label='status', choices=[], coerce=MemberStatus.coerce, db_map='Member.status')
    member_type = MySelectField(label='member type',
                                choices=MembershipType.choices(extra=[(99, 'adult (!=junior)')], blank=True),
                                coerce=MembershipType.coerce, db_map='Member.member_type')
    start_date = MyStringField(label='start date', db_map='Member.start_date', validators=[validate_date_format])
    end_date = MyStringField('end date', db_map='Member.end_date', validators=[validate_date_format])
    birth_date = MyStringField('birth date', db_map='Member.birth_date', validators=[validate_date_format])
    post_code = MyStringField(label='post code', db_map='Address.post_code')
    country = MySelectField(label='country',
                            choices=country_choices(blank=True, extra=[(9999, 'overseas (!=United Kingdom)')]),
                            coerce=int, db_map='Address.Country.id')
    payment_type = MySelectField(label='payment type', choices=PaymentType.choices(blank=True),
                                 coerce=PaymentMethod.coerce, db_map='Member.Payment.type')
    payment_method = MySelectField(label='payment method', choices=PaymentMethod.choices(blank=True),
                                   coerce=PaymentMethod.coerce, db_map='Member.last_payment_method')
    payment_date = MyStringField(label='payment date', db_map='Member.Payment.date', validators=[validate_date_format])
    payment_comment = MyStringField(label='payment comment', db_map='Payment.comment')
    renewal_activated = MyStringField(label='renewal activated', db_map='Member.renewal_activated()')
    comms = MySelectField(label='comms', choices=CommsType.choices(blank=True), coerce=CommsType.coerce,
                          db_map='Member.comms')
    comms_status = MySelectField(label='comms status', choices=CommsStatus.choices(blank=True), coerce=CommsType.coerce,
                                 db_map='Member.comms_status')
    birth_month = MySelectField(label='birth month', choices=[(0, '')] + months, coerce=int,
                                db_map='Member.birth_date.birth_month()')
    age = MyStringField(label='age', db_map='Member.birth_date.age()')
    current_action = MySelectField(label='current action', choices=MemberAction.choices(blank=True),
                                   coerce=MemberAction.coerce, db_map='Action.action')
    action_status = MySelectField(label='action status', choices=ActionStatus.choices(blank=True),
                                  coerce=ActionStatus.coerce, db_map='Action.status')
    action_date = MyStringField(label='action date', db_map='Action.date', validators=[validate_date_format])
    action_comment = MyStringField(label='action comment', db_map='Action.comment')
    comment_date = MyStringField(label='comment date', db_map='Comment.date', validators=[validate_date_format])
    comment = MyStringField(label='comment', db_map='Comment.comment')

    first_name = MyStringField(label='first name', db_map='Member.first_name')
    last_name = MyStringField(label='last name', db_map='Member.last_name')
    email = MyStringField(label='email', db_map='Member.email')

    query_clauses = HiddenField(label='query')
    display_fields = MultiCheckboxField(label='fields to extract ...',
                                        choices=list(enumerate(extract_fields_map)))
    submit = SubmitField(label='Submit')

    def query_fields(self):
        return [self.number, self.last_updated, self.status, self.member_type, self.start_date, self.end_date,
                self.birth_date, self.comms, self.comms_status, self.birth_month, self.age,
                self.current_action, self.action_date, self.action_status, self.action_comment, self.comment_date,
                self.comment, self.payment_type, self.payment_method, self.payment_date, self.payment_comment,
                self.first_name, self.last_name, self.email, self.post_code, self.country, self.renewal_activated]

    def set_status_choices(self):
        self.status.choices = status_choices()

    def find_members(self):
        query_clauses = select_fields_to_query(self.query_fields(), 'Member')
        return query_clauses

    def get_updates(self):
        updates = select_fields_to_update(self.query_fields(), 'Member')
