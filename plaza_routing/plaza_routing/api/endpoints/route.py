import logging
from flask_restplus import Resource, reqparse, fields

from plaza_routing.api.restplus import api
from plaza_routing.business.plaza_route_service import route

logger = logging.getLogger('plaza_routing')
ns = api.namespace('route', description='Routing operations')

routing_arguments = reqparse.RequestParser()
routing_arguments.add_argument('start', type=str, required=True, help='Start locaton')
routing_arguments.add_argument('destination', type=str, required=True, help='Destination address')

routing_response_model = \
    api.model('RoutingResponse', {
        'coordinates': fields.List(fields.List(fields.Float))
    })


@ns.route('')
class PlazaRouting(Resource):

    @ns.expect(routing_arguments)
    @api.response(200, 'Route successfully retrieved.', routing_response_model)
    def get(self):
        args = routing_arguments.parse_args()
        start = args.get('start')
        destination = args.get('destination')
        logger.debug("Calling route() with start='%s', destination='%s'", start, destination)
        return route(start, destination)
