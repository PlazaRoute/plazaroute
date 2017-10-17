#!/bin/python

import overpy

def parse_bounding_box(south, west, north, east):
    return (str(south) + "," +
            str(west) + "," +
            str(north) + "," +
            str(east))

def get_public_transport_stops(south, west, north, east):
    api = overpy.Overpass(url="http://overpass.osm.ch/api/interpreter")

    bbox = parse_bounding_box(south, west, north, east)

    query_str = """
        [bbox:{0}];
        (
        node["public_transport"="stop_position"];
        way["public_transport"="stop_position"];
        relation["public_transport"="stop_position"];
        );
        out body;
        """.format(bbox)

    result = api.query(query_str)

    for node in result.nodes:
        print(node.tags.get('uic_name'))


south = 47.363536675068296
west = 8.544192910194395
north = 47.366799509164736
east = 8.549686074256897
get_public_transport_stops(south, west, north, east)
