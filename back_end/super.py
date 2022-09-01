from globals import config
from globals.enumerations import MemberAction, MemberStatus, MembershipType, ActionStatus, PaymentType, PaymentMethod
from back_end.interface import get_members_for_query, get_member, save_member, get_region
from back_end.data_utilities import fmt_date, current_year_end, previous_year_end, first_or_default, \
    file_delimiter, parse_date, season_start, renewal_date
from models.dt_db import Action, Payment
from api.secutix import Secutix

import datetime
import csv
import json
from os import path


def renew_recent_joiners():
    season_start_date = season_start()
    start_date = datetime.date(season_start_date.year + 1, 2, 1)
    end_date = renewal_date(season_start_date)
    new_end_date = renewal_date(end_date)

    query_clauses = [
        ('Member', 'start_date', fmt_date(start_date), '>=', None),
        ('Member', 'end_date', fmt_date(end_date), '=', None),
    ]
    members = get_members_for_query(query_clauses)
    count = 0
    message = []
    for member in members:
        member.end_date = new_end_date
        item = first_or_default(
            [a for a in member.actions if a.action == MemberAction.card and a.status == ActionStatus.open], None)
        if not item:
            item = Action(
                member_id=member.id,
                date=datetime.date.today(),
                action=MemberAction.card,
                comment='auto renew recent joiner',
                status=ActionStatus.open
            )
            member.actions.append(item)
        save_member(member)
        message += [member.dt_number()]
        count += 1
    return '\n'.join(['{} new members updated'.format(count)] + message)


def renew_recent_resumers():
    season_start_date = season_start()
    resume_date = datetime.date(season_start_date.year + 1, 2, 1)
    end_date = renewal_date(season_start_date)
    new_end_date = renewal_date(end_date)

    query_clauses = [
        ('Member', 'start_date', fmt_date(season_start_date), '<=', None),
        ('Payment', 'date', resume_date, '>=', None),
        ('Payment', 'type', PaymentType.dues, '=', None),
        ('Member', 'end_date', end_date, '=', None),
    ]
    members = get_members_for_query(query_clauses)
    count = 0
    message = []
    for member in members:
        member.end_date = new_end_date
        item = first_or_default(
            [a for a in member.actions if a.action == MemberAction.card and a.status == ActionStatus.open], None)
        if not item:
            item = Action(
                member_id=member.id,
                date=datetime.date.today(),
                action=MemberAction.card,
                comment='auto renew recent resumer',
                status=ActionStatus.open
            )
            member.actions.append(item)
        message += [member.dt_number()]
        save_member(member)
        count += 1
    return '\n'.join(['{} members updated'.format(count)] + message)


def lapse_expired():
    query_clauses = [
        ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
        ('Member', 'end_date', fmt_date(previous_year_end()), '=', None)
    ]
    members = get_members_for_query(query_clauses)
    count = 0
    for member in members:
        member.status = MemberStatus.lapsed
        save_member(member)
        count += 1
    return '{} records processed'.format(count)


def renew_paid(payment_method, save=True):
    file_name = path.join(config.get('locations')['import'],
                          'paypal_apply.txt' if payment_method == 'cc' else 'dd_apply.txt')
    payment_method = PaymentMethod.cc if payment_method == 'cc' else PaymentMethod.dd
    print('Importing ' + file_name)
    result = []
    with open(file_name, 'r', encoding='latin-1') as in_file:
        reader = csv.DictReader(in_file, delimiter=file_delimiter(file_name))
        count = 0
        for row in reader:
            if len(row['id'].strip()) > 0:
                count += 1
                if count % 50 == 0:
                    if 'id' in row.keys():
                        print('Processing ' + row['id'])
                message = update_member_payment(row, payment_method, save)
                if len(message) > 0:
                    result.append('***' + row['id'] + ': ' + '\n'.join(message))
        if len(result) > 0:
            return '\n'.join(result)
        else:
            return '{} records processed'.format(count)


