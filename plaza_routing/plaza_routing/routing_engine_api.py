import abc
import os
from bravado.client import SwaggerClient


class RoutingEngine:

    def __init__(self, strategy):
        self._strategy = strategy

    def route(self, start, destination):
        return self._strategy.route(start, destination)


class Strategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def route(self, start, destination):
        pass


class GraphhopperStrategy(Strategy):

    def __init__(self):
        dir = os.path.dirname(__file__)
        swagger_file = os.path.abspath('swagger_graphhopper.json')
        self._client = SwaggerClient.from_url(f'file://{swagger_file}')

    def route(self, start, destination):
        result = self._client.Routing.get_route(point=[start, destination],
                                                vehicle='foot',
                                                points_encoded=False,
                                                instructions=False,
                                                key='').result()
        return result


def main():
    routing_engine = RoutingEngine(GraphhopperStrategy())
    result = routing_engine.route('47.366353,8.544976', '47.365888,8.54709')
    for path in result.paths:
        print(path.points.coordinates)


if __name__ == "__main__":
    main()
