import os

import pytest

from plaza_routing.integration.util import search_ch_parser


def test_parse_connections():
    search_ch_response_path = os.path.dirname(__file__)
    search_ch_response_file = os.path.join(search_ch_response_path,
                                           'resources/search_ch_response.json')
    search_ch_response = open(search_ch_response_file, 'r').read()
    search_ch_parser.parse_connections(search_ch_response)


def test_parse_connections_empty_reponse():
    with pytest.raises(ValueError):
        search_ch_parser.parse_connections('')


def test_parse_connections_invalid_response():
    with pytest.raises(RuntimeError):
        search_ch_response_path = os.path.dirname(__file__)
        search_ch_response_file = os.path.join(search_ch_response_path,
                                               'resources/search_ch_invalid_response.json')
        search_ch_response = open(search_ch_response_file, 'r').read()
        search_ch_parser.parse_connections(search_ch_response)
