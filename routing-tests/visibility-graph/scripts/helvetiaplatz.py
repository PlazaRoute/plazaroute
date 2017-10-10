plaza_layer = get_layer('helvetiaplatz plazas')
point_layer = get_layer('helvetiaplatz points')
line_layer = get_layer('helvetiaplatz lines')

plaza_features = plaza_layer.getFeatures()
plaza = next(plaza_features)  # there's only one

remove_layer_if_it_exists('helvetiaplatz_graph')
graph_layer = create_line_memory_layer('helvetiaplatz_graph')
graph_nodes, graph_edges = create_visibility_graph(plaza, point_layer, graph_layer)
filtered_edges = filter(lambda e: edge_is_inside_plaza(plaza, e), graph_edges)
draw_features(graph_layer, filtered_edges)

intersecting_features = get_intersecting_features(plaza, line_layer)
# entry_line_layer = create_line_memory_layer('entry_lines')
# draw_features(entry_line_layer, intersecting_features)
entry_points = get_entry_points(plaza, intersecting_features)
# remove_layer_if_it_exists('entry_points')
# entry_point_layer = create_point_memory_layer('entry_points')
# for p in entry_points:
#     f = QgsFeature(entry_point_layer.pendingFields())
#     f.setGeometry(QgsGeometry.fromPoint(p))
#     draw_features(entry_point_layer, [f])

remove_layer_if_it_exists('shortest_paths')
sp_layer = create_line_memory_layer('shortest_paths')
result_edges = calc_shortest_paths(entry_points, graph_layer)
draw_edges(sp_layer, result_edges)
