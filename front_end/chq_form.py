from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

from front_end.form_helpers import ReadOnlyWidget
from back_end.interface import get_member


class RenewalChequeForm(FlaskForm):
    dt_number = StringField(label='DT number')
    amount = StringField(label='Renewal amount')
    description = StringField(label='Renewal')
    submit = SubmitField(label='Save')

    def populate(self, member_id, upgrade):
        member = get_member(member_id)
        payment = member.last_payment()
        self.description = member.long_membership_type(upgrade)
        self.dt_number.data = member.dt_number()
        self.amount.data = payment.amount

    def make_readonly(self, field):
        prop = getattr(self, field)
        setattr(prop, 'widget', ReadOnlyWidget())
