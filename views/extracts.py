from flask_login import login_required

from globals.decorators import role_required
from main import app
from back_end.extracts import Extracts
from back_end.interface import return_csv_file


@app.route('/extracts/certs', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_certs():
    return return_csv_file(Extracts.extract_certificates(), 'certs.csv')


@app.route('/extracts/cards', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_cards():
    return return_csv_file(Extracts.extract_cards(), 'cards.csv')


@app.route('/extracts/cards_all', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_cards_all():
    return return_csv_file(Extracts.extract_cards_all(), 'cards_all.txt')


@app.route('/extracts/renewals', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_renewals():
    return return_csv_file(Extracts.extract_renewals(), 'renewals.csv')


@app.route('/extracts/juniors', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_juniors():
    return return_csv_file(Extracts.extract_juniors(), 'juniors.txt')


@app.route('/extracts/debits', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_debits():
    return return_csv_file(Extracts.extract_debits(), 'debits.txt')


@app.route('/extracts/select', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_select():
    return Extracts.extract_select()


@app.route('/extracts/show', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_show():
    return Extracts.extract_show()
