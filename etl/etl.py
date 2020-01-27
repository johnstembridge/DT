import csv
import re
import os
from datetime import date

from models.dt_db import Member, Address, Payment, Comment, Action, Junior, Country, County, State, User
from globals.enumerations import MemberStatus, MembershipType, Sex, Title, CommsType, PaymentMethod, PaymentType, \
    CommsStatus, MemberAction, ActionStatus, ExternalAccess, JuniorGift, UserRole
from back_end.data_utilities import parse_date, valid_date, force_list, file_delimiter


def process_etl(import_path, file_in, session, etl_fn):
    global db_session
    db_session = session
    file_in = os.path.join(import_path, file_in)
    print('Importing ' + file_in)
    with open(file_in, 'r', encoding='UTF-8') as in_file:
        reader = csv.DictReader(in_file, delimiter=file_delimiter(file_in))
        count = 0
        for row in reader:
            count += 1
            if count % 100 == 0:
                if 'Member ID' in row.keys():
                    print('Processing ' + row['Member ID'])
            obj = etl_fn(row)
            save_object(obj)


def user_etl(rec):
    if rec == 'header':
        return ['member_number', 'user_name', 'role', 'password']
    user = User(
        member_id=get_member_id(rec['member_number']),
        user_name=rec['user_name']
    )
    user.set_password(rec['password'])
    user.role = UserRole.from_name(rec['role'])
    return user


def country_etl(rec):
    country = Country(
        code=rec['code'],
        name=rec['name'],
    )
    return country


def county_etl(rec):
    county = County(
        name=rec['name'],
    )
    return county


def state_etl(rec):
    state = State(
        code=rec['code'],
        name=rec['name'],
    )
    return state


def address_etl(rec):
    address = Address(
        line_1=rec['Address Line 1'],
        line_2=rec['Address Line 2'],
        line_3=rec['Address Line 3'],
        city=rec['City'],
        county_id=get_county_id(rec['County']),
        state_id=get_state_id(rec['State/Province']),
        post_code=rec['ZIP/Post Code'],
        country_id=get_country_id(rec['Country Code'])
    )
    return address


def member_etl(rec):
    member = Member(
        number=int(rec['Member ID'][2:]),  # drop "0-"
        sex=Sex.male if rec['Sex'] == 'M' else Sex.female if rec['Sex'] == 'F' else None,
        title=Title[rec['Prefix']] if rec['Prefix'] != '' else None,
        first_name=rec['First Name'],
        last_name=rec['Last Name'],
        birth_date=parse_date(rec['Birthdate'], sep='/', reverse=True, default=None),
        email=rec['Email Address'],
        home_phone=rec['Home Phone'],
        mobile_phone=rec['Other Phone'],
        status=status_etl[rec['Status Code']],
        start_date=parse_date(rec['Start Date'], sep='/', reverse=True),
        end_date=parse_date(rec['End Date'], sep='/', reverse=True),
        last_updated=parse_date(rec['Updated'], sep='/', reverse=True),
        last_payment_method=PaymentMethod[rec['Direct Debit']] if rec['Direct Debit'] != '' else None,
        external_access=external_access_etl(rec),
        comms=CommsType.email if rec['Use email'] == 'yes' else CommsType.post,
        comms_status=CommsStatus.email_fail if (rec['Email Address'] != '') and (
                rec['Use email'] == 'bounced') else CommsStatus.all_ok,
        address=address_etl(rec),
        actions=actions_etl(rec)
    )
    member.member_type = type_etl(member, rec['Status Code'], rec['Concession Type'])
    if member.member_type == MembershipType.junior:
        member.junior = Junior(
            email=rec['Junior email'],
            gift=junior_gift_etl[rec['Junior Gift']] if rec['Junior Gift'] != '' else None
        )
    return member


status_etl = {
    'LIF': MemberStatus.life,
    'JLF': MemberStatus.life,
    'FJ': MemberStatus.founder,
    'FI': MemberStatus.founder,
    'F': MemberStatus.founder,
    'S': MemberStatus.current,
    'J': MemberStatus.current,
    'I': MemberStatus.current,
    'H': MemberStatus.current,
    'L': MemberStatus.lapsed,
    'SUS': MemberStatus.suspended,
    'N': MemberStatus.cancelled,
    'X': MemberStatus.cancelled,
    'R': MemberStatus.reserved,
    'D': MemberStatus.deceased
}

junior_gift_etl = {
    'Lunchbox': JuniorGift.LunchBox,
    'Building bricks': JuniorGift.BuildingBricks,
    'Baseball cap': JuniorGift.BaseballCap,
    'Mini football': JuniorGift.MiniFootball
}


def type_etl(member, old_status, old_concession_type):
    concession_type_map = {
        'Senior': MembershipType.senior,
        'Senior+Donation': MembershipType.senior,
        'Incapacity': MembershipType.incapacity,
        'Job Seeker': MembershipType.job_seeker,
        'Student': MembershipType.student,
        'Young Adult': MembershipType.intermediate
    }
    if member.is_active():
        type = {
            'LIF': MembershipType.standard,
            'JLF': MembershipType.junior,
            'FJ': MembershipType.junior,  # if age < 16 else MembershipType.intermediate,
            'FI': MembershipType.intermediate,
            'F': MembershipType.standard,
            'S': MembershipType.standard,
            'J': MembershipType.junior,  # if age < 16 else MembershipType.intermediate,
            'I': MembershipType.intermediate,
            'H': MembershipType.honorary
        }[old_status]
        if type == MembershipType.standard and old_concession_type != '':
            type = concession_type_map[old_concession_type]
    else:
        age = member.age(default=True)
        if age < 16:
            type = MembershipType.junior
        elif age < 21:
            type = MembershipType.intermediate
        elif age > 60:
            type = MembershipType.senior
        else:
            type = MembershipType.standard
        if type == MembershipType.standard and old_concession_type != '':
            type = concession_type_map[old_concession_type]
    return type


