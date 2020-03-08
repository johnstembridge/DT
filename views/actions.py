from flask_login import login_required
from flask import request, flash, redirect, url_for
from globals.decorators import role_required
from main import app
from front_end.actions import MaintainActions


@app.route('/actions/show', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def show_actions():
    type = request.args.get('type')
    page = request.args.get('page', 1, int)
    return MaintainActions.list_actions(type, page)


@app.route('/actions/clear', methods=['GET', 'POST'])
@login_required
@role_required('extract')
def clear_actions():
    type = request.args.get('type')
    query = request.args.get('query_clauses')
    MaintainActions.clear_actions(query)
    flash('Actions closed', 'success')
    return redirect(url_for('show_actions', type=type))