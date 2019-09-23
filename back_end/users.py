from globals.email import send_mail
from globals.enumerations import UserRole
from models.dt_db import User, Role
from back_end.interface import get_member, get_user, save_user
from back_end.data_utilities import is_valid_email


def register_user(member_number, email, user_name, password, role=UserRole.user):
    user_id = 0
    if is_valid_email(email):
        if user_name and password:
            member = get_member(member_number)
            if member:
                if not member.is_active():
                    ok, message, message_type = False, 'Sorry, you are not a current member', 'warning'
                elif member.email.lower() != email.lower():
                    ok, message, message_type = False, 'Please give your Dons Trust contact email address', 'warning'
                else:
                    user = get_user(user_name=user_name)
                    if user and user.member_id != member.id:
                        ok, message, message_type = False, 'User name already in use', 'warning'
                    else:
                        if not member.user:
                            user = User(user_name=user_name, member_id=member.id)
                        if not user.check_password(password):
                            ok, message, message_type = True, 'Password updated', 'success'
                        else:
                            ok, message, message_type = True, 'You are now a registered user', 'success'
                        user.set_password(password)
                        if not user.roles:
                            user.roles = [Role(role=role)]
                        save_user(user)
                        user_id = user.id
            else:
                ok, message, message_type = False, 'Cannot find your membership', 'warning'
        else:
            ok, message, message_type = False, 'Missing user name/password', 'warning'
    else:
        ok, message, message_type = False, 'Invalid email address', 'warning'
    return ok, user_id, message, message_type


def change_user_password(user_id, new_password):
    user = get_user(user_id)
    if user:
        user.set_password(new_password)
        save_user(user)
        ok, message, message_type = True, 'Password updated', 'success'
    else:
        ok, message, message_type = False, 'User not not found', 'warning'
    return ok, message, message_type
