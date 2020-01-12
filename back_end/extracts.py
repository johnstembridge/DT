from back_end.query import Query
from back_end.data_utilities import fmt_date
from globals.enumerations import MembershipType, MemberStatus, MemberAction, ActionStatus, PaymentMethod, CommsType, \
    CommsStatus
import datetime


class Extracts:

    @staticmethod
    def extract_certificates():
        # new member packs
        query_clauses = [
            ('Action', 'status', ActionStatus.open.value, '=', None),
            ('Action', 'action', [a.value for a in MemberAction.send_certificates()], 'in', None)
        ]
        display_fields = ['number', 'status', 'member type', 'full name', 'address (line 1)', 'address (line 2)',
                          'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post',
                          'full address', 'certificate date', 'upgrade',
                          'card start year', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_cards():
        # renewal acknowledgement
        query_clauses = [
            ('Action', 'status', ActionStatus.open.value, '=', None),
            ('Action', 'action', [a.value for a in MemberAction.send_cards()], 'in', None)
        ]
        display_fields = ['number', 'status', 'member type', 'full name', 'address (line 1)', 'address (line 2)',
                          'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post', 'recent new',
                          'email bounced', 'card start year', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields)

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
        display_fields = ['number', 'member type', 'use email', 'email', 'full name', 'address (line 1)', 'address (line 2)',
                          'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post', 'first name',
                          'last name']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_cards_all():
        # annual replacement cards for printers
        query_clauses = [('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None)]
        display_fields = ['next member type', 'number', 'full name', 'card start year']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_renewals():
        # for renewal notices at membership year end
        end_date = fmt_date(datetime.date(datetime.date.today().year + 1, 8, 1))
        query_clauses = [
            ('Member', 'end_date', end_date, '=', None),
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None)
        ]
        display_fields = \
            ['number', 'member type', 'full name', 'address (line 1)', 'address (line 2)',
             'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post',
             'dues', 'payment method', 'birth date', 'email', 'use email', 'AFCW access', '3rd pty access',
             'home phone', 'mobile phone', 'junior email', 'volatile concession', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_debits():
        end_date = fmt_date(datetime.date(datetime.date.today().year + 1, 8, 1))
        query_clauses = [
            ('Member', 'end_date', end_date, '=', None),
            ('Member', 'last_payment_method', PaymentMethod.dd, '=', None),
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None)
        ]
        display_fields = \
            ['number', 'member type', 'full name', 'dues', 'email', 'address (line 1)', 'address (line 2)',
             'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields)
