import osmium
from osmium._osmium import InvalidLocationError
import shapely.wkb as wkblib

WKBFAB = osmium.geom.WKBFactory()


def import_osm(filename):
    """ imports a OSM / PBF file and returns a holder with all plazas, buildings,
    lines and points with shapely geometries """
    handler = _PlazaHandler()
    # index_type = 'dense_file_array' # uses over 25GB of space for Switzerland
    index_type = 'sparse_mem_array'
    handler.apply_file(filename, locations=True, idx=index_type)
    print(f'{len(handler.plazas)} plazas')
    print(f'{len(handler.buildings)} buildings')
    print(f'{len(handler.lines)} lines')
    print(f'{len(handler.points)} points')

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
        super().__init__()
        self.plazas = []
        self.buildings = []
        self.points = []
        self.lines = []
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
                geometry = wkblib.loads(wkb, hex=True)
                self.lines.append({'id': w.id, 'geometry': geometry})
            except InvalidLocationError:
                print(f'Invalid location in {w.id}')
                self.invalid_count += 1
            except RuntimeError as ex:
                print(f'Error with {w.id}, {len(w.nodes)} nodes: {ex}')
                self.invalid_count += 1

    def area(self, a):
        if a.tags.get("highway") == "pedestrian" and a.tags.get("area") != "no":
            multipolygon = self._create_multipolygon_geometry(a)

            for polygon in multipolygon.geoms:
                plaza = {
                    'osm_id': a.orig_id(),
                    'geometry': polygon
                }
                self.plazas.append(plaza)

        elif "building" in a.tags and a.tags.get("layer", "0") == "0":
            geom = self._create_multipolygon_geometry(a)
            self.buildings.append(geom)

    def _create_multipolygon_geometry(self, multipolygon):
        wkb = WKBFAB.create_multipolygon(multipolygon)
        return wkblib.loads(wkb, hex=True)
