import logging
import requests

from plaza_routing import config
from plaza_routing.integration.util import search_ch_parser
from plaza_routing.integration.util.exception_util import ServiceError, ValidationError

logger = logging.getLogger('plaza_routing.search_ch_service')


def get_connection(start: str, destination: str, time: str, date='today') -> dict:
    """ retrieves the connection for a given start, destination and time of departure"""
    req = None
    try:
        payload = {'from': start, 'to': destination, 'time': time, 'date': date, 'num': 1}
        req = requests.get(config.search_ch['search_ch_api'], params=payload)
        connections = search_ch_parser.parse_connections(req.text)
        first_connection = connections['connections'][0]
        return first_connection
    except Exception as exception:
        _parse_exception(exception, req)


def _parse_exception(exception: Exception, req):
    if req and "Start- und Zielort müssen sich unterscheiden" in req.text:
        raise ValidationError('start and destination should differ') from None
    if isinstance(exception, RuntimeError):
        raise exception
    msg = f'search.ch is not running correctly: {exception}'
    logger.error(msg)
    raise ServiceError(msg) from None
