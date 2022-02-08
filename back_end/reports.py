from collections import OrderedDict

from globals.enumerations import MemberStatus
from back_end.interface import get_members_for_query, get_all_districts, get_all_regions


class Reports:

    @staticmethod
    def regions():
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Country', 'code', 'UK', '=', None)
        ]
        return Reports.show_regions_report(query_clauses)

    @staticmethod
    def districts():
        query_clauses = [
            ('Member', 'status', [s.value for s in MemberStatus.all_active()], 'in', None),
            ('Country', 'code', 'UK', '=', None)
        ]
        return Reports.show_districts_report(query_clauses)

    @staticmethod
    def show_regions_report(query_clauses):
        members = get_members_for_query(query_clauses)
        all_regions = get_all_regions()
        csv = []
        region_count = {r: 0 for r in sorted(set(all_regions.values()))}
        for member in members:
            if member.address.region_id:
                region_count[member.address.region.region] += 1
        #region_count = OrderedDict(sorted(region_count.items(), key=lambda x: x[1], reverse = True))
        head = ['region', 'count']
        csv.append(head)
        for region in region_count:
            csv.append([region, region_count[region]])
        return csv

    @staticmethod
    def show_districts_report(query_clauses):
        members = get_members_for_query(query_clauses)
        all_districts = get_all_districts()
        csv = []
        count = {r: 0 for r in sorted(set([d[1] for d in all_districts]))}
        regions = dict(set([(d[1], d[2]) for d in all_districts]))
        for member in members:
            if member.address.region_id:
                count[member.address.region.district] += 1
        #count = OrderedDict(sorted(region_count.items(), key=lambda x: x[1], reverse = True))
        head = ['region', 'district', 'count']
        csv.append(head)
        for district in count:
            csv.append([regions[district], district, count[district]])
        return csv
