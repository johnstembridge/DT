from flask_login import login_required, current_user
from flask import request, jsonify, url_for

from globals.decorators import role_required
from globals.enumerations import UserRole
from main import app, csrf_protect
from api.members import MaintainMembers
from back_end.users import register_user, activate_user, get_user, change_user_password
from back_end.data_utilities import list_from_dict
from api.helpers import api_error_response, user_ok_to_view_member, id_is_current_user


@app.route('/api/members/<int:member_number>', methods=['GET'])
@login_required
@role_required('user', 'admin')
def api_get_member(member_number):
    if user_ok_to_view_member(current_user, member_number):
        return MaintainMembers.api_get_member(member_number)
    else:
        return api_error_response(401, 'You can only view your own details')


@app.route('/api/members/<int:member_number>', methods=['PUT'])
@login_required
@role_required('user', 'admin')
@csrf_protect.exempt
def api_update_member(member_number):
    if user_ok_to_view_member(current_user, member_number):
        return MaintainMembers.api_update_member(member_number, request.get_json())
    else:
        return api_error_response(401, 'You can only update your own details')


@app.route('/api/users', methods=['POST'])
@csrf_protect.exempt
def api_register_user():
    #Register a new user
    params = list_from_dict(request.get_json() or {}, ['member_number', 'user_name', 'password'])
    ok, id, message, message_type = register_user(*params + [None, UserRole.user, True, url_for('api_activate_user')])
    return_code = 201 if ok else 401
    response = jsonify({'status': message_type, 'message': message})
    response.status_code = return_code
    if ok:
        response.headers['Location'] = url_for('api_get_user', id=id)
    return response


@app.route('/api/users', methods=['GET'])
@csrf_protect.exempt
def api_activate_user():
    #activate a new user's access
    key = request.args.get('key', '')
    ok, id, message, message_type = activate_user(key)
    return_code = 201 if ok else 401
    response = jsonify({'status': message_type, 'message': message})
    response.status_code = return_code
    if ok:
        response.headers['Location'] = url_for('api_get_user', id=id)
    return response


@app.route('/api/users/<int:id>', methods=['PUT'])
@login_required
@role_required('user', 'admin')
@csrf_protect.exempt
def api_change_user_password(id):
    if id_is_current_user(current_user, id):
        new_password = list_from_dict(request.get_json() or {}, ['new_password'])[0]
        ok, message, message_type = change_user_password(id, new_password)
    else:
        ok, message, message_type = False, 'You can only update your own details', 'warning'
    return_code = 200 if ok else 401
    response = jsonify({'status': message_type, 'message': message})
    response.status_code = return_code
    if ok:
        response.headers['Location'] = url_for('api_get_user', id=id)
    return response


@app.route('/api/users/<int:id>', methods=['GET'])
@login_required
@role_required('user', 'admin')
def api_get_user(id):
    if id_is_current_user(current_user, id):
        return jsonify(get_user(id).to_dict())
    else:
        return api_error_response(401, 'You can only view your own details')
