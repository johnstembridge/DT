from functools import wraps
from threading import Thread

from flask import abort
from flask_login import current_user


def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user:
                current_user_roles = [user_role.role.name for user_role in current_user.roles]
                for role in roles:
                    if role in current_user_roles:
                        return f(*args, **kwargs)
                abort(401, description='Sorry, you do not have access')
        return wrapped
    return wrapper


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper
