from flask import request, render_template, redirect, flash, url_for
from globals.enumerations import MemberStatus, ActionStatus
from front_end.member_list_form import MemberListForm
from front_end.form_helpers import flash_errors, render_link, url_pickle_dump, url_pickle_load
from back_end.query import Query


class MaintainActions:

    @staticmethod
    def list_actions():
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Action', 'status', ActionStatus.open.value, '=', None)
        ]
        display_fields = ['number', 'member type', 'full name', 'action', 'action date', 'action comment']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def clear_actions():
        pass