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
    # print(list(filter(lambda p: len(p['outer_ring_ids']) >2, handler.plazas)))
    print(f'encountered {handler.invalid_count} invalid ways')
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

    def area(self, a):
        if a.tags.get("highway") == "pedestrian" and a.tags.get("area") != "no":
            area = {
                'osm_id': a.orig_id(),
                'geometry': self._create_multipolygon_geometry(a),
                'is_relation': not a.from_way(),
                'outer_ring_ids': []
            }
            self.plazas.append(area)

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

    def _create_multipolygon_geometry(self, multipolygon):
        wkb = WKBFAB.create_multipolygon(multipolygon)
        return wkblib.loads(wkb, hex=True)

    def add_missing_ring_ids(self):
        """ Adds OSM ids of outer rings to plazas that are relations """
        for plaza in self.plazas:
            osm_id = plaza['osm_id']
            if plaza['is_relation']:
                if osm_id not in self._relations:
                    raise KeyError(f'Plaza {osm_id} is not in relations!')
                plaza['outer_ring_ids'] = self._relations.get(osm_id)


if __name__ == '__main__':
    import_osm(PBF_PATH)
