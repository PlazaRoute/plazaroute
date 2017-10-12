plaza_layer = get_layer('helvetiaplatz plazas')
draw_spiderweb_graph(plaza_layer, 45, 0.00001)


plaza_features = plaza_layer.getFeatures()
plaza = next(plaza_features)
line_layer = get_layer('helvetiaplatz lines')

intersecting_features = get_intersecting_features(plaza, line_layer)
entry_points = get_entry_points(plaza, intersecting_features)
print len(entry_points)

spiderweb_layer = get_layer('spiderweb1')

connect_entry_points_with_spiderwebgraph(spiderweb_layer, entry_points)

#remove_layer_if_it_exists('shortest_paths')
#sp_layer = create_line_memory_layer('shortest_paths')
#result_edges = calc_shortest_paths(entry_points, spiderweb_layer)
#draw_edges(sp_layer, result_edges)
