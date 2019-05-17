import logging
from logging.handlers import RotatingFileHandler
from globals import config


def log_init(app):
    # initialize the log handler
    log_path = config.get('locations')['logs'] + '/info.log'

    log_handler = RotatingFileHandler(log_path, maxBytes=1000000, backupCount=1)

    # set the log handler level
    log_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    log_handler.setFormatter(formatter)

    # set the app logger level
    app.logger.setLevel(logging.INFO)

    app.logger.addHandler(log_handler)

    return
