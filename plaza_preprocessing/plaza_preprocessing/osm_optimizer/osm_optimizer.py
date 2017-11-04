from plaza_preprocessing import osm_importer as importer
from plaza_preprocessing.osm_merger import geojson_writer
from plaza_preprocessing.osm_optimizer import helpers
from plaza_preprocessing.osm_optimizer.visibilitygraphprocessor import VisibilityGraphProcessor
from plaza_preprocessing.osm_optimizer.spiderwebgraphprocessor import SpiderWebGraphProcessor
from shapely.geometry import Point, LineString, MultiPolygon, box


class PlazaPreprocessor:

    def __init__(self, osm_id, plaza_geometry, osm_holder, graph_processor):
        self.osm_id = osm_id
        self.plaza_geometry = plaza_geometry
        self.lines = osm_holder.lines
        self.buildings = osm_holder.buildings
        self.points = osm_holder.points
        self.graph_processor = graph_processor
        self.entry_points = []

    def process_plaza(self):
        """ process a single plaza """
        self._calc_entry_points()

        if len(self.entry_points) < 2:
            print(f"Plaza {self.osm_id} has fewer than 2 entry points")
            return

        self._insert_obstacles()
        if not self.plaza_geometry:
            # TODO: Log
            print(f"Plaza {self.osm_id} is completely obstructed by obstacles")
            return

        geojson_writer.write_geojson([self.plaza_geometry], 'plaza.geojson')

        self.graph_processor.entry_points = self.entry_points
        self.graph_processor.plaza_geometry = self.plaza_geometry
        self.graph_processor.create_graph_edges()
        geojson_writer.write_geojson(
            self.graph_processor.graph_edges, 'edges.geojson')

        return self.graph_processor.graph_edges

    def _calc_entry_points(self):
        """
        calculate points where lines intersect with the outer ring of the plaza
        """
        intersecting_lines = self._find_intersescting_lines()

        for line in intersecting_lines:
            intersection = line.intersection(self.plaza_geometry)

            intersection_coords = helpers.unpack_geometry_coordinates(
                intersection)
            intersection_points = list(map(Point, intersection_coords))
            self.entry_points.extend(
                [p for p in intersection_points if self.plaza_geometry.touches(p) and p not in self.entry_points])

    def _find_intersescting_lines(self):
        """ return every line that intersects with the plaza """
        # filtering is slower than checking every line
        # bbox_buffer = 5 * 10**-3  # about 500m
        # lines_in_approx = list(
        #     filter(lambda l: line_in_plaza_approx(l, plaza_geometry, buffer=bbox_buffer), lines))
        return list(filter(self.plaza_geometry.intersects, self.lines))

    def _insert_obstacles(self):
        """ cuts out holes for obstacles on the plaza geometry """
        intersecting_buildings = self._find_intersecting_buildings()

        for building in intersecting_buildings:
            self.plaza_geometry = self.plaza_geometry.difference(building)

        points_on_plaza = self._get_points_inside_plaza()
        point_obstacles = list(
            map(lambda p: self._create_point_obstacle(p, buffer=2), points_on_plaza))

        for p_obstacle in point_obstacles:
            self.plaza_geometry = self.plaza_geometry.difference(p_obstacle)

        if isinstance(self.plaza_geometry, MultiPolygon):
            print("Multipolygon after cut out!")
            # take the largest of the polygons
            self.plaza_geometry = max(
                self.plaza_geometry, key=lambda p: p.area)

    def _find_intersecting_buildings(self):
        """ finds all buildings on the plaza that have not been cut out"""
        return list(filter(self.plaza_geometry.intersects, self.buildings))

    def _get_points_inside_plaza(self):
        """ finds all points that are on the plaza geometry """
        return list(filter(self.plaza_geometry.intersects, self.points))

    def _create_point_obstacle(self, point, buffer=5):
        """ create a polygon around a point with a buffer in meters """
        buffer_deg = helpers.meters_to_degrees(buffer)
        min_x = point.x - buffer_deg
        min_y = point.y - buffer_deg
        max_x = point.x + buffer_deg
        max_y = point.y + buffer_deg
        return box(min_x, min_y, max_x, max_y)

    def _line_in_plaza_approx(self, line, plaza_geometry, buffer=0):
        """
        determines if a line's bounding box is in the bounding box of the plaza,
        with optional buffer in degrees (enlarged bounding box)
        """
        min_x1, min_y1, max_x1, max_y1 = plaza_geometry.bounds
        line_bbox = line.bounds
        min_x1 -= buffer / 2
        min_y1 -= buffer / 2
        max_x1 += buffer / 2
        max_y1 += buffer / 2
        return helpers.bounding_boxes_overlap(min_x1, min_y1, max_x1, max_y1, *line_bbox)

    def _point_in_plaza_bbox(self, point, plaza_geometry):
        """ determines whether a point is inside the bounding box of the plaza """
        min_x, min_y, max_x, max_y = plaza_geometry.bounds
        return helpers.point_in_bounding_box(point, min_x, min_y, max_x, max_y)


def preprocess_plazas(osm_holder):
    """ preprocess all plazas from osm_importer """
    # test for helvetiaplatz
    # plaza = next(p for p in osm_holder.plazas if p['osm_id'] == 4533221)
    # test for Bahnhofplatz Bern
    # plaza = next(p for p in osm_holder.plazas if p['osm_id'] == 5117701)
    # plaza = next(p for p in osm_holder.plazas if p['osm_id'] == 182055194)

    # processor = PlazaPreprocessor(
    #     plaza['osm_id'], plaza['geometry'], osm_holder, SpiderWebGraphProcessor(spacing_m=2))
    # processor.process_plaza()

    for plaza in osm_holder.plazas:
        print(f"processing plaza {plaza['osm_id']}")
        processor = PlazaPreprocessor(
            plaza['osm_id'], plaza['geometry'], osm_holder, SpiderWebGraphProcessor(spacing_m=5))
        plaza['graph_edges'] = processor.process_plaza()
        plaza['entry_points'] = processor.entry_points


if __name__ == '__main__':
    # holder = importer.import_osm('data/helvetiaplatz_umfeld.osm')
    # holder = importer.import_osm('data/switzerland-exact.osm.pbf')
    holder = importer.import_osm('data/stadt-zuerich.pbf')
    preprocess_plazas(holder)
