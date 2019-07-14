from enum import Enum


class FormEnum(Enum):
    @classmethod
    def choices(cls, blank=False, extra=None):
        result = [(choice.value, choice.name.replace('_', ' ')) for choice in cls]
        if extra:
            result = extra + result
        if blank:
            result = [(0, '')] + result
        return result

    @classmethod
    def coerce(cls, item):
        if not item:
            return None
        # return cls(int(item)) if not isinstance(item, cls) else item
        if isinstance(item, cls):
            return item.value
        else:
            return int(item)

    def __str__(self):
        return str(self.value)


class MemberStatus(FormEnum):
    life = 1
    founder = 2
    current = 3
    lapsed = 4
    suspended = 5
    cancelled = 6
    deceased = 7

    @staticmethod
    def active():
        return [MemberStatus.founder, MemberStatus.current]

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
    incapacity = 7
    other_concession = 8
    honorary = 9

    @staticmethod
    def all_concessions():
        return [MembershipType.job_seeker, MembershipType.senior, MembershipType.student, MembershipType.incapacity,
                MembershipType.other_concession]


class MemberAction(FormEnum):
    certificate = 1
    card = 2
    upgrade = 3  # junior to intermediate, intermediate to standard, standard to life, etc: see comment
    gift = 4


class ActionStatus(FormEnum):
    open = 1
    closed = 2


class PaymentType(FormEnum):
    dues = 1
    donation = 2
    refund = 3


class PaymentMethod(FormEnum):
    na = 0
    cc = 1
    dd = 2
    chq = 3
    cash = 4
    xfer = 5
    so = 6


class CommsType(FormEnum):
    email = 1
    post = 2


class CommsStatus(FormEnum):
    all_ok = 1
    email_fail = 2
    post_fail = 3
    all_fail = 4


class ExternalAccess(FormEnum):
    none = 0
    AFCW = 1
    all = 2


class UserRole(FormEnum):
    user = 1
    admin = 2


class Sex(FormEnum):
    male = 1
    female = 2
    unknown = 3


class Dues(FormEnum):
    junior_new = 10
    junior = 5
    intermediate = 10
    concession = 10
    standard = 25
    senior = 10


class Months(FormEnum):
    January = 1
    February = 2
    March = 3
    April = 4
    May = 5
    June = 6
    July = 7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12


class Title(FormEnum):
    Mr = 1
    Mrs = 2
    Ms = 3
    Miss = 4
    Dr = 5
    Prof = 6
    Revd = 7
    Sir = 8
    Lord = 9
    Lady = 10


class JuniorGift(FormEnum):
    none = 0
    BaseballCap = 1
    MiniFootball = 2
