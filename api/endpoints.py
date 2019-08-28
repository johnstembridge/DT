from flask_login import login_required
from flask import request, jsonify

from globals.decorators import role_required
from main import app, csrf_protect
from api.members import MaintainMembers
from back_end.users import register_user
from back_end.data_utilities import list_from_dict


@app.route('/api/members/<int:member_number>', methods=['GET'])
@login_required
@role_required('admin')
def api_get_member(member_number):
    return MaintainMembers.api_get_member(member_number)


@app.route('/api/members/<int:member_number>', methods=['PUT', 'POST'])
@login_required
@role_required('admin')
@csrf_protect.exempt
def api_update_member(member_number):
    return MaintainMembers.api_update_member(member_number, request.get_json())


@app.route('/api/register', methods=['POST'])
@csrf_protect.exempt
def api_register():
    params = list_from_dict(request.get_json(), ['email','user_name', 'password'])
    ok, message, message_type = register_user(*params)
    return_code = 201 if ok else 401
    return jsonify({'status': message_type, 'message': message}), return_code
