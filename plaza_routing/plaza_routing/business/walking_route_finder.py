from plaza_routing.integration.routing_engine_service import RoutingEngine
from plaza_routing.integration.routing_strategy.graphhopper_strategy import GraphHopperRoutingStrategy


def get_walking_route(start: tuple, destination: tuple) -> dict:
    """ returns the walking route for a start and destination based on a routing strategy """
    routing_engine = RoutingEngine(GraphHopperRoutingStrategy())
    return routing_engine.route(start, destination)
