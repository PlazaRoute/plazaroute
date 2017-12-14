from tests.util import utils

from plaza_routing import config
from plaza_routing.integration import geocoding_service


def mock_geocode(monkeypatch):
    monkeypatch.setattr(geocoding_service, "_query",
                        lambda payload:
                        utils.get_json_file(_get_geocode_filename(payload), 'geocoding'))


def _get_geocode_filename(params):
    if params['q'] == 'Oberseestrasse 10, Rapperswil-Jona':
        return 'geocoding.json'
    elif params['q'] == 'Hansmusterweg 14, Zürich':
        return 'geocoding_no_coordinates_found.json'
    elif params['q'] == 'Sir Matt Busby Way, Stretford, Manchester M16 0RA':
        return 'geocoding_outside_viewbox.json'


def mock_geocoding_unavailable_url(monkeypatch):
    monkeypatch.setattr(config, "geocoding",
                        utils.mock_value_in_dict(config.geocoding,
                                                 "geocoding_api",
                                                 "https://nominatim.offline.openstreetmap.org/search"))


def mock_geocoding_wrong_url(monkeypatch):
    monkeypatch.setattr(config, "geocoding",
                        utils.mock_value_in_dict(config.geocoding,
                                                 "geocoding_api",
                                                 "https://overpass.osm.ch/api/interpreter"))
