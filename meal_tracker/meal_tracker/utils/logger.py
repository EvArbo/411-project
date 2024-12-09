import logging
import sys

from flask import current_app, has_request_context


def configure_logger(logger):
    logger.setLevel(logging.DEBUG)  

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    if has_request_context():
        app_logger = current_app.logger
        for handler in app_logger.handlers:
            logger.addHandler(handler)
