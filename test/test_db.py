import unittest

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

from globals.enumerations import ActionStatus, MemberAction, MemberStatus
from models.dt_db import Base, Member, Address, Action, Comment, Payment, EnumType
from globals import config


class TestDb(unittest.TestCase):

    def setUp(self):
        db_path = config.get('db_path')
        self.engine = create_engine(db_path, echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # Base.metadata.create_all(self.engine)

    def test_member(self):
        member = self.session.query(Member).get(34)
        pass

    def test_payment(self):
        payment = self.session.query(Payment).get(1)
        pass

    def test_actions(self):
        actions = self.session.query(Action).filter_by(member_id=12).all()
        pass

    def test_get_cards(self):
        details = self.session \
            .query(Member.id, Member.first_name, Member.last_name, Member.start_date, Address, Action) \
            .join(Address) \
            .outerjoin(Action) \
            .filter(Action.status == ActionStatus.open, Action.action == MemberAction.card).all()
        pass

    def test_get_cards_2(self):
        details = self.session \
            .query(Action) \
            .filter(Action.status == ActionStatus.open, Action.action == MemberAction.card).all()
        pass

    def test_check_last_payment(self):
        active = self.session.query(Member).filter(Member.status < MemberStatus.lapsed)
        for member in active:
            pay_method = member.last_payment_method
            if pay_method is None:
                pass
            if len(member.payments) > 0:
                actual = member.payments[0].method
                if actual == pay_method:
                    continue
                else:
                    pass
            else:
                pass


if __name__ == '__main__':
    unittest.main()
