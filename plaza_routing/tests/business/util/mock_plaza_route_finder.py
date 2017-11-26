from tests.util import utils

import plaza_routing.business.walking_route_finder as walking_route_finder
import plaza_routing.business.public_transport_route_finder as public_transport_route_finder

import plaza_routing.integration.geocoding_service as geocoding_service


def mock_test_find_route(monkeypatch):
    monkeypatch.setattr(geocoding_service, 'geocode',
                        lambda destination_address: (8.51976218438478, 47.38790425))
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
                        lambda destination_address: (8.5510247, 47.4109266))
    monkeypatch.setattr(walking_route_finder, 'get_walking_route',
                        lambda start, destination:
                        _mock_test_find_route_only_walking_get_walking_route(start, destination))


def _mock_test_find_route_get_walking_route(start, destination):
    file_name = ''

    # overall walking route from 8.55546, 47.41071 to Zürich, Hardbrücke
    if start == (8.55546, 47.41071) and destination == (8.51976218438478, 47.38790425):
        file_name = '8_55546_47_41071_to_8_51976218438478_47_38790425.json'

    # start walking route from 8.55546, 47.41071 to the following public transport stops
    if start == (8.55546, 47.41071):
        # Zürich, Messe/Hallenstadion
        if destination == (8.5520512, 47.4106724):
            file_name = '8_55546_47_41071_to_messe_hallenstadion.json'
        # Zürich, Hallenbad Oerlikon
        elif destination == (8.5554806, 47.4107529):
            file_name = '8_55546_47_41071_to_hallenbad_oerlikon.json'
        # Zürich, Riedgraben
        elif destination == (8.5592585, 47.4108265):
            file_name = '8_55546_47_41071_to_riedgraben.json'
        # Zürich, Riedbach
        elif destination == (8.5584518, 47.414522):
            file_name = '8_55546_47_41071_to_riedbach.json'
        # Zürich, Leutschenbach
        elif destination == (8.5511875, 47.4145557):
            file_name = '8_55546_47_41071_to_leutschenbach.json'
        # Zürich, Hagenholz
        elif destination == (8.55528, 47.41446):
            file_name = '8_55546_47_41071_to_hagenholz.json'

    # end walking leg from Zürich, Hardbrücke on different tracks to 8.51976218438478, 47.38790425
    if destination == (8.51976218438478, 47.38790425):
        # arriving from Zürich, Hallenbad Oerlikon, Zürich, Leutschenbach,
        # Zürich, Messe/Hallenstadion and Zürich, Riedgraben on track 2
        if start == (8.51768587257564, 47.385087296919714):
            file_name = 'hardbruecke_track2_to_8_51976218438478_47_38790425.json'
        # arriving from Zürich, Riedbach, Zürich, Hagenholz on track 3
        elif start == (8.5173926, 47.3851609):
            file_name = 'hardbruecke_track3_to_8_51976218438478_47_38790425.json'

    return utils.get_json_file(file_name, 'walking_route')


def _mock_test_find_route_only_walking_get_walking_route(start, destination):
    file_name = ''
    if start == (8.55546, 47.41071):
        #  Zürich, Messe/Hallenstadion
        if destination == (8.5510247, 47.4109266):
            file_name = '8_55546_47_41071_to_messe_hallenstadion_only_walking.json'

    return utils.get_json_file(file_name, 'walking_route')


def _mock_test_find_route_get_public_transport_stops(start):
    if start == (8.55546, 47.41071):
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
        return 8.5520512, 47.4106724
    elif public_transport_route['path'][0]['name'] == 'Zürich, Hallenbad Oerlikon':
        return 8.5554806, 47.4107529
    elif public_transport_route['path'][0]['name'] == 'Zürich, Riedgraben':
        return 8.5592585, 47.4108265
    elif public_transport_route['path'][0]['name'] == 'Zürich, Riedbach':
        return 8.5584518, 47.414522
    elif public_transport_route['path'][0]['name'] == 'Zürich, Leutschenbach':
        return 8.5511875, 47.4145557
    elif public_transport_route['path'][0]['name'] == 'Zürich, Hagenholz':
        return 8.55528, 47.41446
    assert False


def _mock_test_find_route_get_destination_position(public_transport_route):
    if public_transport_route['path'][0]['name'] == 'Zürich, Messe/Hallenstadion':
        return 8.51768587257564, 47.385087296919714
    elif public_transport_route['path'][0]['name'] == 'Zürich, Hallenbad Oerlikon':
        return 8.51768587257564, 47.385087296919714
    elif public_transport_route['path'][0]['name'] == 'Zürich, Riedgraben':
        return 8.51768587257564, 47.385087296919714
    elif public_transport_route['path'][0]['name'] == 'Zürich, Riedbach':
        return 8.5173926, 47.3851609
    elif public_transport_route['path'][0]['name'] == 'Zürich, Leutschenbach':
        return 8.51768587257564, 47.385087296919714
    elif public_transport_route['path'][0]['name'] == 'Zürich, Hagenholz':
        return 8.5173926, 47.3851609
    assert False
