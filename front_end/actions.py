from back_end.query import Query
from back_end.extracts import Extracts


class MaintainActions:

    @staticmethod
    def list_actions(action, page):
        if action == 'cert':
            return Extracts.extract_certificates(page)
        if action == 'card':
            return Extracts.extract_cards(page)
        if action == 'other':
            return Extracts.extract_other_actions(page)
        if action == 'renewal':
            return Extracts.extract_pending_renewals(page)

    @staticmethod
    def clear_actions(query_clauses):
        Query.reset_member_actions(query_clauses)
