import requests
from util import search_ch_parser


SEARCH_CH_API_URL = 'https://timetable.search.ch/api/route.json'


def get_connection(start, destination, time):
    """ retrieves the connection for a given start, destination and time of departure"""
    payload = {'from': start, 'to': destination, 'time': time, 'num': 1}
    req = requests.get(SEARCH_CH_API_URL, params=payload)
    connections = search_ch_parser.parse_connections(req.text)
    first_connection = connections['connections'][0]
    return first_connection
