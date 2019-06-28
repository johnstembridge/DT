import unittest

from etl.etl import process_etl_file, process_etl_db, member_etl, payment_etl, donation_etl, comment_etl, parse_comments


class TestEtl(unittest.TestCase):

    @staticmethod
    def members_etl(rec):
        header = ['Member ID', 'Sex', 'Prefix', 'First Name', 'Last Name', 'Birthdate', 'Email Address', 'Home Phone',
                  'Other Phone', 'Concession Type', 'Status Code', 'Start Date', 'End Date', 'Updated', 'Direct Debit',
                  'Use email', 'AFC has access']
        if type(rec) is str:
            return header
        return rec

    def test_member_etl_file(self):
        in_file = 'members_in.txt'
        out_file = 'members_out.txt'
        process_etl_file(in_file, out_file, member_etl)

    def test_payment_etl_file(self):
        in_file = 'payments_in.txt'
        out_file = 'payments_out.txt'
        process_etl_file(in_file, out_file, payment_etl)

    def test_etl_db(self):
        self.test_member_etl_db()
        self.test_payment_etl_db()
        self.test_donation_etl_db()
        self.test_comment_etl_db()

    def test_member_etl_db(self):
        in_file = 'D:\donstrust\exports\members.txt'
        process_etl_db(in_file, member_etl)

    def test_payment_etl_db(self):
        in_file = 'D:\donstrust\exports\payments.txt'
        process_etl_db(in_file, payment_etl)

    def test_donation_etl_db(self):
        in_file = 'D:\donstrust\exports\donations.txt'
        process_etl_db(in_file, donation_etl)

    def test_comment_etl_db(self):
        in_file = 'D:\donstrust\exports\comments.txt'
        process_etl_db(in_file, comment_etl)

    def test_parse_comments(self):
        comment = '13/08/2018: dd payment made'
        #comment = '22/06/2006: address change 05/10/2008: address change 13/02/2011: address change 18/08/2018: dd failed 20/08/2018: dd started again'
        #comment = 'Returned as moved to new (unknown address)'
        #comment = '"responded to final email Hi Do not want to renew.Regards"" Stephen Allen 31/07/2006: sent in renewal form! 04/09/2011: requested supporting eveidence for concession rate 11/09/2011: replied saying he is now employed and will send another £15"""'
        comment = '13/08/2018: dd payment made  12/09/2018: deceased Felix Stride-Darnley'
        comment_etl({'Member ID': '0-00368', 'Comments': comment})
        #parse_comments(comment)
