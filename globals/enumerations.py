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
        if isinstance(item, str) and '(' == item[0]:
            item = eval(item)
        if isinstance(item, cls):
            return item.value
        elif isinstance(item, int):
            return item
        elif isinstance(item, tuple):
            return item[0]
        else:
            return int(item)

    @classmethod
    def from_name(cls, name):
        return [c for c in cls if c.name in name][0]

    @classmethod
    def from_value(cls, value):
        item = [c for c in cls if c.value == value]
        return item[0] if len(item) > 0 else None

    def to_dict(self):
        return self.name

    def __str__(self):
        return str(self.value)


class UserRole(FormEnum):
    none = 0
    member = 1
    afcw = 2
    extract = 3
    jd_admin = 4
    dt_board = 5
    support = 6
    admin = 7
    super = 8

    @staticmethod
    def admin_access():
        return [UserRole.member, UserRole.jd_admin, UserRole.admin, UserRole.super]

    @staticmethod
    def write_access():
        return [UserRole.member, UserRole.jd_admin, UserRole.admin, UserRole.super]

    @staticmethod
    def lapsed_access(type):
        if type == 'all':
            return [UserRole.super, ]
        elif type == 'any':
            return [UserRole.jd_admin, UserRole.dt_board, UserRole.support, UserRole.admin, UserRole.super]
        elif type == '1yr+':
            return [UserRole.support, UserRole.admin, UserRole.super]

    @staticmethod
    def has_lapsed_access(type):
        if type == 'all':
            return [UserRole.super, ]
        elif type == 'any':
            return [UserRole.jd_admin, UserRole.dt_board, UserRole.support, UserRole.admin, UserRole.super]
        elif type == '1yr+':
            return [UserRole.support, UserRole.admin, UserRole.super]


class MemberStatus(FormEnum):
    life = 1
    founder = 2
    current = 3
    lapsed = 4
    suspended = 5
    cancelled = 6
    deceased = 7
    plus = 8
    reserved = 98

    @staticmethod
    def renewal_choices():
        result = [
            (1, 'Life Membership'),
            (2, 'Founder'),
            (3, 'Standard'),
            (8, 'Dons Trust Plus')
        ]
        return result

    @staticmethod
    def all_active(life=True):
        if life:
            return [MemberStatus.life, MemberStatus.founder, MemberStatus.current, MemberStatus.plus]
        else:
            return [MemberStatus.founder, MemberStatus.current, MemberStatus.plus]

    @staticmethod
    def all_including_lapsed():
        return [MemberStatus.life, MemberStatus.founder, MemberStatus.current, MemberStatus.plus, MemberStatus.lapsed]


class MembershipType(FormEnum):
    standard = 1  # adult
    intermediate = 2
    junior = 3
    senior = 4
    student = 5
    job_seeker = 6
    incapacity = 7
    other_concession = 8
    honorary = 9

    @staticmethod
    def renewal_choices():
        result = [(choice.value, choice.name.replace('_', ' ').title()) for choice in MembershipType]
        result[0] = (result[0][0], 'Adult')
        result[1] = (result[1][0], 'Young Adult (age 18-21)')
        result[2] = (result[2][0], result[2][1] + ' (age 0-17)')
        result[3] = (result[3][0], result[3][1] + ' (age 65+)')
        del result[-1]
        return result

    @staticmethod
    def concessions(all=False):
        if all:
            extra = [MembershipType.senior, MembershipType.intermediate]
        else:
            extra = []
        return [MembershipType.job_seeker, MembershipType.student, MembershipType.incapacity,
                MembershipType.other_concession] + extra

    @staticmethod
    def volatile_concessions():
        return [MembershipType.job_seeker, MembershipType.student, MembershipType.incapacity,
                MembershipType.other_concession]

    @staticmethod
    def adult():
        return [m for m in MembershipType if m != MembershipType.junior]


