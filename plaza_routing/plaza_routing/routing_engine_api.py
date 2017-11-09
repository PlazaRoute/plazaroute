from plaza_routing.routing_strategy.graphhopper_strategy import GraphhopperStrategy


class RoutingEngine:

    def __init__(self, strategy):
        self._strategy = strategy

    def route(self, start, destination):
        return self._strategy.route(start, destination)


def main():
    routing_engine = RoutingEngine(GraphhopperStrategy())
    result = routing_engine.route('47.366353,8.544976', '47.365888,8.54709')
    print(result)


if __name__ == "__main__":
    main()
