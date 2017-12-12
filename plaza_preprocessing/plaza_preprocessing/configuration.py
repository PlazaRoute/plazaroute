import os
import ruamel.yaml
import logging
import jsonschema

logger = logging.getLogger('plaza_preprocessing.config')

DEFAULT_CONFIG = """
tag-filter:
  plaza: # what counts as a plaza
    includes:
#     tag-keys: # tag keys only
#       - 
      tag-key-values: # tags with specific values
        - or:
          - highway: pedestrian
        - or:
          - highway: footway
          - area: yes
    excludes: # no tags should match
#     tag-keys:
#       - <key>
      tag-key-values:
        - or:
          - area: no
  barrier: # what OSM "way" constitutes a barrier
    includes:
      tag-key-values:
        - or:
          - barrier: wall
        - or:
          - barrier: fence
        - or:
          - barrier: hedge
        - or:
          - barrier: retaining_wall
  point_obstacle:
    includes:
      tag-keys:
        - amenity
      tag-key-values:
        - or:
          - barrier: block
    excludes:
      tag-keys:
        - indoor

footway-tags: # tags that will be used for the newly generated ways
  - highway: footway

graph-strategy: visibility # one of visibility, spiderweb
spiderweb-grid-size: 2 # grid size in meters, if spiderweb is used
obstacle-buffer: 2 # minimal distance from any obstacles in meters

shortest-path-algorithm: astar # one of astar, dijkstra

entry-point-lookup-buffer: 0.05 # tolerance in meters, will be used to detect slightly offset entry points
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
           'required': ['plaza', 'barrier', 'point_obstacle']
       },
       'footway-tags': {
            'type': 'array',
            'items': {
                'type': 'object',
                'additionalProperties': {'type': 'string'}
            }
       },
       'graph-strategy': {
           'type': 'string',
           'enum': ['visibility', 'spiderweb']
       },
       'spiderweb-grid-size': {
           'type': 'number'
       },
       'obstacle-buffer': {
           'type': 'number'
       },
       'shortest-path-algorithm': {
           'type': 'string',
           'enum': ['astar', 'dijkstra']
       },
       'entry-point-lookup-buffer': {
           'type': 'number',
       }
    },
    'additionalProperties': False,
    'required': ['tag-filter', 'footway-tags', 'graph-strategy', 'spiderweb-grid-size',
                 'obstacle-buffer', 'shortest-path-algorithm', 'entry-point-lookup-buffer'],
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
                        'properties': {
                            'or': {
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
    includes = tag_filter['includes']
    if 'tag-keys' in includes:
        including = any(key in tags for key in includes['tag-keys'])
    if not including:
        if 'tag-key-values' in includes:
            including = _or_filter_matches(includes['tag-key-values'], tags)
    if not including:
        return False

    if 'excludes' in tag_filter:
        excludes = tag_filter['excludes']
        if 'tag-keys' in excludes:
            if any(key in tags for key in excludes['tag-keys']):
                return False
        if 'tag-key-values' in excludes:
            if _or_filter_matches(excludes['tag-key-values'], tags):
                return False

    return True


def _or_filter_matches(or_filter, tags):
    return any(  # or
        all(  # and
            all(tags.get(tag_key) == tag_value for tag_key, tag_value in and_filter.items())
            for and_filter in or_filter['or'])
        for or_filter in or_filter
    )
