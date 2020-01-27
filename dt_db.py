import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.dt_db import *  # Base, EnumType, Member, Address, Action, Comment, Payment etc.
from globals import config
from etl.etl import process_etl, member_etl, payment_etl, donation_etl, comment_etl, country_etl, county_etl, \
    state_etl, user_etl


def delete_tables():
    Base.metadata.drop_all(engine)


def create_tables():
    Base.metadata.create_all(engine)


def import_all():
    process_etl(import_path, 'counties.txt', session, county_etl)
    process_etl(import_path, 'states.txt', session, state_etl)
    process_etl(import_path, 'countries.txt', session, country_etl)
    process_etl(import_path, 'members.txt', session, member_etl)
    process_etl(import_path, 'payments.txt', session, payment_etl)
    process_etl(import_path, 'donations.txt', session, donation_etl)
    process_etl(import_path, 'comments.txt', session, comment_etl)
    process_etl(import_path, 'users.txt', session, user_etl)


if __name__ == '__main__':
    args = sys.argv
    db_path = config.get('db_path')
    import_path = config.get('locations')['import']
    engine = create_engine(db_path, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    if 'test' in args:
        print('Database test')
    if 'delete' in args or 'all' in args:
        delete_tables()
    if 'create' in args or 'all' in args:
        create_tables()
    if 'etl' in args or 'all' in args:
        import_all()
