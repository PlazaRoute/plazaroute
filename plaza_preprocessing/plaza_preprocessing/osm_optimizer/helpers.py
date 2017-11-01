""" helper functions """

def point_in_bounding_box(point, min_x, min_y, max_x, max_y):
    if point.x < min_x or point.x > max_x:
        return False
    if point.y < min_y or point.y > max_y:
        return False
    return True


def meters_to_degrees(meters):
    """ convert meters to approximate degrees """
    #  meters * 360 / (2 * PI * 6400000)
    # multiply by (1/cos(lat) for longitude)
    return meters * 1 / 111701


def bounding_boxes_overlap(min_x1, min_y1, max_x1, max_y1, min_x2, min_y2, max_x2, max_y2):
    """ takes two bounding boxes and checks if they overlap """
    if min_x1 <= min_x2 and max_x1 <= min_x2:
        return False
    if min_y1 <= min_y2 and max_y1 <= min_y2:
        return False
    if min_x1 >= max_x2 or min_y1 >= max_y2:
        return False

    return True


def get_polygon_coords(polygon):
    """ return a list of coordinates of all points in a polygon """
    coords = list(polygon.exterior.coords)
    for ring in polygon.interiors:
        coords.extend(ring.coords)
    return coords

def find_nearest_geometry(obj, geometries):
    """ return the geometry that is nearest to the object """
    return min(geometries, key=lambda g: g.distance(obj))
