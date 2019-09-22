from flask import render_template, redirect, flash, url_for

from front_end.member_list_form import MemberListForm
from front_end.member_details_form import MemberDetailsForm
from front_end.form_helpers import flash_errors, render_link


class MaintainMembers:

    @staticmethod
    def find_members():
        form = MemberListForm()
        if form.is_submitted():
            pass
        form.populate_member_list(None)

        return render_template('member_list.html', form=form, render_link=render_link)

    @staticmethod
    def bulk_update():
        form = MemberListForm()
        if form.is_submitted():
            pass
        form.populate_member_list()

        return render_template('member_list.html', form=form, render_link=render_link)

    @staticmethod
    def list_members():
        form = MemberListForm()
        if form.is_submitted():
            pass
        form.populate_member_list()

        return render_template('member_list.html', form=form, render_link=render_link)

    @staticmethod
    def edit_member(member_number):
        form = MemberDetailsForm()
        form.member_number.data = member_number
        if form.validate_on_submit():
            if form.submit.data:
                if form.save_member(member_number):
                    flash('member saved', 'success')
                    return redirect(url_for('members'))
        elif form.errors:
            flash_errors(form)
        if not form.is_submitted():
            form.populate_member(member_number)
        return render_template('member_details.html', form=form, render_link=render_link)