from globals.email import send_mail
from globals.enumerations import UserRole
from models.dt_db import User, Role
from back_end.interface import get_member, get_user, save_user
from back_end.data_utilities import is_valid_email


def register_user(member_number, email, user_name, password, role=UserRole.user):
    ok = False
    message = None
    message_type = None
    user_id = 0
    if is_valid_email(email):
        if user_name and password:
            member = get_member(member_number)
            if member:
                if not member.is_active():
                    message, message_type = 'Sorry, you are not a current member', 'warning'
                elif member.email.lower() != email.lower():
                    message, message_type = 'Please give your Dons Trust contact email address', 'warning'
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
                        if not user.roles:
                            user.roles = [Role(role=UserRole.user)]
                        save_user(user)
                        user_id = user.id
            else:
                message, message_type = 'Cannot find your membership', 'warning'
        else:
            message, message_type = 'Missing user name/password', 'warning'
    else:
        message, message_type = 'Invalid email address', 'warning'
    return ok, user_id, message, message_type
