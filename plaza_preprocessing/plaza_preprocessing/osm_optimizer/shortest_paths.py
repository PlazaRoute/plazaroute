import logging
import time
import networkx as nx
from shapely.geometry import LineString, Point
from typing import List, Tuple, Set, Dict

logger = logging.getLogger('plaza_preprocessing.osm_optimizer')


def create_graph(graph_edges: List[LineString]) -> nx.Graph:
    """ create a networkx graph with a collection of edges"""
    graph = nx.Graph()
    graph.add_nodes_from(_collect_nodes(graph_edges))
    graph.add_edges_from(_collect_edges(graph_edges))
    return graph


def compute_dijkstra_shortest_paths(graph: nx.Graph, entry_points: List[Point]) -> List[LineString]:
    """
    compute a list of shortest paths as LineStrings between all pairs of entry points
    using the dijkstra algorithm
    """
    entry_coords = list(map(lambda point: (point.x, point.y), entry_points))
    start_time = time.perf_counter()
    paths = dict(nx.all_pairs_dijkstra_path(graph))
    shortest_lines = _extract_lines_between_entry_points(paths, entry_coords)
    end_time = time.perf_counter()
    elapsed_time_ms = (end_time - start_time) * 1000
    logger.debug(f"computed dijkstra shortest paths in {elapsed_time_ms:.2f} milliseconds")
    return shortest_lines


def compute_astar_shortest_paths(graph: nx.Graph, entry_points: List[Point]) -> List[LineString]:
    """
    compute a list of shortest paths as LineStrings between all pairs of entry points
    using the astar algorithm. Uses direct distance between entry points as a heuristic
    """
    entry_coords = list(map(lambda point: (point.x, point.y), entry_points))
    lines = []
    start_time = time.perf_counter()
    for start_node in entry_coords:
        for end_node in entry_coords:
            if start_node < end_node:
                try:
                    path = nx.astar_path(graph, start_node, end_node, heuristic=_distance_between_nodes)
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    logger.debug(f"no path between {start_node} and {end_node}, discarding path")
                    continue
                lines.append(LineString(path))
    end_time = time.perf_counter()
    elapsed_time_ms = (end_time - start_time) * 1000
    logger.debug(f"computed shortest paths with astar in {elapsed_time_ms:.2f} milliseconds")
    return lines


def _extract_lines_between_entry_points(shortest_paths: Dict, entry_coords: List[Tuple]) -> List[LineString]:
    """ create shortest lines between every pair of entry points"""
    lines = []
    for start_node in entry_coords:
        if start_node not in shortest_paths:
            logger.warning(f"entry point {start_node} is not reachable on the graph, discarding paths")
            continue
        for end_node in entry_coords:
            if start_node < end_node:
                path_start = shortest_paths[start_node]
                if end_node not in path_start:
                    logger.debug(f"entry point {end_node} is not reachable from {start_node}, discarding path")
                    continue
                path = path_start[end_node]
                lines.append(LineString(path))
    return lines


def _distance_between_nodes(node_1, node_2):
    x1, y1 = node_1
    x2, y2 = node_2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def _collect_nodes(graph_edges: List[LineString]) -> Set[Tuple[float, float]]:
    """" collect a set of nodes from all edges without duplicates """
    nodes = set()
    coordinates = (coords for line in graph_edges for coords in line.coords)
    for node_coords in coordinates:
        nodes.add(node_coords)
    return nodes


def _collect_edges(graph_edges: List[LineString]) -> List[Tuple[float, float, Dict[str, float]]]:
    """ collect edges with corresponding weights as the geometric distance between the points """
    edges = []
    for line in graph_edges:
        weight = _calculate_weight_of_line(line)
        edges.append((line.coords[0], line.coords[1], {'weight': weight}))
    return edges


def _calculate_weight_of_line(line: LineString) -> float:
    """ calculate the weight of a line as the distance between the points """
    weight = 0
    point = Point(line.coords[0])
    for coords in line.coords[1:]:
        next_point = Point(coords)
        weight += point.distance(next_point)
        point = next_point
    return weight
