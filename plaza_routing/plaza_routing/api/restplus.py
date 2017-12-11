import logging
from flask_restplus import Api

from plaza_routing.integration.util.exception_util import ValidationError, ServiceError


api = Api(version='1.0', title='PlazaRouting API', description='PlazaRouting API')

logger = logging.getLogger('plaza_routing')


@api.errorhandler(ValidationError)
def validation_error_handler(e):
    """When the user passed an invalid parameter the API"""
    return {'message': str(e)}, 400


@api.errorhandler(ServiceError)
def service_error_handler():
    """When a third party system is temporarily unavailable"""
    return {'message': 'third party system is temporarily unavailable'}, 503


@api.errorhandler
def default_error_handler():
    return {'message': 'plaza route is temporarily unavailable'}, 500
