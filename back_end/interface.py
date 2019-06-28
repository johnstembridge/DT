from sqlalchemy import text, and_, func
import datetime
from flask import send_file
import io, csv

from globals.enumerations import MemberStatus, MembershipType, PaymentMethod, PaymentType, MemberAction, UserRole, ActionStatus, Sex, CommsType
from main import db
from models.dt_db import Member, Address, User, Payment, Action, Comment
from back_end.data_utilities import first_or_default, unique, pop_next

db_session = db.session


def save_object(object):
    if not object.id:
        db_session.add(object)
    db_session.commit()


# region Members
def get_member_by_email(email):
    # case-insensitive
    return db_session.query(Member).filter(func.lower(Member.email) == func.lower(email)).first()


def get_member(member_id):
    return db_session.query(Member).filter_by(id=member_id).first()


def get_new_member():
    member = Member()

    #member.id = 0
    member.first_name = 'new'
    member.last_name = 'member'
    member.status = MemberStatus.current
    member.member_type = MembershipType.standard
    member.sex = Sex.unknown
    member.start_date = datetime.date.today()
    member.end_date = datetime.date(year=2019, month=8, day=1)
    member.comms = CommsType.email

    member.address = get_new_address()

    return member


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


def select(select, where):
    return db_session.query(select).filter(*where)


def get_members_for_query(query_clauses, default_table='Member', limit=None):
    tables = unique([globals()[t[0]] for t in [[default_table]] + query_clauses])
    clauses = []
    for field in query_clauses:
        table, column, value, condition, func = field
        type, values = field_type(table, column)
        table = class_name_to_table_name(table)
        if type == 'string':
            if condition == '=':
                s = 'lower({}.{}) like lower("%{}%")'.format(table, column, value)
            else:
                s = '{}.{} {} "{}"'.format(table, column, condition, value)
        elif type == 'enum':
            s = '{}.{} {} {}'.format(table, column, condition, value)
        elif type == 'date':
            if not func:
                date = datetime.datetime.strptime(value, '%d/%m/%Y').date()
                s = '{}.{} {} "{}"'.format(table, column, condition, date)
            if func == 'month':
                s = 'strftime("%m", {}.{}){} "{:02}"'.format(table, column, condition, value)
            if func == 'age':
                if '>' in condition:
                    condition = condition.replace('>', '<')
                elif '<' in condition:
                    condition = condition.replace('<', '>')
                s = '{}.{} {} date("now", "-{} years")'.format(table, column, condition, value)
        else:
            s = '{}.{} {} {}'.format(table, column, condition, value)
        clauses.append(s)
    q = db_session.query(tables[0])
    for table in tables[1:]:
        q = q.join(table)
    if len(clauses) > 0:
        statement = ' and '.join(clauses)
        q = q.filter(text(statement))
    if limit:
        q = q.limit(limit)
    return q


def save_member(member_id, details):
    if member_id > 0:
        member = get_member(member_id)
    else:
        member = get_new_member()
        db_session.add(member)

    member.title = details['title'] if details['title'] > 0 else None
    member.first_name = details['first_name']
    member.last_name = details['last_name']
    member.sex = Sex(details['sex'])

    member.member_type = MembershipType(details['member_type'])
    member.status = MemberStatus(details['status'])
    member.start_date = details['start_date']
    member.end_date = details['end_date']
    member.birth_date = details['birth_date']

    member.home_phone = details['home_phone']
    member.mobile_phone = details['mobile_phone']
    member.comms = CommsType(details['comms'])
    member.comms_status = CommsType(details['comms_status'])

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
            item.type = PaymentType(payment['pay_type'])
            item.amount = payment['amount']
            item.method = PaymentMethod(payment['method']) if payment['method'] > 0 else None
            item.comment = payment['comment']
        else:
            item = Payment(
                member_id=member_id,
                date=payment['date'],
                type=PaymentType(payment['pay_type']),
                amount=payment['amount'],
                method=PaymentMethod(payment['method']) if payment['method'] > 0 else None,
                comment=payment['comment']
            )
        payments.append(item)
    member.payments = payments

    if len(payments) > 0:
        member.last_payment_method = [p.method for p in payments if p.date == max([p.date for p in payments])][0]

    actions = []
    for action in details['actions']:
        if action['action'] == 0:
            continue
        item = first_or_default([a for a in member.actions if a.date == action['date']], None)
        if item:
            item.date = action['date']
            item.action = MemberAction(action['action'])
            item.comment = action['comment']
            item.status = ActionStatus(action['status'])
        else:
            item = Action(
                member_id=member_id,
                date=action['date'],
                action=MemberAction(action['action']),
                comment=action['comment'],
                status=ActionStatus(action['status'])
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
        method=None
    )


def get_new_address():
    return Address()


def get_attr(obj, attr):
    attr, tail = pop_next(attr, '.')
    if '()' in attr:    # function call
        res = getattr(obj, attr.replace('()', ''))()
    elif '[]' in attr:  # list - get first
        res = first_or_default(getattr(obj, attr.replace('[]', '')), None)
    else:               # property
        res = getattr(obj, attr)
    if res and tail:
        res = get_attr(res, tail)
    return res


def class_name_to_table_name(name):
    if name.lower() == 'address':
        name = name + 'e'
    return name.lower() + 's'


def field_type(table, field_name):
    f_type = globals()[table].__table__.c[field_name].type
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


def list_to_csv_object(csv_list):
    csv_object = io.StringIO()
    writer = csv.writer(csv_object)
    writer.writerows(csv_list)
    return csv_object


def stringIO_to_bytesIO(stringIO_object):
    # Creating a bytesIO object from a StringIO Object
    bytesIO_object = io.BytesIO()
    bytesIO_object.write(stringIO_object.getvalue().encode('utf-8'))
    # seeking was necessary. Python 3.5.2, Flask 0.12.2
    bytesIO_object.seek(0)
    stringIO_object.close()
    return bytesIO_object


def return_csv_file(csv_list, file_name):
    return return_file(stringIO_to_bytesIO(list_to_csv_object(csv_list)), file_name)


def return_file(file_path_or_object, filename, mime_type='text/csv'):
    try:
        return send_file(file_path_or_object, mimetype=mime_type, attachment_filename=filename, as_attachment=True)
    except Exception as e:
        return str(e)
