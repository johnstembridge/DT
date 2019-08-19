from flask import request
from flask_login import LoginManager
from front_end import login
from main import app
from globals import config
from back_end.interface import get_user, get_user_by_api_key
import base64

login_manager = LoginManager(app)
login_manager.login_view = 'user_login'
#login_manager.login_message = 'You must be a Dons Trust member to access this page'


@login_manager.user_loader
def load_user(id):
    return get_user(id=int(id))


@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = get_user_by_api_key(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = get_user_by_api_key(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    next_page = request.args.get('next')
    return login.user_login(next_page)


@app.route('/logout', methods=['GET', 'POST'])
def user_logout():
    return login.user_logout()


@app.route('/register', methods=['GET', 'POST'])
def user_register():
    return login.user_register()
