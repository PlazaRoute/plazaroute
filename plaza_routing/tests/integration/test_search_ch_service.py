import pytest

from plaza_routing.integration import search_ch_service


def test_get_connection():
    connection = search_ch_service.get_connection('Zürich, Sternen Oerlikon',
                                                  'Zürich, Messe/Hallenstadion',
                                                  '14:11')
    assert connection is not None
    assert connection['from'] == 'Zürich, Sternen Oerlikon'
    assert connection['to'] == 'Zürich, Messe/Hallenstadion'
    assert len(connection['legs']) == 1
    assert connection['number_of_legs'] == 1


def test_get_connection_same_start_and_destination():
    with pytest.raises(RuntimeError):
        search_ch_service.get_connection('Zürich, Hallenstadionn',
                                         'Zürich, Messe/Hallenstadion',
                                         '07:00')
    # TODO should we handle this case with a dedicated validation before we pass the response to the parser