def update_member_payment(rec, payment_method, save=True):
    # rec is line of payments file with keys id, date, amount and note
    message = []
    number = int(rec['id'][4:])
    date = parse_date(rec['date'], sep='/', reverse=True)
    amount = float(rec['amount'])
    member = get_member(number)
    if not member:
        print("Member not found for record".format(rec))
    pending = first_or_default(
        [p for p in member.payments if p.type == PaymentType.pending and p.method == payment_method], None)
    payment_comment = 'from payments file'
    if pending:
        comment = ['']
        if pending.amount != amount:
            comment = ["Expected amount {}, got {}".format(pending.amount, amount)]
            message += comment
        pending.type = PaymentType.dues
        pending.date = date
        pending.amount = amount
        pending.comment = payment_comment + ' ' + comment[0]
    else:
        dues = first_or_default(
            [p for p in member.payments if p.type == PaymentType.dues and p.method == payment_method], None)
        if dues and dues.amount == amount and dues.date == date and dues.comment.startswith(payment_comment):
            message += ['Payment already processed']
            return message
        else:
            add = "no pending payment, adding one"
            expected = member.dues(datetime.date(2022, 8, 1))
            if expected != amount:
                comment = " Expected amount {}, got {}".format(expected, amount)
                message += [add + ", " + comment]
            else:
                message += [add]
                comment = ""
            pending = Payment(
                member_id=member.id,
                date=date,
                amount=amount,
                type=PaymentType.dues,
                method=payment_method,
                comment=payment_comment + comment
            )
            member.payments.append(pending)
    action = first_or_default(
        [a for a in member.actions if a.action == MemberAction.card and a.status == ActionStatus.open], None)
    if not action:
        action = Action(
            member_id=member.id,
            date=datetime.date.today(),
            action=MemberAction.card,
            status=ActionStatus.open,
            comment=payment_comment
        )
        member.actions.append(action)
    upgrade = amount in [20.0, 30.0, 45.0] and member.status != MemberStatus.plus
    downgrade = amount in [10.0, 25.0] and member.status == MemberStatus.plus
    action = first_or_default(
        [a for a in member.actions if a.action == MemberAction.upgrade and a.status == ActionStatus.open], None)
    if action:
        if upgrade:
            member.status = MemberStatus.plus
            action.status = ActionStatus.closed
    else:
        if upgrade:
            member.status = MemberStatus.plus
            action = Action(
                member_id=member.id,
                date=date,
                action=MemberAction.upgrade,
                status=ActionStatus.closed,
                comment=payment_comment
            )
            member.actions.append(action)
    action = first_or_default(
        [a for a in member.actions if a.action == MemberAction.downgrade and a.status == ActionStatus.open], None)
    if action:
        if downgrade:
            member.status = MemberStatus.current
            action.status = ActionStatus.closed
    else:
        if downgrade:
            member.status = MemberStatus.current
            action = Action(
                member_id=member.id,
                date=date,
                action=MemberAction.downgrade,
                status=ActionStatus.closed,
                comment=payment_comment
            )
            member.actions.append(action)
    member.end_date = datetime.date(2023, 7, 1)
    member.last_payment_method = payment_method
    if save:
        save_member(member)
    return message


def change_member_type_by_age():
    message = []
    message += ['standard to senior']
    query_clauses = [
        ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
        ('Member', 'member_type', MembershipType.standard, '=', None),
        ('Member', 'birth_date', 65, '>=', 'age()'),
    ]
    members = get_members_for_query(query_clauses)
    count_senior = 0
    for member in members:
        if member.member_type != MembershipType.senior:
            message += [member.dt_number()]  # member_type_change(member)
            member.member_type = MembershipType.senior
            count_senior += 1
            save_member(member)

    message += ['junior to intermediate']
    query_clauses = [
        ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
        ('Member', 'member_type', MembershipType.junior, '=', None),
        ('Member', 'birth_date', 16, '>', 'age()'),
    ]
    members = get_members_for_query(query_clauses)
    count_junior = 0
    for member in members:
        new = member.member_type_at_renewal()
        if new == MembershipType.intermediate:
            message += [member.dt_number()]  # member_type_change(member)
            member.member_type = MembershipType.intermediate
            count_junior += 1
            save_member(member)

    message += ['Intermediates to standard']
    query_clauses = [
        ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
        ('Member', 'member_type', MembershipType.intermediate, '=', None),
        ('Member', 'birth_date', 20, '>', 'age()'),
    ]
    members = get_members_for_query(query_clauses)
    count_intermediate = 0
    for member in members:
        new = member.member_type_at_renewal()
        if new == MembershipType.standard:
            message += [member.dt_number()]  # member_type_change(member)
            member.member_type = MembershipType.standard
            count_intermediate += 1
            save_member(member)
    totals = '{} senior records processed, {} junior, {} intermediate'.format(count_senior, count_junior,
                                                                              count_intermediate)
    return '\n'.join([totals] + message)


