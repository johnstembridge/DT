from flask_login import login_required
from flask import render_template
from globals.decorators import role_required
from main import app


@app.route('/', methods=['GET', 'POST'])
@app.route('/index')
@login_required
@role_required('admin')
def payments_main():
    return render_template('home.html')

