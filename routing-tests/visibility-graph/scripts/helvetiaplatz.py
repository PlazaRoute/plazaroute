def get_layer(layerName):
    layerList = QgsMapLayerRegistry.instance().mapLayersByName(layerName)
    if not layerList: 
        raise Exception("Failed to select layer.")
    return layerList[0] # should only return one layer

def get_feature(featureId, layer):
    expr = QgsExpression('"id"=%d' % featureId)
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
    
def create_line_memory_layer(name):
        memLayer = QgsVectorLayer("linestring?crs=epsg:4326&field=MYNUM:integer&field=MYTXT:string", 
        name, "memory")
        QgsMapLayerRegistry.instance().addMapLayer(memLayer)
        return memLayer
        
mp_layer = get_layer('helvetiaplatz multipolygons')
mp_features = mp_layer.getFeatures()
for f in mp_features:
    print(f.attributes())
