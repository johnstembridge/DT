import unittest
import os

from globals import config
from etl.etl import process_etl, member_etl, payment_etl, donation_etl, comment_etl, country_etl, county_etl, \
    state_etl, user_etl


class TestEtl(unittest.TestCase):
    def setUp(self):
        self.import_path = config.get('locations')['import']

    def test_etl_db(self):
        self.county_etl_db()
        self.state_etl_db()
        self.country_etl_db()
        self.member_etl_db()
        self.payment_etl_db()
        self.donation_etl_db()
        self.comment_etl_db()
        self.user_etl_db()

    def user_etl_db(self):
        in_file = os.path.join(self.import_path, 'users.txt')
        process_etl(in_file, user_etl)

    def country_etl_db(self):
        in_file = os.path.join(self.import_path, 'countries.txt')
        process_etl(in_file, country_etl)

    def county_etl_db(self):
        in_file = os.path.join(self.import_path, 'counties.txt')
        process_etl(in_file, county_etl)

    def state_etl_db(self):
        in_file = os.path.join(self.import_path, 'states.txt')
        process_etl(in_file, state_etl)

    def member_etl_db(self):
        in_file = os.path.join(self.import_path, 'members.txt')
        process_etl(in_file, member_etl)

    def payment_etl_db(self):
        in_file = os.path.join(self.import_path, 'payments.txt')
        process_etl(in_file, payment_etl)

    def donation_etl_db(self):
        in_file = os.path.join(self.import_path, 'donations.txt')
        process_etl(in_file, donation_etl)

    def comment_etl_db(self):
        in_file = os.path.join(self.import_path, 'comments.txt')
        process_etl(in_file, comment_etl)

    def xtest_parse_comments(self):
        comment = '13/08/2018: dd payment made'
        # comment = '22/06/2006: address change 05/10/2008: address change 13/02/2011: address change 18/08/2018: dd failed 20/08/2018: dd started again'
        # comment = 'Returned as moved to new (unknown address)'
        # comment = '"responded to final email Hi Do not want to renew.Regards"" Stephen Allen 31/07/2006: sent in renewal form! 04/09/2011: requested supporting eveidence for concession rate 11/09/2011: replied saying he is now employed and will send another £15"""'
        comment = '13/08/2018: dd payment made  12/09/2018: deceased Felix Stride-Darnley'
        comment_etl({'Member ID': '0-00368', 'Comments': comment})
        # parse_comments(comment)
