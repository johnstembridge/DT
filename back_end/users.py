from globals.email import send_mail
from models.dt_db import User
from back_end.interface import get_member_by_email, get_user, save_user


def register_user(email, user_name, password):
    member = get_member_by_email(email)
    ok = False
    message = None
    message_type = None
    if member:
        if not member.is_active():
            message, message_type = 'Sorry, you are not a current member', 'danger'
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
    return ok, message, message_type
