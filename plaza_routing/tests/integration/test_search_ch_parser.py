import pytest

from tests.util import utils

from plaza_routing.integration.util import search_ch_parser


def test_parse_connections_empty_reponse():
    with pytest.raises(ValueError):
        search_ch_parser.parse_connections('')


def test_parse_connections_invalid_response():
    with pytest.raises(RuntimeError):
        search_ch_response = utils.get_file('search_ch_invalid_response.json', 'search_ch')
        search_ch_parser.parse_connections(search_ch_response)


def test_parse_connection_with_no_timetables():
    with pytest.raises(RuntimeError):
        search_ch_response = utils.get_file('search_ch_response_no_timetable_information.json', 'search_ch')
        search_ch_parser.parse_connections(search_ch_response)