def external_access_etl(rec):
    afc = rec['AFC has access']
    pty = rec['3rdPty have acc']
    if afc == 'no':
        return ExternalAccess.none
    if afc == 'yes':
        if pty == 'yes':
            return ExternalAccess.all
        else:
            return ExternalAccess.AFCW


def actions_etl(rec):
    actions = []
    card = rec['Card']
    action = None
    if 'new' in card:
        action = Action(action=MemberAction.certificate)
    if 'replacement' in card:
        action = Action(action=MemberAction.replacement)
    if 'print' in card:
        action = Action(action=MemberAction.card)
    if 'resend' in card:
        action = Action(action=MemberAction.resend)
    elif 'send' in card:
        action = Action(action=MemberAction.send)
    elif 'upgrade' in card:
        action = Action(action=MemberAction.upgrade)
    if action:
        action.date = date.today()
        action.status = ActionStatus.open
        action.comment = 'from import: {}'.format(card)
        actions.append(action)
    return actions


def donation_etl(rec):
    header = ['Member ID', 'Donation Date Posted', 'Donation Amount Posted', 'Donation Posting Type',
              'Donation Cheque Nbr', 'Donation Comments']
    payment = Payment(
        member_id=get_member_id(int(rec['Member ID'][2:])),  # drop "0-"
        date=parse_date(rec['Donation Date Posted'], sep='/', reverse=True),
        amount=float(rec['Donation Amount Posted']),
        type=PaymentType.donation,
        method=payment_method_etl(rec['Donation Cheque Nbr']),
        comment=rec['Donation Comments']
    )
    return payment


def payment_etl(rec):
    header = ['Member ID', 'Dues Date Posted', 'Dues Amount Posted', 'Dues Posting Type', 'Dues Cheque Nbr',
              'Dues Comments']
    payment = Payment(
        member_id=get_member_id(int(rec['Member ID'][2:])),  # drop "0-"
        date=parse_date(rec['Dues Date Posted'], sep='/', reverse=True),
        amount=float(rec['Dues Amount Posted']),
        type=PaymentType.dues,
        method=payment_method_etl(rec['Dues Cheque Nbr']),
        comment=rec['Dues Comments']
    )
    return payment


payment_method_map = {
    'cash': PaymentMethod.cash,
    'dd': PaymentMethod.dd,
    'cc': PaymentMethod.cc,
    'card': PaymentMethod.cc,
    'so': PaymentMethod.so,
    's/o': PaymentMethod.so,
    'credit xfer': PaymentMethod.xfer,
    'cheque': PaymentMethod.chq,
    'chq': PaymentMethod.chq,
}


def payment_method_etl(old):
    if old in payment_method_map.keys():
        return payment_method_map[old]
    return None


def comment_etl(rec):
    member_id = get_member_id(int(rec['Member ID'][2:]))  # drop "0-"
    recs = parse_comments(rec['Comments'].strip())
    objects = []
    for rec in recs:
        if rec['Comment'] == 'dd payment made':
            agedate = date(2019, 8, 1)
            paydate = parse_date(rec['Date'], sep='/', reverse=True)
            payment = Payment(
                member_id=member_id,
                date=paydate,
                amount=db_session.query(Member).filter_by(id=member_id).first().dues(agedate, default=True),
                type=PaymentType.dues,
                method=PaymentMethod.dd,
                comment=None
            )
            objects.append(payment)
        else:
            comment = Comment(
                member_id=member_id,
                date=parse_date(rec['Date'], sep='/', reverse=True),
                comment=rec['Comment']
            )
            objects.append(comment)
    return objects


def parse_comments(comment):
    items = re.split(r'(\d+/\d+/\d+):', comment.replace('"', ''))  # split on dates
    items = [i.strip() for i in items if i != '']
    if len(items) >= 1 and not valid_date(items[0]):
        items = ['01/01/2000'] + items
    if len(items) % 2 != 0:
        items = items + ['']
    items = zip(*[iter(items)] * 2)  # to pairs
    keys = ['Date', 'Comment']
    recs = []
    for item in items:
        recs.append(dict(zip(keys, item)))
    return recs


def save_object(objects):
    for object in force_list(objects):
        if not object.id:
            db_session.add(object)
        db_session.commit()


def get_member_id(member_number):
    return db_session.query(Member).filter(Member.number == member_number).first().id


def get_country_id(country_code):
    country = db_session.query(Country).filter(Country.code == country_code).first()
    if country:
        return country.id
    return None


def get_county_id(county_name):
    if county_name != '':
        county = db_session.query(County).filter(County.name == county_name).first()
        if county:
            return county.id
    return None


def get_state_id(state_code):
    if state_code != '':
        state = db_session.query(State).filter(State.code == state_code).first()
        if state:
            return state.id
    return None
