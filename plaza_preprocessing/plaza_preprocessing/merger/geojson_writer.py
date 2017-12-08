import geojson

# TODO: remove!


def write_geojson(geometries, filename):
    """ write geojson from a list of shapely geometries """
    features = [geojson.Feature(geometry=geom) for geom in geometries]
    feature_collection = geojson.FeatureCollection(features)
    with open(filename, 'w') as fp:
        geojson.dump(feature_collection, fp)