class MemberAction(FormEnum):
    certificate = 1
    card = 2
    upgrade = 3  # junior to intermediate, intermediate to standard, standard to life, etc: see comment
    replacement = 4  # certificate
    send = 5
    resend = 6  # card
    gift = 7
    other = 8
    check_payment = 9 # check that correct payment made after late change of membership

    @staticmethod
    def send_certificates():
        return [MemberAction.certificate, MemberAction.replacement]

    @staticmethod
    def send_cards():
        return [MemberAction.card, MemberAction.resend]

    @staticmethod
    def send_other():
        return [MemberAction.gift, MemberAction.other]


class Dues(FormEnum):
    junior_new = 15
    junior = 5
    intermediate = 10
    concession = 10
    standard = 25
    senior = 10
    plus = 45


class PlusDues(FormEnum):
    intermediate = 30
    concession = 30
    standard = 45
    senior = 30


class PlusUpgradeDues(FormEnum):
    intermediate = 20
    concession = 20
    standard = 20
    senior = 20


class AgeBand(FormEnum):
    junior = (0, 17)  # was (0, 15)
    intermediate = (18, 21)  # was (16, 20)
    adult = (22, 64)  # was (21, 59)
    senior = (65, 200)  # was (60, 200)

    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper


class OldAgeBand(FormEnum):
    junior = (0, 15)
    intermediate = (16, 20)
    adult = (21, 59)
    senior = (60, 200)

    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper


class RenewalPayment(Enum):
    Adult = "Adult £25.00 GBP"
    Concession = "Concession £10.00 GBP"
    Junior_Dons_new = "Junior Dons (0-17) new £15.00 GBP"
    Junior_Dons_renewal = "Junior Dons renewal £5.00 GBP"
    Dons_Trust_Plus_Adult = "Dons Trust Plus (Adult) £45.00 GBP"
    Dons_Trust_Plus_Concession = "Dons Trust Plus (Concession) £30.00 GBP"
    Dons_Trust_Plus_Adult_upgrade = "Dons Trust Plus Adult upgrade £20.00 GBP"
    Dons_Trust_Plus_Concession_upgrade = "Dons Trust Plus Concession upgrade £20.00 GBP"

    @classmethod
    def choices(cls):
        result = [(choice.name.replace('_', ' '), choice.value) for choice in cls]
        return result


class EmandatePaymentPlan(Enum):
    # Adult = "93346a7b-09b2-44bf-b50b-8b24d6f7d259"
    Adult = "e6fba0e8-1ac1-435f-a8af-259f6e0dbb67"
    Concession = "3c60ea5-655c-4d83-81e9-d871d643817d"
    Junior_Dons_new = "f917f19b-ed94-4822-8b3e-8e80a026e0f2"
    Junior_Dons_renewal = "62f200d4-2e3e-460d-9aa9-36ce052ea126"
    Dons_Trust_Plus_Adult = "b25bc6a8-2c4d-45f3-8be7-f67d773a202e"
    Dons_Trust_Plus_Concession = "573fbdde-e8d8-4097-b2c8-960a520a1a96"

    @classmethod
    def choices(cls):
        result = [(choice.name.replace('_', ' '), choice.value) for choice in cls]
        return result


class ActionStatus(FormEnum):
    open = 1
    closed = 2


class PaymentType(FormEnum):
    dues = 1
    donation = 2
    refund = 3
    pending = 4
    unpaid = 5


class PaymentMethod(FormEnum):
    cc = 1
    dd = 2
    chq = 3
    cash = 4
    xfer = 5
    so = 6
    dd_cancelled = 7
    dd_pending = 8

    @staticmethod
    def renewal_choices():
        result = [
            (1, 'Credit/Debit card'),
            (2, 'Direct Debit'),
            (3, 'Cheque')
        ]
        return result


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


class Sex(FormEnum):
    male = 1
    female = 2


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
    Mx = 11


class JuniorGift(FormEnum):
    LunchBox = 1
    BuildingBricks = 2
    BaseballCap = 3
    MiniFootball = 4


class YesNo(FormEnum):
    no = 0
    yes = 1
