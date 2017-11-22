from shapely.geometry import LineString, Polygon
from typing import List
from plaza_preprocessing.optimizer import utils
from plaza_preprocessing.optimizer.graphprocessor.graphprocessor import GraphProcessor


class VisibilityGraphProcessor(GraphProcessor):
    """ process a plaza using a visibility graph """

    def create_graph_edges(self, plaza_geometry, entry_points):
        """ create a visibility graph with all plaza and entry points """
        if not plaza_geometry:
            raise ValueError("Plaza geometry not defined for visibility graph processor")
        if not entry_points:
            raise ValueError("No entry points defined for graph processor")

        plaza_coords = utils.get_polygon_coords(plaza_geometry)
        entry_coords = [(p.x, p.y) for p in entry_points]
        all_coords = set().union(plaza_coords, entry_coords)
        indexed_coords = {i: coords for i, coords in enumerate(all_coords)}

        graph_edges = []
        for start_id, start_coords in indexed_coords.items():
            for end_id, end_coords in indexed_coords.items():
                if (start_id > end_id):
                    line = LineString([start_coords, end_coords])
                    if utils.line_visible(plaza_geometry, line):
                        graph_edges.append(line)
        return graph_edges

    def optimize_lines(self, plaza_geometry: Polygon, lines: List[LineString], tolerance_m: float) -> List[LineString]:
        return lines
