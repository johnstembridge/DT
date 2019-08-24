from flask import render_template


def unauthorised(e):
    message = getattr(e, 'description', 'unauthorised')
    return render_template('401.html', message=message), 404


def page_not_found(e):
    message = getattr(e, 'description', 'not found')
    return render_template('404.html', message=message), 404


def internal_error(e):
    message = getattr(e, 'description', 'unexpected error')
    return render_template('500.html', message=message), 500

