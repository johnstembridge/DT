import unittest
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from flask import jsonify
from models.dt_db import Member, Address, Action, Comment, Payment, EnumType
from globals import config


class TestDbSerialise(unittest.TestCase):

    def setUp(self):
        db_path = config.get('db_path')
        self.engine = create_engine(db_path, echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # Base.metadata.create_all(self.engine)

    def test_member(self):
        member = self.session.query(Member).get(561)
        json = member.to_dict()
        member.from_dict(json)
        pass

if __name__ == '__main__':
    unittest.main()
