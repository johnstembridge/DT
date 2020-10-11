from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Optional, Email
from wtforms.fields.html5 import DateField

from back_end.interface import get_member, save_member_contact_details, country_choices, county_choices, state_choices, \
    get_country, get_county, get_state, get_junior
from front_end.form_helpers import MySelectField
from globals.enumerations import MemberStatus, MembershipType, Sex, CommsType, PaymentMethod, Title, CommsStatus, \
    JuniorGift, ExternalAccess, PayPalPayment, MemberAction
from back_end.data_utilities import fmt_date


class MemberEditForm(FlaskForm):
    renewal = HiddenField(label='Renewal')
    last_updated = StringField(label='Last Update')
    full_name = StringField(label='Full Name')
    return_url = HiddenField(label='Return URL')
    member_number = HiddenField(label='Member Number')
    dt_number = StringField(label='Id')

    start_date = StringField(label='Joined')
    birth_date = DateField(label='Date of Birth', validators=[InputRequired()])
    age = HiddenField(label='Age')
    season_ticket = StringField(label='Season Ticket')
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
    comms = MySelectField(label='Communications preference ', choices=CommsType.choices(), coerce=CommsType.coerce)
    comms_status = MySelectField(label='Status ', choices=CommsStatus.choices(), coerce=CommsStatus.coerce)

    jd_email = StringField(label='JD Email ', validators=[Optional(), Email("Invalid email address")])
    jd_gift = MySelectField(label='JD Gift', choices=JuniorGift.choices(blank=True), coerce=JuniorGift.coerce)

    afcw_access = BooleanField(label='Make my contact details available to AFC Wimbledon Limited')
    third_pty_access = BooleanField(
        label='Make my contact details available to other organisations approved by the Trust ')

    # dues = StringField(label='Dues')
    upgrade = BooleanField(label='I wish to change my membership to Dons Trust Plus')
    payment_method = MySelectField(label='Payment Method', choices=PaymentMethod.renewal_choices(),
                                   coerce=PaymentMethod.coerce)
    comment = TextAreaField(label='Please add any comments about the renewal here')
    last_payment_method = HiddenField(label='Last Payment Method')
    notes = HiddenField(label='Notes')

    status = HiddenField(label='Member Status')
    plus = HiddenField(label='DT plus')
    type = MySelectField(label='Member Type', choices=MembershipType.renewal_choices(), coerce=MembershipType.coerce)

    submit = SubmitField(label='Save')

    def populate_member(self, member_number, return_url, renewal):
        self.return_url.data = return_url
        self.renewal.data = renewal
        member = get_member(member_number)
        address = member.address
        self.member_number.data = str(member.number)
        self.dt_number.data = member.dt_number()
        self.status.data = member.status.name
        self.plus.data = ' (Dons Trust Plus)' if member.status == MemberStatus.plus else ''
        self.type.data = member.member_type_at_renewal().value

        self.start_date.data = fmt_date(member.start_date)
        self.birth_date.data = member.birth_date
        self.age.data = str(member.age()) if member.age() is not None else None

        self.season_ticket.data = member.season_ticket_id if member.season_ticket_id else ''
        self.external_access.data = (member.external_access or ExternalAccess.none).value
        self.last_updated.data = fmt_date(member.last_updated)

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

        if member.member_type_at_renewal() == MembershipType.junior:
            if not member.junior:
                member.junior = get_junior()
            self.jd_email.data = member.junior.email or ''
            self.jd_gift.data = member.junior.gift.value if member.junior.gift else ''
        else:
            self.jd_email = self.jd_gift = None

        self.afcw_access.data = member.afcw_has_access()
        self.third_pty_access.data = member.third_pty_access()

        self.payment_method.data = self.last_payment_method.data = \
            member.last_payment_method.value if member.last_payment_method else ''

        self.upgrade.data = member.current_action() and member.current_action().action == MemberAction.upgrade

        self.notes.data = member.edit_notes()

        return member.renewal_activated()

    def save_member(self, member_number):
        member = {
            'title': self.title.data,
            'first_name': self.first_name.data.strip(),
            'last_name': self.last_name.data.strip(),
            'sex': self.sex.data,

            'member_type': self.type.data,
            # 'status': self.status.data,
            # 'start_date': self.start_date.data,
            # 'end_date': self.end_date.data,
            'birth_date': self.birth_date.data,

            # 'access': self.access.data,
            # 'season_ticket': self.season_ticket.data,

            'home_phone': self.home_phone.data.strip(),
            'mobile_phone': self.mobile_phone.data.strip(),
            'email': self.email.data.strip(),
            'comms': self.comms.data,
            # 'comms_status': self.comms_status.data,

            'line_1': self.line1.data.strip(),
            'line_2': self.line2.data.strip(),
            'line_3': self.line3.data.strip(),
            'city': self.city.data.strip(),
            'state': get_state(self.state.data),
            'post_code': self.post_code.data.strip(),
            'county': get_county(self.county.data),
            'country': get_country(self.country.data),

            'external_access': self.external_access(self.afcw_access.data, self.third_pty_access.data),

            'payment_method': self.payment_method.data,
            'comment': self.comment.data,
            'upgrade': self.upgrade.data
        }
        if self.type.data == MembershipType.junior.value:
            member['jd_mail'] = self.jd_email.data.strip()
            member['jd_gift'] = self.jd_gift.data

        member = save_member_contact_details(member_number, member, self.renewal.data)

        # return key info for save message
        payment_method = PaymentMethod.from_value(self.payment_method.data)
        upgrade = self.upgrade.data
        member_type = member.long_membership_type() + (' (DT Plus)' if upgrade else '')
        dues = member.dues() + (member.upgrade_dues() if upgrade else 0)
        if member.is_recent_renewal() and not upgrade:
            dues = -1
        paypal_payment = self.get_paypal_payment(payment_method, member, upgrade)
        return payment_method, paypal_payment, dues, member_type, member

    @staticmethod
    def get_paypal_payment(payment_method, member, upgrade):
        if payment_method == PaymentMethod.cc:
            member_type = member.member_type_at_renewal()
            if member.status == MemberStatus.life:
                return None
            new_member = member.is_recent_new() or member.is_recent_renewal()
            if new_member:
                if member_type == MembershipType.junior:
                    return None
                elif member_type in MembershipType.all_concessions(plus=True):
                    return PayPalPayment.Dons_Trust_Plus_Concession_upgrade if upgrade else None
                elif member_type == MembershipType.standard:
                    return PayPalPayment.Dons_Trust_Plus_Adult_upgrade if upgrade else None
            else:
                if member_type == MembershipType.junior:
                    return PayPalPayment.Junior_Dons_renewal
                elif member_type in MembershipType.all_concessions(plus=True):
                    return PayPalPayment.Dons_Trust_Plus_Concession if upgrade else PayPalPayment.Concession
                elif member_type == MembershipType.standard:
                    return PayPalPayment.Dons_Trust_Plus_Adult if upgrade else PayPalPayment.Adult
        else:
            return None

    @staticmethod
    def external_access(afcw, third_pty):
        access = ExternalAccess.none
        if afcw:
            access = ExternalAccess.AFCW
        if third_pty:
            access = ExternalAccess.all
        return access
