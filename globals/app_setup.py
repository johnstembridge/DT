from flask_bootstrap import Bootstrap
from flask_sendmail import Mail

from globals import logging, config

mail = Mail()


def init_app(app):
    app.config['SECRET_KEY'] = config.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = config.get('db_path')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    Bootstrap(app)
    logging.log_init(app)
    mail.init_app(app)
