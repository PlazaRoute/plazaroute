import re
import requests
from plaza_routing.integration.util import search_ch_parser

SEARCH_CH_API_URL = 'https://timetable.search.ch/api/route.json'
TIME_REGEX = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')


def _validate_arguments(start: str, destination: str, time: str):
    if not start or not destination or not time:
        raise ValueError('empty arguments are not allowed')
    if not TIME_REGEX.match(time):
        raise ValueError('invalid time format: %H:%M')


def get_connection(start: str, destination: str, time: str) -> dict:
    """ retrieves the connection for a given start, destination and time of departure"""
    _validate_arguments(start, destination, time)
    payload = {'from': start, 'to': destination, 'time': time, 'num': 1}
    req = requests.get(SEARCH_CH_API_URL, params=payload)
    connections = search_ch_parser.parse_connections(req.text)
    first_connection = connections['connections'][0]
    return first_connection
