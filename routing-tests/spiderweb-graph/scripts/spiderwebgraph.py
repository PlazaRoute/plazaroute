from math import *

def calculate_boundingbox(features):
    box = None
    for feature in features:
        if box is None:
            box = feature.geometry().boundingBox()
        else:
            box.combineExtentWith(feature.geometry().boundingBox())
    return box

def calculate_offsets(boundingbox):
    top_left = QgsPoint(boundingbox.xMinimum(), boundingbox.yMaximum())
    top_right = QgsPoint(boundingbox.xMaximum(), boundingbox.yMaximum())
    bottom_left = QgsPoint(boundingbox.xMinimum(), boundingbox.yMinimum())

    # diagonal of the bounding box
    diagonal = QgsGeometry().fromPoint(top_left).distance(QgsGeometry().fromPoint(boundingbox.center())) * 2

    # calculate the offset based on the diagonal and the top horizonatal line of the bounding box
    offset_horizontal = (diagonal - QgsGeometry().fromPoint(top_left).distance(QgsGeometry().fromPoint(top_right))) / 2

    # calculate the offset based on the diagonal and the left vertical line of the bounding box
    offset_vertical = (diagonal - QgsGeometry().fromPoint(top_left).distance(QgsGeometry().fromPoint(bottom_left))) / 2

    return offset_horizontal, offset_vertical

def rotate_feature(feature, center, degree):
    geom = feature.geometry()
    geom.rotate(degree, QgsPoint(center))

def keep_intersection_of_feature(feature, geometry):
    intersection = feature.geometry().intersection(geometry)
    feature.setGeometry(intersection)

def get_rotated_intersection_line(start, end, degree, center, base_area):
    line = QgsGeometry.fromPolyline([start, end])
    line_feature = QgsFeature()
    line_feature.setGeometry(line)

    rotate_feature(line_feature, center, degree)
    if line_feature.geometry().intersects(base_area):
        keep_intersection_of_feature(line_feature, base_area)
        return line_feature
    else:
        return None

def draw_grid(layer, plaza, degree, spacing):
    plaza_geom = plaza.geometry()
    boundingbox = calculate_boundingbox([plaza])
    center = boundingbox.center()

    (offset_horizontal, offset_vertical) = calculate_offsets(boundingbox)

    # add offsets so that the rectangles still fit the square after the rotation
    xleft = boundingbox.xMinimum() - offset_horizontal
    xright = boundingbox.xMaximum() + offset_horizontal

    ytop = boundingbox.yMaximum() + offset_vertical
    ybottom = boundingbox.yMinimum() - offset_vertical

    # based on https://github.com/michaelminn/mmqgis
    rows = int(ceil((ytop - ybottom) / spacing))
    columns = int(ceil((xright - xleft) / spacing))

    features = []
    for column in range(0, columns):
        for row in range(0, rows):

            x1 = xleft + (column * spacing)
            x2 = xleft + ((column + 1) * spacing)
            y1 = ybottom + (row * spacing)
            y2 = ybottom + ((row + 1) * spacing)

            start = QgsPoint(x1, y1)
            # horizontal line
            if (column < columns):
                line_feature = get_rotated_intersection_line(start, QgsPoint(x2, y1), degree, center, plaza_geom)
                if line_feature:
                    features.append(line_feature)

            # vertical line
            if (row < rows):
                line_feature = get_rotated_intersection_line(start, QgsPoint(x1, y2), degree, center, plaza_geom)
                if line_feature:
                    features.append(line_feature)

    layer.dataProvider().addFeatures(features)
    QgsMapLayerRegistry.instance().addMapLayer(layer)

def connect_entry_points_with_spiderwebgraph(layer, entry_points):
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

def draw_spiderweb_graph(layer, degree, spacing):
    for plaza in layer.getFeatures():
        grid_layer = create_line_memory_layer('spiderweb' + str(plaza.id()))
        draw_grid(grid_layer, plaza, degree, spacing)
