import jwt
##import requests
from datetime import datetime, timedelta, timezone
from flask import abort


class requests:

    @staticmethod
    def post(endpoint, json, headers):
        return None


class Secutix:

    service_url = "https://afcw.pp-ws.secutix.com/tnco/backend-apis/"

    @staticmethod
    def forge_jwt():
        iat = datetime.now(tz=timezone.utc)
        payload = {
            "sub": "AFCW",
            "aud": "AFCW_DONST",
            "iss": "Dons Trust",
            "iat": int(datetime.timestamp(iat)),
            "exp": int(datetime.timestamp(iat + timedelta(seconds=30)))
        }
        secret = "h2QGmAyu7kDwVE"
        encoded_jwt = jwt.encode(payload, secret, algorithm="HS256")
        header = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + encoded_jwt.decode('utf-8')
        }
        return header

    def get_details(self, fan_id):
        endpoint = self.service_url + "contactInformationPublicService/v2_21/getContactData"
        header = self.forge_jwt()
        response = requests.post(endpoint,
                                 json={"contactNumber": "{}".format(fan_id),
                                       "details": [
                                           "GENERAL",
                                           "QUALITIES",
                                           "AUTHORIZATIONS",
                                           "CRITERIA",
                                           "INDICATORS",
                                           "ADVANTAGES",
                                           "ADDRESSES",
                                           "COM_MEANS",
                                           "FINANCIAL",
                                           "CONNECTIONS",
                                           "INDIVIDUAL_PHOTO",
                                           "INVALIDATED_QUALITIES"
                                       ]
                                       },
                                 headers=header)
        if response.ok:
            return response
        else:
            return abort(response.status_code, "{} for FanId {} returned error {}".format(endpoint, fan_id, response.status_code))
