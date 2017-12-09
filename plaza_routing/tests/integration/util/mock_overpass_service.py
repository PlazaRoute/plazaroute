import overpy


from plaza_routing.integration import overpass_service


def mock_overpass_unavailable_url(monkeypatch):
    monkeypatch.setattr(overpass_service, "API",
                        _mock_overpy_api("https://overpass.offline.ch/api/interpreter"))


def mock_overpass_wrong_url(monkeypatch):
    monkeypatch.setattr(overpass_service, "API",
                        _mock_overpy_api("https://nominatim.openstreetmap.org/search"))


def _mock_overpy_api(new_url: str):
    return overpy.Overpass(url=new_url)
