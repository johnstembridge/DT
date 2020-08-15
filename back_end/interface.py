from sqlalchemy import text, and_, func
import datetime
from flask import send_file
import io, csv

from globals.enumerations import MemberStatus, MembershipType, PaymentMethod, PaymentType, MemberAction, ActionStatus, \
    Title, Sex, CommsType, CommsStatus, JuniorGift, ExternalAccess, UserRole
from main import db
from models.dt_db import Member, Address, User, Payment, Action, Comment, Junior, Country, County, State
from back_end.data_utilities import first_or_default, unique, pop_next, fmt_date, file_delimiter, current_year_end, \
    match_string


def save_object(object):
    if not object.id:
        db.session.add(object)
    db.session.commit()


def add_object(object):
    if not object.id:
        db.session.add(object)


def select(select, where):
    return db.session.query(select).filter(*where)


# region Members
def get_member_by_email(email):
    # case-insensitive
    return db.session.query(Member).filter(func.lower(Member.email) == func.lower(email)).first()


def get_member(member_number):
    member = db.session.query(Member).filter_by(number=member_number).first()
    if member and member.member_type == MembershipType.junior and not member.junior:
        member.junior = Junior()
    return member


def get_new_member():
    member = Member()
    member.number = 0
    member.first_name = 'new'
    member.last_name = 'member'
    member.status = MemberStatus.current
    member.member_type = MembershipType.standard
    member.sex = None
    member.start_date = datetime.date.today()
    member.end_date = datetime.date(2021, 8, 1) # current_year_end()
    member.comms = CommsType.email

    member.address = get_new_address()

    member.junior = Junior()

    return member


def get_junior():
    return Junior()


def get_members_by_name(name):
    name = name.split()
    if len(name) == 2:
        return db.session.query(Member).filter(and_(
            func.lower(Member.first_name) == func.lower(name[0]),
            func.lower(Member.last_name) == func.lower(name[1])
        )).all()
    elif len(name) == 1:
        return db.session.query(Member).filter(func.lower(Member.last_name) == func.lower(name[0])).all()
    else:
        return []


def reset_member_actions_for_query(query_clauses):
    for member in get_members_for_query(query_clauses):
        for action in [a for a in member.actions if a.status == ActionStatus.open]:
            action.status = ActionStatus.closed
        member.last_updated = datetime.date.today()
    db.session.commit()


def get_members_for_query(query_clauses, default_table='Member', limit=None):
    clauses = []
    tables = tables_needed_for_query(default_table, query_clauses)
    engine = db.session.bind.engine.name
    for field in query_clauses:
        if len(field) == 5:
            field = field + (default_table,)
        table, column, value, condition, func, field_name = field
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
            if func == 'birth_month()':
                if engine == 'sqlite':
                    s = 'strftime("%m", {}.{}){} "{:02}"'.format(table, column, condition, value)
                elif engine == 'mysql':
                    s = 'MONTH({}.{}){}{}'.format(table, column, condition, value)
                else:
                    s = 'Unknown engine: ' + engine
            if func == 'age()':
                if '>' in condition:
                    condition = condition.replace('>', '<')
                elif '<' in condition:
                    condition = condition.replace('<', '>')
                if engine == 'sqlite':
                    s = '{}.{} {} date("now", "-{} years")'.format(table, column, condition, value)
                elif engine == 'mysql':
                    s = '{}.{} {} date_add(current_date(), interval -{} year)'.format(table, column, condition, value)
                else:
                    s = 'Unknown engine: ' + engine
        else:
            s = '{}.{} {} {}'.format(table, column, condition, value)
        if isinstance(value, list):
            s = s.replace('[', '(').replace(']', ')')
        clauses.append(s)
    q = db.session.query(tables[0])

    for table in tables[1:]:
        q = q.join(table)
    if len(clauses) > 0:
        statement = ' and '.join(clauses)
        q = q.filter(text(statement))
    if globals()['Member'] in tables:
        q = q.order_by('number')
    if limit:
        q = q.limit(limit)
    return q


def tables_needed_for_query(default_table, query_clauses):
    # find all tables required for a query defined by query_clauses
    tables = unique([default_table] + [q[0] for q in query_clauses])
    # Address is also needed if any second level table is required
    second_level = ['Country', 'County', 'State']
    if ('Address' not in tables) and len([t for t in tables if t in second_level]) > 0:
        tables = [tables[0]] + ['Address'] + tables[1:]
    tables = [globals()[t] for t in tables]
    return tables


def save_member(member):
    member.last_updated = datetime.date.today()
    save_object(member)


