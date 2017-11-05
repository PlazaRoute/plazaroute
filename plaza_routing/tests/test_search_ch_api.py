import pytest
from plaza_routing import search_ch_api


def test_get_connection():
    connection = search_ch_api.get_connection('Sternen Oerlikon', 'Zürich Altstetten', '14:11')
    assert connection is not None
    assert connection['from'] == 'Zürich, Sternen Oerlikon'
    assert connection['to'] == 'Zürich Altstetten, Bahnhof'
    assert len(connection['legs']) == 4
    # last leg should be a final station or an address without an exit
    assert connection['legs'][3]['exit'] == []


def test_get_connection_empty_input():
    with pytest.raises(ValueError):
        search_ch_api.get_connection('', '', '')


def test_get_connection_invalid_time():
    with pytest.raises(ValueError):
        search_ch_api.get_connection('Sternen Oerlikon', 'Altstetten', '07/00')
