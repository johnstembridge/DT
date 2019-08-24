from flask_login import login_required

from globals.decorators import role_required
from main import app
from api.members import api_get_member


@app.route('/api/members/<int:member_number>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def api_edit_member(member_number):
    return api_get_member(member_number)
