from back_end.query import Query
from back_end.data_utilities import fmt_date
from globals.enumerations import MembershipType, MemberStatus, MemberAction, ActionStatus, PaymentMethod, CommsType, \
    CommsStatus
import datetime


class Extracts:

    @staticmethod
    def extract_certificates():
        # new member packs
        head = ['id', 'status', 'type', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city',
                'county', 'state', 'post_code', 'country', 'address', 'cert_date', 'upgrade']
        query_clauses = [
            ('Action', 'status', ActionStatus.open.value, '=', None),
            ('Action', 'action', [MemberAction.certificate.value, MemberAction.upgrade.value, MemberAction.replacement.value], 'in', None)
        ]
        display_fields = ['number', 'status', 'member type', 'full name', 'address (line 1)', 'address (line 2)',
                          'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post',
                          'full address', 'certificate date', 'upgrade',
                          'card start year', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_cards():
        # renewal acknowledgement
        head = ['id', 'type', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'recent_new', 'bounced_email']
        query_clauses = [
            ('Action', 'status', ActionStatus.open.value, '=', None),
            ('Action', 'action', [MemberAction.card.value, MemberAction.resend.value], 'in', None)
        ]
        display_fields = ['number', 'status', 'member type', 'full name', 'address (line 1)', 'address (line 2)',
                          'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post', 'recent new',
                          'email bounced', 'card start year', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_juniors():
        head = ['id', 'status', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county',
                'state', 'post_code', 'country', 'amount', 'first_name', 'last_name']
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
        head = ['id', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3',
                'city', 'county', 'state', 'post_code', 'country', 'email', 'home_phone', 'mobile_phone', 'birth_date',
                'age_next_birthday', 'first_name', 'last_name']
        today = datetime.date.today()
        if not month:
            month = today.month % 12 + 1  # next month
        query_clauses = [
            ('Member', 'member_type', MembershipType.junior.value, '=', None),
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Member', 'birth_date', month, '=', 'month'),
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
        head = ['id', 'type', 'first_name', 'last_name', 'use_email', 'email',
                'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county', 'state', 'post_code', 'country']

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
        head = ['member_id', 'status', 'type', 'fullname', 'address_line_1', 'address_line_2', 'address_line_3', 'city',
                'county', 'state', 'post_code', 'country', 'amount', 'pay_method', 'birth_date', 'email', 'use_email',
                'afcw_access', 'third_pty_access', 'home_phone', 'mobile_phone', 'jd_email', 'volatile_concession',
                'latest_action']
        end_date = fmt_date(datetime.date(datetime.date.today().year + 1, 8, 1))
        query_clauses = [
            ('Member', 'end_date', end_date, '=', None),
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None)
        ]
        display_fields = \
            ['number', 'status', 'member type', 'full name', 'address (line 1)', 'address (line 2)',
             'address (line 3)', 'city', 'county', 'state', 'post code', 'country for post',
             'dues', 'payment method', 'birth date', 'email', 'use email', 'AFCW access', '3rd pty access',
             'home phone', 'mobile phone', 'junior email', 'volatile concession', 'first name', 'last name']
        return Query.show_found_do(query_clauses, display_fields)

    @staticmethod
    def extract_debits():
        head = ['id', 'type', 'first_name', 'last_name', 'amount', 'email', 'home_phone', 'mobile_phone',
                'address_line_1', 'address_line_2', 'address_line_3', 'city', 'county', 'state', 'post_code', 'country']
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
