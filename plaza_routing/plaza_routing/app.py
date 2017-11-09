from flask import Flask, Blueprint
from plaza_routing.api.restplus import api
from plaza_routing.api.endpoints.route import ns as route_namespace

# TODO move settings to config
# Flask settings
FLASK_SERVER_NAME = 'localhost:5000'
FLASK_DEBUG = True  # Do not use debug mode in production

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = FLASK_SERVER_NAME
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    configure_app(flask_app)

    api_blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(api_blueprint)
    api.add_namespace(route_namespace)
    flask_app.register_blueprint(api_blueprint)


def main():
    app = Flask(__name__)
    initialize_app(app)
    app.run(debug=FLASK_DEBUG)


if __name__ == "__main__":
    main()
