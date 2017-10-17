#!/bin/python

def create_visibility_graph(plaza, building_layer, line_layer, point_layer):
    intersecting_buildings = find_buildings_inside_plaza(plaza, building_layer)
    obstacle_geom = create_obstacle_geometry(plaza, intersecting_buildings)
    intersecting_features = get_intersecting_features(plaza, line_layer)
    entry_points = get_entry_points(plaza, intersecting_features)
    point_features = get_points_inside_plaza(point_layer.getFeatures(), plaza, obstacle_geom)

    draw_entry_points(entry_points)

    vis_graph_nodes = get_visibility_graph_nodes(plaza, obstacle_geom, point_features, entry_points)
    remove_layer_if_it_exists('visibility_graph')
    graph_layer = create_line_memory_layer('visibility_graph')

    vis_graph_edges = calc_visiblity_graph_edges(graph_layer, vis_graph_nodes)
    filtered_edges = filter(lambda e: edge_is_inside_plaza(plaza, obstacle_geom, e), vis_graph_edges)
    draw_features(graph_layer, filtered_edges)

    return calc_shortest_paths(entry_points, graph_layer)


def draw_entry_points(entry_points):
    remove_layer_if_it_exists('entry_points')
    entry_point_layer = create_point_memory_layer('entry_points')
    entry_point_features = []
    for p in entry_points:
        f = QgsFeature(entry_point_layer.pendingFields())
        f.setGeometry(QgsGeometry.fromPoint(p))
        entry_point_features.append(f)
    draw_features(entry_point_layer, entry_point_features)


def get_visibility_graph_nodes(plaza, obstacle_geom, point_features, entry_points):
    plaza_nodes = get_nodes(plaza)
    obstacle_nodes = unpack_multipolygon(obstacle_geom)
    enclosed_nodes = [get_nodes(p) for p in point_features]
    nodes = set().union(plaza_nodes, enclosed_nodes, obstacle_nodes, entry_points)
    print('regarded %d nodes for visibility graph' % len(nodes))
    return nodes


def calc_visiblity_graph_edges(memLayer, nodes):
    edges = []
    indexed_nodes = {i: node for i, node in enumerate(nodes)}
    for start_id, start_node in indexed_nodes.items():
        for target_id, target_node in indexed_nodes.items():
            if (start_id > target_id):
                line = QgsFeature(memLayer.pendingFields())
                line.setGeometry(QgsGeometry.fromPolyline([start_node, target_node]))
                edges.append(line)
    return edges
