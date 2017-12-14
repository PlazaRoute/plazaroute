import overpy

from tests.util import utils

from plaza_routing.integration import overpass_service


def mock_get_public_transport_stops_query(monkeypatch, current_location):
    api = overpy.Overpass()
    monkeypatch.setattr(overpass_service.API, "query",
                        lambda query: api.parse_json(
                            utils.get_file(_get_public_transport_stops_result_filename(current_location), 'overpass')))


def mock_get_connection_coordinates_query(monkeypatch, current_location, exit_uic_ref):
    api = overpy.Overpass()
    call_counter = 0  # is used to determine if a fallback method is querying overpass

    def mockreturn(current_location_inner, exit_uic_ref_inner, call_counter_inner):
        return api.parse_json(utils.get_file(
            _get_connection_coordinates_result_filename(current_location_inner, exit_uic_ref_inner, call_counter_inner),
            'overpass'))

    def wrapper(query):
        nonlocal call_counter
        call_counter += 1
        return mockreturn(current_location, exit_uic_ref, call_counter)

    monkeypatch.setattr(overpass_service.API, "query", wrapper)


def _get_public_transport_stops_result_filename(current_location):
    # files are named after the tests
    if current_location == (8.5458, 47.3661):
        return 'public_transport_stops.json'
    elif current_location == (8.8249, 47.2100):
        return 'public_transport_stops_empty_result.json'
    elif current_location == (8.67263, 47.38516):
        return 'public_transport_stops_highway_bus_stop.json'
    elif current_location == (8.54679, 47.41025):
        return 'public_transport_stops_nodes_without_uic_ref.json'


def _get_connection_coordinates_result_filename(current_location, exit_uic_ref, call_counter):
    # files are named after the tests
    if current_location == (8.55240, 47.41077) and exit_uic_ref == '8591382':
        return 'connection_coordinates.json'
    elif current_location == (8.55240, 47.41077) and exit_uic_ref == '8591175':
        return 'connection_coordinates_other_direction.json'
    elif current_location == (8.54679, 47.41025) and exit_uic_ref == '8580449':
        return 'connection_coordinates_end_terminal.json'
    elif current_location == (8.54466, 47.41142) and exit_uic_ref == '8591382':
        return 'connection_coordinates_start_terminal.json'
    elif current_location == (8.55283, 47.31044) and exit_uic_ref == '8590783' and call_counter == 1:
        return 'connection_coordinates_fallback_first_try.json'
    elif current_location == (8.55283, 47.31044) and exit_uic_ref == '8590783' and call_counter == 2:
        return 'connection_coordinates_fallback_second_try_start_stop_and_relation.json'
    elif current_location == (8.55283, 47.31044) and exit_uic_ref == '8590783' and call_counter == 3:
        return 'connection_coordinates_fallback_second_try_end_stop.json'
    elif current_location == (8.54644, 47.41012) and exit_uic_ref == '8503020' and call_counter == 1:
        return 'connection_coordinates_corrupt_relation_first_try.json'
    elif current_location == (8.54644, 47.41012) and exit_uic_ref == '8503020' and call_counter == 2:
        return 'connection_coordinates_corrupt_relation_second_try_start_stop_and_relation.json'
    elif current_location == (8.66724, 47.38510) and exit_uic_ref == '8576127' and call_counter == 1:
        return 'connection_coordinates_relation_without_uic_ref_first_try.json'
    elif current_location == (8.66724, 47.38510) and exit_uic_ref == '8576127' and call_counter == 2:
        return 'connection_coordinates_relation_without_uic_ref_second_try_start_stop_and_relation.json'
    elif current_location == (8.53531, 47.36343) and exit_uic_ref == '8591058' and call_counter == 1:
        return 'connection_coordinates_empty_result_first_try.json'
    elif current_location == (8.53531, 47.36343) and exit_uic_ref == '8591058' and call_counter == 2:
        return 'connection_coordinates_empty_result_second_try_start_stop_and_relation.json'
    elif current_location == (8.53528, 47.36331) and exit_uic_ref == '8591058':
        return 'connection_coordinates_multiple_relations_for_line.json'
    elif current_location == (8.53528, 47.36331) and exit_uic_ref == '8591059':
        return 'connection_coordinates_multiple_relations_for_line_one_option.json'
    elif current_location == (8.67316, 47.38566) and exit_uic_ref == '8576139' and call_counter == 1:
        return 'connection_coordinates_one_line_both_directions_first_try.json'
    elif current_location == (8.67316, 47.38566) and exit_uic_ref == '8576139' and call_counter == 2:
        return 'connection_coordinates_one_line_both_directions_second_try_start_stop_and_relation.json'
    elif current_location == (8.66828, 47.38491) and exit_uic_ref == '8589106' and call_counter == 1:
        return 'connection_coordinates_one_line_both_directions_other_direction_first_try.json'
    elif current_location == (8.66828, 47.38491) and exit_uic_ref == '8589106' and call_counter == 2:
        return 'connection_coordinates_one_line_both_directions_other_direction_second_try_start_stop_and_relation.json'
    elif current_location == (8.67316, 47.38566) and exit_uic_ref == '8576127' and call_counter == 1:
        return 'connection_coordinates_one_line_both_directions_no_exit_uic_ref_first_try.json'
    elif current_location == (8.67316, 47.38566) and exit_uic_ref == '8576127' and call_counter == 2:
        return 'connection_coordinates_one_line_both_directions_no_exit_uic_ref_second_try_start_stop_and_relation.json'


def mock_overpass_unavailable_url(monkeypatch):
    monkeypatch.setattr(overpass_service, "API",
                        _mock_overpy_api("https://overpass.offline.ch/api/interpreter"))


def mock_overpass_wrong_url(monkeypatch):
    monkeypatch.setattr(overpass_service, "API",
                        _mock_overpy_api("https://nominatim.openstreetmap.org/search"))


def _mock_overpy_api(new_url: str):
    return overpy.Overpass(url=new_url)
