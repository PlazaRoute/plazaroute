from tests.util import utils
from tests.business.util import mock_plaza_route_finder as mock

from plaza_routing.business import plaza_route_finder


def test_find_route(monkeypatch):
    """ tests the route from 47.41071, 8.55546 to Zürich, Hardbrücke """
    mock.mock_test_find_route(monkeypatch)

    expected_response = utils.get_json_file('find_route_expected_result.json')
    assert expected_response == plaza_route_finder.find_route('47.41071, 8.55546', 'Zürich, Hardbrücke', '14:42')


def test_find_route_only_walking(monkeypatch):
    """
    Tests the route from  47.41071, 8.55546 to Zürich, Messe/Hallenstadion.
    The destination is in walking distance thus only a walking route should be returned.
    """
    mock.mock_test_find_route_only_walking(monkeypatch)

    expected_response = utils.get_json_file('find_route_only_walking_expected_result.json')
    assert expected_response == plaza_route_finder.find_route('47.41071, 8.55546', 'Zürich, Messe/Hallenstadion',
                                                              '14:42')
