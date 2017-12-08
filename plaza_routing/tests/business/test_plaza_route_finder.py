from tests.util import utils
from tests.business.util import mock_plaza_route_finder as mock

from plaza_routing.business import plaza_route_finder


def test_find_route(monkeypatch):
    """ tests the route from 8.55546, 47.41071 to Zürich, Hardbrücke """
    mock.mock_test_find_route(monkeypatch)

    expected_response = utils.get_json_file('find_route_expected_result.json')
    assert expected_response == plaza_route_finder.find_route('8.55546, 47.41071', 'Zürich, Hardbrücke',
                                                              '14:42', True)


def test_find_route_only_walking(monkeypatch):
    """
    Tests the route from  8.55546, 47.41071 to Zürich, Messe/Hallenstadion.
    The destination is in walking distance thus only a walking route should be returned.
    """
    mock.mock_test_find_route_only_walking(monkeypatch)

    expected_response = utils.get_json_file('find_route_only_walking_expected_result.json')
    assert expected_response == plaza_route_finder.find_route('8.55546, 47.41071', 'Zürich, Messe/Hallenstadion',
                                                              '14:42', True)


def test_calc_public_transport_departure(monkeypatch):
    """
    It takes 609 seconds to get from 8.55546, 47.41071 to 8.55528, 47.41446,
    thus 609 seconds will be added to the provided departure time.
    """
    mock.mock_test_find_route(monkeypatch)
    departure = plaza_route_finder._calc_public_transport_departure('14:42', (8.55546, 47.41071), (8.55528, 47.41446))
    assert '14:52' == departure


def test_find_route_walking_faster(monkeypatch):
    """
    Tests the route from 8.54556659082, 47.3659258552 to Zürich, Kreuzplatz.
    The destination is not in walking distance but walking is faster than waiting for and taking the public transport.
    """
    mock.mock_test_find_route_walking_faster(monkeypatch)
    expected_response = utils.get_json_file('find_route_walking_faster_result.json')
    assert expected_response == plaza_route_finder.find_route('8.54556659082, 47.3659258552', 'Zürich, Kreuzplatz',
                                                              '14:42', False)
