import logging
import requests

from plaza_routing import config
from plaza_routing.integration.util import search_ch_parser
from plaza_routing.integration.util.exception_util import ServiceError, ValidationError

logger = logging.getLogger('plaza_routing.search_ch_service')


def get_connection(start: str, destination: str, time: str, date='today') -> dict:
    """ retrieves the connection for a given start, destination and time of departure"""
    response = None
    try:
        payload = {'from': start, 'to': destination, 'time': time, 'date': date, 'num': 1}
        response = _query(payload)
        connections = search_ch_parser.parse_connections(response)
        first_connection = connections['connections'][0]
        return first_connection
    except Exception as exception:
        _parse_exception(exception, response)


def _query(payload: dict) -> str:
    req = requests.get(config.search_ch['search_ch_api'], params=payload)
    return req.text


def _parse_exception(exception: Exception, response: str):
    if response and "Start- und Zielort müssen sich unterscheiden" in response:
        raise ValidationError('start and destination should differ') from None
    if isinstance(exception, RuntimeError):
        raise exception
    msg = f'search.ch is not running correctly: {exception}'
    logger.error(msg)
    raise ServiceError(msg) from None
