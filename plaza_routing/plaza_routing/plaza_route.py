from plaza_routing.external_service.routing_engine_api import RoutingEngine
from plaza_routing.external_service.routing_strategy.graphhopper_strategy import GraphhopperStrategy


def route(start, destination):
    start = '47.366353,8.544976'
    destination = '47.365888,8.54709'

    routing_engine = RoutingEngine(GraphhopperStrategy())
    result = routing_engine.route(start, destination)
    return {'coordinates': result}

