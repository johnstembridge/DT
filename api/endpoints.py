from flask_login import login_required
from flask import request, jsonify

from globals.decorators import role_required
from main import app
from api.members import MaintainMembers
from back_end.users import register_user


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


@app.route('/api/register', methods=['POST'])
def api_register():
    params = request.get_json()
    ok, message, message_type = register_user(params['email'], params['user_name'], params['password'])
    return_code = 201 if ok else 401
    return jsonify({'status': message_type, 'message': message}), return_code
