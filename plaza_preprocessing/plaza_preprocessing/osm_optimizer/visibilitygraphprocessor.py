from plaza_preprocessing.osm_optimizer import utils
from shapely.geometry import LineString


class VisibilityGraphProcessor:
    """ process a plaza using a visibility graph """
    def __init__(self):
        self.plaza_geometry = None
        self.entry_points = []
        self.graph_edges = []

    def create_graph_edges(self):
        """ create a visibility graph with all plaza and entry points """
        if not self.plaza_geometry:
            raise ValueError("Plaza geometry not defined for visibility graph processor")
        if not self.entry_points:
            raise ValueError("No entry points defined for graph processor")

        plaza_coords = utils.get_polygon_coords(self.plaza_geometry)
        entry_coords = [(p.x, p.y) for p in self.entry_points]
        all_coords = set().union(plaza_coords, entry_coords)
        indexed_coords = {i: coords for i, coords in enumerate(all_coords)}
        for start_id, start_coords in indexed_coords.items():
            for end_id, end_coords in indexed_coords.items():
                if (start_id > end_id):
                    line = LineString([start_coords, end_coords])
                    if self._line_visible(line):
                        self.graph_edges.append(line)

    def _line_visible(self, line):
        """ check if the line is "visible", i.e. unobstructed through the plaza """
        return line.equals(self.plaza_geometry.intersection(line))
