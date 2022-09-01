import subprocess
from flask import flash, render_template

from scripts import scripts
from back_end.super import renew_recent_joiners, renew_recent_resumers, renew_paid, change_member_type_by_age, \
    lapse_expired, season_tickets, set_region, check_fan_ids


class Super:

    @staticmethod
    def backup_database():
        res = subprocess.run([scripts.file_name("backup")], stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        return Super.return_result('Backup', res)

    @staticmethod
    def restore_database():
        res = subprocess.run([scripts.file_name("restore")], stderr=subprocess.PIPE, universal_newlines=True,
                             shell=True)
        return Super.return_result('Restore backup', res)

    @staticmethod
    def renew_recent_joiners():
        # auto renew members who joined on or after 1st Feb of previous membership year
        res = renew_recent_joiners()
        return Super.return_result('Renew recent join', res)

    @staticmethod
    def renew_recent_resumers():
        # auto renew members who resumed on or after 1st Feb of previous membership year
        res = renew_recent_resumers()
        return Super.return_result('Renew recent resume', res)

    @staticmethod
    def change_member_type_by_age():
        # change any age related member type for those passing age breakpoint
        res = change_member_type_by_age()
        return Super.return_result('Update member type by age', res)

    @staticmethod
    def renew_paid(payment_method, save=True):
        # renew members who have paid according to payment file
        res = renew_paid(payment_method, save)
        return Super.return_result('Renew paid by ' + payment_method, res)

    @staticmethod
    def lapse_expired():
        # lapse any members who have passed the grace period for renewal payment
        res = lapse_expired()
        return Super.return_result('Expired members lapsed', res)

    @staticmethod
    def season_tickets():
        # update season ticket numbers
        res = season_tickets()
        return Super.return_result('Season tickets updated', res)

    @staticmethod
    def check_fan_ids():
        # update season ticket numbers
        res = check_fan_ids()
        return Super.return_result('Fan Ids checked, see file ', res)

    @staticmethod
    def return_result(mode, res):
        if type(res) != str:
            text = res.stderr
            return_code = res.returncode
        else:
            text = res
            return_code = 0
        text = text.split('\n')
        if return_code != 2:
            flash(mode + ' successful', 'success')
        else:
            flash(mode + ' errored', 'danger')
        return render_template('bulk_update_result.html', mode=mode, result_text=text)

    @staticmethod
    def set_region():
        # Set region for all UK members
        res = set_region()
        return Super.return_result('Region set', res)
