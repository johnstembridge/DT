import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.dt_db import *  # Base, Member, Address, Action, Comment, Payment, EnumType
from globals import config


class TestDb(unittest.TestCase):

    def setUp(self):
        db_path = config.get('db_path')
        self.engine = create_engine(db_path, echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

    def test_create_tables(self):
        pass

