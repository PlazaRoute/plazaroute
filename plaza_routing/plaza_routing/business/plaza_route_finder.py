from ast import literal_eval
from typing import List
from datetime import datetime, timedelta
import logging

from plaza_routing import config

from plaza_routing.business import walking_route_finder
from plaza_routing.business import public_transport_route_finder
from plaza_routing.business.util import route_cost_matrix
from plaza_routing.business.util import validator

from plaza_routing.integration import geocoding_service

MAX_WALKING_DURATION = config.plaza_route_finder['max_walking_duration']
PUBLIC_TRANSPORT_ROUTE_DURATION_FORMAT = '%Y-%m-%d %H:%M:%S'
DEPARTURE_FORMAT = '%H:%M'

logger = logging.getLogger('plaza_routing.plaza_route_finder')


def find_route(start: str, destination: str, departure: str, precise_public_transport_stops: bool) -> dict:
    logger.info(f'route from {start} to {destination}')

    start = _parse_location(start)
    destination = _parse_location(destination)
    departure = _parse_departure(departure)

    overall_walking_route = walking_route_finder.get_walking_route(start, destination)

    if overall_walking_route['duration'] <= MAX_WALKING_DURATION:
        logger.info("Walking is faster than using public transport, return walking only route")
        return _convert_walking_route_to_overall_response(overall_walking_route)

    route_combinations = _get_route_combinations(start, destination, departure, precise_public_transport_stops)
    if not route_combinations:
        logger.info("No public transport route was returned because the path consists only of walking legs")
        return _convert_walking_route_to_overall_response(overall_walking_route)

    best_route_combination = _get_best_route_combination(route_combinations)

    if _is_walking_faster_than_route_combination(overall_walking_route, best_route_combination, departure):
        return _convert_walking_route_to_overall_response(overall_walking_route)

    return best_route_combination


def _get_route_combinations(start: tuple, destination: tuple,
                            departure: str, precise_public_transport_stops: bool) -> List[dict]:
    """ retrieves all possible routes for a specific start and destination address """

    public_transport_stops = public_transport_route_finder.get_public_transport_stops(start)

    routes = []
    for public_transport_stop_uic_ref, public_transport_stop_position in public_transport_stops.items():
        logger.debug(f'retrieve route with start at public transport stop: {public_transport_stop_uic_ref}')

        public_transport_departure = _calc_public_transport_departure(departure, start, public_transport_stop_position)

        public_transport_route = public_transport_route_finder.get_public_transport_route(public_transport_stop_uic_ref,
                                                                                          destination,
                                                                                          public_transport_departure,
                                                                                          precise_public_transport_stops)
        if not public_transport_route['path']:
            continue  # skip empty paths, this happens if the path only consists of walking legs

        public_transport_route_start = \
            public_transport_route_finder.get_start_position(public_transport_route,
                                                             precise_public_transport_stops)
        start_walking_route = walking_route_finder.get_walking_route(start, public_transport_route_start)

        public_transport_route_destination = \
            public_transport_route_finder.get_destination_position(public_transport_route,
                                                                   precise_public_transport_stops)
        end_walking_route = walking_route_finder.get_walking_route(public_transport_route_destination, destination)

        accumulated_duration = \
            start_walking_route['duration'] + public_transport_route['duration'] + end_walking_route['duration']

        routes.append({
            'start_walking_route': start_walking_route,
            'public_transport_connection': public_transport_route,
            'end_walking_route': end_walking_route,
            'accumulated_duration': accumulated_duration

        })
    return routes


def _get_best_route_combination(route_combinations: List[dict]) -> dict:
    """ retrieves the best route combination based on a cost matrix """
    temp_smallest_route_costs = 0
    temp_best_route_combination = None
    for route_combination in route_combinations:
        legs = (route_combination['start_walking_route'],
                route_combination['public_transport_connection'],
                route_combination['end_walking_route'])
        total_cost = route_cost_matrix.calculate_costs(legs)
        if total_cost < temp_smallest_route_costs or temp_smallest_route_costs == 0:
            temp_smallest_route_costs = total_cost
            temp_best_route_combination = route_combination
    return temp_best_route_combination


def _convert_walking_route_to_overall_response(walking_route: dict) -> dict:
    return {
        'start_walking_route': walking_route,
        'public_transport_connection': {},
        'end_walking_route': {},
        'accumulated_duration': walking_route['duration']
    }


def _calc_public_transport_departure(departure: str, start: tuple, destination: tuple) -> str:
    """
    Adds the duration that it takes to get from start to destination to the provided departure time.
    The destination should be a public transport stop to make sure that the pedestrian has enough time to catch
    the public transport.
    """
    walking_route = walking_route_finder.get_walking_route(start, destination)

    initial_departure = datetime.strptime(departure, DEPARTURE_FORMAT)
    public_transport_departure = initial_departure + timedelta(seconds=walking_route['duration'])
    return '{:%H:%M}'.format(public_transport_departure)


def _calc_waiting_time(departure: str, public_transport_route: dict) -> float:
    """ calculates the waiting based on the initial departure and the first public transport connection """
    public_transport_departure = public_transport_route['path'][0]['departure']
    diff = datetime.strptime(public_transport_departure, PUBLIC_TRANSPORT_ROUTE_DURATION_FORMAT) - \
           datetime.strptime(departure, DEPARTURE_FORMAT)
    return diff.seconds


def _is_walking_faster_than_route_combination(walking_route: dict, route_combination: dict, departure: str) -> bool:
    """ check if walking is faster than waiting for and taking the public transport """
    waiting_time = _calc_waiting_time(departure, route_combination['public_transport_connection'])
    if not route_combination or walking_route['duration'] < route_combination['accumulated_duration'] + waiting_time:
        logger.info(f"walking route ({walking_route['duration']:.1f}) faster than "
                    f"public transport and waiting time combined ({route_combination['accumulated_duration']:.1f} + "
                    f"{waiting_time:.1f}), returning walking route only")
        return True
    return False


def _parse_location(location: str) -> tuple:
    """ validates and returns the provided location (address or coordinate string) as a coordinate tuple """
    if validator.is_address(location):
        return geocoding_service.geocode(location)
    elif validator.is_valid_coordinate(location):
        return literal_eval(location)
    else:
        raise ValueError(f'invalid coordinate or location {location}')


def _parse_departure(departure: str) -> str:
    """
    If the provided departure is missing or invalid, the current time will be returned.
    Otherwise the passed departure will simply be returned.
    """
    if not departure or not validator.is_valid_departure(departure):
        return '{:%H:%M}'.format(datetime.now())
    return departure


if __name__ == "__main__":
    import time
    start_time = time.time()
    print(find_route('8.55546, 47.41071', 'Zürich, Hardbrücke', '14:42', True))
    print(time.time() - start_time)
