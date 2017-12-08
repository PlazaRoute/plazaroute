from tests.business.util import mock_public_transport_connection_finder as mock

from plaza_routing.business import public_transport_connection_finder


def test_get_public_transport_connection_single_leg(monkeypatch):
    mock.mock_test_get_public_transport_connection(monkeypatch)

    expected_response = {
        'type': 'public_transport',
        'path': [{
            'name': 'Zürich, Rote Fabrik',
            'line_type': 'bus',
            'line': '161',
            'track': '',
            'destination': 'Zürich, Stadtgrenze',
            'terminal': 'Kilchberg ZH, Kirche',
            'departure': '2017-11-12 13:35:00',
            'arrival': '2017-11-12 13:38:00',
            'start_position': [8.536018254050866, 47.34272717279221],
            'exit_position': [8.541470480777495, 47.33503823573056],
            'start_stop_uicref': '8587347',
            'exit_stop_uicref': '8591378',
            'stopovers': [[8.53813643293702, 47.338911019762165]]
        }],
        'duration': 180,
        'number_of_legs': 1
    }
    actual_response = public_transport_connection_finder.get_public_transport_connection('8587347',
                                                                                         (8.5411959, 47.3353129),
                                                                                         '13:35')
    assert expected_response == actual_response


def test_get_public_transport_connection_filtered_walking_leg(monkeypatch):
    mock.mock_test_get_public_transport_connection(monkeypatch)

    expected_response = {
        'type': 'public_transport',
        'path': [{
            'name': 'Zürich, Post Wollishofen',
            'line_type': 'tram',
            'line': '7',
            'track': '',
            'destination': 'Zürich Enge, Bahnhof',
            'terminal': 'Stettbach, Bahnhof',
            'departure': '2017-11-12 13:50:00',
            'arrival': '2017-11-12 13:56:00',
            'start_position': [8.532957182471279, 47.34446532240397],
            'exit_position': [8.531573261985752, 47.36412398805734],
            'start_stop_uicref': '8591304',
            'exit_stop_uicref': '8591058',
            'stopovers': [[8.532917131553525, 47.3470293465808], [8.531975688485307, 47.35146391904956],
                          [8.53221694130198, 47.35613015465174], [8.531556360868755, 47.36071496835658]]
        }],
        'duration': 840,
        'number_of_legs': 1
    }
    actual_response = public_transport_connection_finder.get_public_transport_connection('8587347',
                                                                                         (8.5307605, 47.3641833),
                                                                                         '13:40')
    assert expected_response == actual_response


def test_get_public_transport_connection_filtered_multiple_leg(monkeypatch):
    mock.mock_test_get_public_transport_connection(monkeypatch)

    expected_response = {
        'type': 'public_transport',
        'duration': 840,
        'number_of_legs': 2,
        'path': [{
            'name': 'Zürich, Seerose',
            'line_type': 'bus',
            'line': '161',
            'track': '',
            'destination': 'Zürich, Rentenanstalt',
            'terminal': 'Zürich, Bürkliplatz',
            'departure': '2017-11-12 14:07:00',
            'arrival': '2017-11-12 14:13:00',
            'start_position': [8.53813643293702, 47.338911019762165],
            'exit_position': [8.535039877782896, 47.36338051530903],
            'start_stop_uicref': '8591357',
            'exit_stop_uicref': '8591317',
            'stopovers': [[8.536018254050866, 47.34272717279221], [8.53434462886726, 47.347582510434506],
                          [8.534229187336443, 47.35098380529947], [8.534296858420255, 47.354923072728766],
                          [8.53551062114295, 47.35987691121706]]
            },
            {
                'name': 'Zürich, Rentenanstalt',
                'line_type': 'tram',
                'line': '5',
                'track': '',
                'destination': 'Zürich Enge, Bahnhof',
                'terminal': 'Zürich Enge, Bahnhof',
                'departure': '2017-11-12 14:19:00',
                'arrival': '2017-11-12 14:21:00',
                'start_position': [8.535039877782896, 47.36338051530903],
                'exit_position': [8.531573261985752, 47.36412398805734],
                'start_stop_uicref': '8591317',
                'exit_stop_uicref': '8591058',
                'stopovers': []
            }]
    }

    actual_response = public_transport_connection_finder.get_public_transport_connection('8591357',
                                                                                         (8.5307605, 47.3641833),
                                                                                         '14:07')
    assert expected_response == actual_response
