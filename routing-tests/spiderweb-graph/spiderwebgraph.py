from math import *

def calculate_boundingbox(features):
    box = None
    for feature in features:
        if box is None:
            box = feature.geometry().boundingBox()
        else:
            box.combineExtentWith(feature.geometry().boundingBox())
    return box

def get_intersection_line(start, end, plaza, obstacle_geom):
    line = QgsGeometry.fromPolyline([start, end])
    line_feature = QgsFeature()
    line_feature.setGeometry(line)
    line_geom = line_feature.geometry()
    plaza_geom = plaza.geometry()


    #if (line_geom.intersects(plaza_geom)) and not line_geom.intersects(obstacle_geom):
    if edge_is_inside_plaza(plaza, obstacle_geom, line_feature):
        intersection = line_geom.intersection(plaza_geom)
        line_feature.setGeometry(intersection)
        return line_feature
    else:
        return None

def connect_entry_points_with_spiderweb_graph(layer, entry_points):
    spindex = QgsSpatialIndex()
    for feature in layer.getFeatures():
        spindex.insertFeature(feature)

    line_features = []
    for entry_point in entry_points:
        neighborid = spindex.nearestNeighbor(QgsPoint(entry_point), 1)
        neighbors = layer.getFeatures(QgsFeatureRequest().setFilterFid(neighborid[0]))
        neighbor = neighbors.next()

        target = neighbor.geometry().asPolyline()[1]
        line = QgsFeature()
        line.setGeometry(QgsGeometry.fromPolyline([entry_point, target]))
        line_features.append(line)

    layer.dataProvider().addFeatures(line_features)
    QgsMapLayerRegistry.instance().addMapLayer(layer)


def create_spiderweb_graph(layer, plaza, spacing, obstacle_geom):
    plaza_geom = plaza.geometry()
    boundingbox = calculate_boundingbox([plaza])

    xleft = boundingbox.xMinimum()
    xright = boundingbox.xMaximum()
    ytop = boundingbox.yMaximum()
    ybottom = boundingbox.yMinimum()

    # based on https://github.com/michaelminn/mmqgis
    rows = int(ceil((ytop - ybottom) / spacing))
    columns = int(ceil((xright - xleft) / spacing))

    features = []
    for column in range(0, columns + 1):
        for row in range(0, rows + 1):

            x1 = xleft + (column * spacing)
            x2 = xleft + ((column + 1) * spacing)
            y1 = ybottom + (row * spacing)
            y2 = ybottom + ((row + 1) * spacing)

            top_left = QgsPoint(x1, y1)
            top_right = QgsPoint(x2, y1)
            bottom_left = QgsPoint(x1, y2)
            bottom_right = QgsPoint(x2, y2)

            # horizontal line
            if (column < columns):
                horizontal_line = get_intersection_line(top_left, top_right, plaza, obstacle_geom)
                if horizontal_line:
                    features.append(horizontal_line)

            # vertical line
            if (row < rows):
                vertical_line = get_intersection_line(top_left, bottom_left, plaza, obstacle_geom)
                if vertical_line:
                    features.append(vertical_line)

            # diagonal line
            if (row < rows and column < columns): # TODO correct constraint?
                diagonal_line = get_intersection_line(top_left, bottom_right, plaza, obstacle_geom)
                if diagonal_line:
                    features.append(diagonal_line)
                diagonal_line = get_intersection_line(bottom_left, top_right, plaza, obstacle_geom)
                if diagonal_line:
                    features.append(diagonal_line)

    layer.dataProvider().addFeatures(features)
    QgsMapLayerRegistry.instance().addMapLayer(layer)

def create_spiderweb_graphs(plaza_layer, building_layer, spacing):
    for plaza in plaza_layer.getFeatures():
        intersecting_buildings = find_buildings_inside_plaza(plaza, building_layer)
        obstacle_geom = create_obstacle_geometry(plaza, intersecting_buildings)
        graph_layer = create_line_memory_layer('spiderweb' + str(plaza.id()))
        create_spiderweb_graph(graph_layer, plaza, spacing, obstacle_geom)
        intersecting_features = get_intersecting_features(plaza, line_layer)
        entry_points = get_entry_points(plaza, intersecting_features)
        connect_entry_points_with_spiderweb_graph(graph_layer, entry_points)
