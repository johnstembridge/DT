from flask import render_template, redirect, url_for, request

from front_end.form_helpers import flash_errors, render_link, url_pickle_dump, url_pickle_load
from front_end.query import QueryForm
from front_end.extract_form import ExtractForm
from back_end.interface import select, get_attr, get_members_for_query
from back_end.data_utilities import fmt_date, yes_no
from globals.enumerations import MembershipType, MemberStatus, MemberAction, ActionStatus, PaymentMethod
from models.dt_db import Action, Member, Junior
import datetime


class Extracts:

    @staticmethod
    def extract_certificates():
        certs = select(Action, (Action.status == ActionStatus.open, Action.action == MemberAction.certificate))
        csv = []
        head = ['id', 'type', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'address']
        csv.append(head)
        for cert in certs:
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
                cert.member.address.full()
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_cards():
        cards = select(Action, (Action.status == ActionStatus.open, Action.action == MemberAction.card))
        csv = []
        head = ['id', 'status', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'since']
        csv.append(head)
        for card in cards:
            row = [
                card.member.dt_number(),
                card.member.status.name,
                card.member.full_name(),
                card.member.address.line_1,
                card.member.address.line_2,
                card.member.address.line_3,
                card.member.address.city,
                card.member.address.county,
                card.member.address.state,
                card.member.address.post_code,
                card.member.address.country_for_mail(),
                card.member.start_date.year
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_cards_all():
        # annual replacement cards
        members = select(Member, (Member.status.in_(MemberStatus.all_active()),))
        csv = []
        head = ['id', 'name', 'since']
        csv.append(head)
        for member in members:
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
        end_date = datetime.date(datetime.date.today().year, 8, 1).strftime('%Y-%m-%d')
        members = select(Member, (Member.end_date == end_date, Member.status.in_(MemberStatus.active())))
        csv = []
        head = ['member_id', 'status', 'type', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city',
                'county', 'state', 'post_code', 'country', 'amount', 'pay_method', 'birth_date', 'email', 'use_email',
                'afcw_access', 'third_pty_access', 'home_phone', 'mobile_phone', 'jd_email', 'volatile_concession']
        csv.append(head)
        for member in members:
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
                yes_no(member.volatile_concession())
            ]
            csv.append(row)
        return csv

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
    def extract_debits():
        end_date = datetime.date(datetime.date.today().year, 8, 1).strftime('%Y-%m-%d')
        members = select(Member, (Member.end_date == end_date, Member.last_payment_method == PaymentMethod.dd))
        csv = []
        head = ['id', 'status', 'email', 'home_phone', 'mobile_phone', 'fullname', 'address_line_1', 'address_line_2',
                'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'amount']
        csv.append(head)
        for member in members:
            row = [
                member.dt_number(),
                member.status.name,
                member.full_name(),
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
                member.address.country_for_mail(),
                member.dues()
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

        return render_template('query.html', form=form, render_link=render_link)

    @staticmethod
    def extract_show():
        page = request.args.get('page', 1, int)
        query_clauses = url_pickle_load(request.args.get('query_clauses'))
        form = ExtractForm()
        query = get_members_for_query(query_clauses)
        fields, page = form.populate_result(clauses=url_pickle_dump(query_clauses), query=query, page_number=page)
        return render_template('extract.html', form=form, data=page.items, fields=fields, get_attr=get_attr)
