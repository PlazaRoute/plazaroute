import logging
import osmium
from osmium._osmium import InvalidLocationError
import shapely.wkb as wkblib
from plaza_preprocessing.importer import osmholder
from plaza_preprocessing import configuration

logger = logging.getLogger('plaza_preprocessing.importer')
WKBFAB = osmium.geom.WKBFactory()


def import_osm(filename, tag_filters):
    """ imports a OSM / PBF file and returns a holder with all plazas, buildings,
    lines and points with shapely geometries """
    logger.info(f'importing {filename}')
    handler = _PlazaHandler(tag_filters)

    index_type = 'sparse_mem_array'
    handler.apply_file(filename, locations=True, idx=index_type)

    logger.debug(f'found {len(handler.plazas)} plazas')
    logger.debug(f'found {len(handler.buildings)} buildings')
    logger.debug(f'found {len(handler.lines)} lines')
    logger.debug(f'found {len(handler.points)} points')

    if handler.invalid_count > 0:
        logger.warning(f'encountered {handler.invalid_count} invalid objects (may be because of boundaries)')
    return osmholder.OSMHolder(handler.plazas, handler.buildings, handler.lines, handler.points)


class _PlazaHandler(osmium.SimpleHandler):
    def __init__(self, tag_filters):
        super().__init__()
        self.tag_filters = tag_filters
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
                logger.debug(f'Encountered invalid location in way {way.id}')
                self.invalid_count += 1
            except RuntimeError as ex:
                logger.debug(f'Error importing way {way.id}: {ex}')
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
        return configuration.filter_tags(area.tags, self.tag_filters['plaza'])

    def _is_relevant_building(self, area):
        return "building" in area.tags \
            and area.tags.get("layer", "0") == "0"
