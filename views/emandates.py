from flask import request

from main import app
from front_end.emandates import Emandates


@app.route('/emandates/confirm', methods=['GET'])
def emandates_confirm():
    app.logger.info(request.get_data())
    app.logger.info(request)
    app.logger.info(request.args)
    app.logger.info("confirmed")
    return Emandates.emandates_confirm(request.args)


@app.route('/emandates/cancel', methods=['GET'])
def emandates_cancel():
    return Emandates.emandates_deny(request.args)
