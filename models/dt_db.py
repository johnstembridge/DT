from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import calendar
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, SmallInteger, Date, Numeric, ForeignKey, TypeDecorator, DateTime, Enum

from globals.enumerations import MembershipType, MemberStatus, PaymentType, PaymentMethod, Sex, UserRole, CommsType, \
    Dues, ExternalAccess, MemberAction, ActionStatus, JuniorGift, Title, AgeBand, CommsStatus, PlusUpgradeDues, \
    PlusDues, YesNo
from back_end.data_utilities import fmt_date, parse_date, first_or_default, current_year_end, encode_date_formal, \
    previous_year_end, match_string, fmt_phone, fmt_curr, current_renewal_date
from datetime import datetime
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
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=True)
    region = relationship('Region', back_populates='addresses')
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
        return '<Action {} {} {} {}>'.format(self.member_id, self.date, self.action.name, self.status.name)


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
    parental_consent = Column(EnumType(YesNo), nullable=True)

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

    def dt_number(self, renewal=False):
        member_prefix = 'JD' if not self.voter(renewal) else 'DT'
        status = self.member_status_at_renewal() if renewal else self.status
        return '{}0{}{:05d}'.format(member_prefix, '+' if status == MemberStatus.plus else '-', self.number or 0)

    def fmt_id_number(self):
        return '{:05d}'.format(self.number)

    def voter(self, renewal=False):
        if self.start_date > previous_year_end():
            age = self.age(self.start_date, default=True)
        else:
            age = self.age_last_renewal(default=True)
        return age >= 16

    def title_for_ptx(self):
        if self.title:
            title = self.title.name
            if title not in ['Mr', 'Mrs', 'Miss', 'Dr']:
                title = ''
        else:
            title = ''
        return title

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

    def is_pending_upgrade(self):
        last_payment = self.last_payment()
        return last_payment and last_payment.type == PaymentType.pending and last_payment.amount > self.base_dues()

    def is_pending_downgrade(self):
        last_payment = self.last_payment()
        return last_payment and last_payment.type == PaymentType.pending and last_payment.amount < self.base_dues()

    def is_recent_new(self):
        return self.start_date >= datetime(current_year_end().year, 2, 1).date()

    def is_recent_resume(self):
        if self.status == MemberStatus.life:
            return False
        last = self.last_payment()
        if not last:
            resume = False
        else:
            resume = last.comment == 'resume lapsed' and last.date >= datetime(current_year_end().year, 2, 1).date()
        not_dd_pending = self.last_payment_method != PaymentMethod.dd_pending
        return resume and not_dd_pending

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
            birth_date = self.birth_date
            leap = birth_date.month == 2 and birth_date.day == 29
            if leap:
                birth_date = birth_date.replace(day=28)
            if not as_of:
                as_of = datetime.today().date()
            years = as_of.year - birth_date.year
            if as_of.month < birth_date.month or (
                    as_of.month == birth_date.month and as_of.day < birth_date.day):
                years -= 1
            return years
        else:
            if default:
                return self.default_age()
            else:
                return None

    def default_age(self):
        if self.member_type:
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

    def phone(self):
        if self.mobile_phone:
            ret = self.mobile_phone
        else:
            ret = self.home_phone
        return fmt_phone(ret, self.address.country.code)

    def dt_number_at_renewal(self):
        return self.dt_number(renewal=True)

    def age_at_renewal(self, default=False):
        next_renewal_date = current_year_end()
        return self.age(next_renewal_date, default)

    def age_last_renewal(self, default=False):
        last_renewal_date = previous_year_end()
        return self.age(last_renewal_date, default)

    def member_status_at_renewal(self):
        status = self.status
        if status not in [MemberStatus.life, MemberStatus.plus]:
            upgrade = first_or_default([a for a in self.actions if
                                        a.action == MemberAction.upgrade and
                                        a.status == ActionStatus.open and
                                        a.comment == 'Upgrade to DT plus'],
                                       None)
            if upgrade:
                status = MemberStatus.plus
        return status

    def member_type_at_renewal(self, as_of=None):
        if self.member_type in MembershipType.concessions():
            return self.member_type
        if not as_of:
            as_of = current_renewal_date()
        age = self.age(as_of, True)
        if age <= AgeBand.junior.upper:
            return MembershipType.junior
        if age <= AgeBand.intermediate.upper:
            return MembershipType.intermediate
        if age < AgeBand.senior.lower:
            return MembershipType.standard
        if age >= AgeBand.senior.lower:
            return MembershipType.senior
        return MembershipType.standard

    def extended_member_type_at_renewal(self, as_of=None):
        type = self.member_type_at_renewal().name
        if self.is_plus():
            return type + ', plus'
        else:
            return type

    def dues(self, as_of=None):
        if self.status == MemberStatus.life or self.is_recent_resume() or self.is_recent_new():
            return 0
        status = self.member_status_at_renewal()
        if status == MemberStatus.plus:
            return self.plus_dues(as_of)
        else:
            return self.base_dues(as_of=as_of)

    def base_dues(self, type=None, as_of=None):
        if not as_of:
            as_of = current_year_end()
        if not type:
            type = self.member_type
        else:
            type = self.member_type_at_renewal(as_of)
        if self.status == MemberStatus.life or self.is_recent_resume() or self.is_recent_new():
            return 0
        if type in MembershipType.concessions():
            return Dues.concession.value
        if type == MembershipType.junior:
            return Dues.junior.value
        if type == MembershipType.intermediate:
            return Dues.intermediate.value
        if type == MembershipType.senior:
            return Dues.senior.value
        return Dues.standard.value

    def plus_dues(self, as_of=None):
        if self.status == MemberStatus.life:
            return 0
        if not as_of:
            as_of = current_year_end()
        type = self.member_type_at_renewal(as_of)
        if type in MembershipType.concessions():
            return PlusDues.concession.value
        if type == MembershipType.intermediate:
            return PlusDues.intermediate.value
        if type == MembershipType.senior:
            return PlusDues.senior.value
        return PlusDues.standard.value

    def upgrade_dues(self, as_of=None):
        if self.status == [MemberStatus.life]:
            return 0
        if not as_of:
            as_of = current_year_end()
        type = self.member_type_at_renewal(as_of)
        if type in MembershipType.concessions():
            return PlusUpgradeDues.concession.value
        if type == MembershipType.intermediate:
            return PlusUpgradeDues.intermediate.value
        if type == MembershipType.senior:
            return PlusUpgradeDues.senior.value
        return PlusUpgradeDues.standard.value

    def fmt_dues_including_update(self, as_of=None, default=True):
        return fmt_curr(self.dues_including_update(as_of, default), '')

    def dues_including_update(self, as_of=None, default=True):
        dues = self.dues()
        if self.last_payment('type') == PaymentType.pending.name:
            amount = self.last_payment('amount')
            dues = amount
        return dues

    def use_email(self):
        return self.comms == CommsType.email and self.comms_status != CommsStatus.email_fail

    def comms_ptx(self):
        return 'EMAIL' if self.email else ''

    def afcw_has_access(self):
        return (self.external_access or ExternalAccess.AFCW).value > ExternalAccess.none.value

    def third_pty_access(self):
        return (self.external_access or ExternalAccess.AFCW) == ExternalAccess.all

    def volatile_concession(self):
        return self.member_type in MembershipType.volatile_concessions()

    def start_year_for_card(self):
        extra = ''
        if self.is_founder():
            extra += ' founder'
        if self.is_life():
            extra += ' life member'
        if len(extra) > 0:
            extra = ' (' + extra[1:] + ')'
        return str(self.start_date.year) + extra

    def certificate_date(self):
        return encode_date_formal(self.start_date)

    def last_action(self):
        current = [a for a in self.actions if a.status == ActionStatus.open]
        if len(current) > 0:
            return sorted(current, key=lambda action: action.date, reverse=True)[0]
        else:
            return None

    def has_open_action(self, action_type):
        current = [a.action for a in self.actions if a.status == ActionStatus.open]
        return action_type in current

    def last_payment(self, item=None):
        dates = [p.date for p in self.payments]
        if len(dates) > 0:
            latest = [p for p in self.payments if p.date == max(dates)][0]
            if not item:
                return latest
            if item == 'date':
                return latest.date
            if item == 'type':
                if latest.type:
                    return latest.type.name
                else:
                    return None
            if item == 'amount':
                return latest.amount
            if item == 'method':
                if latest.method:
                    return latest.method.name
                else:
                    return None
            if item == 'comment':
                return latest.comment
        else:
            latest = None
        return latest

    def last_payment_date(self):
        return self.last_payment('date')

    def last_payment_amount(self):
        return self.last_payment('amount')

    def last_payment_type(self):
        return self.last_payment('type')

    def last_payment_comment(self):
        return self.last_payment('comment')

    def last_payment_method_(self):
        return self.last_payment('method')

    def previous_renewal_payment(self):
        prev = self.last_payment()
        if prev and prev.type != PaymentType.pending:
            return self.last_payment_method
        dates = [p.date for p in self.payments]
        if len(dates) <= 1:
            return None
        dates.sort(reverse=True)
        previous = [p for p in self.payments if p.date == dates[1]][0]
        return previous.method

    def check_credentials(self, user_name, password):
        if not match_string(user_name, str(self.number)):
            return False, 'Email does not match', 'warning'
        post_code = password.split('!')[0]
        if not match_string(post_code, self.address.post_code):
            return False, 'Post Code does not match', 'warning'
        return True, '', ''

    def concession_type(self):
        if self.member_type in MembershipType.concessions(all=True):
            long = [c for c in MembershipType.renewal_choices() if c[0] == self.member_type.value][0][1]
        else:
            long = ''
        return long

    def long_membership_type(self, member_type=None, upgrade=False, downgrade=False):
        if not member_type:
            member_type =  self.member_type
        long_type = [c for c in MembershipType.renewal_choices() if c[0] == member_type.value][0][1]
        if self.status == MemberStatus.life:
            status = '(Life)'
        elif upgrade or self.status == MemberStatus.plus and not downgrade:
            status = '(Plus)'
        else:
            status = ''
        return long_type + status

    def edit_notes(self):
        notes = []
        if self.comms == CommsType.email and self.email_bounced():
            notes += [
                'We have tried to use the email address that we have for you but emails have been returned ' \
                'undeliverable. Please check your email address.', ]
        if not self.birth_date:
            notes += [
                'Can you please supply your date of birth', ]
        return notes

    def renewal_notes_as_text(self):
        return '\n'.join(self.renewal_notes())

    def renewal_notes(self):
        age = self.age_at_renewal(default=True)
        new_member = self.is_recent_new()
        recent_resume = self.is_recent_resume()
        renewal_dues = '£' + str(self.dues())
        renewal_cost = "The renewal cost is {}. ".format(renewal_dues) if not (new_member or recent_resume) else ''
        upgrade_dues = '£' + str(
            self.upgrade_dues() if (new_member or recent_resume) else self.dues() + self.upgrade_dues())
        upgrade_para = ''
        if self.status != MemberStatus.plus:
            if not self.is_pending_upgrade():
                upgrade_para = "You may upgrade to Dons Trust Plus membership at a total cost of {}.".format(
                    upgrade_dues)
            else:
                upgrade_para = 'You have chosen to upgrade to Dons Trust Plus membership'
        downgrade_dues = '£' + str(0 if (new_member or recent_resume) else self.base_dues())
        if self.status == MemberStatus.plus:
            if not self.is_pending_downgrade():
                upgrade_para = "You may switch to Dons Trust Standard membership at a total renewal cost of {}.".format(
                    downgrade_dues)
            else:
                upgrade_para = 'You have chosen to switch to Dons Trust Standard membership'
        member_type = self.member_type_at_renewal()
        life_member = self.status == MemberStatus.life
        member_type_switch = member_type != self.member_type and not life_member
        junior = member_type == MembershipType.junior
        notes = []
        if life_member:
            notes = [
                "As you are a life member, there is no payment required. " \
                "We will send your new membership card in due course.", ]
        else:
            if member_type == MembershipType.intermediate:
                if member_type_switch:
                    notes = [
                        "As you have passed your 18th birthday, your membership will change to Young Adult (18-21)", \
                        "{}{}".format(renewal_cost, upgrade_para)]
                else:
                    notes = ["{}{}".format(renewal_cost, upgrade_para)]
            elif junior:
                notes = ["{}".format(renewal_cost), ]
            if member_type == MembershipType.senior:
                if member_type_switch:
                    notes = [
                        "As you have passed your 65th birthday, your membership will change to Senior (65+)", \
                        "{}{}".format(renewal_cost, upgrade_para)]
                else:
                    notes = ["{}{}".format(renewal_cost, upgrade_para), ]
            elif member_type in MembershipType.concessions():
                notes = [
                    "According to our records, you currently have a concessionary membership ({}).".format(
                        member_type.name),
                    "{}{}".format(renewal_cost, upgrade_para),
                    "**If your circumstances have changed please choose the appropriate membership type."]
            else:
                if member_type == MembershipType.standard:
                    if member_type_switch:
                        notes = [
                            "As you have passed your 21st birthday, you membership will change to Adult (22+)", \
                            "{}{}".format(renewal_cost, upgrade_para)]
                    else:
                        notes = ["{}{}".format(renewal_cost, upgrade_para), ]
        if self.last_payment_method == PaymentMethod.dd and not (new_member or recent_resume):
            up = "Unless you wish to upgrade to Dons Trust Plus, you need take no action about payment." \
                if not junior and self.status != MemberStatus.plus else ''
            notes = [
                        "According to our records you currently pay by direct debit. " + up,
                        "Provided the payment is taken successfully, your membership will be automatically updated.",
                    ] + notes
        if new_member and not life_member:
            notes = [
                        "As you joined relatively late during the membership year we will automatically extend " \
                        "your membership until July 2023.", ] + notes
        if recent_resume and not life_member:
            notes = [
                        "As you resumed a lapsed membership recently we will automatically extend " \
                        "your membership until July 2023.", ] + notes
        if self.comms == CommsType.post:
            notes = [
                        "You have currently opted to receive communications by post. If possible, please choose " \
                        "email, this will save money for the Trust and ease the admin burden.", ] + notes
        return notes

    def renewal_activated(self):
        last_payment = self.last_payment()
        if last_payment and last_payment.type == PaymentType.pending:
            last_action = self.last_action()
            if last_action and last_action.action == MemberAction.upgrade and last_action.status == ActionStatus.open:
                return 'Renewal was activated {} ({})'.format(fmt_date(last_action.date), last_action.comment)
            else:
                return 'Renewal was activated {}'.format(fmt_date(last_payment.date))
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


class Region(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True)
    postcode_prefix = Column(String(5), nullable=False)
    district = Column(String(45), nullable=False)
    region = Column(String(45), nullable=False)
    addresses = relationship("Address", back_populates="region")

    def __repr__(self):
        return '<Region {}: {}>'.format(self.district, self.region)
