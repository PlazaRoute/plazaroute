import pytest
import os

from plaza_routing.integration.util import search_ch_parser
from plaza_routing.business import public_transport_service


def test_get_path_for_public_transport_connection_single_leg():
    expected_response = {
        'type': 'public_transport',
        'duration': 180,
        'number_of_legs': 1,
        'path': [{
                    'name': 'Zürich, Rote Fabrik',
                    'line_type': 'bus',
                    'line': '161',
                    'destination': 'Zürich, Stadtgrenze',
                    'terminal': 'Kilchberg ZH, Kirche',
                    'arrival': '2017-11-12 13:38:00',
                    'departure': '2017-11-12 13:35:00',
                    'start_position': [47.3424624, 8.5362646],
                    'exit_position': [47.3349277, 8.5416616]
                }]
    }

    search_ch_response_path = os.path.dirname(__file__)
    search_ch_response_file = os.path.join(search_ch_response_path, '../resources/search_ch_response_single_leg.json')
    search_ch_response = open(search_ch_response_file, 'r').read()
    parsed_response = search_ch_parser.parse_connections(search_ch_response)

    actual_response = public_transport_service.get_path_for_public_transport_connection(
        parsed_response['connections'][0])

    assert expected_response == actual_response


def test_get_path_for_public_transport_connection_filtered_walking_leg():
    expected_response = {
        'type': 'public_transport',
        'duration': 840,
        'number_of_legs': 1,
        'path': [{
                    'name': 'Zürich, Post Wollishofen',
                    'line_type': 'tram',
                    'line': '7',
                    'destination': 'Zürich Enge, Bahnhof',
                    'terminal': 'Stettbach, Bahnhof',
                    'arrival': '2017-11-12 13:56:00',
                    'departure': '2017-11-12 13:50:00',
                    'start_position': [47.3448353, 8.5333468],
                    'exit_position': [47.3643805, 8.5314319]  # TODO check
                }]
    }

    search_ch_response_path = os.path.dirname(__file__)
    search_ch_response_file = os.path.join(search_ch_response_path,
                                           '../resources/search_ch_response_walking_leg.json')
    search_ch_response = open(search_ch_response_file, 'r').read()
    parsed_response = search_ch_parser.parse_connections(search_ch_response)

    actual_response = public_transport_service.get_path_for_public_transport_connection(
        parsed_response['connections'][0])

    assert expected_response == actual_response


def test_get_path_for_public_transport_connection_multiple_leg():
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
                    'arrival': '2017-11-12 14:13:00',
                    'departure': '2017-11-12 14:07:00',
                    'start_position': [47.338911019762165, 8.53813643293702],
                    'exit_position': [47.36338051530903, 8.535039877782896]
                },
                {
                    'name': 'Zürich, Rentenanstalt',
                    'line_type': 'tram',
                    'line': '5',
                    'destination': 'Zürich Enge, Bahnhof',
                    'terminal': 'Zürich Enge, Bahnhof',
                    'arrival': '2017-11-12 14:21:00',
                    'departure': '2017-11-12 14:19:00',
                    'start_position': [47.3634496, 8.5345504],
                    'exit_position': [47.3640971, 8.5314535]
                }]
    }

    search_ch_response_path = os.path.dirname(__file__)
    search_ch_response_file = os.path.join(search_ch_response_path,
                                           '../resources/search_ch_response_multiple_legs.json')
    search_ch_response = open(search_ch_response_file, 'r').read()
    parsed_response = search_ch_parser.parse_connections(search_ch_response)

    actual_response = public_transport_service.get_path_for_public_transport_connection(
        parsed_response['connections'][0])

    assert expected_response == actual_response
