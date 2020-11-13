from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import InputRequired
from wtforms.fields.html5 import DateField

from front_end.form_helpers import MySelectField
from globals.enumerations import MembershipType


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