def member_type_change(member):
    return [[member.dt_number(), member.age(), member.age_at_renewal(), member.member_type.name,
             member.member_type_at_renewal().name]]


def season_tickets():
    file_name = path.join(config.get('locations')['import'], 'season tickets.csv')
    print('Importing ' + file_name)
    result = []
    with open(file_name, 'r', encoding='latin-1') as in_file:
        reader = csv.DictReader(in_file, delimiter=file_delimiter(file_name))
        count = 0
        for row in reader:
            count += 1
            if count % 50 == 0:
                if 'dt id' in row.keys():
                    print('Processing ' + row['dt id'])
            message = update_member_season_ticket(row)
            if len(message) > 0:
                result.append('***' + row['dt id'] + ': ' + '\n'.join(message))
        if len(result) > 0:
            return '\n'.join(result)
        else:
            return '{} records processed'.format(count)


def check_fan_ids(update=False):
    file_name = path.join(config.get('locations')['export'], 'check_fan_ids.csv')
    print('Checking...')
    api = Secutix()
    with open(file_name, 'w', encoding='latin-1', newline='') as out_file:
        writer = csv.DictWriter(out_file, delimiter=file_delimiter(file_name),
                                fieldnames=
                                ["dt_id", "fan_id", "source", "value", "member_status", "member_type", "updated"])
        writer.writeheader()
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Member', 'season_ticket_id', 'null', '!=', None)
        ]
        members = get_members_for_query(query_clauses)
        count = 0
        for member in members:
            fan_id = member.season_ticket_id
            dt_id = member.dt_number()
            if count % 50 == 0:
                print('Processing ' + dt_id)
            count += 1
            secutix_details = api.get_details(fan_id)
            as_json = json.loads(secutix_details.text)
            source = None
            if "contactCriteria" in as_json:
                contact_criteria = as_json["contactCriteria"]
                (source, value) = find_source_criteria(contact_criteria)

            writer.writerow(
                {"dt_id": dt_id,
                 "fan_id": fan_id,
                 "source": source or "none",
                 "value": value or "none",
                 "member_status": member.status.name,
                 "member_type": member.member_type.name})

        return file_name # '{} records processed'.format(count)


def find_source_criteria(criteria):
    latest = ''
    for item in criteria:
        if item['criterionIdCode'].startswith('SOURCE'):
            value = first_or_default(item['values'], None)
            latest = item['criterionIdCode']
            if value and value.startswith('DONS_TRUST'):
                return (latest, value)
    return (None, None)


def update_member_season_ticket(rec):
    # rec is line of payments file with keys dt id, afcw id
    message = []
    dt_id = rec['dt id'].strip()
    afcw_id = rec['afcw id'].strip()
    if len(afcw_id) > 0:
        if dt_id[0] in ['D', 'J']:
            number = int(dt_id[4:])
        else:
            number = int(dt_id)
        season_ticket = int(afcw_id)
        member = get_member(number)
        if member:
            member.season_ticket_id = season_ticket
            message += ['Season ticket updated: {}'.format(season_ticket)]
            save_member(member)
        else:
            message += ['Member not found: {}'.format(number)]
    return message


def set_region():
    query_clauses = [
        ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
        ('Member', 'end_date', fmt_date(current_year_end()), '=', None)
    ]
    members = get_members_for_query(query_clauses)
    count = 0
    for member in members:
        region = get_region(member.address.country, member.address.post_code)
        if region:
            member.address.region = region
            save_member(member)
        count += 1
    return '{} records processed'.format(count)
