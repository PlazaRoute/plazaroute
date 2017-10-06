from qgis.networkanalysis import *

def get_layer(layerName):
    layerList = QgsMapLayerRegistry.instance().mapLayersByName(layerName)
    if not layerList:
        raise Exception("Failed to select layer.")
    return layerList[0]  # should only return one layer


def get_feature(featureId, layer):
    expr = QgsExpression('"id"=%d' % featureId)
    features = layer.getFeatures(QgsFeatureRequest(expr))
    if not features:
        raise Exception("Failed to retrieve feature.")
    return features  # should only return one feature


def get_nodes(feature):
    geom = feature.geometry()
    if geom.type() == QGis.Polygon:
        if geom.isMultipart():
            nodes = geom.asMultiPolygon()
        else:
            nodes = [geom.asPolygon()]
    elif geom.type() == QGis.Point:
        nodes = geom.asPoint()  # return a single point
    return nodes


def remove_layer_if_it_exists(name):
    layers = QgsMapLayerRegistry.instance().mapLayers()
    for memname, layer in layers.iteritems():
        if memname.startswith(name):
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())


def create_line_memory_layer(name):
    memLayer = QgsVectorLayer(
        "linestring?crs=epsg:4326&field=MYNUM:integer&field=MYTXT:string", name, "memory")
    remove_layer_if_it_exists(name)
    QgsMapLayerRegistry.instance().addMapLayer(memLayer)
    return memLayer


def get_features_inside_plaza(features, plaza):
    plaza_geom = plaza.geometry()
    found_features = []
    for p in features:
        if plaza_geom.contains(p.geometry()):
            found_features.append(p)
    return found_features


def create_visibility_graph(plaza, point_layer):
    enclosed_features = get_features_inside_plaza(point_layer.getFeatures(), plaza)
    plaza_nodes = get_nodes(plaza)[0][0]
    enclosed_nodes = [get_nodes(p) for p in enclosed_features]
    all_nodes = plaza_nodes + enclosed_nodes

    memLayer = create_line_memory_layer('helvetiaplatz_graph')
    edges = calc_visiblity_graph_edges(memLayer, all_nodes)
    return all_nodes, memLayer, edges


def calc_visiblity_graph_edges(memLayer, nodes):
    edges = []
    for start in nodes:
        for target in nodes:
            if (start != target):
                line = QgsFeature(memLayer.pendingFields())
                line.setGeometry(QgsGeometry.fromPolyline([start, target]))
                edges.append(line)
    return edges


def draw_features(layer, features):
    layer.dataProvider().addFeatures(features)
    QgsMapLayerRegistry.instance().addMapLayer(layer)


def edge_is_inside_plaza(plaza, edge):
    intersection = plaza.geometry().intersection(edge.geometry())
    # if polyline is empty, the line isn't entirely inside the plaza
    if intersection.asPolyline():
        return True
    return False


def get_shortest_path(graph_layer, points, from_point, to_point):
    # prepare graph
    director = QgsLineVectorLayerDirector(graph_layer, -1, '', '', '', 3)
    properter = QgsDistanceArcProperter()
    director.addProperter(properter)
    crs = graph_layer.crs()
    builder = QgsGraphBuilder(crs)

    tiedPoints = director.makeGraph(builder, points)
    graph = builder.graph()

    from_id = graph.findVertex(from_point)
    to_id = graph.findVertex(to_point)

    (tree, cost) = QgsGraphAnalyzer.dijkstra(graph, from_id, 0)

    route_points = []
    curPos = to_id
    while (curPos != from_id):
        route_points.append(graph.vertex(graph.arc(tree[curPos]).inVertex()).point())
        curPos = graph.arc(tree[curPos]).outVertex()

        route_points.append(from_point)

    return route_points


plaza_layer = get_layer('helvetiaplatz_plazas')
point_layer = get_layer('helvetiaplatz_points_amenities')

plaza_features = plaza_layer.getFeatures()
plaza = next(plaza_features)  # there's only one
all_nodes, memLayer, edges = create_visibility_graph(plaza, point_layer)
filtered_edges = filter(lambda e: edge_is_inside_plaza(plaza, e), edges)
draw_features(memLayer, filtered_edges)

sp_layer = create_line_memory_layer('shortest_paths')

for node in all_nodes[1:]:
    route_points = get_shortest_path(memLayer, all_nodes, all_nodes[0], node)

    route_line = QgsFeature(memLayer.pendingFields())
    route_line.setGeometry(QgsGeometry.fromPolyline(route_points))
    draw_features(sp_layer, [route_line])
