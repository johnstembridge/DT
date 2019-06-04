from flask import render_template, redirect, flash, url_for, request

from front_end.form_helpers import flash_errors, render_link, url_pickle_dump, url_pickle_load
from back_end.interface import select, get_attr, get_members_for_query
from front_end.query import QueryForm
from front_end.extract import ExtractForm
from globals.enumerations import MembershipType, MemberStatus, MemberAction, ActionStatus
from models.dt_db import Action, Member
import datetime


class Extracts:

    @staticmethod
    def extract_certificates():
        actions = select(Action, (Action.status == ActionStatus.open, Action.action == MemberAction.certificate))
        csv = []
        head = ['id', 'status', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'address']
        csv.append(head)
        for action in actions:
            row = [
                action.member.dt_number(),
                action.member.status.name,
                action.member.full_name(),
                action.member.address.line_1,
                action.member.address.line_2,
                action.member.address.line_3,
                action.member.address.city,
                action.member.address.county,
                action.member.address.state,
                action.member.address.post_code,
                action.member.address.country_for_mail(),
                action.member.address.full()
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_cards():
        actions = select(Action, (Action.status == ActionStatus.open, Action.action == MemberAction.card))
        csv = []
        head = ['id', 'status', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'since']
        csv.append(head)
        for action in actions:
            row = [
                action.member.dt_number(),
                action.member.status.name,
                action.member.full_name(),
                action.member.address.line_1,
                action.member.address.line_2,
                action.member.address.line_3,
                action.member.address.city,
                action.member.address.county,
                action.member.address.state,
                action.member.address.post_code,
                action.member.address.country_for_mail(),
                action.member.start_date.year
            ]
            csv.append(row)
        return csv

    @staticmethod
    def extract_renewals():
        end_date = datetime.date(datetime.date.today().year, 8, 1).strftime('%Y-%m-%d')
        members = select(Member, (Member.end_date == end_date,))  # note trailing comma
        csv = []
        head = ['id', 'status', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'amount']
        csv.append(head)
        for member in members:
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
    def extract_juniors():
        juniors = select(Member, (Member.member_type == MembershipType.junior, Member.status.in_(MemberStatus.all_active())))
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
