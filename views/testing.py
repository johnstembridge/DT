from flask import render_template, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField

from globals.decorators import role_required
from globals.email import send_mail
from main import app
from back_end.interface import get_user


@app.route('/test/password', methods=['GET', 'POST'])
@login_required
@role_required('super')
def test_password():
    username = request.args.get('username')
    user = get_user(user_name=username)
    password = request.args.get('password')
    check = user.check_password(password)
    form = CheckPasswordForm()
    form.populate(username, password, check)
    return render_template('check_password.html', form=form)


class CheckPasswordForm(FlaskForm):
    username = StringField(label='username')
    password = StringField(label='password')
    check = StringField(label='check')

    def populate(self, username, password, check):
        self.username.data = username
        self.password.data = password
        self.check.data = check


@app.route('/test/email', methods=['GET', 'POST'])
@login_required
@role_required('super')
def test_email():
    subject = 'Test email'
    sender = 'membership@thedonstrust.org'
    message = ['test message']
    to = 'john.stembridge@gmail.com'
    #use_sendmail(to=to, sender=sender, cc=None, subject=subject, message=message)
    send_mail(to=to,
              sender=sender,
              cc=[],
              subject='Dons Trust Membership: ' + subject,
              message=message)
    form = SendEmailConfirmationForm()
    form.populate(subject, message)
    return render_template('email_confirmation.html', form=form)


class SendEmailConfirmationForm(FlaskForm):
    title = StringField(label='Title')
    message = StringField(label='Message')

    def populate(self, title, message):
        self.title.data = title
        self.message.data = message
