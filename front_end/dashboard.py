from flask_wtf import FlaskForm
from wtforms import StringField
from globals.enumerations import MemberStatus, MembershipType, PaymentMethod, MemberAction
from back_end.interface import get_members_for_query


class Dashboard(FlaskForm):
    total = StringField(label='Total')
    adults = StringField(label='Standard adults')
    life_adults = StringField(label='Life adults')
    life_juniors = StringField(label='Life juniors')
    plus_standard = StringField(label='DT plus (standard)')
    plus_concession = StringField(label='DT plus (concession)')
    plus_young_adult = StringField(label='DT plus (concession)')
    concessions = StringField(label='Concessions')
    seniors = StringField(label='Seniors')
    students = StringField(label='Students')
    job_seekers = StringField(label='Job Seekers')
    incapacity = StringField(label='Incapacity')
    others = StringField(label='Others')
    honorary = StringField(label='Honorary')
    young_adults = StringField(label='Young Adults')
    juniors = StringField(label='Juniors')

    cash = StringField(label='Cash')
    chq = StringField(label='Cheque')
    cc = StringField(label='Credit Card')
    dd = StringField(label='Direct Debit')
    other_payment = StringField(label='Other')

    cert = StringField(label='New membership packs')
    card = StringField(label='Renewal cards')
    other_action = StringField(label='Other')

    def populate(self):
        query_clauses = [('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None), ]
        query = get_members_for_query(query_clauses)
        member_totals = {
            MembershipType.standard: 0,
            MembershipType.senior: 0,
            MembershipType.student: 0,
            MembershipType.job_seeker: 0,
            MembershipType.incapacity: 0,
            MembershipType.honorary: 0,
            MembershipType.other_concession: 0,
            MembershipType.intermediate: 0,
            MembershipType.junior: 0,
            100: 0, # Life adult
            101: 0, # Life Junior
            102: 0, # DT plus standard
            103: 0, # DT plus concession
            104: 0  # DT plus young adult
        }
        payment_totals = {
            PaymentMethod.cash: 0,
            PaymentMethod.chq: 0,
            PaymentMethod.cc: 0,
            PaymentMethod.dd: 0,
            100: 0  # other
        }
        action_totals = {
            MemberAction.certificate: 0,
            MemberAction.card: 0,
            MemberAction.other: 0
        }

        def add_member(member, member_totals):
            member_type = member.member_type
            member_totals[member_type] += 1
            if member.status == MemberStatus.life:
                if member_type == MembershipType.junior:
                    member_totals[101] += 1
                else:
                    member_totals[100] += 1
            if member.status == MemberStatus.plus:
                if member_type in (MembershipType.concessions() + [MembershipType.senior]):
                    member_totals[103] += 1
                elif member_type == MembershipType.intermediate:
                    member_totals[104] += 1
                else:
                    member_totals[102] += 1
            return

        def add_payment(member, payment_totals):
            if member.last_payment_method:
                if member.last_payment_method.value > PaymentMethod.cash.value:
                    payment_totals[100] += 1  # other
                else:
                    payment_totals[member.last_payment_method] += 1
            else:
                payment_totals[PaymentMethod.chq] += 1
            return

        def add_action(member, action_totals):
            if member.has_open_action(MemberAction.certificate):
                action_totals[MemberAction.certificate] += 1
            if member.has_open_action(MemberAction.card):
                action_totals[MemberAction.card] += 1
            if member.has_open_action(MemberAction.other):
                action_totals[MemberAction.other] += 1
            return

        for member in query.all():
            add_member(member, member_totals)
            add_payment(member, payment_totals)
            add_action(member, action_totals)

        self.adults.data = member_totals[MembershipType.standard]
        self.life_adults.data = member_totals[100]
        self.plus_standard.data = member_totals[102]
        self.plus_concession.data = member_totals[103]
        self.plus_young_adult.data = member_totals[104]
        self.seniors.data = member_totals[MembershipType.senior]
        self.students.data = member_totals[MembershipType.student]
        self.job_seekers.data = member_totals[MembershipType.job_seeker]
        self.incapacity.data = member_totals[MembershipType.incapacity]
        self.honorary.data = member_totals[MembershipType.honorary]
        self.others.data = member_totals[MembershipType.other_concession]
        self.young_adults.data = member_totals[MembershipType.intermediate]
        self.juniors.data = member_totals[MembershipType.junior]
        self.life_juniors.data = member_totals[101]

        self.concessions.data = self.seniors.data + self.students.data + self.job_seekers.data + self.incapacity.data + self.honorary.data + self.others.data
        self.total.data = self.adults.data + self.concessions.data + self.young_adults.data + self.juniors.data

        self.cash.data = payment_totals[PaymentMethod.cash]
        self.chq.data = payment_totals[PaymentMethod.chq]
        self.cc.data = payment_totals[PaymentMethod.cc]
        self.dd.data = payment_totals[PaymentMethod.dd]
        self.other_payment.data = payment_totals[100]

        self.cert.data = action_totals[MemberAction.certificate]
        self.card.data = action_totals[MemberAction.card]
        self.other_action.data = action_totals[MemberAction.other]
