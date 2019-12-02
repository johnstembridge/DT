from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField
from front_end.form_helpers import MultiCheckboxField
import calendar

from front_end.form_helpers import MyStringField, MySelectField, select_fields_to_query, select_fields_to_update, \
    status_choices, validate_date_format
from globals.enumerations import MemberStatus, MembershipType, PaymentMethod, CommsType, MemberAction, ActionStatus


class QueryForm(FlaskForm):
    months = [(m, calendar.month_name[m]) for m in range(1, 13)]
    display_fields = [(i, j) for (i, j) in enumerate(['number', 'status', 'member_type', 'start_date', 'end_date',
                                                      'payment_method', 'comms', 'birth_month', 'age',
                                                      'current_action', 'action_status', 'action_comment',
                                                      'comment_date', 'comment',
                                                      'first_name', 'last_name', 'email', 'post_code', 'country'])]

    number = MyStringField(label='number', db_map='Member.number')
    status = MySelectField(label='status', choices=[], coerce=MemberStatus.coerce, db_map='Member.status')
    member_type = MySelectField(label='member type',
                                choices=MembershipType.choices(extra=[(99, 'adult (!=junior)')], blank=True),
                                coerce=MembershipType.coerce, db_map='Member.member_type')
    start_date = MyStringField(label='start date', db_map='Member.start_date', validators=[validate_date_format])
    end_date = MyStringField('end date', db_map='Member.end_date', validators=[validate_date_format])
    post_code = MyStringField(label='post code', db_map='Address.post_code')
    country = MyStringField(label='country', db_map='Address.country')
    payment_method = MySelectField(label='payment method', choices=PaymentMethod.choices(blank=True),
                                   coerce=PaymentMethod.coerce, db_map='Member.last_payment_method')
    comms = MySelectField(label='comms', choices=CommsType.choices(blank=True), coerce=CommsType.coerce,
                          db_map='Member.comms')
    birth_month = MySelectField(label='birth month', choices=[(0, '')] + months, coerce=int,
                                db_map='Member.birth_date.month')
    age = MyStringField(label='age', db_map='Member.birth_date.age')
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
    display_fields = MultiCheckboxField(label='fields to extract', choices=display_fields)
    submit = SubmitField(label='Submit')

    def query_fields(self):
        return [self.number, self.status, self.member_type, self.start_date, self.end_date,
                self.payment_method, self.comms, self.birth_month, self.age,
                self.current_action, self.action_status, self.action_comment,
                self.comment_date, self.comment,
                self.first_name, self.last_name, self.email, self.post_code, self.country]

    def set_status_choices(self):
        self.status.choices = status_choices()

    def find_members(self):
        query_clauses = select_fields_to_query(self.query_fields(), 'Member')
        return query_clauses

    def get_updates(self):
        updates = select_fields_to_update(self.query_fields(), 'Member')
