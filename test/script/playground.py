def select_layer(layerName):
    layerList = QgsMapLayerRegistry.instance().mapLayersByName(layerName)
    if not layerList: 
        raise Exception("Failed to select layer.")
    return layerList[0] # should only return one layer


def get_feature(featureId, layer):
    expr = QgsExpression( "\"id\"=" + str(featureId))
    features = layer.getFeatures(QgsFeatureRequest(expr))
    if not features: 
        raise Exception("Failed to retrieve feature.")
    return next(features) # should only return one feature


def get_nodes(feature):
    geom = feature.geometry()
    if geom.type() == QGis.Polygon:
        if geom.isMultipart():
          nodes = geom.asMultiPolygon()
        else:
          nodes = [ geom.asPolygon() ]
    return nodes
    
def create_visibility_graph(nodes):
    memLayer = QgsVectorLayer("linestring?crs=epsg:4326&field=MYNUM:integer&field=MYTXT:string", 
        "visibility_graph_layer", "memory") # TODO: only create necessary fields
    if not memLayer.isValid():
        raise Exception("Failed to create memory layer")
    outerNodes = nodes[0][0] # TODO: master multipolygon nesting
    edges = []
    for start in outerNodes:
        for target in outerNodes:
            line = QgsFeature(memLayer.pendingFields())
            line.setGeometry(QgsGeometry.fromPolyline([start, target]))
            edges.append(line)
    memLayer.dataProvider().addFeatures(edges)
    QgsMapLayerRegistry.instance().addMapLayer(memLayer)
    
def test_simple_square():
    layer = select_layer("square")
    feature = get_feature(1, layer)
    nodes = get_nodes(feature)
    create_visibility_graph(nodes)
    
def test_advanced_square():
    layer = select_layer("square")
    feature = get_feature(2, layer)
    nodes = get_nodes(feature)
    create_visibility_graph(nodes)

test_simple_square()
test_advanced_square()
    
    
