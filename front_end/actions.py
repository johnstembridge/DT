from back_end.query import Query
from back_end.extracts import Extracts


class MaintainActions:

    @staticmethod
    def list_actions(action, page):
        if action.startswith('cert_'):
            return Extracts.extract_certificates(page, action[5:])
        if action == 'card':
            return Extracts.extract_cards(page)
        if action == 'other':
            return Extracts.extract_other_actions(page)
        if action == 'renewal':
            return Extracts.extract_pending_renewals(page)
        if action == 'query':
            return Query.show_found()

    @staticmethod
    def clear_actions(query_clauses):
        Query.reset_member_actions(query_clauses)
