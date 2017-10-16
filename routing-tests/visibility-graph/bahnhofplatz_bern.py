plaza_layer = get_layer('bahnhofplatz_bern plazas')
point_layer = get_layer('bahnhofplatz_bern points')
line_layer = get_layer('bahnhofplatz_bern lines')
building_layer = get_layer('bahnhofplatz_bern buildings')

plaza_features = plaza_layer.getFeatures()
plaza = get_feature(6, plaza_layer)

remove_layer_if_it_exists('shortest_paths')
sp_layer = create_line_memory_layer('shortest_paths')
result_edges = create_visibility_graph(plaza, building_layer, line_layer, point_layer)
draw_edges(sp_layer, result_edges)
