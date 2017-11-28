import pytest

from plaza_routing.integration import overpass_service


def test_get_public_transport_stops():
    expected_response = {'8503003', '8503059', '8576193', '8576195',
                         '8576196', '8591105', '8591183', '8591239'}

    sechselaeutenplatz = (8.5458, 47.3661)
    stops = overpass_service.get_public_transport_stops(sechselaeutenplatz)
    assert expected_response == stops


def test_get_public_transport_stops_empty_result():
    obersee = (8.8249, 47.2100)
    with pytest.raises(ValueError):
        overpass_service.get_public_transport_stops(obersee)


def test_get_public_transport_stops_highway_bus_stops():
    expected_response = {'8503156', '8576139', '8588096', '8590851', '8589106'}
    zimikon = (8.67263, 47.38516)
    stops = overpass_service.get_public_transport_stops(zimikon)
    assert expected_response == stops


def test_get_public_transport_stops_nodes_without_uic_ref():
    """" nodes without uic_refs should be discarded, they are ususally part of a relation"""
    expected_response = {'8503006', '8580449', '8591062', '8591063',
                         '8591112', '8591256', '8591273', '8591332', '8591382'}

    oerlikon_sternen = (8.54679, 47.41025)
    stops = overpass_service.get_public_transport_stops(oerlikon_sternen)
    assert stops == expected_response


def test_get_start_exit_stop_position():
    """
    To get from Zürich, Messe/Hallenstadion to Zürich, Sternen Oerlikon you have to take
    the bus with the number 94 that travels from Zentrum Glatt to Zürich, Bahnhof Oerlikon
    at a specific start public transport stop (node with id 701735028 and (8,5520512, 47,4106724)).

    Public transport stops at Zürich, Messe/Hallenstadion have the uic_ref 8591273.
    Public transport stops at Zürich, Sternen Oerlikon have the uic_ref 8591382.
    """
    current_location = (8.55240, 47.41077)
    fallback_start_position = (1, 1)  # irrelevant and will not be used
    fallback_exit_position = (1, 1)  # irrelevant and will not be used
    start_stop_uicref = '8591273'
    exit_stop_uicref = '8591382'
    bus_number = '94'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      bus_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (8.5520512, 47.4106724) == start_position
    assert (8.5467743, 47.4102250) == exit_position


def test_get_start_exit_stop_position_other_direction():
    """
    Same as test_get_start_exit_stop_position() but in the other
    direction of travel (from Zürich, Messe/Hallenstadion to Zürich, Hallenbad Oerlikon).
    Should return the start public transport stop on the other side of the street
    as in test_get_start_exit_stop_position().

    Public transport stops at Zürich, Messe/Hallenstadion have the uic_ref 8591273.
    Public transport stops at Zürich, Hallenbad Oerlikon have the uic_ref 8591175.
    """
    current_location = (8.55240, 47.41077)
    fallback_start_position = (1, 1)
    fallback_exit_position = (1, 1)
    start_stop_uicref = '8591273'
    exit_stop_uicref = '8591175'
    bus_number = '94'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      bus_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (8.5528703, 47.4107102) == start_position
    assert (8.5562254, 47.4107647) == exit_position


def test_get_start_exit_stop_position_end_terminal():
    """
    Terminals have usually the nature that both direction of travel
    are served from the same stop.

    Public transport stops at Zürich, Sternen Oerlikon have the uic_ref 8591382.
    Public transport stops at Zürich, Bahnhof Oerlikon have the uic_ref 8580449.
    """
    current_location = (8.54679, 47.41025)
    fallback_start_position = (1, 1)
    fallback_exit_position = (1, 1)
    start_stop_uicref = '8591382'
    exit_stop_uicref = '8580449'
    bus_number = '94'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      bus_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (8.5467743, 47.4102250) == start_position
    assert (8.5447442, 47.4114541) == exit_position


def test_get_start_exit_stop_position_start_terminal():
    """
    Same as test_get_start_exit_stop_position_end_terminal
    but with a terminal (Zürich, Bahnhof Oerlikon) as an start stop position.

    Public transport stops at Zürich, Bahnhof Oerlikon have the uic_ref 8580449.
    Public transport stops at Zürich, Sternen Oerlikon have the uic_ref 8591382.
    """
    current_location = (8.54466, 47.41142)
    fallback_start_position = (1, 1)
    fallback_exit_position = (1, 1)
    start_stop_uicref = '8580449'
    exit_stop_uicref = '8591382'
    bus_number = '94'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      bus_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (8.5447442, 47.4114541) == start_position
    assert (8.5468917, 47.4102351) == exit_position


def test_get_start_exit_stop_position_fallback():
    """
    Start and exit stop position for the line 161 to get from Zürich, Rote Fabrik to Zürich, Seerose.

    Both stops do not provide an uic_ref so the fallback method will be used
    to determine the start and exit public transport stop position.
    """
    current_location = (8.53608, 47.34252)
    fallback_start_position = (1, 1)
    fallback_exit_position = (1, 1)
    start_stop_uicref = '8587347'
    exit_stop_uicref = '8591357'
    bus_number = '161'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      bus_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (8.5362646, 47.3424624) == start_position
    assert (8.5383397, 47.3385962) == exit_position


def test_get_start_exit_stop_position_corrupt_relation():
    """
    Start and exit stop position for the line S6 to get from Zürich, Bahnhof Oerlikon to Zürich, Hardbrücke.
    The stop in Zürich, Bahnhof Oerlikon does not provide an uic_ref for the line S6.
    The fallback method will be used in this case.

    The relation for the S6 is wrongly (order of nodes is not correct) mapped and the fallback method will fail too.
    Thus the last option is chosen and the fallback positions will be returned.

    Public transport stops at Zürich, Bahnhof Oerlikon have the uic_ref 8503006.
    Public transport stops at Zürich, Hardbrücke have the uic_ref 8503020.
    """
    current_location = (8.54644, 47.41012)
    fallback_start_position = (8.544113562238525, 47.41152601531714)
    fallback_exit_position = (8.51768587257564, 47.385087296919714)
    start_stop_uicref = '8503006'
    exit_stop_uicref = '8503020'
    train_number = 'S6'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      train_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (8.544113562238525, 47.41152601531714) == start_position
    assert (8.51768587257564, 47.385087296919714) == exit_position


def test_get_start_exit_stop_position_relation_without_uic_ref():
    """
    Start node has an uic_ref, the exit node however does not hold one. The first retrieval method fill fail
    because of this. For the exit node it is not possible to retrieve relations based on the exit_uic_ref because there
    does not exist a relation with it. Thus the last option is chosen and the fallback positions will be
    returned.
    """
    current_location = (8.66724, 47.38510)
    fallback_start_position = (8.659549027875455, 47.383981347638574)
    fallback_exit_position = (8.668385753719784, 47.38524594245153)
    start_stop_uicref = '8576139'
    exit_stop_uicref = '8576127'
    bus_number = '720'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      bus_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (8.659549027875455, 47.383981347638574) == start_position
    assert (8.668385753719784, 47.38524594245153) == exit_position


def test_get_start_exit_stop_position_empty_result():
    """ an empty result set is returned by the Overpass queries based on provided parameters """
    current_location = (8.53531, 47.36343)
    fallback_start_position = (1, 1)
    fallback_exit_position = (1, 1)
    start_stop_uicref = '8591317'
    exit_stop_uicref = '8591058'
    tram_number = '23'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      tram_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (1, 1) == start_position
    assert (1, 1) == exit_position


def test_get_start_exit_stop_position_multiple_relations_for_line():
    """
    Tram 5 has multiple lines with different terminals that serve the stop Zürich, Rentenanstalt
    to Zürich, Bahnhof Enge. All lines are a possible option and all start from the same stop.
    """
    current_location = (8.53528, 47.36331)
    fallback_start_position = (1, 1)
    fallback_exit_position = (1, 1)
    start_stop_uicref = '8591317'
    exit_stop_uicref = '8591058'
    tram_number = '5'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      tram_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (8.5345459, 47.3634506) == start_position
    assert (8.5314535, 47.3640971) == exit_position


def test_get_start_exit_stop_position_multiple_relations_for_line_one_option():
    """
    Tram 5 has multiple lines with different terminals that serve the stop Zürich, Rentenanstalt
    to Zürich, Bahnhof Enge. But to get from Zürich, Rentenanstalt to Bahnhof Enge/Bederstrasse
    just on line is a possible option.
    """
    current_location = (8.53528, 47.36331)
    fallback_start_position = (1, 1)
    fallback_exit_position = (1, 1)
    start_stop_uicref = '8591317'
    exit_stop_uicref = '8591059'
    tram_number = '5'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      tram_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (8.5345459, 47.3634506) == start_position
    assert (8.5302541, 47.3645340) == exit_position
