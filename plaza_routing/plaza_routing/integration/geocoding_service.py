import requests
from plaza_routing import config


def geocode(address: str) -> tuple:
    payload = {'q': address,
               'countrycodes': 'ch',
               'viewbox': config.geocoding['viewbox'],
               'bounded': 1,
               'limit': 1,  # TODO should we handle multiple coordinate options?
               'format': 'json'}
    req = requests.get(config.geocoding['geocoding_api'], params=payload)
    result = req.json()

    if not result:
        raise ValueError(f'no coordinates found for the given address {address}')

    return float(result[0]['lon']), float(result[0]['lat'])
