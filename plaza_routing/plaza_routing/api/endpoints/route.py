import logging
from flask_restplus import Resource, reqparse, fields, inputs

from plaza_routing.api.restplus import api
from plaza_routing.business.plaza_route_finder import find_route

logger = logging.getLogger('plaza_routing')
ns = api.namespace('route', description='Routing operations')

routing_arguments = reqparse.RequestParser()
routing_arguments.add_argument('start', type=str, required=True,
                               help='Start location {longitude, latitude} or address')
routing_arguments.add_argument('destination', type=str, required=True,
                               help='Destination location {longitude, latitude} or address')
routing_arguments.add_argument('departure', type=str, help='Departure {HH:mm}')
routing_arguments.add_argument('precise_public_transport_stops', type=inputs.boolean, default=False,
                               help='Use precise locations for public transport stops (slower)')


WalkingRouteResponse = api.model('WalkingRouteResponse', {
    'type': fields.String(required=True, default='walking'),
    'duration': fields.Float(required=True),
    'path': fields.List(fields.List(fields.Float), required=True, example=[[8.81716, 47.22372], [8.81814, 47.22398]])
})

PublicTransportPathResponse = api.model('PublicTransportPathResponse', {
    'name': fields.String(required=True, example='Zürich Oerlikon'),
    'line_type': fields.String(required=True, example='strain'),
    'line': fields.String(required=True, example='S6'),
    'track': fields.String(example='7'),
    'destination': fields.String(required=True, example='Zürich Hardbrück'),
    'terminal': fields.String(required=True, example='Zürich Stadelhofen'),
    'departure': fields.DateTime(required=True, example='2017-11-18 14:51:00'),
    'arrival': fields.DateTime(required=True, example='2017-11-18 14:54:00'),
    'start_position': fields.List(fields.Float, required=True, example=[8.81716, 47.22372]),
    'exit_position': fields.List(fields.Float, required=True, example=[8.81716, 47.22372]),
    'stopovers': fields.List(fields.List(fields.Float), required=True, default=[],
                             example=[[8.81716, 47.22372], [8.81814, 47.22398]])
})

PublicTransportConnectionResponse = api.model('PublicTransportConnectionResponse', {
    'type': fields.String(required=True, default='public_transport'),
    'duration': fields.Float(required=True),
    'number_of_legs': fields.Integer(required=True),
    'path': fields.List(fields.Nested(PublicTransportPathResponse), required=True)
})

RoutingResponse = api.model('RoutingResponse', {
    'start_walking_route': fields.Nested(WalkingRouteResponse, required=True),
    'public_transport_connection': fields.Nested(PublicTransportConnectionResponse, required=True, default=[]),
    'end_walking_route': fields.Nested(WalkingRouteResponse, required=True, default=[]),
    'accumulated_duration': fields.Float(required=True)
})


@ns.route('')
@api.response(400, 'invalid parameters')
@api.response(503, 'third party system is temporarily unavailable')
@api.response(500, 'plaza route is temporarily unavailable')
class PlazaRouting(Resource):

    @ns.expect(routing_arguments)
    @api.response(200, 'Route successfully retrieved.', RoutingResponse)
    def get(self):
        args = routing_arguments.parse_args()
        start = args.get('start')
        destination = args.get('destination')
        departure = args.get('departure')
        precise_public_transport_stops = args.get('precise_public_transport_stops')
        logger.debug("Calling route() with start='%s', destination='%s', departure='%s', "
                     "precise_public_transport_stops='%s'",
                     start, destination, departure, precise_public_transport_stops)
        return find_route(start, destination, departure, precise_public_transport_stops)
