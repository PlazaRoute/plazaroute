#!/bin/python
from qgis.networkanalysis import *


def get_layer(layerName):
    layerList = QgsMapLayerRegistry.instance().mapLayersByName(layerName)
    if not layerList:
        raise Exception("Failed to select layer.")
    return layerList[0]  # should only return one layer


def get_feature(featureId, layer):
    features = layer.getFeatures(QgsFeatureRequest().setFilterFid(featureId))
    if not features:
        raise Exception("Failed to retrieve feature.")
    return next(features)  # should only return one feature


def unpack_multipolygon(multipolygon):
    """ returns a list with all points in all polygons of a multipolygon geometry"""
    if multipolygon.type() != QGis.Polygon or not multipolygon.isMultipart():
        return []
    points = []
    [points.extend(ring) for polygon in multipolygon.asMultiPolygon() for ring in polygon]
    return points


def get_nodes(feature):
    geom = feature.geometry()
    if geom.type() == QGis.Polygon:
        if geom.isMultipart():
            nodes = unpack_multipolygon(geom)
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


def create_memory_layer(layer_type, name):
    memLayer = QgsVectorLayer(
        "%s?crs=epsg:4326&field=MYNUM:integer&field=MYTXT:string" % layer_type, name, "memory")
    remove_layer_if_it_exists(name)
    QgsMapLayerRegistry.instance().addMapLayer(memLayer)
    return memLayer


def create_line_memory_layer(name):
    return create_memory_layer('linestring', name)


def create_point_memory_layer(name):
    return create_memory_layer('point', name)


def find_buildings_inside_plaza(plaza, building_layer):
    """ finds all buildings on the plaza that have not beeen cut out"""
    buildings = building_layer.getFeatures()
    plaza_geom = plaza.geometry()
    intersecting_buildings = []
    for b in buildings:
        if b.geometry().intersects(plaza_geom):
            intersecting_buildings.append(b)
    return intersecting_buildings


def create_obstacle_geometry(plaza, intersecting_buildings):
    """ create a geometry that contains every obstacle on the plaza """
    if not intersecting_buildings:
        return QgsGeometry()  # return emtpy geometry
    geom = None
    for building in intersecting_buildings:
        b_geom = building.geometry()
        i = b_geom.intersection(plaza.geometry())
        if i.type() == QGis.Polygon:
            polygon = i.asMultiPolygon()[0][0] if i.isMultipart() else i.asPolygon()[0]
            # TODO: doesn't work with multipolygon intersection yet
            if geom:  # create first geometry and add subsequent parts
                geom.addPartGeometry(QgsGeometry.fromPolygon([polygon]))
            else:
                geom = QgsGeometry.fromPolygon([polygon])
    return geom


def get_plaza_outer_geometry(plaza):
    """ return the outermost ring geometry for the plaza """
    geom = plaza.geometry()
    if not geom.isMultipart():
        return geom
    plaza_polygon = geom.asMultiPolygon()[0][0]  # first is outer ring
    return QgsGeometry.fromPolygon([plaza_polygon])


def is_relevant_point(point_feature):
    """ returns whether point is a relevant obstacle"""
    if point_feature["indoor"] != NULL:
        return False
    if point_feature["level"] and point_feature["level"] != "0":
        return False
    if point_feature["layer"] and point_feature["layer"] != "0":
        return False
    return True


def get_points_inside_plaza(features, plaza, obstacle_geom):
    found_features = []
    for p in features:
        p_geom = p.geometry()
        if plaza.geometry().intersects(p_geom) and not obstacle_geom.intersects(p_geom):
            found_features.append(p)
    filtered_points = filter(lambda p: is_relevant_point(p), found_features)
    return filtered_points


def draw_features(layer, features):
    layer.dataProvider().addFeatures(features)
    QgsMapLayerRegistry.instance().addMapLayer(layer)


def edge_is_inside_plaza(plaza, obstacle_geom, edge):
    """ returns true iff edge feature does not collide with obstacles or plaza boundaries """
    edge_geom = edge.geometry()
    i_plaza = plaza.geometry().intersection(edge_geom)
    intersects_obstacle = obstacle_geom.intersects(edge_geom)
    i_obstacle = obstacle_geom.intersection(edge_geom)
    if ((intersects_obstacle and i_obstacle.type() != QGis.Point) or
            i_plaza.length() < edge_geom.length()):
        return False
    return True


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
                intersection_points = []
                [intersection_points.extend(line) for line in intersection.asMultiPolyline() for p in line]
            else:
                intersection_points = intersection.asPolyline()
            for point in intersection_points:
                if not plaza_geom.contains(point) and point not in entry_points:
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
            print("no path to %s found" % entry_point)
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
