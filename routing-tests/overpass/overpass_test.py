#!/bin/python

import overpass

def parse_bounding_box(south, west, north, east):
    return (str(south) + "," +
            str(west) + "," +
            str(north) + "," +
            str(east))

def get_public_transport_stops(south, west, north, east):
    api = overpass.API(endpoint="http://overpass.osm.ch/api/interpreter")

    bbox = parse_bounding_box(south, west, north, east)

    query_str = """
        (
        node["public_transport"="stop_position"]({0});
        way["public_transport"="stop_position"]({0});
        relation["public_transport"="stop_position"]({0});
        )
        """.format(bbox)

    result = api.Get(query_str)

    for feature in result['features']:
        print(feature.properties.get('uic_name'))


south = 47.363536675068296
west = 8.544192910194395
north = 47.366799509164736
east = 8.549686074256897
get_public_transport_stops(south, west, north, east)
