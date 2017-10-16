plaza_layer = get_layer('bahnhofplatz_bern plazas')
point_layer = get_layer('bahnhofplatz_bern points')
line_layer = get_layer('bahnhofplatz_bern lines')
building_layer = get_layer('bahnhofplatz_bern buildings')

plaza_features = plaza_layer.getFeatures()
plaza = get_feature(6, plaza_layer)

remove_layer_if_it_exists('spiderweb_graph')
graph_layer = create_line_memory_layer('spiderweb_graph')

intersecting_buildings = find_buildings_inside_plaza(plaza, building_layer)
obstacle_geom = create_obstacle_geometry(plaza, intersecting_buildings)

spacing = 0.5* 10**-5
create_spiderweb_graph(graph_layer, plaza, spacing, obstacle_geom)

intersecting_features = get_intersecting_features(plaza, line_layer)
entry_points = get_entry_points(plaza, intersecting_features)
connect_entry_points_with_spiderweb_graph(graph_layer, entry_points)

remove_layer_if_it_exists('shortest_paths')
sp_layer = create_line_memory_layer('shortest_paths')
result_edges = calc_shortest_paths(entry_points, graph_layer)
draw_edges(sp_layer, result_edges)
