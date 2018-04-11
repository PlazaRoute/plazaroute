from datetime import datetime
from osmium import SimpleWriter
from osmium.osm.mutable import Way, Node


OSM_ID_START = 10**10


def transform_plazas(plazas, node_file, way_file, footway_tags):
    """ transforms plazas to OSM and write them to a file """
    node_writer = SimpleWriter(node_file)
    way_writer = SimpleWriter(way_file)

    entry_node_mappings = {}
    osm_id_nodes = osm_id_ways = OSM_ID_START

    try:
        for plaza in plazas:
            if "graph_edges" not in plaza:
                raise ValueError(f"No graph edges in {plaza['osm_id']}")
            if "entry_points" not in plaza:
                raise ValueError(f"No entry points in {plaza['osm_id']}")

            transformer = PlazaTransformer(osm_id_nodes, osm_id_ways, footway_tags)
            transformer.transform_plaza(plaza)

            # merge entry node mappings
            entry_node_mappings = {**entry_node_mappings, **transformer.entry_node_mappings}

            for node in transformer.nodes.values():
                node_writer.add_node(node)
            for way in transformer.ways:
                way_writer.add_way(way)

            osm_id_nodes += len(transformer.nodes)
            osm_id_ways += len(transformer.ways)
    finally:
        node_writer.close()
        way_writer.close()
    return entry_node_mappings


class PlazaTransformer:
    """
    Transforms plaza graph edges to an OSM Format
    """

    def __init__(self, start_id_nodes, start_id_ways, footway_tags):
        self.osm_id_nodes = start_id_nodes
        self.osm_id_ways = start_id_ways
        # use coordinates as keys and osmium objects as values
        self.nodes = {}
        self.ways = []
        # maps entry ways of plazas to entry node ids
        self.entry_node_mappings = {}
        self.footway_tags = [(key, value) for tag in footway_tags for key, value in tag.items()]

    def transform_plaza(self, plaza):
        """ takes a plaza with edge geometries and constructs nodes and ways """

        for edge in plaza['graph_edges']:
            self._create_way(edge)

        for entry_line in plaza.get('entry_lines'):
            self.entry_node_mappings[entry_line['way_id']] = [
                {
                    'id': self._get_node_id((p.x, p.y)),
                    'coords': (p.x, p.y)
                }
                for p in entry_line['entry_points']]

    def _create_way(self, edge):
        """ create a way with corresponding nodes """
        node_refs = []
        for coords in edge.coords:
            node_refs.append(self._get_node_id(coords))
        way_id = self._get_new_way_osm_id()
        way = Way(nodes=node_refs)
        way.tags = self.footway_tags
        way.id = way_id
        way.version = 1
        way.timestamp = self._create_osm_timestamp()
        self.ways.append(way)

    def _get_node_id(self, coords):
        """
        get a node id for the coords, creates a new node if it doesn't exist yet
        """
        if coords in self.nodes:
            return self.nodes[coords].id
        else:
            node_id = self._get_new_node_osm_id()
            node = Node(location=coords)
            node.id = node_id
            node.version = 1
            node.timestamp = self._create_osm_timestamp()
            self.nodes[coords] = node
            return node_id

    def _get_new_node_osm_id(self):
        self.osm_id_nodes += 1
        return self.osm_id_nodes

    def _get_new_way_osm_id(self):
        self.osm_id_ways += 1
        return self.osm_id_ways

    def _create_osm_timestamp(self):
        now = datetime.utcnow()
        return now.strftime('%Y-%m-%dT%H:%M:%SZ')
