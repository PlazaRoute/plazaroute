import requests

GEOCODING_API_URL = 'http://nominatim.openstreetmap.org/search'
BOUNDING_BOX_SWITZERLAND = '5.9559,45.818,10.4921,47.8084'


def geocode(address):
    payload = {'q': address,
               'countrycodes': 'ch',
               'viewbox': BOUNDING_BOX_SWITZERLAND,
               'bounded': 1,
               'limit': 1,  # TODO should we handle multiple coordinate options?
               'format': 'json'}
    req = requests.get(GEOCODING_API_URL, params=payload)
    result = req.json()

    if not result:
        raise ValueError(f'no coordinates found for the given address {address}')

    return float(result[0]['lat']), float(result[0]['lon'])
