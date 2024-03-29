from flask_login import login_required

from globals.decorators import role_required
from main import app
from back_end.extracts import Extracts
from back_end.reports import Reports
from back_end.query import Query
from back_end.interface import return_csv_file
import datetime


@app.route('/extracts/certs', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_certs():
    return Extracts.extract_certificates()


@app.route('/extracts/cards', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_cards():
    return Extracts.extract_cards()


@app.route('/extracts/juniors', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_juniors():
    return Extracts.extract_juniors()


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
        month = datetime.date.today().month % 12 + 1
    return Extracts.extract_junior_birthdays(month)


@app.route('/extracts/afcw', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_for_afcw():
    return Extracts.extract_for_afcw()


@app.route('/extracts/email_senior', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_email_senior():
    return Extracts.extract_email_senior()


@app.route('/extracts/email_junior', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_email_junior():
    return Extracts.extract_email_junior()


@app.route('/extracts/comms', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_comms():
    return Extracts.extract_comms()


@app.route('/extracts/region', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_region_report():
    return return_csv_file(Reports.regions(), 'extract.csv')


@app.route('/extracts/district', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_district_report():
    return return_csv_file(Reports.districts(), 'extract.csv')


@app.route('/extracts/cards_all', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_cards_all():
    return Extracts.extract_cards_all()


@app.route('/extracts/renewals', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_renewals():
    return Extracts.extract_renewals()


@app.route('/extracts/debits', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_debits():
    return Extracts.extract_debits()


@app.route('/extracts/debits_ptx', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_debits_for_ptx():
    return Extracts.extract_debits_for_ptx()


@app.route('/extracts/custom', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_custom():
    return Query.select(title='Custom extract')


@app.route('/extracts/show', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_show():
    return Query.show_found()


@app.route('/extracts/extract', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def extracts_extract():
    return return_csv_file(Query.extract(), 'extract.csv')


@app.route('/extracts/bulk_update', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def extracts_bulk_update():
    return Query.bulk_update()
