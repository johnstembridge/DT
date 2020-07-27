from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import calendar
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, SmallInteger, Date, Numeric, ForeignKey, TypeDecorator, DateTime, Enum

from globals.enumerations import MembershipType, MemberStatus, PaymentType, PaymentMethod, Sex, UserRole, CommsType, \
    Dues, ExternalAccess, MemberAction, ActionStatus, JuniorGift, Title, AgeBand, CommsStatus, PlusUpgradeDues
from back_end.data_utilities import fmt_date, parse_date, first_or_default, current_year_end, encode_date_formal, \
    match_string
from datetime import datetime, date
from time import time, localtime, strftime

Base = declarative_base()


class EnumType(TypeDecorator):
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


class IntArray(TypeDecorator):
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
    county_id = Column(Integer, ForeignKey('counties.id'), nullable=True)
    county = relationship('County', back_populates='addresses')
    state_id = Column(Integer, ForeignKey('states.id'), nullable=True)
    state = relationship('State', back_populates='addresses')
    post_code = Column(String(20))
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    country = relationship('Country', back_populates='addresses')

    members = relationship('Member', back_populates='address')

    dict_fields = ['line_1', 'line_2', 'line_3', 'city', 'county', 'state', 'post_code', 'country']

    def to_dict(self):
        data = {}
        for field in self.dict_fields:
            value = getattr(self, field)
            data[field] = value
        return data

    def from_dict(self, data):
        for field in self.dict_fields:
            if field in data:
                value = data[field]
                setattr(self, field, value)

    def country_for_mail(self):
        return self.country.name if self.country.code != 'UK' else ''

    def full(self):
        return ', '.join(
            [item for item in
             [self.line_1,
              self.line_2,
              self.line_3,
              self.city,
              self.county.name if self.county else '',
              self.state.code if self.state else '',
              self.post_code,
              self.country_for_mail()
              ]
             if item and len(item) > 0])

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
    comment = Column(String(1024), nullable=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    member = relationship('Member', back_populates='comments')

    def __repr__(self):
        return '<Comment {} {} {}>'.format(self.member_id, self.date, self.comment)


class Junior(Base):
    __tablename__ = 'juniors'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'))
    member = relationship('Member', back_populates='junior')
    email = Column(String(120))
    gift = Column(EnumType(JuniorGift), nullable=True)

    def __repr__(self):
        return '<Junior {} {} {}>'.format(self.member_id, self.parent_email, self.gift)


class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=True)
    sex = Column(EnumType(Sex), nullable=True)
    title = Column(EnumType(Title), nullable=True)
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
    comms_status = Column(EnumType(CommsStatus), nullable=True)
    external_access = Column(EnumType(ExternalAccess), nullable=True)
    season_ticket_id = Column(Integer, nullable=True)
    user = relationship('User', uselist=False, back_populates='member')
    payments = relationship('Payment', order_by='desc(Payment.date)', back_populates='member')
    comments = relationship('Comment', order_by='desc(Comment.date)', back_populates='member')
    actions = relationship('Action', order_by='desc(Action.date)', back_populates='member')
    junior = relationship('Junior', uselist=False, back_populates='member')

    # region Member extras
    dict_fields = ['number', 'start_date', 'end_date', 'status', 'member_type', 'sex', 'birth_date', 'title',
                   'first_name', 'last_name', 'address', 'email', 'home_phone', 'mobile_phone', 'comms',
                   'external_access']

    def to_dict(self):
        data = {}
        for field in self.dict_fields:
            value = getattr(self, field)
            if 'date' in field:
                value = fmt_date(value)
            elif isinstance(value, Enum):
                value = value.to_dict()
            elif field == 'address':
                value = value.to_dict()
            data[field] = value
        return data

    def from_dict(self, data):
        for field in self.dict_fields:
            if field in data:
                if 'date' in field:
                    setattr(self, field, parse_date(data[field], reverse=True))
                elif field == 'address':
                    self.address.from_dict(data[field])
                else:
                    if data[field] and isinstance(getattr(Member, field).property.columns[0].type, EnumType):
                        field_type = type(getattr(self, field))
                        value = field_type.from_name(data[field])
                    else:
                        value = data[field]
                    setattr(self, field, value)

    def dt_number(self):
        member_prefix = 'JD' if self.member_type == MembershipType.junior else 'DT'
        return '{}0-{:05d}'.format(member_prefix, self.number or 0)

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def formal_name(self):
        if not self.title:
            title = ''
        else:
            title = self.title.name + ' '
        return title + self.first_name + ' ' + self.last_name

    def is_adult(self):
        return self.member_type in MembershipType.adult()

    def is_active(self):
        return self.status in MemberStatus.all_active()

    def is_upgrade(self):
        return self.is_adult() and \
               first_or_default(self.actions, MemberAction.other) == MemberAction

    def is_recent_new(self):
        return self.start_date >= datetime(current_year_end().year, 2, 1).date()

    def is_founder(self):
        return self.number <= 1889

    def is_life(self):
        return self.end_date == datetime(2100, 8, 1).date()

    def is_plus(self):
        return self.status == MemberStatus.plus

    def email_bounced(self):
        return self.comms_status == CommsStatus.email_fail

    def next_birthday(self, as_of=None):
        if not self.birth_date:
            return None
        if not as_of:
            as_of = datetime.today().date()
        birth_date = self.birth_date
        leap = birth_date.month == 2 and birth_date.day == 29
        if leap:
            birth_date = birth_date.replace(day=28)
        next_birthday = birth_date.replace(year=as_of.year)
        if next_birthday < as_of:
            next_birthday = next_birthday.replace(year=as_of.year + 1)
        if leap and next_birthday.year % 4 == 0:
            next_birthday = next_birthday.replace(day=29)
        return next_birthday

    def birth_month(self):
        if self.birth_date:
            return calendar.month_name[self.birth_date.month]
        return None

    def age(self, as_of=None, default=False):
        if self.birth_date:
            if not as_of:
                as_of = datetime.today().date()
            years = as_of.year - self.birth_date.year
            if as_of.month < self.birth_date.month or (
                    as_of.month == self.birth_date.month and as_of.day < self.birth_date.day):
                years -= 1
            return years
        else:
            # defaults
            if not default:
                return None
            elif self.member_type:
                if self.member_type == MembershipType.junior:
                    return AgeBand.junior.lower
                elif self.member_type == MembershipType.intermediate:
                    return AgeBand.intermediate.lower
                elif self.member_type == MembershipType.senior:
                    return AgeBand.senior.lower
                else:
                    return AgeBand.adult.lower
            else:
                return AgeBand.adult.lower

    def age_next_birthday(self):
        return self.age(self.next_birthday())

    def age_next_renewal(self, default=False):
        next_renewal_date = current_year_end()
        return self.age(next_renewal_date, default)

    def member_type_next_renewal(self, as_of=None):
        if self.member_type in MembershipType.all_concessions():
            return self.member_type
        if not as_of:
            as_of = current_year_end()
        age = self.age(as_of, True)
        if age <= AgeBand.junior.upper:
            return MembershipType.junior
        if age <= AgeBand.intermediate.upper:
            return MembershipType.intermediate
        if age <= AgeBand.senior.lower:
            return MembershipType.standard
        if age > AgeBand.senior.lower:
            return MembershipType.senior
        return MembershipType.standard

    def dues(self, as_of=None, default=True):
        if self.status == MemberStatus.life:
            return 0
        if not as_of:
            as_of = current_year_end()
        type = self.member_type_next_renewal(as_of)
        if type in MembershipType.all_concessions():
            return Dues.concession.value
        if type == MembershipType.junior:
            if self.start_date.year == self.end_date.year and as_of <= self.end_date:
                return Dues.junior_new.value
            return Dues.junior.value
        if type == MembershipType.intermediate:
            return Dues.intermediate.value
        if type == MembershipType.senior:
            return Dues.senior.value
        return Dues.standard.value

    def upgrade_dues(self, as_of=None):
        if self.status == MemberStatus.life:
            return 0
        if not as_of:
            as_of = current_year_end()
        type = self.member_type_next_renewal(as_of)
        if type in MembershipType.all_concessions():
            return PlusUpgradeDues.concession.value
        if type == MembershipType.intermediate:
            return PlusUpgradeDues.intermediate.value
        if type == MembershipType.senior:
            return PlusUpgradeDues.senior.value
        return PlusUpgradeDues.standard.value

    def use_email(self):
        return self.comms == CommsType.email and self.comms_status == CommsStatus.all_ok

    def afcw_has_access(self):
        return (self.external_access or ExternalAccess.AFCW).value > ExternalAccess.none.value

    def third_pty_access(self):
        return (self.external_access or ExternalAccess.AFCW) == ExternalAccess.all

    def volatile_concession(self):
        return self.member_type in MembershipType.volatile_concessions()

    def start_year_for_card(self):
        if self.is_life():
            extra = ' (life member)'
        elif self.is_founder():
            extra = ' (founder)'
        elif self.is_plus():
            extra = ' (plus)'
        else:
            extra = ''
        return str(self.start_date.year) + extra

    def certificate_date(self):
        return encode_date_formal(date.today(), cert=True)

    def current_action(self):
        current = [a for a in self.actions if a.status == ActionStatus.open]
        if len(current) > 0:
            return sorted(current, key=lambda action: action.date, reverse=True)[0]
        else:
            return None

    def last_payment(self):
        dates = [p.date for p in self.payments]
        if len(dates) > 0:
            latest = [p for p in self.payments if p.date == max(dates)][0]
        else:
            latest = None
        return latest

    def last_payment_date(self):
        payment = self.last_payment()
        if payment:
            latest = payment.date
        else:
            latest = None
        return latest

    def last_payment_type(self):
        payment = self.last_payment()
        if payment:
            latest = payment.type.name
        else:
            latest = None
        return latest

    def check_credentials(self, user_name, password):
        if not match_string(user_name, str(self.number)):
            return False, 'Email does not match', 'warning'
        post_code = password.split('!')[0]
        if not match_string(post_code, self.address.post_code):
            return False, 'Post Code does not match', 'warning'
        return True, '', ''

    def concession_type(self):
        if self.member_type in MembershipType.all_concessions(plus=True):
            long = [c for c in MembershipType.renewal_choices() if c[0] == self.member_type.value][0][1]
        else:
            long = ''
        return long

    def long_membership_type(self):
        plus = '' if self.status == MemberStatus.current \
            else ' (' + [c for c in MemberStatus.renewal_choices() if c[0] == self.status.value][0][1] + ')'
        return [c for c in MembershipType.renewal_choices() if c[0] == self.member_type.value][0][1] + plus

    def renewal_notes_as_text(self):
        return '\n'.join(self.renewal_notes())

    def renewal_notes(self):
        age = self.age_next_renewal(default=True)
        new_member = self.is_recent_new()
        renewal_dues = '£' + str(self.dues())
        renewal_cost = "The renewal cost is {}. ".format(renewal_dues) if not new_member else ''
        upgrade_dues = '£' + str(self.upgrade_dues() if new_member else self.dues() + self.upgrade_dues())
        upgrade_para = "You may upgrade to Dons Trust Plus membership at a total cost of {}.".format(upgrade_dues)
        member_type = self.member_type_next_renewal()
        notes = []
        if self.status == MemberStatus.life:
            notes = [
                "As you are a life member, there is no need to do anything further. " \
                "We will send your new membership card in due course.", ]
        else:
            if member_type == MembershipType.intermediate:
                if age == 21:
                    notes = [
                        "Young adult membership has been extended to age 21 in line with Season Tickets.", \
                        "{}{}".format(renewal_cost, upgrade_para)]
                else:
                    notes = ["{}{}".format(renewal_cost, upgrade_para)]
            elif member_type == MembershipType.junior:
                if age in [16, 17]:
                    notes = [
                        "Junior Dons will now cover the age range from 0 to 17-year olds. 16 and 17-year olds will " \
                        "still have full Dons Trust membership rights including voting rights.", \
                        "The Junior Dons membership has been enhanced. Along with the package of benefits that JDs " \
                        "used to receive, the new stadium gives the opportunity to increase the benefits offered.", \
                        "{}".format(renewal_cost), ]
                else:
                    notes = [
                        "The Junior Don membership has been enhanced. Along with the package of benefits that you " \
                        "used to receive, the new stadium gives the opportunity to increase the benefits offered.", \
                        "{}".format(renewal_cost), ]
            elif member_type == MembershipType.senior:
                notes = ["{}{}".format(renewal_cost, upgrade_para), ]
            elif member_type in MembershipType.all_concessions():
                notes = [
                    "According to our records, you currently have a concessionary membership ({}).".format(
                        member_type.name),
                    "{}{}".format(renewal_cost, upgrade_para),
                    "**If your circumstances have changed please choose the appropriate membership type."]
            else:
                if member_type == MembershipType.standard:
                    if age < 60:
                        notes = ["{}{}".format(renewal_cost, upgrade_para), ]
                    elif age in range(60, 64):
                        notes = [
                            "To bring Dons Trust membership age range in line with the Club, we are moving the " \
                            "age range for senior members from 60+ to 65+.", \
                            "{}{}".format(renewal_cost, upgrade_para)]
                    else:
                        notes = ["{}{}".format(renewal_cost, upgrade_para), ]
        if self.last_payment_method == PaymentMethod.dd:
            up = "If you do not wish to upgrade to Dons Trust Plus, you need take no further action." \
                if member_type != MembershipType.junior else ''
            notes = [
                        "According to our records you currently pay by direct debit. " + up,
                        "Provided the payment is taken successfully, your membership will be automatically updated."
                    ] + notes
        elif new_member:
            notes = [
                        "As you joined relatively late during the membership year we will automatically extend " \
                        "your membership until August 2021.", ] + notes
        return notes

    def renewal_activated(self):
        last_payment = self.last_payment()
        if last_payment.type.name == 'pending':
            last_action = self.current_action()
            if last_action.action == MemberAction.upgrade and last_action.status == ActionStatus.open:
                return 'Renewal was activated {} ({})'.format(fmt_date(last_action.date), last_action.comment)
            else:
                return 'Renewal was activated {}'.format(fmt_date(Action.date))
        else:
            return None

    def __repr__(self):
        return '<Member: {} {}>'.format(self.dt_number(), self.full_name())
    # endregion


