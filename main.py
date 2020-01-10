from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
#from flask_httpauth import HTTPBasicAuth

from globals.app_setup import init_app

app = Flask(__name__)
csrf_protect = CSRFProtect(app)
init_app(app)
@app.context_processor
def inject_UserRole_and_current_user():
    return dict(current_user=current_user, UserRole=UserRole)  # available in all templates to restrict access
#auth = HTTPBasicAuth()
db = SQLAlchemy(app)

from views.home import *
from globals.access import *
from views.members import *
from views.actions import *
#from views.reports import *
from views.extracts import *
from views.help import *
from views.testing import *
from views.others import page_not_found, internal_error, unauthorised
from api.endpoints import *
from api.helpers import wants_json_response, api_error_response


@app.errorhandler(400)
def bad_request(e):
    app.logger.error(e)
    if wants_json_response():
        return api_error_response(400, e.description)
    return unauthorised(e)


@app.errorhandler(401)
def not_found(e):
    app.logger.error(e)
    if wants_json_response():
        return api_error_response(401, e.description)
    return unauthorised(e)


@app.errorhandler(404)
def not_found(e):
    app.logger.error(e)
    if wants_json_response():
        return api_error_response(404)
    return page_not_found(e)


@app.errorhandler(500)
def catch_internal_error(e):
    app.logger.error(e)
    if wants_json_response():
        return api_error_response(500)
    return internal_error(e)


if __name__ == '__main__':
    app.run(debug=False)
