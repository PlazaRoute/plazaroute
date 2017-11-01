from flask import Flask
from flask_restplus import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app, version='1.0', title='PlazaRouting API',
          description='PlazaRouting API'
          )

ns = api.namespace('api', description='Routing operations')

parser = reqparse.RequestParser()
parser.add_argument('start', type=str, required=True, help='Start cannot be converted')
parser.add_argument('destination', type=str, required=True, help='Destination cannot be converted')

@ns.route('/route')
class PlazaRouting(Resource):

    @ns.expect(parser, validate=True)
    @ns.param('start', description='Start location')
    @ns.param('destination', description='Destination address')
    def get(self):
        args = parser.parse_args()
        return {'start': args.get('start'), 'destination': args.get('destination')}


if __name__ == '__main__':
    app.run(debug=True)
