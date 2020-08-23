import subprocess
from flask import flash, render_template

from scripts import scripts
from back_end.super import renew_recent, renew_paid


class Super:

    @staticmethod
    def backup_database():
        res = subprocess.run([scripts.file_name("backup")], stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        return Super.return_result('Backup', res)

    @staticmethod
    def restore_database():
        res = subprocess.run([scripts.file_name("restore")], stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        return Super.return_result('Restore', res)

    @staticmethod
    def renew_recent():
        # auto renew members who joined on or after 1st Feb of previous membership year
        res = renew_recent()
        return Super.return_result('Renew recent', res)

    @staticmethod
    def renew_paid():
        # auto renew members who joined on or after 1st Feb of previous membership year
        res = renew_paid()
        return Super.return_result('Renew paid', res)

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
        return render_template('backup_result.html', result_text=text)

