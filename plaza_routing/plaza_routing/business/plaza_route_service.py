from ast import literal_eval
from time import gmtime, strftime

from plaza_routing.business.util import route_cost_matrix
from plaza_routing.integration import geocoding_service
from plaza_routing.integration import overpass_service
from plaza_routing.integration import search_ch_service
from plaza_routing.integration.routing_engine_service import RoutingEngine
from plaza_routing.integration.routing_strategy.graphhopper_strategy import GraphhopperStrategy

MAX_WALKING_TIME = 1000 * 60 * 5


def route(start, destination):
    print(f'route from {start} to {destination}')
    start_tuple = literal_eval(start)
    destination_tuple = geocoding_service.geocode(destination)
    departure = strftime('%H:%M', gmtime())

    routing_engine = RoutingEngine(GraphhopperStrategy())

    walking_route = routing_engine.route(start_tuple, destination_tuple)
    walking_route_time = walking_route['time']
    if walking_route_time <= MAX_WALKING_TIME:
        # walking is faster to even consider public transportation
        # TODO return correct data structure
        return walking_route

    best_route = _retrieve_best_route_combination(start_tuple,
                                                  destination, destination_tuple,
                                                  departure,
                                                  routing_engine)
    if not best_route:
        # TODO can we consider the walking route in this case
        raise ValueError('no connection was found for the given start and destination')

    # TODO check if walking is still faster
    if walking_route_time < best_route['accumulated_time']:
        # walking is still faster than taking the public transportation
        # TODO return correct data structure
        return walking_route

    return best_route


def _retrieve_best_route_combination(start_tuple, destination, destination_tuple, departure, routing_engine):
    temp_smallest_route_costs = 0
    temp_best_route = None
    public_transport_stops = overpass_service.get_public_transport_stops(start_tuple)
    for public_transport_stop in public_transport_stops:
        print(f'public transport stop: {public_transport_stop}')

        connection = search_ch_service.get_connection(public_transport_stop, destination, departure)

        if not _is_relevant_connection(connection):
            continue

        first_leg = connection['legs'][0]
        initial_stop_location = _get_public_transport_stop_location(first_leg, start_tuple)
        start_walking_route = routing_engine.route(start_tuple, initial_stop_location)

        last_leg = connection['legs'][len(connection['legs']) - 2]
        final_stop_location = _get_public_transport_stop_location(last_leg, destination_tuple)
        end_walking_route = routing_engine.route(final_stop_location, destination_tuple)

        total_cost = route_cost_matrix.calculate_costs((start_walking_route, connection, end_walking_route))
        if total_cost < temp_smallest_route_costs or temp_smallest_route_costs == 0:
            temp_smallest_route_costs = total_cost
            temp_best_route = {
                'start_walking_route': start_walking_route,
                'public_transport_connection': connection,
                'end_walking_route': end_walking_route,
                'accumulated_time': start_walking_route['time'] + connection['duration'] + start_walking_route['time']
            }
    return temp_best_route


def _is_relevant_connection(connection):
    if connection['legs'][0]['type'] == 'walk':
        print(f'filter connection: {connection}')
        return False
    return True


def _get_public_transport_stop_location(leg, center_location):
    line = leg['line']
    start_stop_uicref = leg['stopid']
    exit_stop_uicref = leg['exit']['stopid']
    initial_stop_location = overpass_service.get_initial_public_transport_stop_position(center_location,
                                                                                        line,
                                                                                        start_stop_uicref,
                                                                                        exit_stop_uicref)
    return initial_stop_location


if __name__ == "__main__":
    # print(route('47.41071, 8.55546', 'Zürich, Messe/Hallenstadion'))
    print(route('47.366451,8.548779', 'Bellevueplatz, Zürich'))
