from globals import config
from globals.enumerations import MemberAction, MemberStatus, ActionStatus, PaymentType, PaymentMethod
from back_end.interface import get_members_for_query, get_member, save_member
from back_end.data_utilities import fmt_date, current_year_end, first_or_default, file_delimiter, parse_date
from models.dt_db import Action, Payment

import datetime
import csv
from os import path

new_end_date = datetime.date(current_year_end().year + 1, 8, 1)


def renew_recent():
    start_date = fmt_date(datetime.date(current_year_end().year, 2, 1))
    end_date = fmt_date(datetime.date(current_year_end().year, 8, 1))
    query_clauses = [
        ('Member', 'start_date', start_date, '>=', None),
        ('Member', 'end_date', end_date, '=', None),
    ]
    members = get_members_for_query(query_clauses)
    count = 0
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
        count += 1
    return '{} new members updated'.format(count)


def renew_paid():
    file_name = path.join(config.get('locations')['import'], 'paypal_apply.txt')
    print('Importing ' + file_name)
    result = []
    with open(file_name, 'r', encoding='latin-1') as in_file:
        reader = csv.DictReader(in_file, delimiter=file_delimiter(file_name))
        count = 0
        for row in reader:
            count += 1
            if count % 50 == 0:
                if 'id' in row.keys():
                    print('Processing ' + row['id'])
            message = update_member(row)
            if len(message) > 0:
                result.append('***' + row['id'] + ': ' + '\n'.join(message))
        if len(result) > 0:
            return '\n'.join(result)
        else:
            return '{} records processed'.format(count)


def update_member(rec):
    # rec is line of payments file with keys id, date, amount and note
    message = []
    number = int(rec['id'][4:])
    date = parse_date(rec['date'], sep='/', reverse=True)
    amount = float(rec['amount'])
    member = get_member(number)
    pending = first_or_default(
        [p for p in member.payments if p.type == PaymentType.pending and p.method == PaymentMethod.cc], None)
    if pending:
        if pending.amount != amount:
            message += ["Expected amount {}, got {}".format(pending.amount, amount)]
        pending.type = PaymentType.dues
        pending.date = date
        pending.amount = amount
        pending.comment = 'from PayPal'
    else:
        message += ["no cc pending payment: adding one"]
        pending = Payment(
            member_id=member.id,
            date=date,
            amount=amount,
            type=PaymentType.dues,
            method=PaymentMethod.cc,
            comment='from PayPal'
        )
        member.payments.append(pending)
    upgrade = amount in [20.0, 30.0, 45.0]
    action = first_or_default(
        [a for a in member.actions if a.action == MemberAction.upgrade and a.status == ActionStatus.open], None)
    if action:
        if upgrade:
            member.status = MemberStatus.plus
            action.status = ActionStatus.closed
        else:
            message += ['expected an upgrade payment, upgrade action removed']
            member.actions.remove(action)
    else:
        if upgrade:
            action = Action(
                member_id=member.id,
                date=date,
                action=MemberAction.upgrade,
                status=ActionStatus.closed,
                comment='from PayPal'
            )
            member.actions.append(action)
    member.end_date = new_end_date
    save_member(member)
    return message
