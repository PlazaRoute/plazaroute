from plaza_preprocessing import osm_importer as importer
from plaza_preprocessing.osm_merger import geojson_writer
from math import ceil
from shapely.geometry import (Point, MultiPoint, LineString, MultiLineString,
                              MultiPolygon, box)


class PlazaPreprocessor:

    def __init__(self, osm_id, plaza_geometry, lines, buildings, points):
        self.osm_id = osm_id
        self.plaza_geometry = plaza_geometry
        self.lines = lines
        self.buildings = buildings
        self.points = points

    def process_plaza(self):
        """ process a single plaza """
        entry_points = self._calc_entry_points()
        if not entry_points:
            print(f"Plaza {self.osm_id} has no entry points")
            return
        self._insert_obstacles()
        geojson_writer.write_geojson([self.plaza_geometry], 'plaza.geojson')

        # graph_edges = self.create_visibility_graph(entry_points)
        graph_edges = self.create_spiderweb_graph(entry_points)
        geojson_writer.write_geojson(graph_edges, 'edges.geojson')

    def _calc_entry_points(self):
        """
        calculate points where lines intersect with the outer ring of the plaza
        """
        intersecting_lines = self._find_intersescting_lines()

        entry_points = []
        for line in intersecting_lines:
            intersection = line.intersection(self.plaza_geometry)
            intersection_type = type(intersection)
            if intersection_type == Point:
                entry_points.append(intersection)
            elif intersection_type == MultiPoint:
                entry_points.extend(list(intersection))
            else:
                intersection_coords = []
                if intersection_type == MultiLineString:
                    intersection_coords.extend(
                        [c for line in intersection for c in line.coords])
                else:
                    intersection_coords = list(intersection.coords)
                intersection_points = list(map(Point, intersection_coords))
                entry_points.extend(
                    [p for p in intersection_points if self.plaza_geometry.touches(p)])

        return entry_points

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
            plaza_geometry = max(self.plaza_geometry, key=lambda p: p.area)

    def _find_intersecting_buildings(self):
        """ finds all buildings on the plaza that have not been cut out"""
        return list(filter(self.plaza_geometry.intersects, self.buildings))

    def _get_points_inside_plaza(self):
        """ finds all points that are on the plaza geometry """
        return list(filter(self.plaza_geometry.intersects, self.points))

    def _create_point_obstacle(self, point, buffer=5):
        """ create a polygon around a point with a buffer in meters """
        buffer_deg = self.meters_to_degrees(buffer)
        min_x = point.x - buffer_deg
        min_y = point.y - buffer_deg
        max_x = point.x + buffer_deg
        max_y = point.y + buffer_deg
        return box(min_x, min_y, max_x, max_y)

    def create_visibility_graph(self, entry_points):
        """ create a visibility graph with all plaza and entry points """
        plaza_coords = self.get_polygon_coords(
            self.plaza_geometry)  # TODO: extract
        entry_coords = [(p.x, p.y) for p in entry_points]
        all_coords = set().union(plaza_coords, entry_coords)
        indexed_coords = {i: coords for i, coords in enumerate(all_coords)}
        edges = []
        for start_id, start_coords in indexed_coords.items():
            for end_id, end_coords in indexed_coords.items():
                if (start_id > end_id):
                    line = LineString([start_coords, end_coords])
                    if self._line_visible(line):
                        edges.append(line)
        return edges

    def _line_visible(self, line):
        """ check if the line is "visible", i.e. unobstructed through the plaza """
        return line.equals(self.plaza_geometry.intersection(line))

    def get_polygon_coords(self, polygon):
        """ return a list of coordinates of all points in a multipolygon """
        coords = list(polygon.exterior.coords)
        for ring in polygon.interiors:
            coords.extend(ring.coords)
        return coords

    def create_spiderweb_graph(self, entry_points, spacing_m=1):
        """ create a spiderwebgraph and connect edges to entry points """
        graph_edges = self.calc_spiderwebgraph(spacing_m)
        return graph_edges

    def calc_spiderwebgraph(self, spacing_m):
        """ calculate spider web graph edges"""
        spacing = self.meters_to_degrees(spacing_m)
        x_left, y_bottom, x_right, y_top = self.plaza_geometry.bounds

        # based on https://github.com/michaelminn/mmqgis
        rows = int(ceil((y_top - y_bottom) / spacing))
        columns = int(ceil((x_right - x_left) / spacing))

        graph_lines = []
        for column in range(0, columns + 1):
            for row in range(0, rows + 1):

                x_1 = x_left + (column * spacing)
                x_2 = x_left + ((column + 1) * spacing)
                y_1 = y_bottom + (row * spacing)
                y_2 = y_bottom + ((row + 1) * spacing)

                top_left = (x_1, y_1)
                top_right = (x_2, y_1)
                bottom_left = (x_1, y_2)
                bottom_right = (x_2, y_2)

                # horizontal line
                if column < columns:
                    graph_lines.append(
                        self._get_spiderweb_intersection_line(top_left, top_right))

                # vertical line
                if row < rows:
                    graph_lines.append(
                        self._get_spiderweb_intersection_line(top_left, bottom_left))

                # diagonal line
                if row < rows and column < columns:  # TODO correct constraint?
                    graph_lines.append(
                        self._get_spiderweb_intersection_line(top_left, bottom_right))
                    graph_lines.append(
                        self._get_spiderweb_intersection_line(bottom_left, top_right))

        return graph_lines

    def _get_spiderweb_intersection_line(self, start, end):
        """ returns a line that is completely inside the plaza, if possible """
        line = LineString([start, end])
        # if not line_visible(line, plaza_geometry):
        if not self.plaza_geometry.intersects(line):
            return None
        return self.plaza_geometry.intersection(line)

    def line_in_plaza_approx(self, line, plaza_geometry, buffer=0):
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
        return self._bounding_boxes_overlap(min_x1, min_y1, max_x1, max_y1, *line_bbox)

    def _bounding_boxes_overlap(self, min_x1, min_y1, max_x1, max_y1, min_x2, min_y2, max_x2, max_y2):
        """ takes two bounding boxes and checks if they overlap """
        if min_x1 <= min_x2 and max_x1 <= min_x2:
            return False
        if min_y1 <= min_y2 and max_y1 <= min_y2:
            return False
        if min_x1 >= max_x2 or min_y1 >= max_y2:
            return False

        return True

    def point_in_plaza_bbox(self, point, plaza_geometry):
        """ determines whether a point is inside the bounding box of the plaza """
        min_x, min_y, max_x, max_y = plaza_geometry.bounds
        return self.point_in_bounding_box(point, min_x, min_y, max_x, max_y)

    def point_in_bounding_box(self, point, min_x, min_y, max_x, max_y):
        if point.x < min_x or point.x > max_x:
            return False
        if point.y < min_y or point.y > max_y:
            return False
        return True

    def meters_to_degrees(self, meters):
        """ convert meters to approximate degrees """
        #  meters * 360 / (2 * PI * 6400000)
        # multiply by (1/cos(lat) for longitude)
        return meters * 1 / 111701


