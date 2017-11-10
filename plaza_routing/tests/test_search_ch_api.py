import pytest

from plaza_routing.external_service import search_ch_api


def test_get_connection():
    connection = search_ch_api.get_connection('Zürich, Sternen Oerlikon',
                                              'Zürich, Messe/Hallenstadion',
                                              '14:11')
    assert connection is not None
    assert connection['from'] == 'Zürich, Sternen Oerlikon'
    assert connection['to'] == 'Zürich, Messe/Hallenstadion'
    assert len(connection['legs']) == 2
    assert connection['number_of_legs'] == 2

    # last leg should be a final station or an address without an exit
    assert connection['legs'][1]['exit'] == []


def test_get_connection_empty_input():
    with pytest.raises(ValueError):
        search_ch_api.get_connection('', '', '')


def test_get_connection_invalid_time():
    with pytest.raises(ValueError):
        search_ch_api.get_connection('Zürich, Sternen Oerlikon',
                                     'Zürich, Messe/Hallenstadion',
                                     '07/00')
