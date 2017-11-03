import pytest
from plaza_routing import overpass_api


def test_get_public_transport_stops():
    expected_response = set(['Zürich, Kreuzstrasse', 'Zürich, Opernhaus', 'Zürich, Bürkliplatz',
                             'Zürich, Kunsthaus', 'Zürich Stadelhofen FB', 'Zürich, Bellevue',
                             'Zürich Stadelhofen', 'Zürich, Helmhaus'])
    sechselaeutenplatz = {
            'latitude': 47.3661,
            'longitude': 8.5458
    }
    stops = overpass_api.get_public_transport_stops(
        sechselaeutenplatz['latitude'], sechselaeutenplatz['longitude'])
    assert expected_response == stops


def test_get_public_transport_stops_empty_result():
    obersee = {
            'latitude': 47.2100,
            'longitude': 8.8249
    }
    with pytest.raises(ValueError):
        overpass_api.get_public_transport_stops(obersee['latitude'], obersee['longitude'])


def test_get_initial_public_transport_stop_position():
    """
    To get from Zürich, Messe/Hallenstadion to Zürich, Sternen Oerlikon you have to take
    the bus with the number 94 that travels from Zentrum Glatt to Zürich, Bahnhof Oerlikon
    at a specific public transport stop (node with id 701735028 and (47,4106724, 8,5520512)).

    Public transport stops at Zürich, Messe/Hallenstadion have the uic_ref 8591273.
    Public transport stops at Zürich, Sternen Oerlikon have the uic_ref 8591382.
    """
    current_location = (47.41077, 8.55240)
    bus_number = '94'
    start_stop_uicref = '8591273'
    exit_stop_uicref = '8591382'
    stop_position = overpass_api.get_initial_public_transport_stop_position(current_location,
                                                                            bus_number,
                                                                            start_stop_uicref,
                                                                            exit_stop_uicref)
    assert (47.4106724, 8.5520512) == stop_position


def test_get_initial_public_transport_stop_position_other_direction():
    """
    Same as test_get_initial_public_transport_stop_position() but in the other
    direction of travel (from Zürich, Messe/Hallenstadion to Zürich, Hallenbad Oerlikon).
    Should return the public transport stop on the other side of the street
    as in test_get_initial_public_transport_stop_position().

    Public transport stops at Zürich, Messe/Hallenstadion have the uic_ref 8591273.
    Public transport stops at Zürich, Hallenbad Oerlikon have the uic_ref 8591175.
    """
    current_location = (47.41077, 8.55240)
    bus_number = '94'
    start_stop_uicref = '8591273'
    exit_stop_uicref = '8591175'
    stop_position = overpass_api.get_initial_public_transport_stop_position(current_location,
                                                                            bus_number,
                                                                            start_stop_uicref,
                                                                            exit_stop_uicref)
    assert (47.4107102, 8.5528703) == stop_position


def test_get_initial_public_transport_stop_position_end_terminal():
    """
    Terminals have usually the nature that both direction of travel
    are served from the same stop.

    Public transport stops at Zürich, Sternen Oerlikon have the uic_ref 8591382.
    Public transport stops at Zürich, Bahnhof Oerlikon have the uic_ref 8580449.
    """
    current_location = (47.41025, 8.54679)
    bus_number = '94'
    start_stop_uicref = '8591382'
    exit_stop_uicref = '8580449'
    stop_position = overpass_api.get_initial_public_transport_stop_position(current_location,
                                                                            bus_number,
                                                                            start_stop_uicref,
                                                                            exit_stop_uicref)
    assert (47.4102250, 8.5467743) == stop_position


def test_get_initial_public_transport_stop_position_start_terminal():
    """
    Same as test_get_initial_public_transport_stop_position_end_terminal
    but with a terminal (Zürich, Bahnhof Oerlikon) a initial stop position.

    Public transport stops at Zürich, Bahnhof Oerlikon have the uic_ref 8580449.
    Public transport stops at Zürich, Sternen Oerlikon have the uic_ref 8591382.
    """
    current_location = (47.41142, 8.54466)
    bus_number = '94'
    start_stop_uicref = '8580449'
    exit_stop_uicref = '8591382'
    stop_position = overpass_api.get_initial_public_transport_stop_position(current_location,
                                                                            bus_number,
                                                                            start_stop_uicref,
                                                                            exit_stop_uicref)
    assert (47.4114541, 8.5447442) == stop_position
