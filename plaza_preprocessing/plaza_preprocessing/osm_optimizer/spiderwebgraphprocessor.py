from math import ceil
from plaza_preprocessing.osm_optimizer import helpers
from shapely.geometry import Point, LineString

class SpiderWebGraphProcessor:
    """ Process a plaza with a spider web graph """
    def __init__(self, spacing_m):
        self.spacing_m = spacing_m
        self.plaza_geometry = None
        self.entry_points = []
        self.graph_edges = []

    def create_graph_edges(self):
        """ create a spiderwebgraph and connect edges to entry points """
        if not self.plaza_geometry:
            raise ValueError("Plaza geometry not defined for spiderwebgraph processor")
        if not self.entry_points:
            raise ValueError("No entry points defined for spiderwebgraph processor")
        self._calc_spiderwebgraph()
        self._connect_entry_points_with_graph()

    def _calc_spiderwebgraph(self):
        """ calculate spider web graph edges"""
        spacing = helpers.meters_to_degrees(self.spacing_m)
        x_left, y_bottom, x_right, y_top = self.plaza_geometry.bounds

        # based on https://github.com/michaelminn/mmqgis
        rows = int(ceil((y_top - y_bottom) / spacing))
        columns = int(ceil((x_right - x_left) / spacing))

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
                    h_line = self._get_spiderweb_intersection_line(top_left, top_right)
                    if h_line:
                        self.graph_edges.append(h_line)

                # vertical line
                if row < rows:
                    v_line = self._get_spiderweb_intersection_line(top_left, bottom_left)
                    if v_line:
                        self.graph_edges.append(v_line)

                # diagonal line
                if row < rows and column < columns:  # TODO correct constraint?
                    d1_line = self._get_spiderweb_intersection_line(top_left, bottom_right)
                    if d1_line:
                        self.graph_edges.append(d1_line)
                    d2_line = self._get_spiderweb_intersection_line(bottom_left, top_right)
                    if d2_line:
                        self.graph_edges.append(d2_line)

    def _get_spiderweb_intersection_line(self, start, end):
        """ returns a line that is completely inside the plaza, if possible """
        line = LineString([start, end])
        # if not line_visible(line, plaza_geometry):
        if not self.plaza_geometry.intersects(line):
            return None
        intersection = self.plaza_geometry.intersection(line)
        return intersection if isinstance(intersection, LineString) else None

    def _connect_entry_points_with_graph(self):
        connection_lines = []
        for entry_point in self.entry_points:
            neighbor_line = helpers.find_nearest_geometry(entry_point, self.graph_edges)

            target_point = min(
                neighbor_line.coords, key=lambda c: Point(c).distance(entry_point))
            connection_line = (LineString([(entry_point.x, entry_point.y), target_point]))
            connection_lines.append(connection_line)
        self.graph_edges.extend(connection_lines)
