from flask import request, render_template, redirect, flash, url_for
from flask_login import current_user

from front_end.member_list_form import MemberListForm
from front_end.member_details_form import MemberDetailsForm
from front_end.renewal_form import MemberRenewalForm
from front_end.form_helpers import flash_errors, render_link, url_pickle_dump, url_pickle_load, read_only_form
from globals.enumerations import MembershipType


class MaintainMembers:

    @staticmethod
    def find_members():
        form = MemberListForm()
        form.set_status_choices()
        form.set_membership_type_choices()
        form.set_initial_counts()
        if form.validate_on_submit():
            query_clauses = form.find_members()
            return redirect(url_for('members', query_clauses=url_pickle_dump(query_clauses)))
        elif form.errors:
            flash_errors(form)
        return render_template('member_list.html', form=form, render_link=render_link)

    @staticmethod
    def list_members():
        if 'query_clauses' in request.args:
            query_clauses = url_pickle_load(request.args.get('query_clauses'))
        else:
            query_clauses = None
        page = request.args.get('page', 1, int)
        form = MemberListForm()
        form.set_status_choices()
        form.set_membership_type_choices()
        form.set_initial_counts()
        form.populate_member_list(query_clauses, url_pickle_dump(query_clauses), page)
        return render_template('member_list.html', form=form, render_link=render_link)

    @staticmethod
    def bulk_update():
        form = MemberListForm()
        if form.is_submitted():
            pass
        form.populate_member_list()
        return render_template('member_list.html', form=form, render_link=render_link)

    @staticmethod
    def edit_or_view_member(member_number):
        form = MemberDetailsForm()
        if form.validate_on_submit():
            if form.submit.data:
                member = form.save_member(member_number)
                if member:
                    flash('member {} {}'.format(member.dt_number(), 'saved' if member_number == 0 else 'updated'),
                          'success')
                    return redirect(form.return_url.data)
        elif form.errors:
            flash_errors(form)
        if not form.is_submitted():
            form.populate_member(member_number, request.referrer)
            if not current_user.has_write_access():
                read_only_form(form)
        return render_template('member_details.html', form=form, render_link=render_link)

    @staticmethod
    def copy_member(member_number):
        form = MemberDetailsForm()
        if form.validate_on_submit():
            if form.submit.data:
                member_number = 0
                member = form.save_member(member_number)
                if member:
                    flash('member {} {}'.format(member.dt_number(), 'saved' if member_number == 0 else 'updated'),
                          'success')
                    return redirect(form.return_url.data)
        elif form.errors:
            flash_errors(form)
        if not form.is_submitted():
            form.populate_member(member_number, request.referrer, copy=True)
        return render_template('member_details.html', form=form, render_link=render_link)

    @staticmethod
    def renew_member(member_number):
        # check current user is member member_number
        if current_user.member_id != member_number:
            return redirect('/members/{}/renewal'.format(current_user.member_id))
        form = MemberRenewalForm()
        if form.validate_on_submit():
            if form.submit.data:
                card_payment, paypal_payment, member = form.save_member(member_number)
                if card_payment and member:
                    flash('member {} {}'.format(member.dt_number(), 'saved' if member_number == 0 else 'updated'),
                          'success')
                    return render_template('renewal_payment.html',
                                           pp_name=paypal_payment.name.replace("_", " "),
                                           pp_value=paypal_payment.value,
                                           dt_number=member.dt_number(),
                                           concession_type=member.concession_type())
        elif form.errors:
            flash_errors(form)
        if not form.is_submitted():
            form.populate_member(member_number, request.referrer)
        return render_template('renewal.html', form=form, render_link=render_link)
