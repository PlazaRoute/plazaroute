import logging
from flask_restplus import Api


FLASK_DEBUG = True

api = Api(version='1.0', title='PlazaRouting API', description='PlazaRouting API')

logger = logging.getLogger('plaza_routing')


@api.errorhandler
def default_error_handler(e):
    message = f'An unhandled exception occurred: {e}'
    logger.error(message)
    if not FLASK_DEBUG:
        return {'message': message}, 500
