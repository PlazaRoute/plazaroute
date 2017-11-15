from plaza_routing.business.util import coordinate_transformer
from plaza_routing.integration import overpass_service


def get_path_for_public_transport_connection(connection):
    """
    Retrieves the start position for each leg in the provided connection
    and produces an routable response.
    """
    legs = connection['legs']
    result = {
        'type': 'public_transport',
        'path': [],
        'time': connection['duration'],
        'number_of_legs': 0
    }

    relevant_legs_counter = 0
    for leg in legs[:-1]:
        if not _is_relevant_leg(leg):
            continue

        line = leg['line']
        start_uic_ref = leg['stopid']
        exit_uic_ref = leg['exit']['stopid']

        fallback_start_position = coordinate_transformer.transform_ch_to_wgs(leg['x'], leg['y'])
        fallback_exit_position = coordinate_transformer.transform_ch_to_wgs(leg['exit']['x'], leg['exit']['y'])

        # TODO we use the same variable twice as parameter because they have a different intend (REFACTORING)
        lookup_position = fallback_start_position
        start_position, exit_position = overpass_service.get_start_exit_stop_position(lookup_position,
                                                                                      start_uic_ref, exit_uic_ref,
                                                                                      line,
                                                                                      fallback_start_position,
                                                                                      fallback_exit_position)

        path = {
            'name': leg['name'],
            'line_type': leg['type'],
            'line': leg['line'],
            'destination': leg['exit']['name'],
            'terminal': leg['terminal'],
            'departure': leg['departure'],
            'arrival': leg['exit']['arrival'],
            'start_position': [*start_position],
            'exit_position': [*exit_position]
        }
        result['path'].append(path)
        relevant_legs_counter += 1

    result['number_of_legs'] = relevant_legs_counter
    return result


def _get_stopovers(stopovers):
    """
    Returns the coordinates for all provided stopovers in a list.
    The approximation based on the search.ch coordinates is enough.
    """
    path = []
    for stopover in stopovers:
        path.append(coordinate_transformer.transform_ch_to_wgs(stopover['x'], stopover['y']))
    return path


def _is_relevant_leg(leg):
    if leg['type'] == 'walk':
        return False
    return True