def save_member_details(member_number, details):
    if member_number > 0:
        member = get_member(member_number)
    else:
        member = get_new_member()

    member.title = Title(details['title']) if details['title'] > 0 else None
    member.first_name = details['first_name']
    member.last_name = details['last_name']
    member.sex = Sex(details['sex']) if details['sex'] > 0 else None

    member.member_type = MembershipType(details['member_type'])
    member.status = MemberStatus(details['status'])
    member.start_date = details['start_date']
    member.end_date = details['end_date']
    member.birth_date = details['birth_date']

    role = UserRole.from_value(details['access'])
    if member.user:
        member.user.role = role
    elif role != UserRole.none:
        member.user = get_new_user(role)

        member.user.password = User.member_password(details['post_code'])

    member.season_ticket_id = int(details['season_ticket']) if details['season_ticket'] else None
    member.external_access = ExternalAccess(details['external_access'])

    member.home_phone = details['home_phone']
    member.mobile_phone = details['mobile_phone']
    member.email = details['email']
    member.comms = CommsType(details['comms'])
    member.comms_status = CommsStatus(details['comms_status'])

    member.address.line_1 = details['line_1']
    member.address.line_2 = details['line_2']
    member.address.line_3 = details['line_3']
    member.address.city = details['city']
    member.address.state = details['state']
    member.address.post_code = details['post_code']
    member.address.county = details['county']
    member.address.country = details['country']

    if member.member_type == MembershipType.junior:
        if not member.junior:
            member.junior = Junior()
        member.junior.email = details['jd_mail']
        member.junior.gift = JuniorGift(details['jd_gift']) if details['jd_gift'] and details['jd_gift'] > 0 else None

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
                member_id=member.id,
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
                member_id=member.id,
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
            item.comment = comment['comment']
        else:
            item = Comment(
                member_id=member.id,
                date=comment['date'],
                comment=comment['comment']
            )
        comments.append(item)
    member.comments = comments

    member.last_updated = datetime.date.today()

    if member.number == 0:
        member.number = next_member_number()
        db.session.add(member)

    db.session.commit()
    return member


def save_member_contact_details(member_number, details):
    if member_number > 0:
        member = get_member(member_number)
    else:
        member = get_new_member()

    member.title = Title(details['title']) if details['title'] > 0 else None
    member.first_name = details['first_name']
    member.last_name = details['last_name']
    member.sex = Sex(details['sex']) if details['sex'] > 0 else None

    member.member_type = MembershipType(details['member_type'])
    member.birth_date = details['birth_date']

    member.home_phone = details['home_phone']
    member.mobile_phone = details['mobile_phone']
    member.email = details['email']
    member.comms = CommsType(details['comms'])
    member.external_access = details['external_access']
    member.address.line_1 = details['line_1']
    member.address.line_2 = details['line_2']
    member.address.line_3 = details['line_3']
    member.address.city = details['city']
    member.address.state = details['state']
    member.address.post_code = details['post_code']
    member.address.county = details['county']
    member.address.country = details['country']

    if member.member_type == MembershipType.junior:
        if not member.junior:
            member.junior = get_junior()
        member.junior.email = details['jd_mail']
        member.junior.gift = JuniorGift(details['jd_gift']) if details['jd_gift'] and details['jd_gift'] > 0 else None

    if not member.member_type in MembershipType.all_concessions():
        member.type = member.member_type_next_renewal()

    dues = member.dues() + (member.upgrade_dues() if details['upgrade'] else 0)
    date = datetime.date.today()
    item = first_or_default([p for p in member.payments if p.type == PaymentType.pending], None)
    if member.status != MemberStatus.life:
        if item:
            item.date = date
            item.type = PaymentType.pending
            item.amount = dues
            item.method = PaymentMethod.from_value(details['payment_method']) if details['payment_method'] > 0 else None
            item.comment = 'renewal payment due'
        else:
            item = Payment(
                member_id=member.id,
                date=date,
                type=PaymentType.pending,
                amount=dues,
                method=PaymentMethod.from_value(details['payment_method']) if details['payment_method'] > 0 else None,
                comment='renewal payment due'
            )
            member.payments.append(item)
    if len(member.payments) > 0:
        member.last_payment_method = \
        [p.method for p in member.payments if p.date == max([p.date for p in member.payments])][0]

    if not details['comment'] in [None, '']:
        date = datetime.date.today()
        item = first_or_default([c for c in member.comments if c.date == date], None)
        if item:
            item.comment = details['comment']
        else:
            item = Comment(
                member_id=member.id,
                date=date,
                comment=details['comment']
            )
            member.comments.append(item)

    item = first_or_default(
        [a for a in member.actions if a.action == MemberAction.upgrade and a.date > datetime.date(2020, 7, 20)], None)
    if details['upgrade']:
        date = datetime.date.today()
        comment = 'Upgrade to DT plus'
        if item:
            item.action = MemberAction.upgrade
            item.comment = comment
            item.status = ActionStatus.open
        else:
            item = Action(
                member_id=member.id,
                date=date,
                action=MemberAction.upgrade,
                comment=comment,
                status=ActionStatus.open
            )
            member.actions.append(item)
    elif item:
        member.actions.remove(item)
    member.last_updated = datetime.date.today()

    if member.number == 0:
        member.number = next_member_number()
        db.session.add(member)

    db.session.commit()
    return member


