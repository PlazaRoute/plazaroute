import osmium
import shapely.wkb as wkblib

# PBF_PATH = "data/helvetiaplatz_umfeld.osm"
PBF_PATH = "data/switzerland-exact.osm.pbf"

WKBFAB = osmium.geom.WKBFactory()


def import_osm(filename):
    """ imports a OSM / PBF file and returns a list of all plazas with shapely geometries """
    handler = _PlazaHandler()
    # index_type = 'dense_file_array' # uses over 25GB of space for Switzerland
    index_type = 'sparse_mem_array'
    handler.apply_file(filename, locations=False, idx=index_type)
    print(len(handler.plazas))
    handler.add_missing_ring_ids()

    return handler.plazas

class _PlazaHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.plazas = []
        self.relations = {}

    def area(self, a):
        if a.tags.get("highway") == "pedestrian" and not a.tags.get("area") == "no":
            wkb = WKBFAB.create_multipolygon(a)
            area = {
                'osm_id': a.orig_id(),
                'geometry': wkblib.loads(wkb, hex=True),
                'is_relation': not a.from_way(),
                'outer_ring_ids': []
            }

            self.plazas.append(area)

    def relation(self, r):
        if r.tags.get("highway") == "pedestrian" and not r.tags.get("area") == "no":
            outer_rings = []
            for member in r.members:
                if member.role == "outer":
                    outer_rings.append(member.ref)

            self.relations[r.replace().id] = outer_rings

    def add_missing_ring_ids(self):
        """ Adds OSM ids of outer rings to plazas that are relations """
        for plaza in self.plazas:
            osm_id = plaza['osm_id']
            if plaza['is_relation']:
                if osm_id not in self.relations:
                    raise KeyError(f'Plaza {osm_id} is not in relations!')
                plaza['outer_ring_ids'] = self.relations.get(osm_id)


if __name__ == '__main__':
    import_osm(PBF_PATH)
