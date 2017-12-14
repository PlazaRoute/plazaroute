from tests.util import utils

from plaza_routing import config
from plaza_routing.integration import search_ch_service


def mock_get_connection(monkeypatch):
    monkeypatch.setattr(search_ch_service, "_query",
                        lambda payload:
                        utils.get_file(_get_get_connection_filename(payload), 'search_ch'))


def _get_get_connection_filename(params):
    if params['from'] == 'Zürich, Sternen Oerlikon' and params['to'] == 'Zürich Altstetten':
        return 'search_ch_response.json'
    elif params['from'] == 'Zürich Hardbrücke' and params['to'] == 'Volketswil, Schwerzenbachstr. 16' \
            and params['time'] == '09:09':
        return 'search_ch_response_address_destination.json'
    elif params['from'] == 'Zürich Hardbrücke' and params['to'] == 'Volketswil, Schwerzenbachstr. 16' \
            and params['time'] == '08:09':
        return 'search_ch_response_disruptions.json'
    elif params['from'] == 'Zürich, Hallenstadionn' and params['to'] == 'Zürich, Messe/Hallenstadion':
        return 'search_ch_response_same_start_and_destination.json'


def mock_search_ch_unavailable_url(monkeypatch):
    monkeypatch.setattr(config, "search_ch",
                        utils.mock_value_in_dict(config.search_ch,
                                                 "search_ch_api",
                                                 "https://timetable.offline.search.ch/api/route.json"))


def mock_search_ch_wrong_url(monkeypatch):
    monkeypatch.setattr(config, "search_ch",
                        utils.mock_value_in_dict(config.search_ch,
                                                 "search_ch_api",
                                                 "https://overpass.osm.ch/api/interpreter"))
