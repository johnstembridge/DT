from flask import render_template
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField

from globals.decorators import role_required
from globals.email import send_mail, use_sendmail
from main import app


@app.route('/test/email', methods=['GET', 'POST'])
@login_required
@role_required('admin')
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
