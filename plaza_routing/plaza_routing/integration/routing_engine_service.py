class RoutingEngine:

    def __init__(self, strategy):
        self._strategy = strategy

    def route(self, start, destination):
        return self._strategy.route(start, destination)
