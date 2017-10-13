plaza_layer = get_layer('bahnhofplatz_bern plazas')
point_layer = get_layer('bahnhofplatz_bern points')
line_layer = get_layer('bahnhofplatz_bern lines')
building_layer = get_layer('bahnhofplatz_bern buildings')

plaza_features = plaza_layer.getFeatures()
plaza = get_feature(6, plaza_layer)

intersecting_buildings = find_buildings_inside_plaza(plaza, building_layer)
obstacle_geom = create_obstacle_geometry(plaza, intersecting_buildings)

intersecting_features = get_intersecting_features(plaza, line_layer)

entry_points = get_entry_points(plaza, intersecting_features)
remove_layer_if_it_exists('entry_points')
entry_point_layer = create_point_memory_layer('entry_points')
entry_point_features = []
for p in entry_points:
    f = QgsFeature(entry_point_layer.pendingFields())
    f.setGeometry(QgsGeometry.fromPoint(p))
    entry_point_features.append(f)
draw_features(entry_point_layer, entry_point_features)


remove_layer_if_it_exists('bahnhofplatz_bern_graph')
graph_layer = create_line_memory_layer('bahnhofplatz_bern_graph')
point_features = get_points_inside_plaza(point_layer.getFeatures(), plaza, obstacle_geom)

graph_edges = create_visibility_graph(plaza, obstacle_geom, point_features, entry_points, graph_layer)
filtered_edges = filter(lambda e: edge_is_inside_plaza(plaza, obstacle_geom, e), graph_edges)
print("edges: %s" % len(filtered_edges))
draw_features(graph_layer, filtered_edges)

#entry_line_layer = create_line_memory_layer('entry_lines')
#draw_features(entry_line_layer, intersecting_features)
#


remove_layer_if_it_exists('shortest_paths')
sp_layer = create_line_memory_layer('shortest_paths')
result_edges = calc_shortest_paths(entry_points, graph_layer)
draw_edges(sp_layer, result_edges)
