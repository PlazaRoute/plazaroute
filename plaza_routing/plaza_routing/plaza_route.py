from time import gmtime, strftime
from ast import literal_eval

from plaza_routing.external_service.routing_engine_api import RoutingEngine
from plaza_routing.external_service.routing_strategy.graphhopper_strategy import GraphhopperStrategy
from plaza_routing.external_service import overpass_api
from plaza_routing.external_service import search_ch_api
from plaza_routing.external_service import geocoding_api
from plaza_routing.util import route_cost_matrix


def route(start, destination):
    print(f'route from {start} to {destination}')
    start_tuple = literal_eval(start)
    destination_tuple = geocoding_api.geocode(destination)
    departure = strftime('%H:%M', gmtime())

    routing_engine = RoutingEngine(GraphhopperStrategy())

    temp_smallest_route_costs = 0
    temp_best_route = None

    public_transport_stops = overpass_api.get_public_transport_stops(start_tuple)
    for public_transport_stop in public_transport_stops:
        print(f'public transport stop: {public_transport_stop}')

        connection = search_ch_api.get_connection(public_transport_stop, destination, departure)

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
                'end_walking_route': end_walking_route
            }

    if not temp_best_route:
        raise ValueError('no connection was found for the given start and destination')

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
    initial_stop_location = overpass_api.get_initial_public_transport_stop_position(center_location,
                                                                                    line,
                                                                                    start_stop_uicref,
                                                                                    exit_stop_uicref)
    return initial_stop_location


if __name__ == "__main__":
    print(route('47.41071, 8.55546', 'Zürich, Messe/Hallenstadion'))
