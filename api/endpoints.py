from flask_login import login_required
from flask import request

from globals.decorators import role_required
from main import app
from api.members import MaintainMembers


@app.route('/api/members/<int:member_number>', methods=['GET'])
@login_required
@role_required('admin')
def api_get_member(member_number):
    return MaintainMembers.api_get_member(member_number)


@app.route('/api/members/<int:member_number>', methods=['POST'])
@login_required
@role_required('admin')
def api_update_member(member_number):
    return MaintainMembers.api_update_member(member_number, request.get_json())
