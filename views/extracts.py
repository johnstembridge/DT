from flask_login import login_required

from globals.decorators import role_required
from globals.enumerations import Months
from main import app
from back_end.extracts import Extracts
from back_end.query import Query
from back_end.interface import return_csv_file
import datetime


@app.route('/extracts/certs', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_certs():
    return return_csv_file(Extracts.extract_certificates(), 'certs.txt')


@app.route('/extracts/cards', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_cards():
    return return_csv_file(Extracts.extract_cards(), 'cards.csv')


@app.route('/extracts/cards_all', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_cards_all():
    return return_csv_file(Extracts.extract_cards_all(), 'cards_all.txt')


@app.route('/extracts/renewals', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_renewals():
    return return_csv_file(Extracts.extract_renewals(), 'renewals.csv')


@app.route('/extracts/juniors', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_juniors():
    return return_csv_file(Extracts.extract_juniors(), 'juniors.csv')


@app.route('/extracts/junior_birthdays', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_junior_birthdays():
    return extracts_junior_birthdays_for_month()


@app.route('/extracts/junior_birthdays/<int:month>', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_junior_birthdays_for_month(month=None):
    if not month:
        month = datetime.date.today().month + 1
    month_name = [m for m in Months if m.value ==12][0].name
    return return_csv_file(Extracts.extract_junior_birthdays(month), 'junior birthdays {}.csv'.format(month_name))


@app.route('/extracts/debits', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_debits():
    return return_csv_file(Extracts.extract_debits(), 'debits.txt')


@app.route('/extracts/email', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_email():
    return return_csv_file(Extracts.extract_email(), 'email.csv')


@app.route('/extracts/comms', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_comms():
    return return_csv_file(Extracts.extract_comms(), 'comms.csv')


@app.route('/extracts/select', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_select():
    return Query.select(title='Select data')


@app.route('/extracts/show', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_show():
    return Query.show_found()


@app.route('/extracts/extract', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_extract():
    return return_csv_file(Query.extract(), 'extract.csv')


@app.route('/extracts/bulk_update', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_bulk_update():
    return Query.bulk_update()


@app.route('/extracts/selected', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_extract_selected():
    return return_csv_file(Extracts.extract_comms(), 'comms.csv')


