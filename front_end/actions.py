from globals.enumerations import MemberStatus, ActionStatus, MemberAction
from back_end.query import Query
from back_end.extracts import Extracts
class MaintainActions:

    @staticmethod
    def list_actions(action, page):
        if action == 'cert':
            return Extracts.extract_certificates()
        if action == 'card':
            return Extracts.extract_cards()

        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Action', 'action', 'other', 'in', None),
            ('Action', 'status', ActionStatus.open.value, '=', None)
        ]
        display_fields = ['number', 'member type', 'full name', 'action', 'action date', 'action comment']
        return Query.show_found_do(query_clauses, display_fields, action=action, page=page)

    @staticmethod
    def clear_actions(query_clauses):
        Query.reset_member_actions(query_clauses)