class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    user_name = Column(String(25), nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(EnumType(UserRole), nullable=False)
    member = relationship('Member', back_populates='user')
    token = Column(String(256), nullable=True, index=True, unique=True)
    expires = Column(DateTime, nullable=True)

    # region User extras
    def to_dict(self):
        data = {
            'id': self.id,
            'user_name': self.user_name,
            'member_number': self.member.dt_number(),
            'role': self.role.name
        }
        return data

    def has_access(self, required_role):
        return self.role.value >= required_role.value

    def is_access(self, required_role):
        return self.role == required_role

    def has_lapsed_access(self, type='any'):
        return self.role in UserRole.lapsed_access(type)

    def access_limit(self):
        if self.role in UserRole.lapsed_access('all'):
            return 100
        if self.role in UserRole.lapsed_access('any'):
            return MemberStatus.lapsed.value
        return MemberStatus.current.value

    def has_write_access(self):
        return self.role in UserRole.write_access()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if self.password:
            return check_password_hash(self.password, password)
        return True

    @staticmethod
    def member_password(post_code):
        return post_code.lower().replace(' ', '') + '!salty'

    def get_token(self, app, expires_in=3600):
        exp = None
        if self.token:
            exp = User.decode_token(self.token, app)['exp']
            # exp = jwt.decode(self.token, app.config['SECRET_KEY'], algorithms=['HS256'])['exp']
        if exp and exp < time() + 60:
            exp = time() + expires_in
            self.token = User.encode_token(self.id, exp, app)
            # self.token = jwt.encode(
            #     {'sub': self.id, 'exp': exp},
            #     app.config['SECRET_KEY'],
            #     algorithm='HS256'
            # ).decode('utf-8')
        return self.token, strftime('%a, %d %b %Y %H:%M:%S +0000', localtime(exp))

    def revoke_token(self, app):
        self.token = User.encode_token(self.id, time() - 1, app)

    @staticmethod
    def check_token(app, token):
        user = User.query.filter_by(token=token).first()
        if user is None or User.decode_token(token, app)['sub'] < time():
            return None
        return user

    @staticmethod
    def validate_token(app, token):
        try:
            id = User.decode_token(token, app)['sub']
            # id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['sub']
        except jwt.ExpiredSignatureError:
            return False, 'Signature expired. Please try again.'
        except jwt.InvalidTokenError:
            return False, 'Invalid token. Please try again.'
        return True, id

    @staticmethod
    def encode_token(id, exp, app):
        return jwt.encode(
            {'sub': id, 'exp': exp},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        ).decode('utf-8')

    @staticmethod
    def decode_token(token, app):
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

    # endregion

    def __repr__(self):
        return '<User {}>'.format(self.user_name)


class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    code = Column(String(5), nullable=False)
    name = Column(String(50), nullable=False)
    addresses = relationship("Address", back_populates="country")

    def is_uk(self):
        return self.code == 'UK'

    def __repr__(self):
        return '<Country {}>'.format(self.code, self.name)


class County(Base):
    __tablename__ = 'counties'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    addresses = relationship("Address", back_populates="county")

    def __repr__(self):
        return '<County {}>'.format(self.name)


class State(Base):
    __tablename__ = 'states'
    id = Column(Integer, primary_key=True)
    code = Column(String(5), nullable=False)
    name = Column(String(50), nullable=False)
    addresses = relationship("Address", back_populates="state")

    def __repr__(self):
        return '<State {}: {}>'.format(self.code, self.name)
