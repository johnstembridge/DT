import subprocess
from flask import request, flash, redirect, url_for, render_template


class Super:

    @staticmethod
    def backup_database():
        res = subprocess.run(["./backup.sh"], stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        text = res.stderr.split('\n')
        if res.returncode == 0:
            flash('Backup successful', 'success')
        else:
            flash('Backup errored', 'danger')
        return render_template('backup_result.html', result_text=text)

    def restore_database(self):
        pass
