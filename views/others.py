from flask import render_template


def bad_request_error(e):
    message = getattr(e, 'description', 'bad request')
    return render_template('400.html', message=message), 400


def unauthorised(e):
    message = getattr(e, 'description', 'unauthorised')
    return render_template('401.html', message=message), 401


def page_not_found(e):
    message = getattr(e, 'description', 'not found')
    return render_template('404.html', message=message), 404


def internal_error(e):
    message = getattr(e, 'description', 'unexpected error')
    return render_template('500.html', message=message), 500


def csrf_error(e):
    reason = e.description
    return render_template('csrf_error.html', reason=reason), 400
