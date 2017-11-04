from osmium.osm.mutable import Way, Node

class OSMWriter:
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

            self.entry_node_mappings[plaza.get('outer_ring_id')] = list(map(
                lambda p: self._get_node_id((p.x, p.y)),
                plaza['entry_points']))

    def write_to_file(self, filename):
        """ write the nodes and ways to an OSM file """
        # TODO: Write using Osmium Writer
        pass

    def _create_way(self, edge):
        """ create a way with corresponding nodes """
        node_refs = []
        for coords in edge.coords:
            node_refs.append(self._get_node_id(coords))
        way_id = self._get_new_way_osm_id()
        way = Way(nodes=node_refs)
        way.id = way_id
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
            self.nodes[coords] = node
            return node_id

    def _get_new_node_osm_id(self):
        self.osm_id_nodes += 1
        return self.osm_id_nodes

    def _get_new_way_osm_id(self):
        self.osm_id_ways += 1
        return self.osm_id_ways
