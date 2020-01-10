from flask_login import login_required
from flask import render_template
from globals.decorators import role_required
from main import app
from front_end.actions import MaintainActions


@app.route('/actions', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def actions_main():
    pass


@app.route('/actions/show', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def show_actions():
    return MaintainActions.list_actions()


@app.route('/actions/clear', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def clear_actions():
    return MaintainActions.clear_actions()
