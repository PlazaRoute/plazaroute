from math import *

def remove_layer_if_it_exists(name):
    layers = QgsMapLayerRegistry.instance().mapLayers()
    for memname, layer in layers.iteritems():
        if memname.startswith(name):
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())


def create_line_memory_layer(name):
    memLayer = QgsVectorLayer(
        "linestring?crs=epsg:4326&field=left:double&field=bottom:double&field=right:double&field=top:double", name, "memory")
    remove_layer_if_it_exists(name)
    QgsMapLayerRegistry.instance().addMapLayer(memLayer)
    return memLayer


def get_layer(layerName):
    layerList = QgsMapLayerRegistry.instance().mapLayersByName(layerName)
    if not layerList:
        raise Exception("Failed to select layer.")
    return layerList[0]  # should only return one layer


def calculate_boundingbox(features):
    box = None
    for feature in features:
        if box is None:
            box = feature.geometry().boundingBox()
        else:
            box.combineExtentWith(feature.geometry().boundingBox())
    return box


def draw_grid(layer, boundingbox, spacing):
    #diagonal of the bounding box
    diagonal = QgsGeometry().fromPoint(QgsPoint(boundingbox.xMinimum(),
        boundingbox.yMaximum())).distance(QgsGeometry().fromPoint(boundingbox.center())) * 2

    #calculate the offset based on the diagonal and the top horizonatal line of the bounding box
    offset_horizontal = (diagonal - QgsGeometry().fromPoint(QgsPoint(boundingbox.xMinimum(),
        boundingbox.yMaximum())).distance(QgsGeometry().fromPoint(QgsPoint(boundingbox.xMaximum(), boundingbox.yMaximum())))) / 2

    #calculate the offset based on the diagonal and the top vertical line of the bounding box
    offset_vertical = (diagonal - QgsGeometry().fromPoint(QgsPoint(boundingbox.xMinimum(),
        boundingbox.yMaximum())).distance(QgsGeometry().fromPoint(QgsPoint(boundingbox.xMinimum(), boundingbox.yMinimum())))) / 2

    #add offsets so that the rectangles still fit the square after the rotation
    xleft = boundingbox.xMinimum() - offset_horizontal
    xright = boundingbox.xMaximum() + offset_horizontal

    ytop = boundingbox.yMaximum() + offset_vertical
    ybottom = boundingbox.yMinimum() - offset_vertical


    # https://github.com/michaelminn/mmqgis
    rows = int(ceil((ytop - ybottom) / spacing))
    columns = int(ceil((xright - xleft) / spacing))

    feature_count = 0
    features = []

    for column in range(0, columns + 1):
        for row in range(0, rows + 1):

            x1 = xleft + (column * spacing)
            x2 = xleft + ((column + 1) * spacing)
            y1 = ybottom + (row * spacing)
            y2 = ybottom + ((row + 1) * spacing)

            # horizontal line
            if (column < columns):
                line = QgsGeometry.fromPolyline([QgsPoint(x1, y1), QgsPoint(x2, y1)])
                feature = QgsFeature()
                feature.setGeometry(line)
                feature.setAttributes([x1, y1, x2, y1])
                features.append(feature)

            # vertical line
            if (row < rows):
                line = QgsGeometry.fromPolyline([QgsPoint(x1, y1), QgsPoint(x1, y2)])
                feature = QgsFeature()
                feature.setGeometry(line)
                feature.setAttributes([x1, y1, x1, y2])
                features.append(feature)

    layer.dataProvider().addFeatures(features)
    QgsMapLayerRegistry.instance().addMapLayer(layer)


def rotate_features(layer, degree):
    bounding_box = calculate_boundingbox(layer.getFeatures())
    center = bounding_box.center()
    for feature in layer.getFeatures():
        geom = feature.geometry()
        geom.rotate(degree, QgsPoint(center))
        layer.dataProvider().changeGeometryValues({ feature.id() : geom })


def remove_lines_outside_of_plaza(plaza, grid_layer):
    plaza_geom = plaza.geometry()
    features = []
    for line_feature in grid_layer.getFeatures():
        intersection = line_feature.geometry().intersection(plaza_geom)
        intersection_feature = QgsFeature()
        intersection_feature.setGeometry(intersection)
        features.append(intersection_feature)

    intersection_layer = create_line_memory_layer(grid_layer.name())
    intersection_layer.dataProvider().addFeatures(features)
    QgsMapLayerRegistry.instance().addMapLayer(intersection_layer)
    
def nearest_neighbor(layer, entry_points):
    spindex = QgsSpatialIndex()
    for feature in layer.getFeatures():
        spindex.insertFeature(feature)
    
    print entry_points
    line_features = []
    for entry_point in entry_points:
        neighborid = spindex.nearestNeighbor(QgsPoint(entry_point),1)
        
        request = QgsFeatureRequest()
        request.setFilterFids(neighborid)
        neighbors = layer.getFeatures(request)
        neighbor = neighbors.next()
    
        line = QgsFeature()
        target = neighbor.geometry().asPolyline()[0]
        line.setGeometry(QgsGeometry.fromPolyline([entry_point, target]))
        line_features.append(line)
    
    print len(line_features)
    test_layer = create_line_memory_layer('test_layer')
    test_layer.dataProvider().addFeatures(line_features)
    QgsMapLayerRegistry.instance().addMapLayer(test_layer)
        

def draw_spiderweb_graph(layer):
    for plaza in layer.getFeatures():
        grid_layer = create_line_memory_layer('spiderweb' + str(plaza.id()))
        boundingbox = calculate_boundingbox([plaza])
        draw_grid(grid_layer, boundingbox, 0.00005)
        rotate_features(grid_layer, 45)
        remove_lines_outside_of_plaza(plaza, grid_layer)
