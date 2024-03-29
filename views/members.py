from flask import request
from flask_login import login_required, current_user


from globals.decorators import role_required
from main import app
from front_end.members_admin import MaintainMembers


@app.route('/members', methods=['GET', 'POST'])
@login_required
@role_required('afcw')
def members():
    if request.method == 'POST':
        return MaintainMembers.find_members()
    else:
        return MaintainMembers.list_members()


@app.route('/members/bulk', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def bulk_update():
    return MaintainMembers.bulk_update()


@app.route('/members/<int:member_number>', methods=['GET', 'POST'])
@login_required
@role_required('afcw')
def edit_or_view_member(member_number):
    return MaintainMembers.edit_or_view_member(member_number)


@app.route('/members/<int:member_number>/copy', methods=['GET', 'POST'])
@login_required
@role_required('afcw')
def copy_member(member_number):
    return MaintainMembers.copy_member(member_number)


@app.route('/members_area', methods=['GET', 'POST'])
@login_required
@role_required('member')
def members_area():
    return None


@app.route('/members/renewal', methods=['GET', 'POST'])
@login_required
@role_required('member')
def renew_member_no_number():
    member_number = current_user.member.number
    return MaintainMembers.renew_member(member_number)


@app.route('/members/<int:member_number>/renewal', methods=['GET', 'POST'])
@login_required
@role_required('member')
def renew_member(member_number):
    return MaintainMembers.renew_member(member_number)


@app.route('/members/<int:member_number>/renewal/dd', methods=['GET', 'POST'])
@login_required
@role_required('member')
def renew_member_dd(member_number):
    upgrade = eval(request.args.get('upgrade'))
    downgrade = eval(request.args.get('downgrade'))
    return MaintainMembers.renewal_debit(member_number, upgrade, downgrade)


@app.route('/members/<int:member_number>/renewal/chq', methods=['GET', 'POST'])
@login_required
@role_required('member')
def renew_member_chq(member_number):
    upgrade = eval(request.args.get('upgrade'))
    downgrade = eval(request.args.get('downgrade'))
    return MaintainMembers.renewal_cheque(member_number, upgrade, downgrade)


@app.route('/members/details', methods=['GET', 'POST'])
@login_required
@role_required('member')
def edit_member_no_number():
    member_number = current_user.member.number
    return MaintainMembers.edit_member(member_number)


@app.route('/members/<int:member_number>/details', methods=['GET', 'POST'])
@login_required
@role_required('member')
def edit_member(member_number):
    return MaintainMembers.edit_member(member_number)

