from tests.util import utils

from plaza_routing import config
from plaza_routing.integration import search_ch_service


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
