from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, BooleanField, TextAreaField, RadioField
from wtforms.validators import InputRequired, Optional, Email
from wtforms.fields.html5 import DateField

from back_end.interface import get_member, save_member_contact_details, country_choices, county_choices, state_choices, \
    get_country, get_county, get_state, get_junior
from front_end.form_helpers import MySelectField
from front_end.diversity_form import diversity_fields, DiversityForm
from globals.enumerations import MemberStatus, MembershipType, Sex, CommsType, PaymentMethod, Title, CommsStatus, \
    JuniorGift, ExternalAccess, RenewalPayment, MemberAction, YesNo
from back_end.data_utilities import fmt_date


class MemberEditForm(FlaskForm):
    form_type = HiddenField(label='Form Type')
    last_updated = StringField(label='Last Update')
    full_name = StringField(label='Full Name')
    return_url = HiddenField(label='Return URL')
    member_number = HiddenField(label='Member Number')
    recent_new = HiddenField(label='Recent new')
    recent_resume = HiddenField(label='Recent resume')
    payment_required = HiddenField(label='payment required')
    current_payment_method = HiddenField(label='current payment method')
    dt_number = StringField(label='Id')

    start_date = StringField(label='Joined')
    birth_date = DateField(label='Date of Birth', validators=[InputRequired()])
    age = HiddenField(label='Age')
    fan_id = StringField(label='AFCW Fan ID')
    title = MySelectField(label='Title', choices=Title.choices(blank=True), coerce=Title.coerce)
    first_name = StringField(label='First', validators=[InputRequired()])
    last_name = StringField(label='Last', validators=[InputRequired()])
    sex = HiddenField(label='Sex')

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

    third_pty_access = BooleanField(label='Please indicate whether you wish to receive this information')

    upgrade = BooleanField(label='I wish to change my membership to Dons Trust Plus')
    payment_method = RadioField(label='Payment Method', choices=PaymentMethod.renewal_choices(),
                                   coerce=PaymentMethod.coerce)
    comment = TextAreaField(label='Please add any comments about the renewal here')
    previous_payment_method = HiddenField(label='Last Payment Method')
    notes = HiddenField(label='Notes')

    status = HiddenField(label='Member Status')
    access = HiddenField(label='User Access')
    plus = HiddenField(label='DT plus')
    type = MySelectField(label='Member Type', choices=MembershipType.renewal_choices(), coerce=MembershipType.coerce)

    (parental_consent, gender, gender_other, gender_identify, disability, disability_type, disability_type_other,
     impairment, marital_status, ethnicity, ethnicity_other, sexual_orientation, religion, religion_other, employment,
     employment_other) = diversity_fields()

    submit = SubmitField(label='Save')

    def populate_member(self, member_number, return_url, renewal):
        self.return_url.data = return_url
        self.form_type.data = 'renewal' if renewal else 'details'
        member = get_member(member_number)
        address = member.address
        self.member_number.data = str(member.number)
        self.recent_new.data = member.is_recent_new()
        self.recent_resume.data = member.is_recent_resume()
        self.payment_required.data = not (member.status == MemberStatus.life) and not (
                    member.status == MemberStatus.plus and member.is_recent_new() or member.is_recent_resume())
        self.current_payment_method.data = member.last_payment_method.value
        self.dt_number.data = member.dt_number()
        self.access.data = member.user.role.value if member.user else 0
        self.status.data = member.status.name
        self.plus.data = ' (Dons Trust Plus)' if member.status == MemberStatus.plus else ''
        self.type.data = member.member_type_at_renewal().value

        self.start_date.data = fmt_date(member.start_date)
        self.birth_date.data = member.birth_date
        self.age.data = str(member.age()) if member.age() is not None else None

        self.fan_id.data = member.season_ticket_id if member.season_ticket_id else ''
        self.external_access.data = (member.external_access or ExternalAccess.none).value
        self.last_updated.data = fmt_date(member.last_updated)

        self.full_name.data = member.full_name()
        self.title.data = member.title.value if member.title else ''
        self.first_name.data = member.first_name
        self.last_name.data = member.last_name
        self.sex.data = member.sex.value if member.sex else 0

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
            self.parental_consent.data = 1 if member.junior.parental_consent else 0
        else:
            self.jd_email = self.jd_gift = None

        self.third_pty_access.data = member.third_pty_access()

        self.payment_method.data = member.last_payment_method.value if member.last_payment_method else 0
        previous = member.previous_renewal_payment()
        self.previous_payment_method.data = previous.value if previous else 0

        self.upgrade.data = member.last_action() and member.last_action().action == MemberAction.upgrade

        self.notes.data = member.renewal_notes() + member.edit_notes()
        self.notes.data += [
            'This year we are collecting diversity information - please complete this section as well.', ]
        self.notes.data += [
            'We are also asking for your AFC Wimbledon Fan ID so please give this if you have one.', ]
        DiversityForm.populate_member(self, member_number, return_url, renewal)
        return member.renewal_activated()

    def save_member(self, member_number):
        member_details = {
            'title': self.title.data,
            'first_name': self.first_name.data.strip(),
            'last_name': self.last_name.data.strip(),
            'sex': int(self.sex.data),

            'member_type': self.type.data,
            'birth_date': self.birth_date.data,

            'access': int(self.access.data),
            'fan_id': self.fan_id.data,

            'home_phone': self.home_phone.data.strip(),
            'mobile_phone': self.mobile_phone.data.strip(),
            'email': self.email.data.strip(),
            'comms': self.comms.data,

            'line_1': self.line1.data.strip(),
            'line_2': self.line2.data.strip(),
            'line_3': self.line3.data.strip(),
            'city': self.city.data.strip(),
            'state': get_state(self.state.data),
            'post_code': self.post_code.data.strip(),
            'county': get_county(self.county.data),
            'country': get_country(self.country.data),

            'external_access': self.external_access(None, self.third_pty_access.data),

            'payment_method': self.payment_method.data,
            'comment': self.comment.data,
            'upgrade': self.upgrade.data
        }
        if self.type.data == MembershipType.junior.value:
            member_details['jd_mail'] = self.jd_email.data.strip()
            member_details['jd_gift'] = self.jd_gift.data
            member_details['parental_consent'] = YesNo.yes if self.parental_consent.data else YesNo.no

        # return key info for save message
        member = get_member(member_number)
        payment_method = PaymentMethod.from_value(self.payment_method.data)
        upgrade = self.upgrade.data
        member_type = member.long_membership_type(upgrade=upgrade)
        dues = member.base_dues() + (member.upgrade_dues() if upgrade and not member.is_pending_upgrade() else 0)
        if member.is_recent_resume() and not upgrade:
            dues = -1
        renewal_payment = self.get_renewal_payment(payment_method, member, upgrade)

        member = save_member_contact_details(member_number, member_details, self.form_type.data == 'renewal', False)
        member = DiversityForm.save_member(self, member)
        return payment_method, renewal_payment, dues, member_type, member

    def get_renewal_payment(self, payment_method, member, upgrade):
        if payment_method == PaymentMethod.cc:
            return self.renewal_payment(member, upgrade)
        elif payment_method == PaymentMethod.dd and \
                member.last_payment_type() == "pending" and member.last_payment_method != PaymentMethod.dd:
            return self.renewal_payment(member, upgrade)
        else:
            return self.renewal_payment(member, upgrade)

    def renewal_payment(self, member, upgrade):
        member_type = member.member_type_at_renewal()
        if member.status == MemberStatus.life:
            return None
        new_member = member.is_recent_new() or member.is_recent_resume()
        if new_member:
            if member_type == MembershipType.junior:
                return None
            elif member_type in MembershipType.concessions(all=True):
                return RenewalPayment.Dons_Trust_Plus_Concession_upgrade if upgrade else None
            elif member_type == MembershipType.standard:
                return RenewalPayment.Dons_Trust_Plus_Adult_upgrade if upgrade else None
        else:
            plus = upgrade or member.status == MemberStatus.plus
            if member_type == MembershipType.junior:
                return RenewalPayment.Junior_Dons_renewal
            elif member_type in MembershipType.concessions(all=True):
                return RenewalPayment.Dons_Trust_Plus_Concession if plus else RenewalPayment.Concession
            elif member_type == MembershipType.standard:
                return RenewalPayment.Dons_Trust_Plus_Adult if plus else RenewalPayment.Adult

    @staticmethod
    def external_access(afcw, third_pty):
        access = ExternalAccess.none
        if afcw:
            access = ExternalAccess.AFCW
        if third_pty:
            access = ExternalAccess.all
        return access
