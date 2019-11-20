from flask import render_template, current_app
from globals.email import send_mail
from globals.enumerations import UserRole
from globals.config import full_url_for
from models.dt_db import User, Role
from back_end.interface import get_member, get_user, save_user


def register_user(member_number, user_name, password, email=None, role=UserRole.member, two_phase=False, activate_url=None):
    user_id = 0
    if user_name and password:
        member = get_member(member_number)
        if member:
            if not member.is_active():
                ok, message, message_type = False, 'Sorry, you are not a current member', 'error'
            else:
                if member.email != email:
                    ok, message, message_type = False, 'Email does not match', 'warning'
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
                            if two_phase:
                                token, expires = user.get_token(current_app)
                                send_mail(
                                    to=member.email,
                                    sender='admin@thedonstrust.org',
                                    cc=[],
                                    subject='Dons Trust Members - registration',
                                    message=render_template('activate.txt',
                                                              full_url_for=full_url_for,
                                                              member=member,
                                                              token=token,
                                                              expires=expires)
                                )
                                ok, message, message_type = True, 'Activation email sent to {}'.format(member.email), 'success'
                            else:
                                ok, message, message_type = True, 'You are now a registered user', 'success'
                        user.set_password(password)
                        if not user.roles:
                            user.roles = [Role(role=role)]
                        else:
                            if not role in [role.role for role in user.roles]:
                                user.roles += [Role(role=role)]
                        save_user(user)
                        user_id = user.id
        else:
            ok, message, message_type = False, 'Cannot find your membership', 'error'
    else:
        ok, message, message_type = False, 'Missing user name/password', 'warning'
    return ok, user_id, message, message_type


def activate_user(key):
    ok, user_id = User.validate_token(current_app, key)
    if ok:
        id, message, message_type = user_id, 'Account successfully activated, login', 'success'
    else:
        id, message, message_type = None, user_id, 'warning'
    return ok, id, message, message_type


def change_user_password(user_id, new_password):
    user = get_user(user_id)
    if user:
        user.set_password(new_password)
        save_user(user)
        ok, message, message_type = True, 'Password updated', 'success'
    else:
        ok, message, message_type = False, 'User not not found', 'warning'
    return ok, message, message_type
