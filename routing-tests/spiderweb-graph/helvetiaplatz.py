plaza_layer = get_layer('helvetiaplatz plazas')
point_layer = get_layer('helvetiaplatz points')
line_layer = get_layer('helvetiaplatz lines')
building_layer = get_layer('helvetiaplatz buildings')

plaza_features = plaza_layer.getFeatures()
plaza = get_feature(1, plaza_layer)

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

remove_layer_if_it_exists('spiderweb_graph')
graph_layer = create_line_memory_layer('spiderweb_graph')

spiderweb_edges = draw_grid(graph_layer, plaza, 0.5* 10**-5, obstacle_geom)

connect_entry_points_with_spiderwebgraph(graph_layer, entry_points)

remove_layer_if_it_exists('shortest_paths')
sp_layer = create_line_memory_layer('shortest_paths')
result_edges = calc_shortest_paths(entry_points, graph_layer)
draw_edges(sp_layer, result_edges)
