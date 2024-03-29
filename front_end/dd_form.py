from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField

from front_end.form_helpers import ReadOnlyWidget
from back_end.interface import get_member
from globals.enumerations import MemberStatus, MembershipType, PaymentMethod, EmandatePaymentPlan
import globals.config as config
from back_end.data_utilities import fmt_curr, append_file, create_data_file, file_exists, path_join


class RenewalDebitForm(FlaskForm):
    account_name = StringField(label='Bank account name')
    account_number = StringField(label='Bank account number')
    account_sort = StringField(label='Bank account sort code')
    dt_number = StringField(label='Payment reference')
    amount = StringField(label='Amount to be debited on 11th August ')
    description = StringField(label='Renewal')
    submit = SubmitField(label='Save')

    def populate(self, member_id, upgrade, downgrade):
        member = get_member(member_id)
        payment = member.last_payment()
        self.description = member.long_membership_type(upgrade=upgrade, downgrade=downgrade)
        self.dt_number.data = member.dt_number()
        self.amount.data = payment.amount

    def save(self, member_id):
        file = path_join(config.get('locations')['export'], 'b_details.csv')
        # if not file_exists(file):
        #     create_data_file(file, ['member_id', 'name', 'number', 'sort'])
        name = self.account_name.data
        number = self.account_number.data
        sort = self.account_sort.data

        rec = '\r' + ','.join([str(member_id), name, number, sort])
        append_file(file, rec)

        return get_member(member_id)

    def make_readonly(self, field):
        prop = getattr(self, field)
        setattr(prop, 'widget', ReadOnlyWidget())


class MemberDebitForm(FlaskForm):
    return_url = HiddenField(label='Return URL')
    payment_plan = StringField(label='Payment Plan')
    txtQuestion1 = StringField(label='Membership number')

    txtTitle = StringField(label='Title')
    txtFirstName = StringField(label='First')
    txtSurname = StringField(label='Last')

    addr1 = StringField(label='Address line 1')
    addr2 = StringField(label='Address line 2')
    addr3 = StringField(label='Address line 3')
    addr4 = StringField(label='County')
    txtAddressTown = StringField(label='Town/City')
    searchPostCode = StringField(label='Post Code')

    txtPhone = StringField(label='Home Phone')
    txtMobile = StringField(label='Mobile')
    txtEmail = StringField(label='Email ')

    txtRegularAmount = StringField(label='Dues')
    txtAccNumArr = StringField(label='Bank Account Number')
    txtSortArr = StringField(label='Bank Sort Code')
    txtAccountHolders = StringField(label="Account holder's name")

    arrayvars = HiddenField()

    submit = SubmitField(label='Create Debit')

    def populate_member(self, member_number, return_url, upgrade):
        self.return_url.data = return_url
        member = get_member(member_number)
        dues = member.base_dues() + (member.upgrade_dues() if upgrade else 0)
        self.payment_plan.data = self.get_dd_payment_plan(PaymentMethod.dd, member, upgrade).value
        self.txtQuestion1.data = member.dt_number()
        self.txtRegularAmount.data = fmt_curr(dues)[1:]

        address = member.address
        self.txtTitle.data = member.title.name if member.title else ''
        self.txtFirstName.data = member.first_name
        self.txtSurname.data = member.last_name

        self.addr1.data = address.line_1
        self.addr2.data = address.line_2
        self.addr3.data = address.line_3
        self.addr4.data = address.county.name if address.county else ''
        self.txtAddressTown.data = address.city
        self.searchPostCode.data = address.post_code
        self.txtPhone.data = member.home_phone
        self.txtMobile.data = member.mobile_phone
        self.txtEmail.data = member.email

        self.arrayvars.data = "dt_number*|*{}*|*amount*|*{}".format(member.dt_number(), fmt_curr(dues)[1:])

        return ''  # member.renewal_activated()

    @staticmethod
    def get_dd_payment_plan(payment_method, member, upgrade):
        if payment_method == PaymentMethod.dd:
            plus = upgrade or member.status == MemberStatus.plus
            member_type = member.member_type_at_renewal()
            if member.status == MemberStatus.life:
                return None
            new_member = member.is_recent_new() or member.is_recent_resume()
            if member_type == MembershipType.junior:
                if new_member:
                    return EmandatePaymentPlan.Junior_Dons_new
                else:
                    return EmandatePaymentPlan.Junior_Dons_renewal
            elif member_type in MembershipType.concessions(all=True):
                return EmandatePaymentPlan.Dons_Trust_Plus_Concession if plus else EmandatePaymentPlan.Concession
            elif member_type == MembershipType.standard:
                return EmandatePaymentPlan.Dons_Trust_Plus_Adult if plus else EmandatePaymentPlan.Adult
        else:
            return None