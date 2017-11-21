import pytest

from plaza_routing.integration import geocoding_service


def test_geocoding():
    result = geocoding_service.geocode('Oberseestrasse 10, Rapperswil-Jona')
    assert (47.2229673, 8.816392) == result


def test_geocoding_no_coordinates_found():
    with pytest.raises(ValueError):
        geocoding_service.geocode('Hansmusterweg 14, Zürich')


def test_geocoding_outside_viewbox():
    with pytest.raises(ValueError):
        geocoding_service.geocode('Sir Matt Busby Way, Stretford, Manchester M16 0RA')
