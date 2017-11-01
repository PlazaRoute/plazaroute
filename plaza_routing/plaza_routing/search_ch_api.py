import requests

SEARCH_CH_API_URL = 'https://timetable.search.ch/api/route.json'


def get_connection(start, destination, time):
    """ retrieves the connection for a given start, destination and time of departure"""
    payload = {'from': start, 'to': destination, 'time': time}
    req = requests.get(SEARCH_CH_API_URL, params=payload)
    return req.json()['connections'][0]  # TODO return fastest connection