def next_member_number():
    return db.session.query(func.max(Member.number)).scalar() + 1


# endregion


# region Users
def get_user(id=None, user_name=None):
    if id:
        return db.session.query(User).filter(User.id == id).first()
    if user_name:
        return db.session.query(User).filter(User.user_name == user_name).first()


def get_user_by_api_key(api_key):
    if ':' in api_key:
        user_name, password = api_key.split(':')
        return get_user(user_name=user_name)
    return db.session.query(User).query.filter_by(api_key=api_key).first()


def save_user(user):
    if not user.id:
        db.session.add(user)
    db.session.commit()


def get_new_user(role):
    return User(role=role)


# endregion


# region Addresses
def country_choices(blank=False, extra=None):
    countries = db.session.query(Country.id, Country.code, Country.name).order_by(Country.name).all()
    ret = [(c.id, c.name) for c in countries]
    if extra:
        ret = extra + ret
    if blank:
        ret = [(0, '')] + ret
    return ret


def county_choices(blank=False, extra=None):
    counties = db.session.query(County.id, County.name).order_by(County.name).all()
    ret = [(c.id, c.name) for c in counties]
    if extra:
        ret = extra + ret
    if blank:
        ret = [(0, '')] + ret
    return ret


def state_choices(blank=False, extra=None):
    states = db.session.query(State.id, State.code, State.name).order_by(State.name).all()
    ret = [(c.id, c.code + '-' + c.name) for c in states]
    if extra:
        ret = extra + ret
    if blank:
        ret = [(0, '')] + ret
    return ret


def get_new_address():
    uk = db.session.query(Country).filter(Country.code == 'UK').first()
    return Address(country=uk)


def get_country(id):
    return db.session.query(Country).filter(Country.id == id).first()


def get_county(id):
    if id == 0:
        return None
    return db.session.query(County).filter(County.id == id).first()


def get_state(id):
    if id == 0:
        return None
    return db.session.query(State).filter(State.id == id).first()


# endregion


# region others
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


# endregion


def get_attr(obj, spec):
    # extract data for attr spec from populated database object
    # e.g. get_attr(member, 'address.line_1')
    # or get_attr(member, 'address.country_for_mail()') - invoke a method
    if '=' == first_or_default(spec, ' '):
        return eval(spec[1:])
    attr, tail = pop_next(spec, '.')
    if '()' in attr:  # function call
        res = getattr(obj, attr.replace('()', ''))()
    elif tail and '()' in tail:  # function call
        res = getattr(obj, attr)
    elif '[]' in attr:  # list - get first
        res = first_or_default(getattr(obj, attr.replace('[]', '')), None)
    else:  # property
        res = getattr(obj, attr)
    if res and tail:
        res = get_attr(res, tail)
    if res and 'date' in spec and isinstance(res, datetime.date):
        res = fmt_date(res)
    return res if res is not None else ''


def class_name_to_table_name(name):
    if name.lower() == 'address':
        name = name + 'e'
    if name.lower() in ['county', 'country']:
        name = name[:-1] + 'ie'
    return name.lower() + 's'


def field_type(table, field_name):
    type = 'unknown'
    data = None
    if field_name in globals()[table].__table__.c:
        f_type = globals()[table].__table__.c[field_name].type
        type_name = str(f_type)

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


# region files
def list_to_csv_object(csv_list, delimiter=','):
    csv_object = io.StringIO()
    if delimiter == '\t':
        dialect = 'excel-tab'
    else:
        dialect = 'excel'
    writer = csv.writer(csv_object, dialect=dialect, delimiter=delimiter)
    writer.writerows(csv_list)
    return csv_object


def stringIO_to_bytesIO(stringIO_object):
    # Creating a bytesIO object from a StringIO Object
    bytesIO_object = io.BytesIO()
    encoding = 'utf-8-sig'  # add BOM signature for Excel
    bytesIO_object.write(stringIO_object.getvalue().encode(encoding))
    # seeking was necessary. Python 3.5.2, Flask 0.12.2
    bytesIO_object.seek(0)
    stringIO_object.close()
    return bytesIO_object


def return_csv_file(csv_list, file_name):
    delimiter = file_delimiter(file_name)
    return return_file(stringIO_to_bytesIO(list_to_csv_object(csv_list, delimiter)), file_name)


def return_file(file_path_or_object, filename, mime_type='text/csv'):
    try:
        return send_file(file_path_or_object, mimetype=mime_type, attachment_filename=filename, as_attachment=True)
    except Exception as e:
        return str(e)
# endregion
