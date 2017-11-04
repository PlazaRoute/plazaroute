from flask import Flask
from flask_restplus import Resource, Api, reqparse, fields

app = Flask(__name__)
api = Api(app,
          version='1.0', title='PlazaRouting API',
          description='PlazaRouting API'
          )

ns = api.namespace('api', description='Routing operations')

routing_arguments = reqparse.RequestParser()
routing_arguments.add_argument('start', type=str, required=True, help='Start locaton')
routing_arguments.add_argument('destination', type=str, required=True, help='Destination address')


routing_response_model = api.model('RoutingResponse', {
    'coordinates': fields.List(fields.List(fields.Float)),
})


@ns.route('/route')
class PlazaRouting(Resource):

    @ns.expect(routing_arguments, validate=True)
    @api.response(200, 'Route successfully retrieved.', routing_response_model)
    def get(self):
        args = routing_arguments.parse_args()
        return route(args.get('start'), args.get('destination'))


def route(start, destination):
    return {'coordinates': [[47.1008, 8.6711], [47.1098, 8.6712]]}


if __name__ == '__main__':
    app.run(debug=True)
