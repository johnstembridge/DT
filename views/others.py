from flask import render_template


def unauthorised(e):
    return render_template('401.html', message=e.description), 404


def page_not_found(e):
    return render_template('404.html', message=e.description), 404


def internal_error(e):
    return render_template('500.html', message=e.description), 500

