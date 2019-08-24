from flask import jsonify
from back_end.interface import get_new_member, get_member
from api.helpers import wants_json_response


def api_get_member(member_number):
    new_member = member_number == 0
    if new_member:
        member = get_new_member()
    else:
        member = get_member(member_number)
    if wants_json_response():
        return jsonify(member.to_dict())
    else:
        return  # html??



