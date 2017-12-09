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


def _mock_value_in_dict(old_dict, key, new_value):
    dict_copy = dict(old_dict)
    dict_copy[key] = new_value
    return dict_copy
