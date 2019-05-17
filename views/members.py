from flask_login import login_required, current_user

from globals.decorators import role_required
from main import app
from front_end.members_admin import MaintainMembers


@app.route('/members', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def members():
    return MaintainMembers.list_members()


@app.route('/members/<int:member_id>/details', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_member(member_id):
    return MaintainMembers.edit_member(member_id)


@app.route('/members_find', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def find_members():
    return MaintainMembers.find_members()


@app.route('/members_add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_member():
    return None


