from flask_login import login_required
from flask_wtf import FlaskForm
from flask import render_template, session
from globals.decorators import role_required
from main import app


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
@login_required
@role_required('admin')
def reports():
    return render_template('home.html')


@app.route('/reports/certs', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def reports_certs():
    return render_template('home.html')


@app.route('/reports/cards', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def reports_cards():
    return render_template('home.html')


@app.route('/reports/labels', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def reports_labels():
    return render_template('home.html')

