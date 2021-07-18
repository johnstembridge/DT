from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, BooleanField

from back_end.interface import get_member, update_member_questions
from front_end.form_helpers import MultiCheckboxField
from front_end.extended_select import SelectFieldWithOptGroup
from back_end.questionnaire import diversity_questionnaire, QuestionId, get_answer


def diversity_fields():
    dq = diversity_questionnaire().questions
    q = dq[QuestionId.ParentalConsent]
    parental_consent = BooleanField(label=q.text, description=q.description)
    q = dq[QuestionId.Gender]
    gender = SelectField(label=q.text, choices=q.choices, coerce=int, description=q.description)
    gender_other = StringField(label='Other (please state)')
    q = dq[QuestionId.GenderIdentify]
    gender_identify = SelectField(label=q.text, choices=q.choices, coerce=int, description=q.description)
    q = dq[QuestionId.Disability]
    disability = SelectField(label=q.text, choices=q.choices, coerce=int, description=q.description)
    q = dq[QuestionId.DisabilityType]
    disability_type = MultiCheckboxField(label=q.text, choices=q.choices, coerce=int, description=q.description)
    disability_type_other = StringField(label='Other (please state)')
    q = dq[QuestionId.Impairment]
    impairment = SelectField(label=q.text, choices=q.choices, coerce=int, description=q.description)
    q = dq[QuestionId.MaritalStatus]
    marital_status = SelectField(label=q.text, choices=q.choices, coerce=int, description=q.description)
    q = dq[QuestionId.Ethnicity]
    ethnicity = SelectFieldWithOptGroup(label=q.text, choices=q.choices, coerce=int, description=q.description)
    ethnicity_other = StringField(label='Other (please state)')
    q = dq[QuestionId.SexualOrientation]
    sexual_orientation = SelectField(label=q.text, choices=q.choices, coerce=int, description=q.description)
    q = dq[QuestionId.Religion]
    religion = SelectField(label=q.text, choices=q.choices, coerce=int, description=q.description)
    religion_other = StringField(label='Other (please state)')
    q = dq[QuestionId.EmploymentStatus]
    employment = SelectField(label=q.text, choices=q.choices, coerce=int, description=q.description)
    employment_other = StringField(label='Other (please state)')
    return (parental_consent, gender, gender_other, gender_identify, disability, disability_type, disability_type_other,
            impairment, marital_status, ethnicity, ethnicity_other, sexual_orientation, religion, religion_other,
            employment, employment_other)


class DiversityForm(FlaskForm):
    form_type = HiddenField(label='Form Type')
    full_name = StringField(label='Full Name')
    return_url = HiddenField(label='Return URL')
    member_number = HiddenField(label='Member Number')
    (parental_consent, gender, gender_other, gender_identify, disability, disability_type, disability_type_other, impairment,
     marital_status, ethnicity, ethnicity_other, sexual_orientation, religion, religion_other, employment,
     employment_other) = diversity_fields()

    submit = SubmitField(label='Save')

    def populate_member(self, member_number, return_url, renewal):
        self.return_url.data = return_url
        self.form_type.data = 'renewal' if renewal else 'details'
        member = get_member(member_number)
        if not member.junior:
            self.parental_consent = None
        self.gender.data = get_answer(member, QuestionId.Gender)
        self.gender_identify.data = get_answer(member, QuestionId.GenderIdentify)
        self.disability.data = get_answer(member, QuestionId.Disability)
        self.disability_type.data = get_answer(member, QuestionId.DisabilityType, single=False)
        self.disability_type_other.data = get_answer(member, QuestionId.DisabilityType, other=True)
        self.impairment.data = get_answer(member, QuestionId.Impairment)
        self.marital_status.data = get_answer(member, QuestionId.MaritalStatus)
        self.ethnicity.data = get_answer(member, QuestionId.Ethnicity)
        self.ethnicity_other.data = get_answer(member, QuestionId.Ethnicity, other=True)
        self.sexual_orientation.data = get_answer(member, QuestionId.SexualOrientation)
        self.religion.data = get_answer(member, QuestionId.Religion)
        self.religion_other.data = get_answer(member, QuestionId.Religion, other=True)
        self.employment.data = get_answer(member, QuestionId.EmploymentStatus)
        self.employment_other.data = get_answer(member, QuestionId.EmploymentStatus, other=True)

    def save_member(self, member_number):
        qandas = [(QuestionId.Gender, self.gender.data, self.gender_other.data),
                  (QuestionId.GenderIdentify, self.gender_identify.data, None),
                  (QuestionId.Disability, self.disability.data, None),
                  (QuestionId.DisabilityType, self.disability_type.data, self.disability_type_other.data),
                  (QuestionId.Impairment, self.impairment.data, None),
                  (QuestionId.MaritalStatus, self.marital_status.data, None),
                  (QuestionId.Ethnicity, self.ethnicity.data, self.ethnicity_other.data),
                  (QuestionId.SexualOrientation, self.sexual_orientation.data, None),
                  (QuestionId.Religion, self.religion.data, self.religion_other.data),
                  (QuestionId.EmploymentStatus, self.employment.data, self.employment_other.data)]
        if type(member_number) == int:
            member = get_member(member_number)
        else:
            member = member_number
        update_member_questions(member, qandas)
        return member
