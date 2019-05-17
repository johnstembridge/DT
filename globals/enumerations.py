from enum import Enum


class FormEnum(Enum):
    @classmethod
    def choices(cls, all=False):
        return [(choice, choice.name.replace('_', ' ')) for choice in cls]

    @classmethod
    def coerce(cls, item):
        if not item:
            return None
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


class MemberStatus(FormEnum):
    life = 1
    founder = 2
    current = 3
    lapsed = 4
    cancelled = 5
    deceased = 6

    @staticmethod
    def all_active():
        return [MemberStatus.life, MemberStatus.founder, MemberStatus.current]


class MembershipType(FormEnum):
    standard = 1
    intermediate = 2
    junior = 3
    senior = 4
    student = 5
    job_seeker = 6
    other_concession = 7
    honorary = 8

    @staticmethod
    def all_concessions():
        return [MembershipType.job_seeker, MembershipType.senior, MembershipType.student, MembershipType.other_concession]


class MemberAction(FormEnum):
    none = 0
    certificate = 1
    card = 2


class ActionStatus(FormEnum):
    none = 0
    open = 1
    closed = 2


class PaymentType(FormEnum):
    dues = 1
    donation = 2


class PaymentMethod(FormEnum):
    unknown = 0
    cc = 1
    dd = 2
    chq = 3
    cash = 4
    xfer = 5
    so = 6


class CommsType(FormEnum):
    email = 1
    post = 2


class ExternalAccess(FormEnum):
    none = 0
    AFCW = 1
    all = 2


class UserRole(FormEnum):
    user = 1
    admin = 2


class Sex(FormEnum):
    unknown = 0
    male = 1
    female = 2


class Dues(FormEnum):
    junior_new = 10
    junior = 5
    intermediate = 10
    concession = 10
    standard = 25


