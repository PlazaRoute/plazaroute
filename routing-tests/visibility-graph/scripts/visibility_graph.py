
from qgis.core import *
from qgis.gui import *
from qgis.networkanalysis import *
from PyQt4.QtCore import *


def get_layer(layerName):
    layerList = QgsMapLayerRegistry.instance().mapLayersByName(layerName)
    if not layerList:
        raise Exception("Failed to select layer.")
    return layerList[0]  # should only return one layer


def get_feature(featureId, layer):
    expr = QgsExpression('"fid"=%d' % featureId)
    features = layer.getFeatures(QgsFeatureRequest(expr))
    if not features:
        raise Exception("Failed to retrieve feature.")
    return next(features)  # should only return one feature


def get_nodes(feature):
    geom = feature.geometry()
    if geom.type() == QGis.Polygon:
        if geom.isMultipart():
            all_nodes = geom.asMultiPolygon()[0]
            nodes = []
            [nodes.extend(n) for n in all_nodes]
        else:
            nodes = geom.asPolygon()
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


def create_point_memory_layer(name):
        memLayer = QgsVectorLayer(
            "point?crs=epsg:4326&field=MYNUM:integer&field=MYTXT:string", name, "memory")
        QgsMapLayerRegistry.instance().addMapLayer(memLayer)
        return memLayer


def get_plaza_inner_rings(plaza):
    """ return geometries of the inner rings """
    if not plaza.geometry().isMultipart():
        return []
    inner_rings = []
    multipolygon = plaza.geometry().asMultiPolygon()[0]
    # first element is outer ring, rest is inner
    for ring_polygon in multipolygon[1:]:
        inner_rings.append(QgsGeometry.fromPolygon([ring_polygon]))
    return inner_rings


def get_plaza_outer_geometry(plaza):
    """ return the outermost ring geometry for the plaza """
    geom = plaza.geometry()
    if not geom.isMultipart():
        return geom
    plaza_polygon = geom.asMultiPolygon()[0][0]  # first is outer ring
    return QgsGeometry.fromPolygon([plaza_polygon])


def get_features_inside_plaza(features, plaza):
    plaza_outer_geom = get_plaza_outer_geometry(plaza)
    plaza_inner_rings = get_plaza_inner_rings(plaza)
    found_features = []
    for p in features:
        if plaza_outer_geom.contains(p.geometry()):
            p_in_ring = False
            for ring in plaza_inner_rings:
                if ring.contains(p.geometry()):
                    p_in_ring = True
            if not p_in_ring:
                found_features.append(p)
    return found_features


def create_visibility_graph(plaza, point_layer, memLayer):
    enclosed_features = get_features_inside_plaza(point_layer.getFeatures(), plaza)
    plaza_nodes = get_nodes(plaza)
    enclosed_nodes = [get_nodes(p) for p in enclosed_features]
    nodes = plaza_nodes + enclosed_nodes

    edges = calc_visiblity_graph_edges(memLayer, nodes)
    return nodes, edges


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


def draw_features(layer, features):
    layer.dataProvider().addFeatures(features)
    QgsMapLayerRegistry.instance().addMapLayer(layer)


def edge_is_inside_plaza(plaza, edge):
    intersection = plaza.geometry().intersection(edge.geometry())
    # if polyline is empty, the line isn't entirely inside the plaza
    if intersection.asPolyline():
        return True
    return False


def get_intersecting_features(plaza, line_layer):
    """ returns all line features that intersect with the plaza """
    index = QgsSpatialIndex(line_layer.getFeatures())
    plaza_geom = get_plaza_outer_geometry(plaza)
    feauture_dict = {f.id(): f for f in line_layer.getFeatures()}
    # restrict features to those that intersect with the bounding box of the plaza
    intersect_ids = index.intersects(plaza_geom.boundingBox())
    intersecting_features = []
    for i in intersect_ids:
        line = feauture_dict[i]
        if line.geometry().intersects(plaza_geom):
            intersecting_features.append(line)
    return intersecting_features


def get_entry_points(plaza, intersecting_features):
    """ returns all entry and exit points of the intersecting features with the plaza """
    plaza_geom = get_plaza_outer_geometry(plaza)
    entry_points = []
    for line_feature in intersecting_features:
        intersection = line_feature.geometry().intersection(plaza_geom)
        if intersection.type() == QGis.Point:
            if intersection.isMultipart():  # if line intersects at multiple points
                for point in intersection.asMultiPoint():
                    entry_points.append(point)
            else:
                entry_points.append(intersection.asPoint())
        else:
            intersection_points = None
            if intersection.isMultipart():
                intersection_points = [p for line in intersection.asMultiPolyline() for p in line]
            else:
                intersection_points = intersection.asPolyline()
            for point in intersection_points:
                if not plaza_geom.contains(point):
                    entry_points.append(point)
    return entry_points


def calc_shortest_paths(entry_points, graph_layer):
    # prepare graph
    director = QgsLineVectorLayerDirector(graph_layer, -1, '', '', '', 3)
    properter = QgsDistanceArcProperter()  # get weights through distance
    director.addProperter(properter)
    crs = graph_layer.crs()
    builder = QgsGraphBuilder(crs)

    director.makeGraph(builder, entry_points)
    graph = builder.graph()

    result_edges = set()
    for start_point in entry_points:
        edges = calc_dijkstra_shortest_tree(graph, start_point, entry_points)
        result_edges = result_edges.union(edges)
    return result_edges


def calc_dijkstra_shortest_tree(graph, start_point, entry_points):
    """ returns a set of edges that belong to the shortest path from
        start_point to every other point in entry_points """
    start_vertex = graph.findVertex(start_point)
    tree = QgsGraphAnalyzer.shortestTree(graph, start_vertex, 0)
    result_edges = set()
    for entry_point in entry_points:
        if (entry_point == start_point):
            continue
        end_vertex = tree.findVertex(entry_point)
        if end_vertex == -1:
            # not found
            print("no path to %s found" % entry_points[3])
        else:
            while start_vertex != end_vertex:
                in_edges = tree.vertex(end_vertex).inArc()
                if len(in_edges) == 0:
                    break
                in_edge = tree.arc(in_edges[0])
                in_point = tree.vertex(in_edge.inVertex()).point()
                out_point = tree.vertex(in_edge.outVertex()).point()
                result_edges.add((in_point, out_point))
                end_vertex = in_edge.outVertex()
    return result_edges


def draw_edges(line_layer, edges):
    """ every edge must be a tuple with two points """
    line_features = []
    for p1, p2 in edges:
        line = QgsFeature(line_layer.pendingFields())
        line.setGeometry(QgsGeometry.fromPolyline([p1, p2]))
        line_features.append(line)
    draw_features(line_layer, line_features)
