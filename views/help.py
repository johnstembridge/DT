from flask_login import login_required

from front_end import DTHelp
from globals.decorators import role_required
from main import app


@app.route('/help', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def list_help():
    return DTHelp.list_help()


@app.route('/help/<subject>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def show_help(subject):
    return DTHelp.show_help(subject)
