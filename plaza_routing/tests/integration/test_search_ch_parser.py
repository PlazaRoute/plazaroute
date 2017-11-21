import pytest

from tests.util import utils

from plaza_routing.integration.util import search_ch_parser


def test_parse_connections():
    search_ch_response = utils.get_file('search_ch_response.json', 'search_ch')
    parsed_response = search_ch_parser.parse_connections(search_ch_response)
    # a walking leg and the last one will be skipped
    assert parsed_response['connections'][0]['number_of_legs'] == 2


def test_parse_connections_empty_reponse():
    with pytest.raises(ValueError):
        search_ch_parser.parse_connections('')


def test_parse_connections_invalid_response():
    with pytest.raises(RuntimeError):
        search_ch_response = utils.get_file('search_ch_invalid_response.json', 'search_ch')
        search_ch_parser.parse_connections(search_ch_response)


def test_parse_connection_address_as_destination():
    search_ch_response = utils.get_file('search_ch_response_address_destination.json', 'search_ch')
    parsed_response = search_ch_parser.parse_connections(search_ch_response)
    # two walking legs and the last one will be skipped
    assert parsed_response['connections'][0]['number_of_legs'] == 3


def test_parse_connection_with_disruptions():
    search_ch_response = utils.get_file('search_ch_response_disruptions.json', 'search_ch')
    parsed_response = search_ch_parser.parse_connections(search_ch_response)
    # two walking legs and the last one will be skipped
    assert parsed_response['connections'][0]['number_of_legs'] == 3
