import pytest
from plaza_routing import overpass_api


def test_get_public_transport_stops():
    sechselaeutenplatz = {
        'latitude': 47.3661,
        'longitude': 8.5458
    }
    overpass_api.get_public_transport_stops(
        sechselaeutenplatz['latitude'], sechselaeutenplatz['longitude'])
    assert True
