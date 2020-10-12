from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from globals.config import full_url
from globals.email import send_mail
from models.dt_db import User
from back_end.interface import get_member_by_email, get_user, save_user
from back_end.users import register_user
from back_end.data_utilities import get_digits, match_string
from front_end.form_helpers import ReadOnlyWidget


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def populate(self):
        pass


class MemberLoginForm(FlaskForm):
    number = StringField('Membership number', validators=[DataRequired()])
    hidden_number = HiddenField()
    email = StringField('Email address', validators=[DataRequired(), Email("Invalid email address")])
    post_code = StringField('Post code', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def populate(self, member_number):
        self.hidden_number.data = member_number
        if member_number:
            prop = getattr(self, 'number')
            setattr(prop, 'widget', ReadOnlyWidget())
            self.number.data = member_number
        pass


def login(next_page, app=None):
    if current_user.is_authenticated:
        return redirect(next_page)
    if not next_page:
        return redirect('/')
    url_components = next_page.split('/')
    is_member_login = 'members' in url_components and ('renewal' in url_components or 'details' in url_components)
    with_number = len(url_components) == 4
    if is_member_login:
        if with_number:
            member_number = int(url_components[2])
        else:
            member_number = None
        return member_login(next_page, member_number, app)
    else:
        return user_login(next_page, app)


def user_login(next_page, app=None):
    form_name = 'login.html'
    form = LoginForm()
    if form.is_submitted():
        if form.validate_on_submit():
            user = get_user(user_name=form.username.data)
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password', 'danger')
                return render_template(form_name, title='Sign In', form=form)
            login_user(user, remember=form.remember_me.data)
            if not next_page:
                next_page = 'index'
            else:
                next_page = next_page
            return redirect(next_page)
    else:
        form.populate()
    return render_template(form_name, title='Sign In', form=form)


def member_login(next_page, member_number=None, app=None):
    form_name = 'member_login.html'
    form = MemberLoginForm()
    if form.is_submitted():
        if form.hidden_number.data:
            form.number.data = int(form.hidden_number.data)
        if form.validate_on_submit():
            no_number = not member_number
            if no_number:
                member_number = int('0' + get_digits(form.number.data))
            user_name = str(member_number)
            password = User.member_password(form.post_code.data)
            user = get_user(user_name=user_name)
            message = None
            if user is None:
                ok, id, message, message_type = member_register(member_number, user_name, password, form.email.data)
                if ok:
                    user = get_user(id=id)
            if not message:
                if user is None:
                    message = 'Email or post code do not match Membership number {}'.format(member_number)
                elif not match_string(user.member.email, form.email.data):
                    message = 'Email does not match the Membership number'
                elif not user.check_password(password):
                    message = 'Post code does not match the Membership number'
            if message:
                flash(message, 'danger')
                if not no_number:
                    form.populate(member_number)
                return render_template(form_name, title='Sign In', form=form)
            login_user(user, remember=form.remember_me.data)
            if not next_page:
                next_page = 'index'
            else:
                next_page = next_page
            return redirect(next_page)
    else:
        form.populate(member_number)
    return render_template(form_name, title='Sign In', form=form)


def validate_username(self, username):
    user = get_user(user_name=username.data)
    if user is not None:
        if user.member.email != self.email.data:
            raise ValidationError('Please use a different username.')


class RegistrationForm(FlaskForm):
    member_number = StringField('Member number', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), validate_username])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


def user_register(new=True):
    # Register user (new is True) or reset login
    if new and current_user.is_authenticated:
        return redirect(full_url('index'))
    form = RegistrationForm()
    form_title = 'Register' if new else 'Reset login details'
    if not new and not form.is_submitted():
        form.member_number.data = current_user.member.dt_number()
        form.username.data = current_user.user_name
        form.email.data = current_user.member.contact.email
        form.email.render_kw = {'readonly': True}
    else:
        if form.validate_on_submit():
            number = int(get_digits(form.member_number.data))
            ok, id, message, message_type = register_user(number, form.username.data, form.password.data, form.email.data)
            if ok:
                if new:
                    flash(message, message_type)
                else:
                    flash('Login details reset', 'success')
                    return redirect(url_for('user_register'))
            else:
                flash(message, message_type)
                return redirect(url_for('user_register'))
    return render_template('register.html', title=form_title, form=form)


def member_register(member_number, user_name, post_code, email, new=True):
    # Register user (new is True) or reset login
    if new and current_user.is_authenticated:
        return
    else:
        ok, id, message, message_type = register_user(member_number, user_name, post_code, email)
        return ok, id, message, message_type


def user_logout():
    logout_user()
    return redirect(full_url('index'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField()


def user_reset_password_request(role, app):
    if current_user.is_authenticated:
        return redirect(full_url('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = get_member_by_email(form.email.data).user
        if user:
            expires = send_password_reset_email(user, app)
            message = 'Check your email for the instructions to reset your password'
            flash(message, 'success')
        else:
            flash('Email not recognised', 'danger')
        return redirect(full_url('user_login'))
    return render_template('user/reset_password_request.html', title='Reset Password', form=form)


def send_password_reset_email(user, app):
    token, expires = user.get_token(app)
    send_mail(to=user.member.contact.email,
              sender='membership@thedonstrust.org',
              subject='[Dons Trust] Reset Your Password',
              message=render_template('user/reset_password.txt',
                                      full_url=full_url,
                                      user=user,
                                      token=token,
                                      expires=expires)
              )


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField()


def user_reset_password(role, app, token):
    if current_user.is_authenticated:
        return redirect(full_url(role, 'index'))
    user = User.verify_reset_password_token(app, token)
    if not user:
        return redirect(full_url(role, 'index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        save_user(user)
        flash('Your password has been reset', 'success')
        return redirect(full_url(role, 'user_login'))
    return render_template('user/reset_password.html', form=form)
