import os

from bravado.client import SwaggerClient

from plaza_routing.integration.routing_strategy.routingstrategy import RoutingStrategy

GRAPHHOPPER_SWAGGER_FILE = 'graphhopper_swagger.json'


class GraphHopperRoutingStrategy(RoutingStrategy):

    def __init__(self):
        swagger_file = os.path.join(os.path.dirname(__file__), GRAPHHOPPER_SWAGGER_FILE)
        self._client = SwaggerClient.from_url(f'file://{swagger_file}')

    def route(self, start, destination):
        response = self._client.Routing.get_route(
            point=[f'{start[1]},{start[0]}', f'{destination[1]},{destination[0]}'],
            vehicle='foot',
            points_encoded=False,
            instructions=False,
            key='').result()
        first_path = response.paths[0]

        return {'type': 'walking',
                'duration': first_path.time / 1000,  # convert time to seconds
                'path': first_path.points.coordinates
                }
