from flask_login import login_required
from globals.decorators import role_required
from main import app
from front_end.super import Super


@app.route('/super/backup', methods=['GET', 'POST'])
@login_required
@role_required('super')
def backup():
    return Super.backup_database()


@app.route('/super/restore', methods=['GET', 'POST'])
@login_required
@role_required('super')
def restore():
    return Super.restore_database()


@app.route('/super/renew_recent', methods=['GET', 'POST'])
@login_required
@role_required('super')
def renew_recent():
    return Super.renew_recent()


@app.route('/super/renew_paid_cc', methods=['GET', 'POST'])
@login_required
@role_required('super')
def renew_paid_cc():
    return Super.renew_paid('cc')


@app.route('/super/renew_paid_dd', methods=['GET', 'POST'])
@login_required
@role_required('super')
def renew_paid_dd():
    return Super.renew_paid('dd')


@app.route('/super/update_by_age', methods=['GET', 'POST'])
@login_required
@role_required('super')
def change_member_type_by_age():
    return Super.change_member_type_by_age()


@app.route('/super/lapse_expired', methods=['GET', 'POST'])
@login_required
@role_required('super')
def lapse_expired():
    return Super.lapse_expired()


@app.route('/super/season_tickets', methods=['GET', 'POST'])
@login_required
@role_required('super')
def season_tickets():
    return Super.season_tickets()
