from globals.enumerations import MemberStatus, MembershipType, PaymentMethod, PaymentType, MemberAction, UserRole, ActionStatus
from main import db
from models.dt_db import Member, Address, User, Payment, Action, Comment
from sqlalchemy import text, and_, func
import datetime

from back_end.data_utilities import first_or_default
from globals import config
from back_end.file_access import get_records, update_html_elements, get_file_contents

db_session = db.session


# region Members
def get_member_by_email(email):
    # case-insensitive
    return db_session.query(Member).filter(func.lower(Member.email) == func.lower(email)).first()


def get_member(member_id):
    return db_session.query(Member).filter_by(id=member_id).first()


def get_new_member():
    member = Member()
    member.address = get_new_address()
    return member


def get_member_by_name(name):
    res = get_members_by_name(name)
    if len(res) == 0:
        return None
    else:
        return res.first()


def get_members_by_name(name):
    name = name.split(' ')
    if len(name) == 2:
        return db_session.query(Member).filter(and_(
            func.lower(Member.first_name) == func.lower(name[0]),
            func.lower(Member.last_name) == func.lower(name[1])
        ))
    elif len(name) == 1:
        return db_session.query(Member).filter(func.lower(Member.last_name) == func.lower(name[0]))
    else:
        return []


def get_members_by_status(status):
    members = db_session.query(Member).filter_by(status=status)
    return members


def get_all_members(select_fields):
    tables = list(set([globals()[t[0]] for t in [['Member']] + select_fields]))
    select = []
    for field in select_fields:
        table, column, value, condition = field
        type, values = field_type(globals()[table], column)
        if type == 'string':
            if condition == '=':
                s = 'lower({}) like lower("%{}%")'.format(column, value)
            else:
                s = '{} {} "{}"'.format(column, condition, value)
        elif type == 'enum':
            s = '{} {} {}'.format(column, condition, value)
        else:
            s = '{} {} {}'.format(column, condition, value)
        select.append(s)
    q = db_session.query(tables[0])
    for table in tables[1:]:
        q = q.join(table)
    if len(select) > 0:
        statement = ' and '.join(select)
        return q.filter(text(statement))
    else:
        return q


def get_all_members_old(select_fields):
    # if current:
    #     return db_session.query(Member) \
    #         .filter(Member.status.in_([MemberStatus.current, MemberStatus.founder, MemberStatus.life]))
    # else:
    #     return db_session.query(Member)
    tables = [Member]
    select = []
    for field in select_fields:
        field_name = field.label.text
        if '.' in field_name:
            table, field_name = field_name.split('.')
            table = globals()[table]
            if table not in tables:
                tables.append(table)
        else:
            table = tables[0]
        type, values = field_type(table, field_name)
        if type == 'string':
            s = 'lower({}) like lower("%{}%")'.format(field_name, field.data)
        elif type == 'enum':
            s = '{} = {}'.format(field_name, field.data.value)
        else:
            s = '{} = {}'.format(field_name, field.data)
        select.append(s)
    q = db_session.query(tables[0])
    for table in tables[1:]:
        q = q.join(table)
    if len(select) > 0:
        statement = ' and '.join(select)
        return q.filter(text(statement))
    else:
        return q


def save_member(member_id, details):
    if member_id > 0:
        member = get_member(member_id)
    else:
        member = get_new_member()
        db_session.add(member)

    member.title = details['title']
    member.first_name = details['first_name']
    member.last_name = details['last_name']
    member.sex = details['sex']

    member.member_type = details['member_type']
    member.status = details['status']
    member.start_date = details['start_date']
    member.end_date = details['end_date']
    member.birth_date = details['birth_date']

    member.home_phone = details['home_phone']
    member.mobile_phone = details['mobile_phone']
    member.mobile_phone = details['mobile_phone']
    member.comms = details['comms']

    member.address.line_1 = details['line_1']
    member.address.line_2 = details['line_2']
    member.address.line_3 = details['line_3']
    member.address.city = details['city']
    member.address.state = details['state']
    member.address.post_code = details['post_code']
    member.address.county = details['county']
    member.address.country = details['country']

    payments = []
    for payment in details['payments']:
        if payment['amount'] is None:
            continue
        item = first_or_default([p for p in member.payments if p.date == payment['date']], None)
        if item:
            item.date = payment['date']
            item.type = payment['pay_type']
            item.amount = payment['amount']
            item.method = payment['method']
            item.comment = payment['comment']
        else:
            item = Payment(
                member_id=member_id,
                date=payment['date'],
                type=payment['pay_type'],
                amount=payment['amount'],
                method=payment['method'],
                comment=payment['comment']
            )
        payments.append(item)
    member.payments = payments

    actions = []
    for action in details['actions']:
        if action['action'] is MemberAction.none:
            continue
        item = first_or_default([a for a in member.actions if a.date == action['date']], None)
        if item:
            item.date = action['date']
            item.action = action['action']
            item.comment = action['comment']
            item.status = action['status']
        else:
            item = Action(
                member_id=member_id,
                date=action['date'],
                action=action['action'],
                comment=action['comment'],
                status=action['status']
            )
        actions.append(item)
    member.actions = actions

    comments = []
    for comment in details['comments']:
        if comment['comment'] in [None, '']:
            continue
        item = first_or_default([c for c in member.comments if c.date == comment['date']], None)
        if item:
            item.date = comment['date']
            item.comment = comment['comment']
        else:
            item = Comment(
                member_id=member_id,
                date=comment['date'],
                comment=comment['comment']
            )
        comments.append(item)
    member.comments = comments

    member.last_updated = datetime.date.today()

    db_session.commit()

# endregion


def get_user(id=None, user_name=None):
    if id:
        return db_session.query(User).filter(User.id == id).first()
    if user_name:
        return db_session.query(User).filter(User.user_name == user_name).first()


def save_user(user):
    if not user.id:
        db_session.add(user)
    db_session.commit()


def get_new_action(new_member=False):
    if new_member:
        return Action(
            date=datetime.date.today(),
            action=MemberAction.certificate,
            status=ActionStatus.open
        )
    return Action(date=datetime.date.today())


def get_new_comment():
    return Comment(
        date=datetime.date.today()
    )


def get_new_payment():
    return Payment(
        date=datetime.date.today(),
        type=PaymentType.dues,
        method=PaymentMethod.unknown
    )


def get_new_address():
    return Address()


def field_type(table, field_name):
    f_type = table.__table__.c[field_name].type
    type_name = str(f_type)
    data = None
    type = 'unknown'
    if 'VARCHAR' in type_name:
        type = 'string'
    else:
        if type_name == 'INTEGER':
            type = 'num'
        elif type_name == 'SMALLINT':
            if hasattr(f_type, 'data'):
                type = 'enum'
                data = f_type.data
            else:
                type = 'num'
        elif type_name == 'DATE':
            type = 'date'
    return type, data
