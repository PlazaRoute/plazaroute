from tests.business.util import mock_public_transport_route_finder as mock

from plaza_routing.business import public_transport_route_finder


def test_get_public_transport_route_single_leg(monkeypatch):
    mock.mock_test_get_public_transport_route(monkeypatch)

    expected_response = {
        'type': 'public_transport',
        'path': [{
            'name': 'Zürich, Rote Fabrik',
            'line_type': 'bus',
            'line': '161',
            'destination': 'Zürich, Stadtgrenze',
            'terminal': 'Kilchberg ZH, Kirche',
            'departure': '2017-11-12 13:35:00',
            'arrival': '2017-11-12 13:38:00',
            'start_position': [47.3424624, 8.5362646],
            'exit_position': [47.3349277, 8.5416616],
            'start_stop_uicref': '8587347',
            'exit_stop_uicref': '8591378'
        }],
        'duration': 180,
        'number_of_legs': 1
    }
    actual_response = public_transport_route_finder.get_public_transport_route('Zürich, Rote Fabrik',
                                                                               'Zürich, Stadtgrenze', '13:35')
    assert expected_response == actual_response


def test_get_public_transport_route_filtered_walking_leg(monkeypatch):
    mock.mock_test_get_public_transport_route(monkeypatch)

    expected_response = {
        'type': 'public_transport',
        'path': [{
            'name': 'Zürich, Post Wollishofen',
            'line_type': 'tram',
            'line': '7',
            'destination': 'Zürich Enge, Bahnhof',
            'terminal': 'Stettbach, Bahnhof',
            'departure': '2017-11-12 13:50:00',
            'arrival': '2017-11-12 13:56:00',
            'start_position': [47.3448353, 8.5333468],
            'exit_position': [47.3643805, 8.5314319],
            'start_stop_uicref': '8591304',
            'exit_stop_uicref': '8591058'
        }],
        'duration': 840,
        'number_of_legs': 1
    }
    actual_response = public_transport_route_finder.get_public_transport_route('Zürich, Rote Fabrik',
                                                                               'Zürich Enge, Bahnhof', '13:40')
    assert expected_response == actual_response


def test_get_public_transport_route_filtered_multiple_leg(monkeypatch):
    mock.mock_test_get_public_transport_route(monkeypatch)

    expected_response = {
        'type': 'public_transport',
        'duration': 840,
        'number_of_legs': 2,
        'path': [{
            'name': 'Zürich, Seerose',
            'line_type': 'bus',
            'line': '161',
            'destination': 'Zürich, Rentenanstalt',
            'terminal': 'Zürich, Bürkliplatz',
            'departure': '2017-11-12 14:07:00',
            'arrival': '2017-11-12 14:13:00',
            'start_position': [47.338911019762165, 8.53813643293702],
            'exit_position': [47.36338051530903, 8.535039877782896],
            'start_stop_uicref': '8591357',
            'exit_stop_uicref': '8591317'
        },
        {
            'name': 'Zürich, Rentenanstalt',
            'line_type': 'tram',
            'line': '5',
            'destination': 'Zürich Enge, Bahnhof',
            'terminal': 'Zürich Enge, Bahnhof',
            'departure': '2017-11-12 14:19:00',
            'arrival': '2017-11-12 14:21:00',
            'start_position': [47.3634496, 8.5345504],
            'exit_position': [47.3640971, 8.5314535],
            'start_stop_uicref': '8591317',
            'exit_stop_uicref': '8591058'
        }]
    }

    actual_response = public_transport_route_finder.get_public_transport_route('Zürich, Seerose',
                                                                               'Zürich Enge, Bahnhof', '14:07')
    assert expected_response == actual_response