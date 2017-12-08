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
        - barrier: fence
        - barrier: hedge
        - barrier: retaining_wall
  point_obstacle:
    includes:
      tag-keys:
        - amenity
      tag-key-values:
        - barrier: block
    excludes:
      tag-keys:
        - indoor

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
               },
               'point_obstacle': {
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
            'required': ['includes'],
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


def load_config(config_path: str) -> dict:
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


def create_default_config(config_path: str):
    """
    Creates the default configuration file.
    """
    logger.info(f"Creating default configuration at {config_path}")
    with open(config_path, 'w') as f:
        f.write(DEFAULT_CONFIG)


def filter_tags(tags: dict, tag_filter: dict) -> bool:
    """filter tags based on a tag filter"""

    including = False
    include = tag_filter['includes']
    if 'tag-keys' in include:
        including = any(key in tags for key in include['tag-keys'])
    if not including:
        if 'tag-key-values' in tag_filter['includes']:
            including = any(tags.get(tag_key) == tag_value for tag in include['tag-key-values']
                            for tag_key, tag_value in tag.items())
    if not including:
        return False

    if 'excludes' in tag_filter:
        if 'tag-keys' in tag_filter['excludes']:
            if any(key in tags for key in tag_filter['excludes']['tag-keys']):
                return False
        if 'tag-key-values' in tag_filter['excludes']:
            if any(tags.get(tag_key) == tag_value for tag in tag_filter['excludes']['tag-key-values']
                   for tag_key, tag_value in tag.items()):
                return False

    return True
