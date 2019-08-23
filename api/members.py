from flask import jsonify
from flask_login import login_required, current_user

from globals.decorators import role_required
from main import app
from back_end.interface import get_new_member, get_member


@app.route('/api/members/<int:member_number>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def api_edit_member(member_number):
    return api_get_member(member_number)


def api_get_member(member_number):
    new_member = member_number == 0
    if new_member:
        member = get_new_member()
    else:
        member = get_member(member_number)
    return jsonify(member.to_dict())



