from back_end.query import Query
from back_end.data_utilities import fmt_date, current_year_end
from globals.enumerations import MembershipType, MemberStatus, MemberAction, ActionStatus, PaymentMethod, CommsType, \
    CommsStatus, PaymentType
import datetime


class Extracts:

    @staticmethod
    def extract_certificates(page):
        # new member packs
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Action', 'status', ActionStatus.open.value, '=', None),
            ('Action', 'action', [a.value for a in MemberAction.send_certificates()], 'in', None)
        ]
        display_fields = ['number', 'status', 'member type', 'full name', 'address (line 1)', 'address (line 2)',
                          'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post',
                          'full address', 'certificate date', 'upgrade',
                          'card start year', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields, action='cert', page=page)

    @staticmethod
    def extract_cards(page):
        # renewal acknowledgement
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Action', 'status', ActionStatus.open.value, '=', None),
            ('Action', 'action', [a.value for a in MemberAction.send_cards()], 'in', None)
        ]
        display_fields = ['number', 'status', 'member type', 'full name', 'address (line 1)', 'address (line 2)',
                          'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post', 'recent new',
                          'email', 'use email', 'email bounced', 'card start year', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields, action='card', page=page)

    @staticmethod
    def extract_other_actions(page):
        # other actions
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Action', 'action', [a.value for a in MemberAction.send_other()], 'in', None),
            ('Action', 'status', ActionStatus.open.value, '=', None)
        ]
        display_fields = ['number', 'member type', 'full name', 'action', 'action date', 'action comment']
        return Query.show_found_do(query_clauses, display_fields, action='other', page=page)

    @staticmethod
    def extract_pending_renewals(page):
        # pending renewals
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Payment', 'type', PaymentType.pending.value, '=', None)
        ]
        display_fields = ['number', 'member type', 'full name', 'use email', 'email', 'action', 'action date',
                          'action comment', 'last payment date', 'last payment amount', 'last payment type', 'payment type',
                          'last payment method', 'last payment comment', 'end']
        return Query.show_found_do(query_clauses, display_fields, action='renewal', payment='pending', page=page)

    @staticmethod
    def extract_juniors():
        query_clauses = [
            ('Member', 'member_type', MembershipType.junior.value, '=', None),
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None)
        ]
        display_fields = ['number', 'status', 'full name', 'address (line 1)', 'address (line 2)',
                          'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post', 'dues',
                          'age', 'use email', 'email', 'email bounced', 'junior email', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_junior_birthdays(month=None):
        today = datetime.date.today()
        if not month:
            month = today.month % 12 + 1  # next month
        query_clauses = [
            ('Member', 'member_type', MembershipType.junior.value, '=', None),
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Member', 'birth_date', month, '=', 'birth_month()'),
            # ('Member', 'age_next_birthday', 16, '<', None)
        ]
        display_fields = ['number', 'full name', 'address (line 1)', 'address (line 2)', 'address (line 3)',
                          'city', 'county', 'state', 'post code', 'country for post', 'use email',
                          'email', 'junior email', 'home phone', 'mobile phone', 'birth date', 'age next bday',
                          'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_email():
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Member', 'comms', CommsType.email.value, '=', None),
            ('Member', 'comms_status', CommsStatus.all_ok.value, '=', None)
        ]
        display_fields = ['number', 'member type', 'first name', 'last name', 'email']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_comms():
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None)
        ]
        display_fields = ['number', 'full name', 'member type', 'use email', 'email', 'mobile phone', 'home phone',
                          'address (line 1)', 'address (line 2)', 'address (line 3)', 'city', 'county', 'state',
                          'post code', 'country for post', 'voter', 'AFCW access', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields, action='query')

    @staticmethod
    def extract_cards_all():
        # annual replacement cards for printers
        query_clauses = [('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None)]
        display_fields = ['status at renewal', 'type at renewal', 'number at renewal', 'full name', 'card start year']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_renewals():
        # for renewal notices at membership year end
        end_date = fmt_date(current_year_end())
        query_clauses = [
            ('Member', 'end_date', end_date, '=', None),
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None)
        ]
        display_fields = \
            ['number', 'id number', 'full name', 'address (line 1)', 'address (line 2)', 'address (line 3)',
             'city', 'county', 'state', 'post code', 'country for post', 'status', 'member type', 'type at renewal',
             'email', 'comms', 'payment method', 'renewal notes', 'home phone', 'mobile phone', 'birth date',
             'junior email', 'AFCW access', '3rd pty access']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_debits():
        end_date = fmt_date(current_year_end())
        query_clauses = [
            ('Member', 'end_date', end_date, '=', None),
            ('Member', 'last_payment_method', PaymentMethod.dd, '=', None),
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None)
        ]
        display_fields = \
            ['number', 'type at renewal', 'full name', 'dues pending', 'email', 'address (line 1)', 'address (line 2)',
             'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields)
