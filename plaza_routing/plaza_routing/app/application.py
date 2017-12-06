import sys
import logging
from flask import Flask, Blueprint

from plaza_routing import config
from plaza_routing.api.restplus import api
from plaza_routing.api.endpoints.route import ns as route_namespace

logger = logging.getLogger('plaza_routing')


def configure_app(flask_app):
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = config.app['restplus']['swagger_ui_doc_expansion']
    flask_app.config['RESTPLUS_VALIDATE'] = config.app['restplus']['validate']
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = config.app['restplus']['mask_swagger']
    flask_app.config['ERROR_404_HELP'] = config.app['restplus']['error_404_help']


def initialize_app(flask_app):
    configure_app(flask_app)

    api_blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(api_blueprint)
    api.add_namespace(route_namespace)
    flask_app.register_blueprint(api_blueprint)


def setup_logging(log_level):
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(levelname)-7s] - %(message)s')

    if log_level == logging.DEBUG:
        formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)-7s] - %(message)s')

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.debug("Setting up logging complete")


def initialize(app):
    initialize_app(app)
    setup_logging(config.app['log_level'])


app = Flask(__name__)
initialize(app)

if __name__ == "__main__":
    app.config['SERVER_NAME'] = config.app['server_url']
    app.run(debug=config.app['debug'])
