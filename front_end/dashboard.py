from flask_wtf import FlaskForm
from wtforms import StringField
from globals.enumerations import MemberStatus, MembershipType
from back_end.interface import get_members_for_query


class Dashboard(FlaskForm):
    total = StringField(label='Total')
    adults = StringField(label='Standard adults')
    life_adults = StringField(label='Life adults')
    life_juniors = StringField(label='Life juniors')
    concessions = StringField(label='Concessions')
    seniors = StringField(label='Seniors')
    students = StringField(label='Students')
    job_seekers = StringField(label='Job Seekers')
    incapacity = StringField(label='Incapacity')
    others = StringField(label='Others')
    honorary = StringField(label='Honorary')

    young_adults = StringField(label='Young Adults')
    juniors = StringField(label='Juniors')

    actions = StringField(label='Outstanding actions')

    def populate(self):
        query_clauses = [('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),]
        query = get_members_for_query(query_clauses)
        totals = {
            MembershipType.standard: 0,
            MembershipType.senior: 0,
            MembershipType.student: 0,
            MembershipType.job_seeker: 0,
            MembershipType.incapacity: 0,
            MembershipType.honorary: 0,
            MembershipType.other_concession: 0,
            MembershipType.intermediate: 0,
            MembershipType.junior: 0,
            100: 0,
            101: 0
        }

        def add_member(member, totals):
            totals[member.member_type] += 1
            if member.status == MemberStatus.life:
                if member.member_type == MembershipType.junior:
                    totals[101] += 1
                else:
                    totals[100] += 1
            return

        for member in query.all():
            add_member(member, totals)

        self.adults.data = totals[MembershipType.standard]
        self.life_adults.data = totals[100]
        self.seniors.data = totals[MembershipType.senior]
        self.students.data = totals[MembershipType.student]
        self.job_seekers.data = totals[MembershipType.job_seeker]
        self.incapacity.data = totals[ MembershipType.incapacity]
        self.honorary.data = totals[MembershipType.honorary]
        self.others.data = totals[MembershipType.other_concession]
        self.young_adults.data = totals[MembershipType.intermediate]
        self.juniors.data = totals[MembershipType.junior]
        self.life_juniors.data = totals[101]

        self.concessions.data = self.seniors.data + self.students.data + self.job_seekers.data + self.incapacity.data + self.honorary.data + self.others.data
        self.total.data = self.adults.data + self.concessions.data + self.young_adults.data + self.juniors.data

        self.actions.data = 0
