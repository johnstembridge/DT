from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, FieldList, FormField, DecimalField
from wtforms.validators import InputRequired, Optional, Email
from wtforms.fields.html5 import DateField

from back_end.interface import get_new_member, get_member, save_member_details, get_new_comment, get_new_payment, \
    get_members_by_name, get_new_action, country_choices, county_choices, state_choices, get_country, get_county, \
    get_state, get_junior
from front_end.form_helpers import MySelectField
from globals.enumerations import MemberStatus, MembershipType, Sex, CommsType, PaymentType, PaymentMethod, MemberAction, \
    ActionStatus, Title, CommsStatus, JuniorGift, ExternalAccess, UserRole
from back_end.data_utilities import fmt_date


class PaymentItemForm(FlaskForm):
    date = DateField(label='Date')
    pay_type = MySelectField(label='Type', choices=PaymentType.choices(), coerce=PaymentType.coerce)
    amount = DecimalField(label='Amount', validators=[Optional()])
    method = MySelectField(label='Method', choices=PaymentMethod.choices(blank=True), coerce=PaymentMethod.coerce)
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
    return_url = HiddenField(label='Return URL')
    member_number = HiddenField(label='Member Number')
    dt_number = StringField(label='Id')
    status = MySelectField(label='Status', choices=MemberStatus.choices(), coerce=MemberStatus.coerce)
    type = MySelectField(label='Type', choices=MembershipType.choices(), coerce=MembershipType.coerce)
    start_date = DateField(label='Start')
    end_date = DateField(label='End')
    birth_date = DateField(label='DoB', validators=[Optional()])
    age = HiddenField(label='Age')
    last_updated = StringField(label='Updated')
    access = MySelectField(label='Access', choices=UserRole.choices(blank=False, ),
                           coerce=UserRole.coerce)
    fan_id = StringField(label='AFCW Fan ID')
    external_access = MySelectField(label='External access', choices=ExternalAccess.choices(),
                                    coerce=ExternalAccess.coerce)
    payment_method = MySelectField(label='Pay method', choices=PaymentMethod.choices(blank=True), coerce=PaymentMethod.coerce)
    title = MySelectField(label='Title', choices=Title.choices(blank=True), coerce=Title.coerce)
    first_name = StringField(label='First', validators=[InputRequired()])
    last_name = StringField(label='Last', validators=[InputRequired()])
    sex = MySelectField(label='Sex', choices=Sex.choices(blank=True), coerce=int)

    line1 = StringField(label='Address line 1')
    line2 = StringField(label='Address line 2')
    line3 = StringField(label='Address line 3')
    city = StringField(label='City')
    state = MySelectField(label='State', choices=state_choices(blank=True), coerce=int)
    post_code = StringField(label='Post Code')
    county = MySelectField(label='County', choices=county_choices(blank=True), coerce=int)
    country = MySelectField(label='Country', choices=country_choices(), coerce=int)

    home_phone = StringField(label='Home Phone')
    mobile_phone = StringField(label='Mobile')
    email = StringField(label='Email ', validators=[Optional(), Email("Invalid email address")])
    comms = MySelectField(label='Comms ', choices=CommsType.choices(), coerce=CommsType.coerce)
    comms_status = MySelectField(label='Status ', choices=CommsStatus.choices(), coerce=CommsStatus.coerce)

    submit = SubmitField(label='Save')

    payment_list = FieldList(FormField(PaymentItemForm))
    action_list = FieldList(FormField(ActionItemForm))
    comment_list = FieldList(FormField(CommentItemForm))

    jd_email = StringField(label='JD Email ', validators=[Optional(), Email("Invalid email address")])
    jd_gift = MySelectField(label='JD Gift', choices=JuniorGift.choices(blank=True), coerce=JuniorGift.coerce)

    def populate_member(self, member_number, return_url, copy=False):
        self.return_url.data = return_url
        new_member = member_number == 0
        if new_member or copy:
            member = get_new_member()
        else:
            member = get_member(member_number)
        if copy:
            base_member = get_member(member_number)
            new_member = True
            member.last_name = base_member.last_name
            member.address = base_member.address
            member.home_phone = base_member.home_phone
            member.mobile_phone = base_member.mobile_phone
            member.email = base_member.email
            member.comms = base_member.comms
        address = member.address
        self.member_number.data = str(member.number)
        self.dt_number.data = member.dt_number()
        self.status.data = member.status.value
        self.type.data = member.member_type.value
        self.start_date.data = member.start_date
        self.end_date.data = member.end_date
        self.birth_date.data = member.birth_date
        self.age.data = str(member.age()) if member.age() is not None else None
        self.last_updated.data = fmt_date(member.last_updated)
        self.access.data = member.user.role.value if member.user else 0

        self.fan_id.data = member.season_ticket_id if member.season_ticket_id else ''
        self.external_access.data = (member.external_access or ExternalAccess.none).value
        self.payment_method.data = member.last_payment_method.value if member.last_payment_method else ''

        self.full_name.data = member.full_name()
        self.title.data = member.title.value if member.title else ''
        self.first_name.data = member.first_name
        self.last_name.data = member.last_name
        self.sex.data = member.sex.value if member.sex else ''

        self.line1.data = address.line_1
        self.line2.data = address.line_2
        self.line3.data = address.line_3
        self.city.data = address.city
        self.state.data = address.state.id if address.state else 0
        self.post_code.data = address.post_code
        self.county.data = address.county.id if address.county else 0
        self.country.data = address.country.id

        self.home_phone.data = member.home_phone
        self.mobile_phone.data = member.mobile_phone
        self.email.data = member.email
        self.comms.data = member.comms.value
        self.comms_status.data = member.comms_status.value if member.comms_status else CommsStatus.all_ok

        for payment in [get_new_payment()] + member.payments:
            item_form = PaymentItemForm()
            item_form.date = payment.date
            item_form.pay_type = payment.type.value  ## nb: don't set the data attribute for select fields in a fieldlist!
            item_form.amount = payment.amount
            item_form.method = payment.method.value if payment.method else None
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

        if new_member or member.member_type == MembershipType.junior:
            if not member.junior:
                member.junior = get_junior()
            self.jd_email.data = member.junior.email or ''
            self.jd_gift.data = member.junior.gift.value if member.junior.gift else ''
        else:
            self.jd_email = self.jd_gift = None

    def validate(self):
        result = True
        new_member = int(self.member_number.data) == 0
        if not super(MemberDetailsForm, self).validate():
            return False
        if new_member:
            name = self.first_name.data + ' ' + self.last_name.data
            existing = get_members_by_name(name)
            if len(existing) > 0:
                self.first_name.errors.append('{} is already member {}'.format(name, existing[0].dt_number()))
                result = False
        return result

    def save_member(self, member_number):
        member_details = {
            'title': self.title.data,
            'first_name': self.first_name.data.strip(),
            'last_name': self.last_name.data.strip(),
            'sex': self.sex.data,

            'member_type': self.type.data,
            'status': self.status.data,
            'start_date': self.start_date.data,
            'end_date': self.end_date.data,
            'birth_date': self.birth_date.data,

            'access': self.access.data,
            'external_access': self.external_access.data,
            'fan_id': self.fan_id.data,
            'payment_method': self.payment_method.data,

            'home_phone': self.home_phone.data.strip(),
            'mobile_phone': self.mobile_phone.data.strip(),
            'email': self.email.data.strip(),
            'comms': self.comms.data,
            'comms_status': self.comms_status.data,

            'line_1': self.line1.data.strip(),
            'line_2': self.line2.data.strip(),
            'line_3': self.line3.data.strip(),
            'city': self.city.data.strip(),
            'state': get_state(self.state.data),
            'post_code': self.post_code.data.strip(),
            'county': get_county(self.county.data),
            'country': get_country(self.country.data),

            'payments': [],
            'actions': [],
            'comments': []
        }
        if self.type.data == MembershipType.junior.value:
            member_details['jd_mail'] = self.jd_email.data.strip()
            member_details['jd_gift'] = self.jd_gift.data

        for payment in self.payment_list.data:
            if payment['amount']:
                member_details['payments'].append(payment)

        for action in self.action_list.data:
            if action['action'] > 0:
                member_details['actions'].append(action)

        for comment in self.comment_list.data:
            if comment['comment']:
                member_details['comments'].append(comment)

        return save_member_details(member_number, member_details)
