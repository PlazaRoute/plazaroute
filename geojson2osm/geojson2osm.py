import sys
from datetime import datetime
import geojson as gjlib
from lxml import etree

this = sys.modules[__name__]
# osm file can't have more than 10^9 xml nodes
this.osm_id = (-1) * 10**9


def read_geojson_file(filename):
    """ reads a geojson file and returns a geojson object"""
    with open(filename, 'r') as fp:
        g = gjlib.load(fp)
    return g


def convert_to_osm(geojson):
    """ returns an OSM-structured XML as an etree"""
    if geojson['type'] != 'FeatureCollection':
        raise TypeError('Top element must be a FeatureCollection')
    nodes, ways = _process_features(geojson)
    return _build_xml(nodes, ways)


def write_xml(root, filename):
    """ writes an xml structure to a file """
    tree = etree.ElementTree(root)
    with open(filename, 'wb') as fp:
        tree.write(fp, encoding="utf-8", xml_declaration=True)


def _process_features(geojson):
    """ read a GeoJson FeatureCollection and construct xml objects """

    xml_nodes = []
    xml_ways = []

    for feature in geojson['features']:
        geometry = feature['geometry']
        geometry_type = geometry['type']

        if geometry_type == 'LineString':
            nodes, way = _process_linestring(geometry)
            xml_nodes.extend(nodes)
            xml_ways.append(way)
        else:
            raise TypeError(f'Geometry type {geometry_type} is not supported')

    return xml_nodes, xml_ways


def _build_xml(xml_nodes, xml_ways):
    root = etree.Element('osm', version='0.6', generator='geojson2osm')

    [root.append(node) for node in xml_nodes]
    [root.append(way) for way in xml_ways]

    return root


def _process_linestring(geometry):
    nodes = {}
    for point in geometry['coordinates']:
        osm_id, xml_node = _create_node(point)
        nodes[osm_id] = xml_node
    way = _create_way(nodes.keys())
    return list(nodes.values()), way


def _create_node(point):
    lon = str(point[0])
    lat = str(point[1])
    osm_id = str(create_osm_id())
    timestamp = create_osm_timestamp()
    xml_node = etree.Element('node', id=osm_id, version='1', visible="true",
                             user="geojson2osm", changeset='1', timestamp=timestamp,
                             lat=lat, lon=lon)
    return osm_id, xml_node


def _create_way(node_ids):
    osm_id = str(create_osm_id())
    timestamp = create_osm_timestamp()
    way = etree.Element('way', id=osm_id, visible='true', user="geojson2osm",
                        version='1', changeset='1', timestamp=timestamp)
    nd_refs = [etree.Element('nd', ref=str(node_id)) for node_id in node_ids]

    [way.append(nd_ref) for nd_ref in nd_refs]
    [way.append(tag) for tag in _get_way_tags()]

    return way


def create_osm_id():
    """ creates a 64-bit random integer """
    # we use negative ids to avoid conflicts with existing OSM data
    this.osm_id += 1
    return this.osm_id


def create_osm_timestamp():
    d = datetime.utcnow()
    return d.strftime('%Y-%m-%dT%H:%M:%SZ')


def _get_way_tags():
    # TODO: Proper tagging for our ways?
    tags = []
    highway_tag = etree.Element('tag', k='highway', v='footway')
    tags.append(highway_tag)
    return tags


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: geojson2osm.py <src-file> <dest-file>')
        exit(1)
    geojson = read_geojson_file(sys.argv[1])
    xml = convert_to_osm(geojson)
    write_xml(xml, sys.argv[2])
