from datetime import datetime
from osmium import SimpleWriter
from osmium.osm.mutable import Way, Node

class PlazaWriter:
    """
    Reads plaza graph edges and produces an OSM Format
    """

    def __init__(self):
        self.osm_id_nodes = self.osm_id_ways = (-1) * 10**9
        # use coordinates as keys and osmium objects as values
        self.nodes = {}
        self.ways = []
        # maps outer ring ways of plazas to entry node ids
        self.entry_node_mappings = {}

    def read_plazas(self, plazas):
        """ takes a list of plazas with edge geometries and constructs nodes and ways """
        for plaza in plazas:
            if not "graph_edges" in plaza:
                raise ValueError(f"No graph edges in {plaza['osm_id']}")
            if not "entry_points" in plaza:
                raise ValueError(f"No entry points in {plaza['osm_id']}")

            for edge in plaza['graph_edges']:
                self._create_way(edge)

            self.entry_node_mappings[plaza.get('outer_ring_id')] = [
                {'id': self._get_node_id((p.x, p.y)), 'coords': (p.x, p.y)}
                for p in plaza['entry_points']]

    def write_to_file(self, filename):
        """ write the nodes and ways to an OSM file """
        writer = SimpleWriter(filename)
        try:
            for node in self.nodes.values():
                writer.add_node(node)
            for way in self.ways:
                writer.add_way(way)
        finally:
            writer.close()

    def _create_way(self, edge):
        """ create a way with corresponding nodes """
        node_refs = []
        for coords in edge.coords:
            node_refs.append(self._get_node_id(coords))
        way_id = self._get_new_way_osm_id()
        way = Way(nodes=node_refs)
        # TODO: configurable tags
        way.tags = [('highway', 'footway')]
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