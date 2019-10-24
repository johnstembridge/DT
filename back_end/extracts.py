from flask import render_template, redirect, url_for, request

from front_end.form_helpers import flash_errors, render_link, url_pickle_dump, url_pickle_load
from front_end.query import QueryForm
from front_end.extract_form import ExtractForm
from back_end.interface import select, get_attr, get_members_for_query
from back_end.data_utilities import fmt_date, yes_no, first_or_default, encode_date_formal
from globals.enumerations import MembershipType, MemberStatus, MemberAction, ActionStatus, PaymentMethod, CommsType
from models.dt_db import Action, Member, Junior
import datetime


class Extracts:

    @staticmethod
    def extract_certificates():
        certs = select(Action, (
            Action.status == ActionStatus.open,
            Action.action.in_([MemberAction.certificate, MemberAction.upgrade]))
                       )
        csv = []
        head = ['id', 'type', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'address', 'cert_date', 'upgrade']
        csv.append(head)
        for cert in certs:
            upgrade = cert.member.member_type == MembershipType.intermediate and \
                      cert.member.actions[0].action == MemberAction.upgrade
            row = [
                cert.member.dt_number(),
                cert.member.member_type.name,
                cert.member.full_name(),
                cert.member.address.line_1,
                cert.member.address.line_2,
                cert.member.address.line_3,
                cert.member.address.city,
                cert.member.address.county,
                cert.member.address.state,
                cert.member.address.post_code,
                cert.member.address.country_for_mail(),
                cert.member.address.full(),
                encode_date_formal(datetime.date.today(), cert=True),
                yes_no(upgrade)
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_cards():
        # renewal cards
        all = select(Action, (Action.status == ActionStatus.open, Action.action == MemberAction.card))
        csv = []
        head = ['id', 'type', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'recent_new']
        csv.append(head)
        count = 0
        for card in all:
            count += 1
            if count % 100 == 0:
                print('Processing ' + card.member.dt_number())
            row = [
                card.member.dt_number(),
                card.member.member_type.name,
                card.member.full_name(),
                card.member.address.line_1,
                card.member.address.line_2,
                card.member.address.line_3,
                card.member.address.city,
                card.member.address.county,
                card.member.address.state,
                card.member.address.post_code,
                card.member.address.country_for_mail(),
                yes_no(card.member.start_date >= datetime.date(datetime.date.today().year, 2, 1))
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_cards_all():
        # annual replacement cards for printers
        end_date = datetime.date(datetime.date.today().year, 8, 1)
        members = select(Member, (Member.status.in_(MemberStatus.all_active()),))
        csv = []
        head = ['id', 'name', 'since']
        csv.append(head)
        for member in members:
            member = Extracts.handle_upgrade(member, end_date, 'extract_cards')
            if member.status == MemberStatus.founder:
                extra = ' (founder)'
            elif member.status == MemberStatus.life:
                extra = ' (life member)'
            else:
                extra = ''
            row = [
                member.dt_number(),
                member.full_name(),
                str(member.start_date.year) + extra
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_renewals():
        end_date = datetime.date(datetime.date.today().year, 8, 1)
        members = select(Member,
                         (Member.end_date == end_date.strftime('%Y-%m-%d'), Member.status.in_(MemberStatus.active())))
        csv = []
        head = ['member_id', 'status', 'type', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city',
                'county', 'state', 'post_code', 'country', 'amount', 'pay_method', 'birth_date', 'email', 'use_email',
                'afcw_access', 'third_pty_access', 'home_phone', 'mobile_phone', 'jd_email', 'volatile_concession',
                'latest_action']
        csv.append(head)
        for member in members:
            member = Extracts.handle_upgrade(member, end_date, 'extract_renewals')
            latest_action = first_or_default(member.actions, None)
            if latest_action:
                latest_action = latest_action.action.name if latest_action.status == ActionStatus.open else None
            row = [
                member.dt_number(),
                member.status.name,
                member.member_type.name,
                member.full_name(),
                member.address.line_1,
                member.address.line_2,
                member.address.line_3,
                member.address.city,
                member.address.county,
                member.address.state,
                member.address.post_code,
                member.address.country_for_mail(),
                member.dues(),
                (member.last_payment_method or PaymentMethod.na).name,
                fmt_date(member.birth_date),
                member.email,
                yes_no(member.use_email()),
                yes_no(member.afcw_has_access()),
                yes_no(member.third_pty_access()),
                member.home_phone,
                member.mobile_phone,
                (member.junior or Junior(email='')).email,
                yes_no(member.volatile_concession()),
                latest_action
            ]
            csv.append(row)
        return csv

    @staticmethod
    def handle_upgrade(member, end_date, action_text):
        age = member.age(end_date)
        if member.member_type == MembershipType.junior and age >= 16:
            member.member_type = MembershipType.intermediate
            member.actions.insert(0, Action(
                date=end_date,
                action=MemberAction.upgrade,
                status=ActionStatus.open,
                comment='Automatic upgrade from Junior on ' + action_text
            ))
        elif member.member_type == MembershipType.intermediate and age >= 21:
            member.member_type = MembershipType.standard
            member.actions.insert(0, Action(
                date=end_date,
                action=MemberAction.upgrade,
                status=ActionStatus.open,
                comment='Automatic upgrade from Young Adult on ' + action_text
            ))
        return member

    @staticmethod
    def extract_juniors():
        juniors = select(Member,
                         (Member.member_type == MembershipType.junior, Member.status.in_(MemberStatus.all_active())))
        csv = []
        head = ['id', 'status', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'amount']
        csv.append(head)
        for member in juniors:
            row = [
                member.dt_number(),
                member.status.name,
                member.full_name(),
                member.address.line_1,
                member.address.line_2,
                member.address.line_3,
                member.address.city,
                member.address.county,
                member.address.state,
                member.address.post_code,
                member.address.country_for_mail(),
                member.dues()
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_junior_birthdays():
        month = datetime.date.today().month + 1
        juniors = select(Member, (
            Member.member_type == MembershipType.junior,
            Member.status.in_(MemberStatus.all_active())
        )
                         )
        csv = []
        head = ['id', 'first_name', 'last_name', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3',
                'city', 'county', 'state', 'post_code', 'country', 'email', 'home_phone', 'mobile_phone', 'birth_date',
                'age']
        csv.append(head)
        for member in juniors:
            if member.age() < 15 and member.birth_date.month == month:
                row = [
                    member.dt_number(),
                    member.first_name,
                    member.last_name,
                    member.full_name(),
                    member.address.line_1,
                    member.address.line_2,
                    member.address.line_3,
                    member.address.city,
                    member.address.county,
                    member.address.state,
                    member.address.post_code,
                    member.address.country_for_mail(),
                    member.email,
                    member.home_phone,
                    member.mobile_phone,
                    fmt_date(member.birth_date),
                    member.age()
                ]
                csv.append(row)
        return csv

    @staticmethod
    def extract_debits():
        end_date = datetime.date(datetime.date.today().year, 8, 1).strftime('%Y-%m-%d')
        members = select(Member, (Member.end_date == end_date,
                                  Member.last_payment_method == PaymentMethod.dd,
                                  Member.status.in_(MemberStatus.active())))
        csv = []
        head = ['id', 'type', 'first_name', 'last_name', 'amount', 'email', 'home_phone', 'mobile_phone',
                'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county', 'state', 'post_code', 'country']
        csv.append(head)
        for member in members:
            row = [
                member.dt_number(),
                member.member_type.name,
                member.first_name,
                member.last_name,
                member.dues(),
                member.email,
                member.home_phone,
                member.mobile_phone,
                member.address.line_1,
                member.address.line_2,
                member.address.line_3,
                member.address.city,
                member.address.county,
                member.address.state,
                member.address.post_code,
                member.address.country_for_mail()
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_email():
        members = select(Member, (Member.comms == CommsType.email,
                                  Member.status.in_(MemberStatus.all_active())))
        csv = []
        head = ['id', 'type', 'first_name', 'last_name', 'email']
        csv.append(head)
        for member in members:
            row = [
                member.dt_number(),
                member.member_type.name,
                member.first_name,
                member.last_name,
                member.email
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_comms():
        members = select(Member, (Member.status.in_(MemberStatus.all_active()),))
        csv = []
        head = ['id', 'type', 'first_name', 'last_name', 'use_email', 'email',
                'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county', 'state', 'post_code', 'country']
        csv.append(head)
        for member in members:
            row = [
                member.dt_number(),
                member.member_type.name,
                member.first_name,
                member.last_name,
                member.use_email(),
                member.email,
                member.address.line_1,
                member.address.line_2,
                member.address.line_3,
                member.address.city,
                member.address.county,
                member.address.state,
                member.address.post_code,
                member.address.country_for_mail()
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_select():
        form = QueryForm()
        if form.validate_on_submit():
            if form.submit.data:
                query_clauses = form.find_members()
                return redirect(url_for('extracts_show', page=1, query_clauses=url_pickle_dump(query_clauses)))
        elif form.errors:
            flash_errors(form)

        return render_template('query.html', form=form, render_link=render_link, title='Select data to extract')

    @staticmethod
    def extract_selected():
        pass # ToDo

    @staticmethod
    def extract_show():
        page = request.args.get('page', 1, int)
        query_clauses = url_pickle_load(request.args.get('query_clauses'))
        form = ExtractForm()
        query = get_members_for_query(query_clauses)
        fields, page = form.populate_result(clauses=url_pickle_dump(query_clauses), query=query, page_number=page)
        return render_template('extract.html', form=form, render_link=render_link, data=page.items, fields=fields, get_attr=get_attr)

    @staticmethod
    def bulk_update():
        form = QueryForm()
        if form.validate_on_submit():
            if form.submit.data:
                query_clauses = url_pickle_load(request.args.get('query_clauses'))
                query = get_members_for_query(query_clauses)
                updates = form.get_updates()
                # ToDo: update here
                # flash updated
                return ##redirect(url_for('extracts_bulk_update', query_clauses=query_clauses))
        elif form.errors:
            flash_errors(form)

        return render_template('query.html', form=form, render_link=render_link, title='Bulk update')
