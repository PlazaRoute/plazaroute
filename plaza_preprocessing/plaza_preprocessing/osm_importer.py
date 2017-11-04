import osmium
from osmium._osmium import InvalidLocationError
import shapely.wkb as wkblib

PBF_PATH = "data/helvetiaplatz_umfeld.osm"
# PBF_PATH = "data/switzerland-exact.osm.pbf"

WKBFAB = osmium.geom.WKBFactory()


def import_osm(filename):
    """ imports a OSM / PBF file and returns a holder with all plazas, buildings,
    lines and points with shapely geometries """
    handler = _PlazaHandler()
    # index_type = 'dense_file_array' # uses over 25GB of space for Switzerland
    index_type = 'sparse_mem_array'
    handler.apply_file(filename, locations=False, idx=index_type)
    print(f'{len(handler.plazas)} plazas')
    print(f'{len(handler.buildings)} buildings')
    print(f'{len(handler.lines)} lines')
    print(f'{len(handler.points)} points')
    handler.add_missing_ring_ids()

    print(f'encountered {handler.invalid_count} invalid objects (probably because of boundaries)')
    return OSMHolder(handler.plazas, handler.buildings, handler.lines, handler.points)


class OSMHolder:
    def __init__(self, plazas, buildings, lines, points):
        self.plazas = plazas
        self.buildings = buildings
        self.lines = lines
        self.points = points


class _PlazaHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.plazas = []
        self.buildings = []
        self.points = []
        self.lines = []
        self._relations = {}
        self._closed_ways = {}
        self.invalid_count = 0

    def node(self, n):
        # TODO: Proper tag filtering
        if "amenity" in n.tags:
            if "indoor" in n.tags or n.tags.get("level", "0") != "0" or n.tags.get("layer", "0") != "0":
                return
            wkb = WKBFAB.create_point(n)
            self.points.append(wkblib.loads(wkb, hex=True))

    def way(self, w):
        # TODO: proper filtering
        if ("highway" in w.tags or w.tags.get("railway") == "tram") and not w.is_closed():
            try:
                wkb = WKBFAB.create_linestring(w)
                self.lines.append(wkblib.loads(wkb, hex=True))
            except InvalidLocationError:
                print(f'Invalid location in {w.id}')
                self.invalid_count += 1
            except RuntimeError as ex:
                print(f'Error with {w.id}, {len(w.nodes)} nodes: {ex}')
                self.invalid_count += 1
        elif w.is_closed():
            w_mutable = w.replace()
            try:
                self._closed_ways[w_mutable.id] = [(n.lon, n.lat) for n in w_mutable.nodes]
            except InvalidLocationError:
                print(f'Invalid location for closed way in {w.id}')
                self.invalid_count += 1
            except RuntimeError as ex:
                print(f'Error with {w.id}, {len(w.nodes)} nodes: {ex}')
                self.invalid_count += 1

    def area(self, a):
        if a.orig_id() == 1255716:
            print(a.num_rings())
        if a.tags.get("highway") == "pedestrian" and a.tags.get("area") != "no":
            multipolygon = self._create_multipolygon_geometry(a)

            for outer_ring in a.outer_rings():
                polygon = self._get_polygon_for_outer_ring(multipolygon, outer_ring)

                # ring id for relation will be added later
                outer_ring_id = a.orig_id() if a.from_way() else None
                plaza = {
                    'osm_id': a.orig_id(),
                    'geometry': polygon,
                    'is_relation': not a.from_way(),
                    'outer_ring_id': outer_ring_id
                }
                self.plazas.append(plaza)

        elif "building" in a.tags and a.tags.get("layer", "0") == "0":
            geom = self._create_multipolygon_geometry(a)
            self.buildings.append(geom)

    def relation(self, r):
        if r.tags.get("highway") == "pedestrian" and r.tags.get("area") != "no":
            outer_rings = []
            for member in r.members:
                if member.role == "outer":
                    outer_rings.append(member.ref)

            self._relations[r.replace().id] = outer_rings

    def add_missing_ring_ids(self):
        """ 
        Adds OSM id of outer ring to plazas that are parts of relations. 
        Discard plazas that are mapped with relations with unclosed ways
        """
        discard_list = []
        for plaza in self.plazas:
            osm_id = plaza['osm_id']
            if plaza['is_relation']:
                if osm_id not in self._relations:
                    raise KeyError(f'Plaza {osm_id} is not in relations!')

                outer_ring_id = self._get_outer_ring_id_for_polygon(
                    plaza['geometry'], osm_id)
                if not outer_ring_id:
                    discard_list.append(plaza)
                else:
                    plaza['outer_ring_id'] = outer_ring_id

        for plaza in discard_list:
            self.plazas.remove(plaza)

    def _create_multipolygon_geometry(self, multipolygon):
        wkb = WKBFAB.create_multipolygon(multipolygon)
        return wkblib.loads(wkb, hex=True)

    def _get_polygon_for_outer_ring(self, multipolygon, outer_ring):
        """ match the outer_ring to the polygon in a multipolygon """
        if len(multipolygon.geoms) == 1:
            return multipolygon.geoms[0]
        node_refs = list(outer_ring)
        for polygon in multipolygon.geoms:
            exterior_coords = polygon.exterior.coords
            if all([(n.lon, n.lat) in exterior_coords for n in node_refs]):
                return polygon
        raise RuntimeError("No polygon found for outer ring")
    
    def _get_outer_ring_id_for_polygon(self, polygon, rel_id):
        """ match an outer ring to a polygon """
        outer_rings = self._relations.get(rel_id)
        if len(outer_rings) == 1:
            return outer_rings[0]
        exterior_coords = polygon.exterior.coords
        for outer_ring in outer_rings:
            nodes = self._closed_ways.get(outer_ring)
            if not nodes:
                print(f"Discarding plaza {rel_id}, outer ring is not closed")
                return None
            if all([coords in nodes for coords in exterior_coords]):
                return outer_ring
        print(f"Discarding plaza {rel_id}: No outer ring found")
        return None


if __name__ == '__main__':
    holder = import_osm(PBF_PATH)
    # print(holder.plazas)