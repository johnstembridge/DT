from flask import make_response
from back_end.interface import get_member, save_member_details


class Emandates:

    @staticmethod
    def emandates_confirm(params):
        reply = 'Mandate confirmed: ' + ', '.join({k + ': ' + v for (k,v) in params.items()})
        response = make_response(reply)
        response.status_code = 200
        return response

    @staticmethod
    def emandates_deny(params):
        reply = 'Mandate denied: ' + ', '.join({k + ': ' + v for (k, v) in params.items()})
        response = make_response(reply)
        response.status_code = 200
        return response

