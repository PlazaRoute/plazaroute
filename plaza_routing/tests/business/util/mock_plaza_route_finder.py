from tests.util import utils

import plaza_routing.business.walking_route_finder as walking_route_finder
import plaza_routing.business.public_transport_route_finder as public_transport_route_finder

import plaza_routing.integration.geocoding_service as geocoding_service


def mock_test_find_route(monkeypatch):
    monkeypatch.setattr(geocoding_service, 'geocode',
                        lambda destination_address: (47.38790425, 8.51976218438478))
    monkeypatch.setattr(walking_route_finder, 'get_walking_route',
                        lambda start, destination:
                        _mock_test_find_route_get_walking_route(start, destination))
    monkeypatch.setattr(public_transport_route_finder, 'get_public_transport_stops',
                        lambda start:
                        _mock_test_find_route_get_public_transport_stops(start))
    monkeypatch.setattr(public_transport_route_finder, 'get_public_transport_route',
                        lambda start, destination, departure:
                        _mock_test_find_route_get_public_transport_route(start))
    monkeypatch.setattr(public_transport_route_finder, 'get_start_position',
                        lambda public_transport_route:
                        _mock_test_find_route_get_start_position(public_transport_route))
    monkeypatch.setattr(public_transport_route_finder, 'get_destination_position',
                        lambda public_transport_route:
                        _mock_test_find_route_get_destination_position(public_transport_route))


def mock_test_find_route_only_walking(monkeypatch):
    monkeypatch.setattr(geocoding_service, 'geocode',
                        lambda destination_address: (47.4109266, 8.5510247))
    monkeypatch.setattr(walking_route_finder, 'get_walking_route',
                        lambda start, destination:
                        _mock_test_find_route_only_walking_get_walking_route(start, destination))


def _mock_test_find_route_get_walking_route(start, destination):
    file_name = ''

    # overall walking route from 47.41071, 8.55546 to Zürich, Hardbrücke
    if start == (47.41071, 8.55546) and destination == (47.38790425, 8.51976218438478):
        file_name = '47_41071_8_55546_to_47_38790425_8_51976218438478.json'

    # start walking route from 47.41071, 8.55546 to the following public transport stops
    if start == (47.41071, 8.55546):
        # Zürich, Messe/Hallenstadion
        if destination == (47.4106724, 8.5520512):
            file_name = '47_41071_8_55546_to_messe_hallenstadion.json'
        # Zürich, Hallenbad Oerlikon
        elif destination == (47.4107529, 8.5554806):
            file_name = '47_41071_8_55546_to_hallenbad_oerlikon.json'
        # Zürich, Riedgraben
        elif destination == (47.4108265, 8.5592585):
            file_name = '47_41071_8_55546_to_riedgraben.json'
        # Zürich, Riedbach
        elif destination == (47.414522, 8.5584518):
            file_name = '47_41071_8_55546_to_riedbach.json'
        # Zürich, Leutschenbach
        elif destination == (47.4145557, 8.5511875):
            file_name = '47_41071_8_55546_to_leutschenbach.json'
        # Zürich, Hagenholz
        elif destination == (47.41446, 8.55528):
            file_name = '47_41071_8_55546_to_hagenholz.json'

    # end walking leg from Zürich, Hardbrücke on different tracks to 47.38790425, 8.51976218438478
    if destination == (47.38790425, 8.51976218438478):
        # arriving from Zürich, Hallenbad Oerlikon, Zürich, Leutschenbach,
        # Zürich, Messe/Hallenstadion and Zürich, Riedgraben on track 2
        if start == (47.385087296919714, 8.51768587257564):
            file_name = 'hardbruecke_track2_to_47_38790425_8_51976218438478.json'
        # arriving from Zürich, Riedbach, Zürich, Hagenholz on track 3
        elif start == (47.3851609, 8.5173926):
            file_name = 'hardbruecke_track3_to_47_38790425_8_51976218438478.json'

    return utils.get_json_file(file_name, 'walking_route')


def _mock_test_find_route_only_walking_get_walking_route(start, destination):
    file_name = ''
    if start == (47.41071, 8.55546):
        #  Zürich, Messe/Hallenstadion
        if destination == (47.4109266, 8.5510247):
            file_name = '47_41071_8_55546_to_messe_hallenstadion_only_walking.json'

    return utils.get_json_file(file_name, 'walking_route')


def _mock_test_find_route_get_public_transport_stops(start):
    if start == (47.41071, 8.55546):
        return {'Zürich, Messe/Hallenstadion', 'Zürich, Hallenbad Oerlikon',
                'Zürich, Riedgraben', 'Zürich, Riedbach',
                'Zürich, Leutschenbach', 'Zürich, Hagenholz'}
    assert False


def _mock_test_find_route_get_public_transport_route(public_transport_stop):
    file_name = ''

    if public_transport_stop == 'Zürich, Messe/Hallenstadion':
        file_name = 'messe_hallenstadion_hardbruecke.json'
    elif public_transport_stop == 'Zürich, Hallenbad Oerlikon':
        file_name = 'hallenbad_oerlikon_hardbruecke.json'
    elif public_transport_stop == 'Zürich, Riedgraben':
        file_name = 'riedgraben_hardbruecke.json'
    elif public_transport_stop == 'Zürich, Riedbach':
        file_name = 'riedbach_hardbruecke.json'
    elif public_transport_stop == 'Zürich, Leutschenbach':
        file_name = 'leutschenbach_hardbruecke.json'
    elif public_transport_stop == 'Zürich, Hagenholz':
        file_name = 'hagenholz_hardbruecke.json'

    return utils.get_json_file(file_name, 'public_transport_route')


def _mock_test_find_route_get_start_position(public_transport_route):
    if public_transport_route['path'][0]['name'] == 'Zürich, Messe/Hallenstadion':
        return 47.4106724, 8.5520512
    elif public_transport_route['path'][0]['name'] == 'Zürich, Hallenbad Oerlikon':
        return 47.4107529, 8.5554806
    elif public_transport_route['path'][0]['name'] == 'Zürich, Riedgraben':
        return 47.4108265, 8.5592585
    elif public_transport_route['path'][0]['name'] == 'Zürich, Riedbach':
        return 47.414522, 8.5584518
    elif public_transport_route['path'][0]['name'] == 'Zürich, Leutschenbach':
        return 47.4145557, 8.5511875
    elif public_transport_route['path'][0]['name'] == 'Zürich, Hagenholz':
        return 47.41446, 8.55528
    assert False


def _mock_test_find_route_get_destination_position(public_transport_route):
    if public_transport_route['path'][0]['name'] == 'Zürich, Messe/Hallenstadion':
        return 47.385087296919714, 8.51768587257564
    elif public_transport_route['path'][0]['name'] == 'Zürich, Hallenbad Oerlikon':
        return 47.385087296919714, 8.51768587257564
    elif public_transport_route['path'][0]['name'] == 'Zürich, Riedgraben':
        return 47.385087296919714, 8.51768587257564
    elif public_transport_route['path'][0]['name'] == 'Zürich, Riedbach':
        return 47.3851609, 8.5173926
    elif public_transport_route['path'][0]['name'] == 'Zürich, Leutschenbach':
        return 47.385087296919714, 8.51768587257564
    elif public_transport_route['path'][0]['name'] == 'Zürich, Hagenholz':
        return 47.3851609, 8.5173926
    assert False
