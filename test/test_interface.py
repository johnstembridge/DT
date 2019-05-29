import unittest

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

from globals.enumerations import ActionStatus, MemberAction
from models.dt_db import Base, Member, Address, Action, Comment, Payment, EnumType
from globals import config

from back_end.interface import select


class TestDb(unittest.TestCase):

    def setUp(self):
        db_path = config.get('db_path')
        self.engine = create_engine(db_path, echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # Base.metadata.create_all(self.engine)

    def test_select(self):
        actions = select(Action, Action, (Action.status == ActionStatus.open, Action.action == MemberAction.card))

        pass

