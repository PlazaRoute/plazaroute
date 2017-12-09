import requests
import logging

from plaza_routing import config
from plaza_routing.integration.util.exception_util import ValidationError, ServiceError


logger = logging.getLogger('plaza_routing.graphhopper_routing_strategy')


def geocode(address: str) -> tuple:
    payload = {'q': address,
               'countrycodes': 'ch',
               'viewbox': config.geocoding['viewbox'],
               'bounded': 1,
               'limit': 1,  # TODO should we handle multiple coordinate options?
               'format': 'json'}
    try:
        req = requests.get(config.geocoding['geocoding_api'], params=payload)
        result = req.json()

        if not result:
            raise ValidationError(f'no coordinates found for the given address {address}')

        return float(result[0]['lon']), float(result[0]['lat'])
    except ValidationError as exception:
        raise exception
    except Exception as exception:
        msg = f'geocoding is not running correctly: {exception}'
        logger.error(msg)
        raise ServiceError(msg) from None
