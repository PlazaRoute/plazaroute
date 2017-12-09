from plaza_routing import config


def mock_geocoding_unavailable_url(monkeypatch):
    monkeypatch.setattr(config, "geocoding",
                        _mock_value_in_dict(config.geocoding,
                                            "geocoding_api",
                                            "https://nominatim.offline.openstreetmap.org/search"))


def mock_geocoding_wrong_url(monkeypatch):
    monkeypatch.setattr(config, "geocoding",
                        _mock_value_in_dict(config.geocoding,
                                            "geocoding_api",
                                            "https://overpass.osm.ch/api/interpreter"))


def mock_search_ch_unavailable_url(monkeypatch):
    monkeypatch.setattr(config, "search_ch",
                        _mock_value_in_dict(config.search_ch,
                                            "search_ch_api",
                                            "https://timetable.offline.search.ch/api/route.json"))


def mock_search_ch_wrong_url(monkeypatch):
    monkeypatch.setattr(config, "search_ch",
                        _mock_value_in_dict(config.search_ch,
                                            "search_ch_api",
                                            "https://overpass.osm.ch/api/interpreter"))


def _mock_value_in_dict(old_dict: dict, key: str, new_value) -> dict:
    dict_copy = dict(old_dict)
    dict_copy[key] = new_value
    return dict_copy
