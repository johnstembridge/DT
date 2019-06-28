from flask import render_template, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField

from flask import url_for


class DTHelp:

    @staticmethod
    def list_help():
        pass

    @staticmethod
    def show_help(subject):
        if subject == '':
            return redirect(url_for('list_help'))
        form = HelpSubjectForm()
        if form.is_submitted():
            if form.save.data:
                m = form.save_help(subject)
                if m:
                    flash('Help ' + m, 'success')
                    return redirect(url_for('list_help'))
            if form.add_item.data:
                form.add_news_item()
        else:
            form.populate_help(subject)
        return render_template('help.html', form=form, topic=subject)


class HelpSubjectForm(FlaskForm):
    title = StringField(label='Subject')
    #text = TextAreaField()

    def populate_help(self, subject):
        self.title.data = subject

    def save_help(self, subject):
        return ''
