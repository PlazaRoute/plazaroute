from bravado.client import SwaggerClient
client = SwaggerClient.from_url('file:///opt/dev/git/PlazaNav/PlazaNav/routing-tests/graphhopper/swagger.json')
result = client.Routing.get_route(point=['47.366353,8.544976', '47.365888,8.54709'], vehicle='foot', points_encoded=False, key='', instructions=False).result()

for path in result.paths:
    print(path.points.coordinates)
