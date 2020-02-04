from flask_login import login_required
from flask import request, flash, redirect, url_for
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
    type = request.args.get('type')
    return MaintainActions.list_actions(type)


@app.route('/actions/clear', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def clear_actions():
    type = request.args.get('type')
    query = request.args.get('query_clauses')
    MaintainActions.clear_actions(query)
    flash('Actions closed', 'success')
    return redirect(url_for('show_actions', type=type))