from flask import request, render_template, redirect, flash, url_for
from flask_login import current_user, logout_user

from front_end.member_list_form import MemberListForm
from front_end.member_details_form import MemberDetailsForm
from front_end.renewal_form import MemberEditForm
from front_end.diversity_form import DiversityForm
from front_end.dd_form import RenewalDebitForm, MemberDebitForm
from front_end.chq_form import RenewalChequeForm
from front_end.form_helpers import flash_errors, render_link, url_pickle_dump, url_pickle_load, read_only_form
from globals.enumerations import UserRole, MembershipType, PaymentMethod, MemberAction
from globals.config import full_url


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
    def edit_member(member_number):
        redirect = MaintainMembers.current_user_is_member(member_number)
        if redirect:
            return redirect
        form = MemberEditForm()
        if form.validate_on_submit():
            if form.submit.data:
                payment_method, paypal_payment, dues, member_type, member = form.save_member(member_number)
                if member:
                    flash('member {} {}'.format(member.dt_number(), 'saved' if member_number == 0 else 'updated'),
                          'success')
                form.populate_member(member_number, request.referrer, renewal=False)
        elif form.errors:
            flash_errors(form)
        if not form.is_submitted():
            message = form.populate_member(member_number, request.referrer, renewal=False)
            if message:
                flash(message, 'success')
        return render_template('renewal.html', form=form, MembershipType=MembershipType, render_link=render_link)

    @staticmethod
    def renew_member(member_number):
        goto = MaintainMembers.current_user_is_member(member_number, 'renewal')
        if goto:
            return goto
        form = MemberEditForm()
        if form.validate_on_submit():
            if form.submit.data:
                previous_payment_method = PaymentMethod.from_value(int(form.previous_payment_method.data))
                payment_method, renewal_payment, dues, member_type, member = form.save_member(member_number)
                logout = True
                if member:
                    flash('member {} {}'.format(member.dt_number(), 'saved' if member_number == 0 else 'updated'),
                          'success')
                    if renewal_payment and payment_method == PaymentMethod.cc:
                        next = render_template('renewal_paypal.html',
                                               pp_name=renewal_payment.name.replace("_", " "),
                                               pp_value=renewal_payment.value,
                                               dt_number=member.dt_number(),
                                               concession_type=member.concession_type())
                    elif renewal_payment and payment_method == PaymentMethod.dd and previous_payment_method != PaymentMethod.dd:
                        upgrade = member.last_action() and member.last_action().action == MemberAction.upgrade
                        next = redirect(full_url('members/{}/renewal/dd?upgrade={}'.format(member.number, upgrade or False)))
                        logout = False
                    elif renewal_payment and payment_method == PaymentMethod.chq:
                        upgrade = member.last_action() and member.last_action().action == MemberAction.upgrade
                        next = redirect(
                            full_url('members/{}/renewal/chq?upgrade={}'.format(member.number, upgrade or False)))
                        logout = False
                    else:
                        next = render_template('renewal_acknowledge.html',
                                               dt_number=member.dt_number(),
                                               member_status=member.status.name,
                                               payment_method=payment_method.name if payment_method else None,
                                               dues=dues,
                                               renewal_type=member_type
                                               )
                    if logout and current_user.role != UserRole.super:
                        logout_user()
                    return next
                form.populate_member(member_number, request.referrer, renewal=True)
        elif form.errors:
            flash_errors(form)
        if not form.is_submitted():
            message = form.populate_member(member_number, request.referrer, renewal=True)
            if message:
                flash(message, 'success')
        return render_template('renewal.html', form=form, MembershipType=MembershipType, render_link=render_link)

    @staticmethod
    def renewal_debit(member_number, upgrade):
        goto = MaintainMembers.current_user_is_member(member_number, 'renewal')
        if goto:
            return goto
        form = RenewalDebitForm()
        form.make_readonly('dt_number')
        form.make_readonly('amount')

        if form.validate_on_submit():
            member = None
            if form.submit.data:
                member = form.save(member_number)
            elif form.errors:
                flash_errors(form)
            if member:
                payment = member.last_payment()
                upgrade_text = ' upgrade' if upgrade else ''
                return render_template('renewal_acknowledge.html',
                                       dt_number=member.dt_number(),
                                       member_status=member.status.name,
                                       payment_method=payment.method.name if payment else None,
                                       dues=payment.amount if payment else None,
                                       renewal_type=member.long_membership_type(upgrade=upgrade) + upgrade_text
                                       )
        if not form.is_submitted():
            form.populate(member_number, upgrade)
        return render_template('renewal_dd.html', form=form, MembershipType=MembershipType, render_link=render_link)

    @staticmethod
    def renewal_cheque(member_number, upgrade):
        goto = MaintainMembers.current_user_is_member(member_number, 'renewal')
        if goto:
            return goto
        form = RenewalChequeForm()
        form.make_readonly('dt_number')
        form.make_readonly('amount')

        form.populate(member_number, upgrade)
        return render_template('renewal_chq.html', form=form, MembershipType=MembershipType, render_link=render_link)

    @staticmethod
    def dd_mandate(member_number):
        redirect = MaintainMembers.current_user_is_member(member_number)
        if redirect:
            return redirect
        form = MemberDebitForm()
        message = form.populate_member(member_number, request.referrer, upgrade=False)
        if message:
            flash(message, 'success')
        return render_template('emandate.html', form=form)

    @staticmethod
    def current_user_is_member(member_number, goto='renewal'):
        # check current user is member member_number
        if current_user.user_name != str(member_number) and current_user.role != UserRole.super:
            return redirect('/members/{}/{}'.format(current_user.member.number, goto))
        else:
            return None

    @staticmethod
    def diversity_member(member_number):
        redirect = MaintainMembers.current_user_is_member(member_number)
        if redirect:
            return redirect
        form = DiversityForm()
        if form.validate_on_submit():
            if form.submit.data:
                member = form.save_member(member_number)
                if member:
                    flash('member {} {}'.format(member.dt_number(), 'saved' if member_number == 0 else 'updated'),
                          'success')
                form.populate_member(member_number, request.referrer, renewal=False)
        elif form.errors:
            flash_errors(form)
        if not form.is_submitted():
            message = form.populate_member(member_number, request.referrer, renewal=False)
            if message:
                flash(message, 'success')
        return render_template('diversity.html', form=form, render_link=render_link)


