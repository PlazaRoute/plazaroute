from plaza_routing.integration import geocoding_service, overpass_service, search_ch_service


def test_geocoding_service_health():
    response = geocoding_service.geocode('Oberseestrasse 10, Rapperswil-Jona')
    assert response is not None
    assert isinstance(response, tuple)
    assert all(response)


def test_overpass_service_health():
    response = overpass_service.get_public_transport_stops((8.5458, 47.3661))
    assert response is not None
    assert isinstance(response, dict)
    assert all(value for value in response.values())


def test_search_ch_service_health():
    response = search_ch_service.get_connection('Zürich, Sternen Oerlikon',
                                                'Zürich, Messe/Hallenstadion',
                                                '14:11')
    assert response is not None
    assert isinstance(response, dict)
    assert all(value for value in response.values())
