from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, FieldList, FormField, DecimalField
from wtforms.validators import InputRequired, Optional, Email
from wtforms.fields.html5 import DateField
import datetime

from back_end.interface import get_new_member, get_member, save_member, get_new_comment, get_new_payment, \
    get_members_by_name, get_new_action
from front_end.form_helpers import MySelectField, set_select_field
from globals.enumerations import MemberStatus, MembershipType, Sex, CommsType, PaymentType, PaymentMethod, MemberAction, \
    ActionStatus


class PaymentItemForm(FlaskForm):
    date = DateField(label='Date')
    pay_type = MySelectField(label='Type', choices=PaymentType.choices(), coerce=PaymentType.coerce)
    amount = DecimalField(label='Amount', validators=[Optional()])
    method = MySelectField(label='Method', choices=PaymentMethod.choices(), coerce=PaymentMethod.coerce)
    comment = StringField(label='Comment')


class ActionItemForm(FlaskForm):
    date = DateField(label='Date')
    action = MySelectField(label='Action', choices=MemberAction.choices(blank=True), coerce=MemberAction.coerce)
    comment = StringField(label='Comment')
    status = MySelectField(label='Status', choices=ActionStatus.choices(blank=True), coerce=ActionStatus.coerce)


class CommentItemForm(FlaskForm):
    date = DateField(label='Date')
    comment = StringField(label='Comment')


class MemberDetailsForm(FlaskForm):
    full_name = StringField(label='Full Name')

    member_id = HiddenField(label='Member Id')
    number = StringField(label='Id')
    status = MySelectField(label='Status', choices=MemberStatus.choices(), coerce=MemberStatus.coerce)
    type = MySelectField(label='Type', choices=MembershipType.choices(), coerce=MembershipType.coerce)
    start_date = DateField(label='Start')
    end_date = DateField(label='End')
    birth_date = DateField(label='Birth', validators=[Optional()])
    age = HiddenField(label='Age')

    title = StringField(label='Title')
    first_name = StringField(label='First', validators=[InputRequired()])
    last_name = StringField(label='Last', validators=[InputRequired()])
    sex = MySelectField(label='Sex', choices=Sex.choices(), coerce=int)

    line1 = StringField(label='Address line 1')
    line2 = StringField(label='Address line 2')
    line3 = StringField(label='Address line 3')
    city = StringField(label='City')
    state = StringField(label='State')
    post_code = StringField(label='Post Code')
    county = StringField(label='County')
    country = StringField(label='Country')

    home_phone = StringField(label='Home Phone')
    mobile_phone = StringField(label='Mobile')
    email = StringField(label='Email', validators=[Optional(), Email("Invalid email address")])
    comms = MySelectField(label='Comms', choices=CommsType.choices(), coerce=CommsType.coerce)

    submit = SubmitField(label='Save')

    payment_list = FieldList(FormField(PaymentItemForm))
    action_list = FieldList(FormField(ActionItemForm))
    comment_list = FieldList(FormField(CommentItemForm))

    def populate_member(self, member_id):
        new_member = member_id == 0
        if new_member:
            member = get_new_member()
        else:
            member = get_member(member_id)
        address = member.address

        self.number.data = member.dt_number()
        self.status.data = member.status.value
        self.type.data = member.member_type.value
        self.start_date.data = member.start_date
        self.end_date.data = member.end_date
        self.birth_date.data = member.birth_date
        self.age.data = member.age()

        self.full_name.data = member.full_name()
        self.title.data = member.title
        self.first_name.data = member.first_name
        self.last_name.data = member.last_name
        self.sex.data = (member.sex or Sex.unknown).value

        self.line1.data = address.line_1
        self.line2.data = address.line_2
        self.line3.data = address.line_3
        self.city.data = address.city
        self.state.data = address.state
        self.post_code.data = address.post_code
        self.county.data = address.county
        self.country.data = address.country

        self.home_phone.data = member.home_phone
        self.mobile_phone.data = member.mobile_phone
        self.email.data = member.email
        self.comms.data = member.comms.value

        for payment in [get_new_payment()] + member.payments:
            item_form = PaymentItemForm()
            item_form.date = payment.date
            item_form.pay_type = payment.type.value ## nb: don't set the data attribute for select fields in a fieldlist!
            item_form.amount = payment.amount
            item_form.method = (payment.method or PaymentMethod.na).value
            item_form.comment = payment.comment or ''
            self.payment_list.append_entry(item_form)

        for action in [get_new_action(new_member)] + member.actions:
            item_form = ActionItemForm()
            if action.action:
                item_form.action = action.action.value
            if action.status:
                item_form.status = action.status.value
            item_form.date = action.date
            item_form.comment = action.comment or ''
            self.action_list.append_entry(item_form)

        for comment in [get_new_comment()] + member.comments:
            item_form = CommentItemForm()
            item_form.date = comment.date
            item_form.comment = comment.comment or ''
            self.comment_list.append_entry(item_form)

    def validate(self):
        result = True
        new_member = self.member_id.data == 0
        if not super(MemberDetailsForm, self).validate():
            return False
        if new_member:
            name = self.first_name.data + ' ' + self.last_name.data
            existing = get_members_by_name(name).all()
            if len(existing) > 0:
                self.first_name.errors.append('{} is already member {}'.format(name, existing[0].dt_number()))
                result = False
        return result

    def save_member(self, member_id):
        member = {
            'title': self.title.data,
            'first_name': self.first_name.data,
            'last_name': self.last_name.data,
            'sex': self.sex.data,

            'member_type': self.type.data,
            'status': self.status.data,
            'start_date': self.start_date.data,
            'end_date': self.end_date.data,
            'birth_date': self.birth_date.data,

            'home_phone': self.home_phone.data,
            'mobile_phone': self.mobile_phone.data,
            'email': self.email.data,
            'comms': self.comms.data,

            'line_1': self.line1.data,
            'line_2': self.line2.data,
            'line_3': self.line3.data,
            'city': self.city.data,
            'state': self.state.data,
            'post_code': self.post_code.data,
            'county': self.county.data,
            'country': self.country.data,

            'payments': [],
            'actions': [],
            'comments': []
        }
        for payment in self.payment_list.data:
            if payment['amount']:
                member['payments'].append(payment)

        for action in self.action_list.data:
            if action['action'] > 0:
                member['actions'].append(action)

        for comment in self.comment_list.data:
            if comment['comment']:
                member['comments'].append(comment)

        save_member(member_id, member)
        return True
