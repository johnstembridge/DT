from flask_login import login_required
from flask import request, flash, redirect, url_for, render_template
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
