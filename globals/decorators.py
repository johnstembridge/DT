from functools import wraps
from threading import Thread

from flask import abort
from flask_login import current_user
from globals.enumerations import UserRole


def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user:
                required_role = UserRole.from_value(min([UserRole.from_name(role).value for role in roles]))
                if current_user.has_access(required_role):
                    return f(*args, **kwargs)
                abort(401, description='Sorry, you do not have access')
        return wrapped
    return wrapper


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper
