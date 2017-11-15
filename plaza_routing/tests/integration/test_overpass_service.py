import pytest

from plaza_routing.integration import overpass_service


def test_get_public_transport_stops():
    expected_response = {'Zürich, Kreuzstrasse', 'Zürich, Opernhaus', 'Zürich, Bürkliplatz',
                         'Zürich, Kunsthaus', 'Zürich Stadelhofen FB', 'Zürich, Bellevue',
                         'Zürich Stadelhofen', 'Zürich, Helmhaus'}
    sechselaeutenplatz = (47.3661, 8.5458)
    stops = overpass_service.get_public_transport_stops(sechselaeutenplatz)
    assert expected_response == stops


def test_get_public_transport_stops_empty_result():
    obersee = (47.2100, 8.8249)
    with pytest.raises(ValueError):
        overpass_service.get_public_transport_stops(obersee)


def test_get_public_transport_stops_highway_bus_stops():
    expected_response = {'Volketswil, Hofwisen', 'Volketswil, Chappeli', 'Volketswil, Hegnau',
                         'Volketswil, Zimikon', 'Volketswil, In der Höh'}
    zimikon = (47.38516, 8.67263)
    stops = overpass_service.get_public_transport_stops(zimikon)
    assert expected_response == stops


def test_get_start_exit_stop_position():
    """
    To get from Zürich, Messe/Hallenstadion to Zürich, Sternen Oerlikon you have to take
    the bus with the number 94 that travels from Zentrum Glatt to Zürich, Bahnhof Oerlikon
    at a specific start public transport stop (node with id 701735028 and (47,4106724, 8,5520512)).

    Public transport stops at Zürich, Messe/Hallenstadion have the uic_ref 8591273.
    Public transport stops at Zürich, Sternen Oerlikon have the uic_ref 8591382.
    """
    current_location = (47.41077, 8.55240)
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
    assert (47.4106724, 8.5520512) == start_position
    assert (47.4102250, 8.5467743) == exit_position


def test_get_start_exit_stop_position_other_direction():
    """
    Same as test_get_start_exit_stop_position() but in the other
    direction of travel (from Zürich, Messe/Hallenstadion to Zürich, Hallenbad Oerlikon).
    Should return the start public transport stop on the other side of the street
    as in test_get_start_exit_stop_position().

    Public transport stops at Zürich, Messe/Hallenstadion have the uic_ref 8591273.
    Public transport stops at Zürich, Hallenbad Oerlikon have the uic_ref 8591175.
    """
    current_location = (47.41077, 8.55240)
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
    assert (47.4107102, 8.5528703) == start_position
    assert (47.4107647, 8.5562254) == exit_position


def test_get_start_exit_stop_position_end_terminal():
    """
    Terminals have usually the nature that both direction of travel
    are served from the same stop.

    Public transport stops at Zürich, Sternen Oerlikon have the uic_ref 8591382.
    Public transport stops at Zürich, Bahnhof Oerlikon have the uic_ref 8580449.
    """
    current_location = (47.41025, 8.54679)
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
    assert (47.4102250, 8.5467743) == start_position
    assert (47.4114541, 8.5447442) == exit_position


def test_get_start_exit_stop_position_start_terminal():
    """
    Same as test_get_start_exit_stop_position_end_terminal
    but with a terminal (Zürich, Bahnhof Oerlikon) as an start stop position.

    Public transport stops at Zürich, Bahnhof Oerlikon have the uic_ref 8580449.
    Public transport stops at Zürich, Sternen Oerlikon have the uic_ref 8591382.
    """
    current_location = (47.41142, 8.54466)
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
    assert (47.4114541, 8.5447442) == start_position
    assert (47.4102351, 8.5468917) == exit_position


def test_get_start_exit_stop_position_fallback():
    """
    Start and exit stop position for the line 161 to get from Zürich, Rote Fabrik to Zürich, Seerose.

    Both stops do not provide an uic_ref so the fallback method will be used
    to determine the start and exit public transport stop position.
    """
    current_location = (47.34252, 8.53608)
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
    assert (47.3424624, 8.5362646) == start_position
    assert (47.3385962, 8.5383397) == exit_position


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
    current_location = (47.41012, 8.54644)
    fallback_start_position = (47.41152601531714, 8.544113562238525)
    fallback_exit_position = (47.385087296919714, 8.51768587257564)
    start_stop_uicref = '8503006'
    exit_stop_uicref = '8503020'
    train_number = 'S6'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      train_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (47.41152601531714, 8.544113562238525) == start_position
    assert (47.385087296919714, 8.51768587257564) == exit_position


def test_get_start_exit_stop_position_relation_without_uic_ref():
    """
    Start node does not have an uic_ref, the exit node however holds an uic_ref. The first retrieval method fill fail
    because of this. For the exit node it is not possible to retrieve relations based on the exit_uic_ref because there
    does not exist one with it. Thus the last option is chosen and the fallback positions will be
    returned.
    """
    current_location = (47.33937, 8.53810)
    fallback_start_position = (47.338911019762165, 8.53813643293702)
    fallback_exit_position = (47.36338051530903, 8.535039877782896)
    start_stop_uicref = '8591357'
    exit_stop_uicref = '8591317'
    bus_number = '161'
    start_position, exit_position = \
        overpass_service.get_start_exit_stop_position(current_location,
                                                      start_stop_uicref, exit_stop_uicref,
                                                      bus_number,
                                                      fallback_start_position,
                                                      fallback_exit_position)
    assert (47.338911019762165, 8.53813643293702) == start_position
    assert (47.36338051530903, 8.535039877782896) == exit_position


def test_get_start_exit_stop_position_empty_result():
    """ an empty result set is returned by the Overpass queries based on provided parameters """
    current_location = (47.36343, 8.53531)
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
    current_location = (47.36331, 8.53528)
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
    assert (47.3634496, 8.5345504) == start_position
    assert (47.3640971, 8.5314535) == exit_position


def test_get_start_exit_stop_position_multiple_relations_for_line_one_option():
    """
    Tram 5 has multiple lines with different terminals that serve the stop Zürich, Rentenanstalt
    to Zürich, Bahnhof Enge. But to get from Zürich, Rentenanstalt to Bahnhof Enge/Bederstrasse
    just on line is a possible option.
    """
    current_location = (47.36331, 8.53528)
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
    assert (47.3634496, 8.5345504) == start_position
    assert (47.3645340, 8.5302541) == exit_position
