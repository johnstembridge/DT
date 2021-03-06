from flask import jsonify, abort
from back_end.interface import get_new_member, get_member
from api.helpers import wants_json_response


class MaintainMembers:

    @staticmethod
    def api_get_member(member_number):
        new_member = member_number == 0
        if new_member:
            member = get_new_member()
        else:
            member = get_member(member_number)
        if member:
            if wants_json_response():
                return jsonify(member.to_dict())
            else:
                return jsonify(member.to_dict()) # html??
        else:
            abort(404)

    @staticmethod
    def api_update_member(member_number, payload):
        new_member = member_number == 0
        if new_member:
            member = get_new_member()
        else:
            member = get_member(member_number)
        if member:
            member.from_dict(payload)
            if wants_json_response():
                return jsonify(member.to_dict())
            else:
                return jsonify(member.to_dict()) # html??
        else:
            abort(404)
