from flask_login import UserMixin
from main import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from back_end.data_utilities import fmt_date, in_date_range
from globals.enumerations import MembershipType, MemberStatus, PaymentType, PaymentMethod, Sex, UserRole, \
    CommsType, Dues, ExternalAccess, MemberAction, ActionStatus

import datetime
from time import time, localtime, strftime

Base = db.Model
Column = db.Column
Integer = db.Integer
SmallInteger = db.SmallInteger
Date = db.Date
Time = db.Time
Numeric = db.Numeric
String = db.String
ForeignKey = db.ForeignKey
Boolean = db.Boolean
relationship = db.relationship
backref = db.backref


class EnumType(db.TypeDecorator):
    impl = SmallInteger

    def __init__(self, data, **kw):
        self.data = data
        super(EnumType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        if value in ['', None]:
            return None
        return value.value

    def process_result_value(self, value, dialect):
        if value in ['', None]:
            return None
        return self.data(value)


class IntArray(db.TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = ','.join([str(x) for x in value])
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = [int(x) for x in value.split(',')]
        return value


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    line_1 = Column(String(50))
    line_2 = Column(String(50))
    line_3 = Column(String(50))
    city = Column(String(30))
    county = Column(String(20))
    state = Column(String(10))
    post_code = Column(String(20))
    country = Column(String(25))
    members = relationship('Member', back_populates='address')

    def full(self):
        return [item for item in
                [self.line_1,
                 self.line_2,
                 self.line_3,
                 self.county,
                 self.state,
                 self.post_code,
                 self.country]
                if len(item) > 0]

    def __repr__(self):
        return '<Address: {}>'.format(', '.join(self.full()))


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    amount = Column(Numeric(precision=6, scale=2), nullable=False)
    type = Column(EnumType(PaymentType), nullable=False)
    method = Column(EnumType(PaymentMethod), nullable=True)
    comment = Column(String(100), nullable=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    member = relationship('Member', back_populates='payments')

    def __repr__(self):
        return '<Payment {} {} {}>'.format(self.member.full_name(), self.date, self.amount)


class Action(Base):
    __tablename__ = 'actions'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    action = Column(EnumType(MemberAction), nullable=True)
    status = Column(EnumType(ActionStatus), nullable=True)
    comment = Column(String(100), nullable=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    member = relationship('Member', back_populates='actions')

    def __repr__(self):
        return '<Action {} {} {} {}>'.format(self.member_id, self.date, self.action, self.status)


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    comment = Column(String(250), nullable=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    member = relationship('Member', back_populates='comments')

    def __repr__(self):
        return '<Comment {} {} {}>'.format(self.member_id, self.date, self.comment)


class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    sex = Column(EnumType(Sex), nullable=True)
    title = Column(String(10), nullable=True)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    birth_date = Column(Date)
    email = Column(String(120))
    home_phone = Column(String(25))
    mobile_phone = Column(String(25))
    address_id = Column(Integer, ForeignKey('addresses.id'), nullable=False)
    address = relationship('Address', back_populates='members')
    member_type = Column(EnumType(MembershipType), nullable=False)
    status = Column(EnumType(MemberStatus), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    last_updated = Column(Date)
    last_payment_method = Column(EnumType(PaymentMethod), nullable=True)
    comms = Column(EnumType(CommsType), nullable=True)
    external_access = Column(EnumType(ExternalAccess), nullable=True)
    user = relationship('User', uselist=False, back_populates='member')
    payments = relationship('Payment', order_by='desc(Payment.date)', back_populates='member')
    comments = relationship('Comment', order_by='desc(Comment.date)', back_populates='member')
    actions = relationship('Action', order_by='desc(Action.date)', back_populates='member')

    def dt_number(self):
        member_type = 'JD' if self.member_type == MembershipType.junior else 'DT'
        return '{}0-{:05d}'.format(member_type, self.id)

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def active(self):
        return self.status in MemberStatus.all_active()

    def age(self, as_of=None):
        if self.birth_date:
            if not as_of:
                as_of = datetime.date.today()
            years = as_of.year - self.birth_date.year
            if as_of.month < self.birth_date.month or (
                    as_of.month == self.birth_date.month and as_of.day < self.birth_date.day):
                years -= 1
            return years
        return None

    def dues(self, as_of=None):
        if not as_of:
            as_of = self.end_date
        age = self.age(as_of)
        if age < 16:
            if self.start_date.year == self.end_date.year and as_of < self.end_date:
                return Dues.junior_new.value
            return Dues.junior.value
        if age <= 21:
            return Dues.intermediate.value
        if self.member_type in MembershipType.all_concessions():
            return Dues.concession.value
        return Dues.standard.value

    def current_payment_method(self):
        return self.payments[0].method

    def __repr__(self):
        return '<Member: {} {}>'.format(self.dt_number(), self.full_name())


class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    user_name = Column(String(25), nullable=False)
    password = Column(String(100), nullable=False)
    roles = relationship('Role', back_populates='user')
    member = relationship('Member', back_populates='user')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_reset_password_token(self, app, expires_in=600):
        exp = time() + expires_in
        token = jwt.encode(
            {'reset_password': self.id, 'exp': exp},
            app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')
        return token, strftime('%a, %d %b %Y %H:%M:%S +0000', localtime(exp))

    @staticmethod
    def verify_reset_password_token(app, token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.user_name)


class Role(Base):
    __tablename__ = 'roles'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, primary_key=True)
    role = Column(EnumType(UserRole), nullable=False, primary_key=True)
    user = relationship('User', back_populates='roles')

    def __repr__(self):
        return '<Role {}>'.format(self.role.name)
