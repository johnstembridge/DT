from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, BooleanField
from wtforms.validators import InputRequired, Optional, Email
from wtforms.fields.html5 import DateField

from back_end.interface import get_member, save_member_contact_details, country_choices, county_choices, state_choices, \
    get_country, get_county, get_state, get_junior
from front_end.form_helpers import MySelectField, read_only_form
from globals.enumerations import MemberStatus, MembershipType, Sex, CommsType, PaymentType, PaymentMethod, MemberAction, \
    ActionStatus, Title, CommsStatus, JuniorGift, ExternalAccess, UserRole
from back_end.data_utilities import fmt_date
import datetime


class CommentItemForm(FlaskForm):
    date = DateField(label='Date')
    comment = StringField(label='Comment')


class RenewalPaymentForm(FlaskForm):
    last_updated = StringField(label='Last Update')
    full_name = StringField(label='Full Name')
    return_url = HiddenField(label='Return URL')
    member_number = HiddenField(label='Member Number')
    dt_number = StringField(label='Id')
    type = MySelectField(label='Type', choices=MembershipType.renewal_choices(), coerce=MembershipType.coerce)
    start_date = StringField(label='Start')
    birth_date = DateField(label='Date of Birth', validators=[InputRequired()])
