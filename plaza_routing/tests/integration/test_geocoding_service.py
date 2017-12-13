import pytest

from tests.integration.util import mock_config as mock

from plaza_routing.integration import geocoding_service
from plaza_routing.integration.util.exception_util import ValidationError, ServiceError


def test_geocoding():
    result = geocoding_service.geocode('Oberseestrasse 10, Rapperswil-Jona')
    assert result is not None
    assert isinstance(result, tuple)
    assert all(result)


def test_geocoding_no_coordinates_found():
    with pytest.raises(ValidationError):
        geocoding_service.geocode('Hansmusterweg 14, Zürich')


def test_geocoding_outside_viewbox():
    with pytest.raises(ValidationError):
        geocoding_service.geocode('Sir Matt Busby Way, Stretford, Manchester M16 0RA')


def test_geocoding_unavailable_service(monkeypatch):
    mock.mock_geocoding_unavailable_url(monkeypatch)
    with pytest.raises(ServiceError):
        geocoding_service.geocode('Oberseestrasse 10, Rapperswil-Jona')


def test_geocoding_breaking_changes(monkeypatch):
    """ uses different service to test breaking changes in the api """
    mock.mock_geocoding_wrong_url(monkeypatch)
    with pytest.raises(ServiceError):
        geocoding_service.geocode('Oberseestrasse 10, Rapperswil-Jona')
