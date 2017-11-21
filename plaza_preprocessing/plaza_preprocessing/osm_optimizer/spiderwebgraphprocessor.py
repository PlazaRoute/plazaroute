from math import ceil
from plaza_preprocessing.osm_optimizer import utils
from shapely.geometry import Point, LineString


class SpiderWebGraphProcessor:
    """ Process a plaza with a spider web graph """
    def __init__(self, spacing_m):
        self.spacing_m = spacing_m

    def create_graph_edges(self, plaza_geometry, entry_points):
        """ create a spiderwebgraph and connect edges to entry points """
        if not plaza_geometry:
            raise ValueError("Plaza geometry not defined for spiderwebgraph processor")
        if not entry_points:
            raise ValueError("No entry points defined for spiderwebgraph processor")
        graph_edges = self._calc_spiderwebgraph(plaza_geometry)
        return self._connect_entry_points_with_graph(entry_points, graph_edges)

    def _calc_spiderwebgraph(self, plaza_geometry):
        """ calculate spider web graph edges"""
        spacing = utils.meters_to_degrees(self.spacing_m)
        x_left, y_bottom, x_right, y_top = plaza_geometry.bounds

        # based on https://github.com/michaelminn/mmqgis
        rows = int(ceil((y_top - y_bottom) / spacing))
        columns = int(ceil((x_right - x_left) / spacing))

        graph_edges = []

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
                    h_line = self._get_spiderweb_intersection_line(plaza_geometry, top_left, top_right)
                    if h_line:
                        graph_edges.append(h_line)

                # vertical line
                if row < rows:
                    v_line = self._get_spiderweb_intersection_line(plaza_geometry, top_left, bottom_left)
                    if v_line:
                        graph_edges.append(v_line)

                # diagonal line
                if row < rows and column < columns:  # TODO correct constraint?
                    d1_line = self._get_spiderweb_intersection_line(plaza_geometry, top_left, bottom_right)
                    if d1_line:
                        graph_edges.append(d1_line)
                    d2_line = self._get_spiderweb_intersection_line(plaza_geometry, bottom_left, top_right)
                    if d2_line:
                        graph_edges.append(d2_line)
        return graph_edges

    def _get_spiderweb_intersection_line(self, plaza_geometry, start, end):
        """ returns a line that is completely inside the plaza, if possible """
        line = LineString([start, end])
        if not utils.line_visible(plaza_geometry, line):
            return None
        return line

    def _connect_entry_points_with_graph(self, entry_points, graph_edges):
        connection_lines = []
        for entry_point in entry_points:
            neighbor_line = utils.find_nearest_geometry(entry_point, graph_edges)

            target_point = min(
                neighbor_line.coords, key=lambda c: Point(c).distance(entry_point))
            connection_line = (LineString([(entry_point.x, entry_point.y), target_point]))
            connection_lines.append(connection_line)
        graph_edges.extend(connection_lines)
        return graph_edges
