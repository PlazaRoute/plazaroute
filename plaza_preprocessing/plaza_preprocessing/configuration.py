import os
import ruamel.yaml
import logging
import jsonschema

logger = logging.getLogger('plaza_preprocessing.config')

DEFAULT_CONFIG = """
tag-filter:
  plaza: # what counts as a plaza
    includes: # one or more tags must match
#     tag-keys: # tag keys only
#       - 
      tag-key-values: # tags with specific values
        - highway: pedestrian
    excludes: # no tags should match
#     tag-keys:
#       - <key>
      tag-key-values:
        - area: no
  barrier: # what OSM "way" constitutes a barrier
    includes:
      tag-key-values:
        - barrier: wall

graph-strategy: visibility # one of visibility, spiderweb
spiderweb-grid-size: 2 # grid size in meters, if spiderweb is used
obstacle-buffer: 2 # minimal distance from any obstacles in meters

shortest-path-algorithm: astar # one of astar, dijkstra
"""

SCHEMA = {
    'title': 'plaza_preprocessing configuration Schema',
    'type': 'object',
    'properties': {
       'tag-filter': {
           'type': 'object',
           'properties':  {
               'plaza': {
                   'type': 'object',
                   '$ref': '#/definitions/tag-filter'
               },
               'barrier': {
                   'type': 'object',
                   '$ref': '#/definitions/tag-filter'
               }
           },
           'additionalProperties': False,
           'required': ['plaza', 'barrier']
       },
       'graph-strategy': {
           'type': 'string',
           'enum': ['visibility', 'spiderweb']
       },
       'spiderweb-grid-size': {
           'type': 'integer'
       },
       'obstacle-buffer': {
           'type': 'integer'
       },
       'shortest-path-algorithm': {
           'type': 'string',
           'enum': ['astar', 'dijkstra']
       }
    },
    'additionalProperties': False,
    'required': ['tag-filter', 'graph-strategy', 'spiderweb-grid-size', 'obstacle-buffer', 'shortest-path-algorithm'],
    'definitions': {
        'tag-filter': {
            'properties': {
                'includes': {
                    'type': 'object',
                    '$ref': '#/definitions/tag-listing'
                },
                'excludes': {
                    'type': 'object',
                    '$ref': '#/definitions/tag-listing'
                }
            },
            'additionalProperties': False,
        },
        'tag-listing': {
            'properties': {
                'tag-keys': {
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                'tag-key-values': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'additionalProperties': {'type': 'string'}
                    }
                }
            }
        }
    }
}


def load_config(config_path):
    """
    Loads the configuration and creates the default configuration if it does not yet exist.
    """

    # create default config if it does not yet exist
    if not os.path.exists(config_path):
        create_default_config(config_path)

    config = None
    with open(config_path, 'r') as f:
        config = ruamel.yaml.load(f, ruamel.yaml.RoundTripLoader)

    jsonschema.validate(config, SCHEMA)

    return config


def create_default_config(config_path):
    """
    Creates the a default configuration file.
    """
    logger.info('Creating default configuration')
    with open(config_path, 'w') as f:
        f.write(DEFAULT_CONFIG)