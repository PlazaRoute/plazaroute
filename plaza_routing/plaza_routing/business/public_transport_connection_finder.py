from typing import List
import logging

from plaza_routing.business.util import coordinate_transformer

from plaza_routing.integration import overpass_service
from plaza_routing.integration import search_ch_service

logger = logging.getLogger('plaza_routing.public_transport_connection_finder')


def get_public_transport_stops(start: tuple) -> dict:
    return overpass_service.get_public_transport_stops(start)


def get_public_transport_connection(start_uic_ref: str, destination: tuple, departure: str) -> dict:
    connection = search_ch_service.get_connection(start_uic_ref, _tuple_to_str(destination), departure)
    return _generate_public_transport_connection(connection)


def optimize_public_transport_connection(public_transport_connection: dict) -> dict:
    """ retrieves accurate coordinates for the public transport stops in each leg """
    for leg in public_transport_connection['path']:
        logger.debug(f'optimize public transport connection leg: {leg["start"]} to {leg["destination"]}')
        fallback_start_position = tuple(leg['start_position'])
        fallback_exit_position = tuple(leg['exit_position'])

        lookup_position = fallback_start_position
        start_position, exit_position = overpass_service.get_connection_coordinates(lookup_position,
                                                                                    leg['start_stop_uicref'],
                                                                                    leg['exit_stop_uicref'],
                                                                                    leg['line'],
                                                                                    fallback_start_position,
                                                                                    fallback_exit_position)
        leg['start_position'] = [*start_position]
        leg['exit_position'] = [*exit_position]
    return public_transport_connection


def _generate_public_transport_connection(connection: dict) -> dict:
    """ produces an routable public transport connection """
    legs = connection['legs']
    result = {
        'type': 'public_transport',
        'path': [],
        'duration': connection['duration'],
        'number_of_legs': 0
    }

    for leg in legs:
        start_position = coordinate_transformer.transform_ch_to_wgs(leg['x'], leg['y'])
        exit_position = coordinate_transformer.transform_ch_to_wgs(leg['exit']['x'], leg['exit']['y'])

        result['path'].append(_generate_path(leg, start_position, exit_position))

    result['number_of_legs'] = len(result['path'])
    return result


def _generate_path(leg: dict, start_position: tuple, exit_position: tuple) -> dict:
    return {
            'start': leg['name'],
            'destination': leg['exit']['name'],
            'line_type': leg['type'],
            'line': leg['line'],
            'track': leg['track'],
            'terminal': leg['terminal'],
            'departure': leg['departure'],
            'arrival': leg['exit']['arrival'],
            'start_position': [*start_position],
            'exit_position': [*exit_position],
            'start_stop_uicref': leg['stopid'],
            'exit_stop_uicref': leg['exit']['stopid'],
            'stopovers': _get_stopovers(leg['stops'])
            }


def _get_stopovers(stopovers: List[dict]) -> List[List[float]]:
    """
    Returns the coordinates for all provided stopovers in a list.
    The approximation based on the search.ch coordinates is enough.
    """
    path = []
    for stopover in stopovers:
        path.append([*coordinate_transformer.transform_ch_to_wgs(stopover['x'], stopover['y'])])
    return path


def _tuple_to_str(value: tuple) -> str:
    """ returns a tuple as a string without parentheses """
    return ','.join(map(str, value))
