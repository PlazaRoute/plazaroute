from flask_restplus import Resource, reqparse, fields

from plaza_routing.api.restplus import api
from plaza_routing.plaza_route import route

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
        return route(args.get('start'), args.get('destination'))
