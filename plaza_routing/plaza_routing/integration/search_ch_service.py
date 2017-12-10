import requests
from plaza_routing.integration.util import search_ch_parser
from plaza_routing import config


def get_connection(start: str, destination: str, time: str, date='today') -> dict:
    """ retrieves the connection for a given start, destination and time of departure"""
    payload = {'from': start, 'to': destination, 'time': time, 'date': date, 'num': 1}
    req = requests.get(config.search_ch['search_ch_api'], params=payload)
    connections = search_ch_parser.parse_connections(req.text)
    first_connection = connections['connections'][0]
    return first_connection
