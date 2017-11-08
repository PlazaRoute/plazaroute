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

    def node(self, node):
        if self._is_relevant_node(node):
            point_wkb = WKBFAB.create_point(node)
            point_geometry = wkblib.loads(point_wkb, hex=True)
            self.points.append(point_geometry)

    def way(self, way):
        if self._is_relevant_way(way):
            try:
                line_wkb = WKBFAB.create_linestring(way)
                line_geometry = wkblib.loads(line_wkb, hex=True)
                self.lines.append({'id': way.id, 'geometry': line_geometry})
            except InvalidLocationError:
                print(f'Invalid location in {way.id}')
                self.invalid_count += 1
            except RuntimeError as ex:
                print(f'Error with {way.id}, {len(way.nodes)} nodes: {ex}')
                self.invalid_count += 1

    def area(self, area):
        if self._is_plaza(area):
            multipolygon_wkb = WKBFAB.create_multipolygon(area)
            multipolygon_geom = wkblib.loads(multipolygon_wkb, hex=True)

            for polygon in multipolygon_geom.geoms:
                plaza = {
                    'osm_id': area.orig_id(),
                    'geometry': polygon
                }
                self.plazas.append(plaza)

        elif self._is_relevant_building(area):
            building_wkb = WKBFAB.create_multipolygon(area)
            building_geom = wkblib.loads(building_wkb, hex=True)
            self.buildings.append(building_geom)

    def _is_relevant_node(self, node):
        return "amenity" in node.tags and \
            "indoor" not in node.tags and \
            node.tags.get("level", "0") == "0" and \
            node.tags.get("layer", "0") == "0"

    def _is_relevant_way(self, way):
        return not way.is_closed() and \
            "highway" in way.tags or \
            way.tags.get("railway") == "tram"

    def _is_plaza(self, area):
        return area.tags.get("highway") == "pedestrian" and \
            area.tags.get("area") != "no"

    def _is_relevant_building(self, area):
        return "building" in area.tags \
            and area.tags.get("layer", "0") == "0"
