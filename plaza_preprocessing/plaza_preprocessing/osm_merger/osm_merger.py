from sys import maxsize
from os import remove
from datetime import datetime
from osmium import SimpleHandler, SimpleWriter
from osmium.osm.mutable import Way
from shapely.geometry import Point, LineString
from plaza_preprocessing.osm_merger.plazawriter import PlazaWriter
import plaza_preprocessing.osm_merger.osmosishelper as osmosishelper

class WayExtractor(SimpleHandler):
    """ collect outer ways of plazas """
    def __init__(self, entry_node_mappings):
        SimpleHandler.__init__(self)
        self.entry_node_mappings = entry_node_mappings
        self.ways = {}

    def way(self, w):
        """ collect outer rings of plazas into a dictionary"""
        if w.is_closed() and w.id in self.entry_node_mappings:
            w_mutable = w.replace()
            self.ways[w.id] = {
                'version': w.version,
                'nodes': [{'id': n.ref, 'coords': (n.lon, n.lat)} for n in w.nodes]
            }


def merge_plaza_graphs(plazas, osm_file, merged_file):
    """
    merge graph edges of plazas back into the "big" OSM file
    """
    # TODO: Proper temp file
    plazas_file = 'plazas.osm'
    modified_ways_file = 'modified_ways.osm'
    try:
        entry_node_mappings = _write_plazas_to_osm(plazas, plazas_file)

        plaza_ways = _extract_plaza_ways(entry_node_mappings, osm_file)
        insert_entry_nodes(plaza_ways, entry_node_mappings)

        write_modified_ways(plaza_ways, modified_ways_file)

        osmosishelper.merge_three_osm_files(
            merged_file, osm_file, plazas_file, modified_ways_file)
    finally:
        remove(plazas_file)
        remove(modified_ways_file)


def insert_entry_nodes(plaza_ways, entry_node_mappings):
    """ insert entry node refs to the ways in the correct position """
    for way_id, entry_nodes in entry_node_mappings.items():
        if way_id not in plaza_ways:
            raise RuntimeError(f"Way {way_id} was not found in large osm file")
        way_nodes = plaza_ways.get(way_id).get('nodes')
        for entry_node in entry_nodes:
            way_nodes = _insert_entry_node(entry_node, way_nodes)


def write_modified_ways(plaza_ways, filename):
    """
    write the modified ways (plaza polygons) to an OSM file
    """
    ways = []
    for way_id, way in plaza_ways.items():
        node_refs = [node['id'] for node in way['nodes']]
        osm_way = Way(nodes=node_refs)
        osm_way.id = way_id
        # TODO: configurable tags
        osm_way.tags = ('highway', 'footway')
        # increase version number to overwrite original way
        osm_way.version = way['version'] + 1
        osm_way.timestamp = _create_osm_timestamp()
        ways.append(osm_way)

    writer = SimpleWriter(filename)
    try:
        for way in ways:
            writer.add_way(way)
    finally:
        writer.close()


def _write_plazas_to_osm(plazas, filename):
    plaza_writer = PlazaWriter()
    plaza_writer.read_plazas(plazas)
    plaza_writer.write_to_file(filename)
    return plaza_writer.entry_node_mappings


def _insert_entry_node(entry_node, way_nodes):
    """ insert node_id in the correct position of way_nodes """
    insert_position = _find_insert_position(entry_node, way_nodes)
    way_nodes.insert(insert_position, entry_node)
    return way_nodes


def _find_insert_position(entry_node, way_nodes):
    entry_point = Point(entry_node['coords'])
    exact_match = _find_exact_insert_position(entry_point, way_nodes)

    return exact_match if exact_match else (
        _find_interpolated_insert_position(entry_point, way_nodes))


def _find_exact_insert_position(entry_point, way_nodes):
    """
    try to find a point in the way_nodes that overlaps
    the entry point exactly
    """
    for i, node in enumerate(way_nodes):
        way_point = Point(node['coords'])
        if way_point.equals(entry_point):
            return i
    return None


def _find_interpolated_insert_position(entry_point, way_nodes):
    """
    draws a line between pairs of polygon points and returns the
    index of the end node of the line to which the entry point is
    closest to
    """
    min_node = {'pos': None, 'distance': maxsize}
    for i in range(0, len(way_nodes) - 1):
        # first and last nodes are the same
        start_node = way_nodes[i]
        end_node = way_nodes[i + 1]
        line = LineString(
            [start_node['coords'], end_node['coords']])
        distance = line.distance(entry_point)
        if distance == 0:
            return i + 1

        if distance < min_node['distance']:
            min_node['pos'] = i + 1
            min_node['distance'] = distance
    return min_node['pos']

def _extract_plaza_ways(entry_node_mappings, osm_file):
    way_extractor = WayExtractor(entry_node_mappings)
    index_type = 'sparse_mem_array'
    way_extractor.apply_file(osm_file, locations=True, idx=index_type)
    return way_extractor.ways


def _create_osm_timestamp():
    now = datetime.utcnow()
    return now.strftime('%Y-%m-%dT%H:%M:%SZ')