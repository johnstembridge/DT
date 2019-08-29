from globals.email import send_mail
from models.dt_db import User
from back_end.interface import get_member_by_email, get_user, save_user
from back_end.data_utilities import is_valid_email


def register_user(email, user_name, password):
    ok = False
    message = None
    message_type = None
    if is_valid_email(email):
        if user_name and password:
            member = get_member_by_email(email)
            if member:
                if not member.is_active():
                    message, message_type = 'Sorry, you are not a current member', 'warning'
                else:
                    user = get_user(user_name=user_name)
                    if user and user.member_id != member.id:
                        message, message_type = 'User name already in use', 'warning'
                    else:
                        if not member.user:
                            user = User(user_name=user_name, member_id=member.id)
                        if not user.check_password(password):
                            ok, message, message_type = True, 'Password updated', 'success'
                        else:
                            ok, message, message_type = True, 'You are now a registered user', 'success'
                        user.set_password(password)
                        save_user(user)
            else:
                message, message_type = 'Cannot find your membership - please give your Dons Trust contact email address', 'warning'
        else:
            message, message_type = 'Missing user name/password', 'warning'
    else:
        message, message_type = 'Invalid email address', 'warning'
    return ok, message, message_type
