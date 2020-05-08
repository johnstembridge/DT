import subprocess
from flask import flash, render_template

from scripts import scripts


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
    def return_result(mode, res):
        text = res.stderr.split('\n')
        if res.returncode != 2:
            flash(mode + ' successful', 'success')
        else:
            flash(mode + ' errored', 'danger')
        return render_template('backup_result.html', result_text=text)

