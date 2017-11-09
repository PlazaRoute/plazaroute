import os
from bravado.client import SwaggerClient
from plaza_routing.routing_strategy.strategy import Strategy


GRAPHHOPPER_SWAGGER_FILE = 'graphhopper_swagger.json'


class GraphhopperStrategy(Strategy):

    def __init__(self):
        swagger_file = os.path.join(os.path.dirname(__file__), GRAPHHOPPER_SWAGGER_FILE)
        self._client = SwaggerClient.from_url(f'file://{swagger_file}')

    def route(self, start, destination):
        result = self._client.Routing.get_route(point=[start, destination],
                                                vehicle='foot',
                                                points_encoded=False,
                                                instructions=False,
                                                key='').result()
        # return the first path
        return result.paths[0].points.coordinates
