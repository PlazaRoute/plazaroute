plaza_layer = get_layer('helvetiaplatz plazas')
point_layer = get_layer('helvetiaplatz points')
line_layer = get_layer('helvetiaplatz lines')
building_layer = get_layer('helvetiaplatz buildings')

plaza_features = plaza_layer.getFeatures()
plaza = get_feature(1, plaza_layer)

remove_layer_if_it_exists('shortest_paths')
sp_layer = create_line_memory_layer('shortest_paths')
result_edges = create_visibility_graph(plaza, building_layer, line_layer, point_layer)
draw_edges(sp_layer, result_edges)