def preprocess_plazas(osm_holder):
    """ preprocess all plazas from osm_importer """
    # test for helvetiaplatz
    # plaza = next(p for p in osm_holder.plazas if p['osm_id'] == 4533221)
    # test for Bahnhofplatz Bern
    # plaza = next(p for p in osm_holder.plazas if p['osm_id'] == 5117701)
    # processor = PlazaPreprocessor(
    #   plaza['geometry'], osm_holder.lines, osm_holder.buildings, osm_holder.points)
    # processor.process_plaza()

    for plaza in osm_holder.plazas:
        print(f"processing plaza {plaza['osm_id']}")
        if isinstance(plaza['geometry'], MultiPolygon):
            for polygon in plaza['geometry']:
                processor = PlazaPreprocessor(
                   plaza['osm_id'], polygon, osm_holder.lines, osm_holder.buildings, osm_holder.points)
                processor.process_plaza()

        else:
            processor = PlazaPreprocessor(
                plaza['osm_id'], plaza, osm_holder.lines, osm_holder.buildings, osm_holder.points)
            processor.process_plaza()


if __name__ == '__main__':
    # holder = importer.import_osm('data/helvetiaplatz_umfeld.osm')
    holder = importer.import_osm('data/switzerland-exact.osm.pbf')
    preprocess_plazas(holder)
