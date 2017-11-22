import abc
from typing import List
from shapely.geometry import Polygon, Point, LineString


class GraphProcessor(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_graph_edges(self, plaza_geometry: Polygon, entry_points: List[Point]) -> List[LineString]:
        """
        create graph edges to connect all entry points
        """
        pass

    @abc.abstractmethod
    def optimize_lines(self, plaza_geometry: Polygon, lines: List[LineString], tolerance_m: float) -> List[LineString]:
        """
        optimize or simplify a list of shortest paths
        :param plaza_geometry: The geometry which the optimized lines must be inside of
        :param lines: a list of lines to optimize
        :param tolerance_m: new line will be inside this tolerance (in meters). Should be the same as obstacle buffer.
        :return: List of optimized LineStrings
        """
        pass
