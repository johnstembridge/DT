from flask import current_app
from flask_sendmail import Message

from globals import config
from globals.decorators import async
from back_end.data_utilities import force_list
from globals.app_setup import mail

import os

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, sender, cc=None, subject=None, message=None):
    #in order to get this to work, had to change the libraries as follows:
    #/home/admin/wagsv_python/venv/lib/python3.5/site-packages/flask_sendmail/connection.py[23]
    #   sm.stdin.write(str.encode(message.dump()))
    #/usr/lib/python3.5/email/mime/text.py[17]
    #   def __init__(self, _text, _subtype='plain', _charset='utf-8'):
    to = force_list(to)
    msg = Message(subject)
    msg.sender = sender
    msg.recipients = to
    msg.cc = force_list(cc)
    msg.body = '\n'.join(force_list(message))
    app = current_app._get_current_object()
    if config.get('send_mail'):
        #send_async_email(app, msg)
        mail.send(msg)
    else:
        out = [
            'Email:',
            'from: ' + sender,
            'to: ' + ', '.join(to),
            'subject: ' + subject,
            'message:']
        print('\n'.join(out + force_list(message)))


def use_sendmail(to, sender, cc=None, subject='', message=''):
    sendmail_location = "/usr/sbin/sendmail"
    p = os.popen("{} -t" .format(sendmail_location), "w")
    p.write("From: {}\n" .format(sender))
    p.write("To: {}\n" .format(';'.join(to) if type(to) is list else to))
    if cc:
        p.write("Cc: {}\n" .format(';'.join(cc) if type(cc) is list else cc))
    p.write("Subject: {}\n".format(subject))
    p.write("\n")  # blank line separating headers from body
    p.write('\n'.join(message) if type(message) is list else message)
    status = p.close()
    #if status and status != 0:
    #    raise ValueError("Sendmail exit status {}".format(status))
