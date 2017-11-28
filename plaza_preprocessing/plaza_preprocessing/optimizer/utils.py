import logging
import time
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString, GeometryCollection

logger = logging.getLogger('plaza_preprocessing.optimizer')


def point_in_bounding_box(point, min_x, min_y, max_x, max_y):
    if point.x < min_x or point.x > max_x:
        return False
    if point.y < min_y or point.y > max_y:
        return False
    return True


def unpack_geometry_coordinates(geometry):
    """ return a set with every point in LineString and Point geometries """
    geom_type = type(geometry)
    if geom_type == GeometryCollection:
        coords = set()
        for geom in geometry:
            coords = coords.union(unpack_geometry_coordinates(geom))
        return coords
    elif geom_type == MultiLineString or geom_type == MultiPoint:
        return set().union([c for element in geometry for c in element.coords])
    elif geom_type == LineString or geom_type == Point:
        return set(geometry.coords)
    else:
        raise ValueError(f"Unsupported Geometry type {geom_type}")


def meters_to_degrees(meters):
    """ convert meters to approximate degrees """
    #  meters * 360 / (2 * PI * 6400000)
    # multiply by (1/cos(lat) for longitude)
    return meters * 1 / 111701


def get_polygon_coords(polygon):
    """ return a list of coordinates of all points in a polygon """
    coords = list(polygon.exterior.coords)
    for ring in polygon.interiors:
        coords.extend(ring.coords)
    return coords


def find_nearest_geometry(obj, geometries):
    """ return the geometry that is nearest to the object """
    return min(geometries, key=lambda g: g.distance(obj))


def line_visible(plaza_geometry, line):
    """ check if the line is "visible", i.e. unobstructed through the plaza """
    return line.equals(plaza_geometry.intersection(line))


def timing(f):
    """ decorator function to measure runtime of a function """
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        logger.debug('%s function took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap
