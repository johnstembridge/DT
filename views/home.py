from flask_login import login_required
from flask import render_template
from globals.decorators import role_required
from main import app
from front_end.dashboard import Dashboard
from front_end.form_helpers import flash_errors, render_link


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
@login_required
@role_required('afcw')
def index():
    form = Dashboard()
    form.populate()
    return render_template('home.html', form=form, render_link=render_link)

