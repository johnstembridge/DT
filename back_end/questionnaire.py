from enum import Enum
from globals.enumerations import YesNo
from back_end.data_utilities import first_or_default


class Questionnaire():
    def __init__(self, questions):
        self.questions = {q.id:q for q in questions}


class Question():
    def __init__(self, id, text, description, choices):
        self.id = id
        self.text = text
        self.description = description
        self.choices = choices


class QuestionId(Enum):
    ParentalConsent = 0
    Gender = 1
    GenderIdentify = 2
    Disability = 3
    DisabilityType = 4
    Impairment = 5
    MaritalStatus = 6
    Ethnicity = 7
    SexualOrientation = 8
    Religion = 9
    EmploymentStatus = 10


def choice_number(choices, find_name):
    l = len(find_name)
    find_name = find_name.lower()
    return first_or_default([number for (number, name) in choices if name.lower()[:l] == find_name], None)


def choice_name(choices, find_number):
    return first_or_default([name for (number, name) in choices if number == find_number], None)


def get_question(question, choice):
    name = question.name
    choices = name + '_choices'
    if choices not in locals():
        choices = name + 'yes_no_choices'
    return question.name, locals()[choices][choice]


def get_answer(member, question, single=True, other=False):
    if other:
        ret = [q.other for q in member.qandas if q.question_id == question]
    else:
        ret = [q.answer for q in member.qandas if q.question_id == question]
    if single:
        return first_or_default(ret, None)
    else:
        return ret


def diversity_questionnaire():
    return Questionnaire([
        Question(
            id=QuestionId.ParentalConsent,
            text='Parental Consent',
            description='Parent/Guardian approval for diversity data to be shared',
            choices=YesNo
        ),
        Question(
            id=QuestionId.Gender,
            text='Gender',
            description='What is your gender?',
            choices=gender_choices
        ),
        Question(
            id=QuestionId.GenderIdentify,
            text='Gender Identification',
            description='Do you identify as trans?',
            choices=yes_no_choices
        ),
        Question(
            id=QuestionId.Disability,
            text='Disability',
            description='The Equality Act 2010 defines disability as ‘a physical or mental impairment which has a substantial & long-term effect on a person’s ability to carry out normal day to day activities’. Do you consider yourself to have a disability, impairment, learning difference or long-term condition?',
            choices=yes_no_choices
        ),
        Question(
            id=QuestionId.DisabilityType,
            text='Disability Type',
            description='If you have answered ‘yes’ to the question above, what best describes your disability, impairment, learning difference or long-term condition (please tick all that apply)',
            choices=disability_types
        ),
        Question(
            id=QuestionId.Impairment,
            text='Impairment',
            description='Does your condition or illness/do any of your conditions or illnesses reduce your ability to carry out day-to-day activities?',
            choices=impairment_choices
        ),
        Question(
            id=QuestionId.MaritalStatus,
            text='Marital Status',
            description='Are you married or in a civil partnership?',
            choices=yes_no_choices
        ),
        Question(
            id=QuestionId.Ethnicity,
            text='Ethnicity',
            description='Please choose one of the following options that most accurately describes your ethnic group or background',
            choices=ethnicity_choices
        ),
        Question(
            id=QuestionId.SexualOrientation,
            text='Sexual Orientation',
            description='What is your sexual orientation?',
            choices=sexual_orientation_choices
        ),
        Question(
            id=QuestionId.Religion,
            text='Religion or belief',
            description='What is your Religion or belief?',
            choices=religion_choices
        ),
        Question(
            id=QuestionId.EmploymentStatus,
            text='Employment Status',
            description='In the past 12 months, what has been your employment status for the majority of that time?',
            choices=employment_choices
        )
    ])


gender_choices = [
    (0, ''),
    (1, 'Man'),
    (2, 'Non-binary / gender fluid'),
    (3, 'Woman'),
    (4, 'Prefer not to say'),
    (5, 'Other (please state)')
]

yes_no_choices = [
    (0, ''),
    (1, 'Yes'),
    (2, 'No'),
    (3, 'Prefer not to say')
]

disability_types = [
    (1, 'Two or more impairments and/or long-term conditions'),
    (2, 'A specific learning difference such as dyslexia, dyspraxia or AD(H)D'),
    (3, 'General learning disability (such as Down’s syndrome)'),
    (4, 'A social/communication impairment such as Asperger’s syndrome/other autistic spectrum disorder'),
    (5, 'A long-standing illness or health condition such as cancer, HIV, diabetes, chronic heart disease or epilepsy'),
    (6, 'A mental health condition, such as depression, schizophrenia or anxiety disorder'),
    (8, 'A physical impairment or mobility issues, such as difficulty using arms or using a wheelchair or crutches'),
    (9, 'Deaf or serious hearing impairment'),
    (10, 'Blind or a serious visual impairment uncorrected by glasses'),
    (11, 'I prefer not to say')
]

impairment_choices = [
    (0, ''),
    (1, 'Yes, a lot'),
    (2, 'Yes, a little'),
    (3, 'Prefer not to say')
]

ethnicity_choices = (
    (0, ''),
    ('White', (
        (1, 'English / Welsh / Scottish / Northern Irish / British'),
        (2, 'Irish'),
        (3, 'Gypsy or Irish Traveller'),
        (4, 'Other White background (please state)')
    )),
    ('Asian / Asian British', (
        (5, 'Indian'),
        (6, 'Pakistani'),
        (7, 'Bangladeshi'),
        (8, 'Chinese')
    )),
    ('Black African/Caribbean/Black British', (
        (9, 'African'),
        (10, 'Caribbean')
    )),
    ('Other ethnic group', (
        (11, 'Arab'),
    )),
    (12, 'Prefer not to say'),
    (13, 'Other (please state)')
)

sexual_orientation_choices = [
    (0, ''),
    (1, 'Bisexual / Pansexual'),
    (2, 'Gay man'),
    (3, 'Gay woman / lesbian'),
    (4, 'Heterosexual / straight'),
    (5, 'Asexual'),
    (6, 'Prefer not to say')
]

religion_choices = [
    (0, ''),
    (1, 'Buddhist'),
    (2, 'Christian'),
    (3, 'Hindu'),
    (4, 'Jewish'),
    (5, 'Muslim'),
    (6, 'Sikh'),
    (7, 'No religion or atheist'),
    (8, 'Prefer not to say'),
    (9, 'Other (please state)')
]

employment_choices = [
    (0, ''),
    (1, 'Agency staff (hired on a temporary basis through an agency)'),
    (2, 'Permanent contract (hired on a permanent basis)'),
    (3, 'Fixed-term contracts (hired on a temporary basis)'),
    (5, 'Self-employed without employees e.g. freelancer trading as an individual (sole trader) or limited company (Ltd)'),
    (6, 'Self-employed with employees'),
    (7, 'Zero-hour contracts (hired on a temporary basis through a zero hour contract)'),
    (8, 'Intern (paid)'),
    (9, 'Apprentice'),
    (10, 'Volunteer (unpaid)'),
    (11, 'Student'),
    (12, 'Unemployed'),
    (13, 'Retired'),
    (14, 'Prefer not to say'),
    (15, 'Other (please state)')
]