from ast import literal_eval
from typing import List
import logging

from plaza_routing.business import walking_route_finder
from plaza_routing.business import public_transport_route_finder
from plaza_routing.business.util import route_cost_matrix

from plaza_routing.integration import geocoding_service

MAX_WALKING_DURATION = 60 * 5

logger = logging.getLogger('plaza_routing.plaza_route_finder')


def find_route(start: str, destination_address: str, departure) -> dict:
    logger.info(f'route from {start} to {destination_address}')

    start = literal_eval(start)
    destination = geocoding_service.geocode(destination_address)

    overall_walking_route = walking_route_finder.get_walking_route(start, destination)

    if overall_walking_route['duration'] <= MAX_WALKING_DURATION:
        logger.info("Walking is faster than using public transport, return walking only route")
        return _convert_walking_route_to_overall_response(overall_walking_route)

    route_combinations = _get_route_combinations(start, destination_address, departure)
    best_route_combination = _get_best_route_combination(route_combinations)

    if not best_route_combination or overall_walking_route['duration'] < best_route_combination['accumulated_duration']:
        logger.info(f"{overall_walking_route['duration']} smaller than "
                    f"{best_route_combination['accumulated_duration']}, returning walking route only")
        return _convert_walking_route_to_overall_response(overall_walking_route)

    return best_route_combination


def _get_route_combinations(start: tuple, destination_address: str, departure) -> List[dict]:
    """ retrieves all possible routes for a specific start and destination address """
    destination = geocoding_service.geocode(destination_address)

    public_transport_stops = public_transport_route_finder.get_public_transport_stops(start)

    routes = []
    logger.debug(public_transport_stops)
    for public_transport_stop in public_transport_stops:
        logger.debug(f'retrieve route with start at public transport stop: {public_transport_stop}')
        public_transport_route = public_transport_route_finder.get_public_transport_route(public_transport_stop,
                                                                                          destination_address,
                                                                                          departure)
        public_transport_route_start = \
            public_transport_route_finder.get_start_position(public_transport_route)
        start_walking_route = walking_route_finder.get_walking_route(start, public_transport_route_start)

        public_transport_route_destination = \
            public_transport_route_finder.get_destination_position(public_transport_route)
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


if __name__ == "__main__":
    import time
    start_time = time.time()
    print(find_route('8.55546, 47.41071', 'Zürich, Hardbrücke', '14:42'))
    print(time.time() - start_time)
