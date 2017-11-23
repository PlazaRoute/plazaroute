from shapely.geometry import LineString, Point
from plaza_preprocessing.optimizer import shortest_paths


def test_create_graph_simple_edges():
    graph_edges = [LineString([(0, 0), (0, 1)]), LineString([(0, 1), (1, 1)]),
                   LineString([(1, 1), (1, 0)]), LineString([(0, 0), (1, 1)])]

    expected_edges = [((0.0, 1.0), (0.0, 0.0)), ((0.0, 1.0), (1.0, 1.0)),
                      ((1.0, 0.0), (1.0, 1.0)), ((0.0, 0.0), (1.0, 1.0))]

    graph = shortest_paths.create_graph(graph_edges)

    assert graph.number_of_nodes() == 4
    assert all(edge in graph.edges for edge in expected_edges)
    assert all(graph.edges.get(edge).get('weight') != 0 for edge in expected_edges)


def test_compute_dijkstra_shortest_paths():
    graph_edges = [LineString([(0, 0), (0, 1)]), LineString([(0, 1), (1, 1)]),
                   LineString([(1, 1), (1, 0)]), LineString([(0, 0), (1, 0)]),
                   LineString([(0, 0), (1, 1)]), LineString([(1, 1), (2, 1)])]

    entry_points = [Point((0, 0)), Point((2, 1)), Point((1, 0))]
    expected_lines = [[(0, 0), (1, 1), (2, 1)], [(0, 0), (1, 0)], [(1, 0), (1, 1), (2, 1)]]

    graph = shortest_paths.create_graph(graph_edges)
    lines = shortest_paths.compute_dijkstra_shortest_paths(graph, entry_points)
    assert expected_lines == [list(line.coords) for line in lines]


def test_compute_astar_shortest_paths():
    graph_edges = [LineString([(0, 0), (0, 1)]), LineString([(0, 1), (1, 1)]),
                   LineString([(1, 1), (1, 0)]), LineString([(0, 0), (1, 0)]),
                   LineString([(0, 0), (1, 1)]), LineString([(1, 1), (2, 1)])]

    entry_points = [Point((0, 0)), Point((2, 1)), Point((1, 0))]
    expected_lines = [[(0, 0), (1, 1), (2, 1)], [(0, 0), (1, 0)], [(1, 0), (1, 1), (2, 1)]]

    graph = shortest_paths.create_graph(graph_edges)
    lines = shortest_paths.compute_dijkstra_shortest_paths(graph, entry_points)
    assert expected_lines == [list(line.coords) for line in lines]
