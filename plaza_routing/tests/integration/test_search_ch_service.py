import pytest

from tests.integration.util import mock_search_ch_service as mock

from plaza_routing.integration import search_ch_service
from plaza_routing.integration.util.exception_util import ValidationError, ServiceError


def test_get_connection():
    connection = search_ch_service.get_connection('Zürich, Sternen Oerlikon',
                                                  'Zürich, Messe/Hallenstadion',
                                                  '14:11')
    assert connection is not None
    assert connection['from'] == 'Zürich, Sternen Oerlikon'
    assert connection['to'] == 'Zürich, Messe/Hallenstadion'
    assert len(connection['legs']) == 1
    assert connection['number_of_legs'] == 1


def test_get_connection_same_start_and_destination():
    with pytest.raises(ValidationError):
        search_ch_service.get_connection('Zürich, Hallenstadionn',
                                         'Zürich, Messe/Hallenstadion',
                                         '07:00')


def test_get_connection_unavailble_service(monkeypatch):
    mock.mock_search_ch_unavailable_url(monkeypatch)
    with pytest.raises(ServiceError):
        search_ch_service.get_connection('Zürich, Sternen Oerlikon',
                                         'Zürich, Messe/Hallenstadion',
                                         '14:11')


def test_get_connection_breaking_changes(monkeypatch):
    """ uses different service to test breaking changes in the api """
    mock.mock_search_ch_wrong_url(monkeypatch)
    with pytest.raises(ServiceError):
        search_ch_service.get_connection('Zürich, Sternen Oerlikon',
                                         'Zürich, Messe/Hallenstadion',
                                         '14:11')