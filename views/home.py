from flask_login import login_required
from flask_wtf import FlaskForm
from flask import render_template, session
from globals.decorators import role_required
from main import app


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
@login_required
@role_required('admin')
def index():
    return render_template('home.html')

