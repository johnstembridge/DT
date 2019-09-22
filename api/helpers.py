from flask import jsonify, request
from werkzeug.http import HTTP_STATUS_CODES

from globals.enumerations import UserRole


def api_error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def wants_json_response():
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']


def user_ok_to_view_member(current_user, member_number):
    if UserRole.admin in [user_role.role for user_role in current_user.roles]:
        return True
    return current_user.member_id == member_number
