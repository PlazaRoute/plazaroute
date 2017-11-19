from typing import Set, List
import logging

from plaza_routing.business.util import coordinate_transformer

from plaza_routing.integration import overpass_service
from plaza_routing.integration import search_ch_service

logger = logging.getLogger('plaza_routing.public_transport_route_finder')


def get_public_transport_stops(start: tuple) -> Set[str]:
    return overpass_service.get_public_transport_stops(start)


def get_public_transport_route(start: str, destination: str, departure: str) -> dict:
    connection = search_ch_service.get_connection(start, destination, departure)
    return _get_path_for_public_transport_connection(connection)


def get_start_position(public_transport_route: dict) -> tuple:
    first_leg = public_transport_route['path'][0]
    return _get_start_exit_stop_position(first_leg)[0]


def get_destination_position(public_transport_route: dict) -> tuple:
    last_leg = public_transport_route['path'][-1]
    return _get_start_exit_stop_position(last_leg)[1]


def _get_start_exit_stop_position(leg: dict) -> tuple:
    fallback_start_position = tuple(leg['start_position'])
    fallback_exit_position = tuple(leg['exit_position'])
    return overpass_service.get_start_exit_stop_position(fallback_start_position,
                                                         leg['start_stop_uicref'],
                                                         leg['exit_stop_uicref'],
                                                         leg['line'],
                                                         fallback_start_position,
                                                         fallback_exit_position)


def _get_path_for_public_transport_connection(connection: dict) -> dict:
    """ retrieves the start position for each leg in the provided connection and produces an routable response """
    legs = connection['legs']
    result = {
        'type': 'public_transport',
        'path': [],
        'duration': connection['duration'],
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

        lookup_position = fallback_start_position
        start_position, exit_position = overpass_service.get_start_exit_stop_position(lookup_position,
                                                                                      start_uic_ref, exit_uic_ref,
                                                                                      line,
                                                                                      fallback_start_position,
                                                                                      fallback_exit_position)

        result['path'].append(_generate_path(leg, start_position, exit_position))
        relevant_legs_counter += 1

    result['number_of_legs'] = relevant_legs_counter
    return result


def _generate_path(leg: dict, start_position: tuple, exit_position: tuple) -> dict:
    return {
            'name': leg['name'],
            'line_type': leg['type'],
            'line': leg['line'],
            'destination': leg['exit']['name'],
            'terminal': leg['terminal'],
            'departure': leg['departure'],
            'arrival': leg['exit']['arrival'],
            'start_position': [*start_position],
            'exit_position': [*exit_position],
            'start_stop_uicref': leg['stopid'],
            'exit_stop_uicref': leg['exit']['stopid']
            }


def _get_stopovers(stopovers: List[dict]) -> List[List[float]]:
    """
    Returns the coordinates for all provided stopovers in a list.
    The approximation based on the search.ch coordinates is enough.
    """
    path = []
    for stopover in stopovers:
        path.append([coordinate_transformer.transform_ch_to_wgs(stopover['x'], stopover['y'])])
    return path


def _is_relevant_leg(leg: dict) -> bool:
    if leg['type'] == 'walk':
        logger.debug(f'filter leg: {leg}')
        return False
    return True
