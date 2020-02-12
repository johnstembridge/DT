from globals.enumerations import MemberStatus, ActionStatus, MemberAction
from back_end.query import Query


class MaintainActions:

    @staticmethod
    def list_actions(action, page):
        actions = {
            'cert': MemberAction.send_certificates(),
            'card': MemberAction.send_cards(),
            'other': MemberAction.send_other()
        }
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Action', 'action', [a.value for a in actions[action]], 'in', None),
            ('Action', 'status', ActionStatus.open.value, '=', None)
        ]
        display_fields = ['number', 'member type', 'full name', 'action', 'action date', 'action comment']
        return Query.show_found_do(query_clauses, display_fields, action=action, page=page)

    @staticmethod
    def clear_actions(query_clauses):
        Query.reset_member_actions(query_clauses)
