from plaza_preprocessing import osm_importer as importer
from plaza_preprocessing.osm_merger import geojson_writer
from shapely.geometry import (Point, MultiPoint, LineString, MultiLineString,
                              Polygon, MultiPolygon, box)


def preprocess_plazas(osm_holder):
    """ preprocess all plazas from osm_importer """
    # test for helvetiaplatz
    # plaza = next(p for p in osm_holder.plazas if p['osm_id'] == 4533221)
    # test for Bahnhofplatz Bern
    plaza = next(p for p in osm_holder.plazas if p['osm_id'] == 5117701)
    # process_plaza(plaza['geometry'], osm_holder.lines, osm_holder.buildings, osm_holder.points)

    for plaza in osm_holder.plazas:
        print(f"processing plaza {plaza['osm_id']}")
        if isinstance(plaza['geometry'], MultiPolygon):
            for polygon in plaza['geometry']:
                process_plaza(polygon, osm_holder.lines, osm_holder.buildings, osm_holder.points)
        else:
            process_plaza(plaza, osm_holder.lines, osm_holder.buildings, osm_holder.points)


def process_plaza(plaza_geometry, lines, buildings, points):
    """ process a single plaza """
    entry_points = calc_entry_points(plaza_geometry, lines)
    if not entry_points:
        print(f"Plaza {plaza['osm_id']} has no entry points")
        return
    plaza_geometry = insert_obstacles(plaza_geometry, buildings, points)
    geojson_writer.write_geojson([plaza_geometry], 'plaza.geojson')
 
    graph_edges = create_visibility_graph(plaza_geometry, entry_points)
    geojson_writer.write_geojson(graph_edges, 'edges.geojson')



def calc_entry_points(plaza_geometry, lines):
    """
    calculate points where lines intersect with the outer ring of the plaza
    """
    intersecting_lines = find_intersescting_lines(plaza_geometry, lines)

    entry_points = []
    for line in intersecting_lines:
        intersection = line.intersection(plaza_geometry)
        intersection_type = type(intersection)
        if intersection_type == Point:
            entry_points.append(intersection)
        elif intersection_type == MultiPoint:
            entry_points.extend(list(intersection))
        else:
            intersection_coords = []
            if intersection_type == MultiLineString:
                intersection_coords.extend(
                    [c for line in intersection for c in line.coords])
            else:
                intersection_coords = list(intersection.coords)
            intersection_points = list(map(Point, intersection_coords))
            entry_points.extend(
                [p for p in intersection_points if plaza_geometry.touches(p)])

    return entry_points


def find_intersescting_lines(plaza_geometry, lines):
    """ return every line that intersects with the plaza """
    # filtering is slower than checking every line
    # bbox_buffer = 5 * 10**-3  # about 500m
    # lines_in_approx = list(
    #     filter(lambda l: line_in_plaza_approx(l, plaza_geometry, buffer=bbox_buffer), lines))
    return list(filter(plaza_geometry.intersects, lines))


def insert_obstacles(plaza_geometry, buildings, points):
    """ cuts out holes for obstacles on the plaza geometry """
    intersecting_buildings = find_intersecting_buildings(plaza_geometry, buildings)

    for building in intersecting_buildings:
        plaza_geometry = plaza_geometry.difference(building)

    points_on_plaza = get_points_inside_plaza(plaza_geometry, points)
    point_obstacles = list(map(lambda p: create_point_obstacle(p, buffer=2), points_on_plaza))

    for p_obstacle in point_obstacles:
        plaza_geometry = plaza_geometry.difference(p_obstacle)
    
    if isinstance(plaza_geometry, MultiPolygon):
        print("Multipolygon after cut out!")
        # take the largest of the polygons
        plaza_geometry = max(plaza_geometry, key=lambda p: p.area)

    return plaza_geometry


def find_intersecting_buildings(plaza_geometry, buildings):
    """ finds all buildings on the plaza that have not been cut out"""
    return list(filter(plaza_geometry.intersects, buildings))


def get_points_inside_plaza(plaza_geometry, points):
    """ finds all points that are on the plaza geometry """
    return list(filter(plaza_geometry.intersects, points))


def create_point_obstacle(point, buffer=5):
    """ create a polygon around a point with a buffer in meters """
    buffer_deg = meters_to_degrees(buffer)
    min_x = point.x - buffer_deg
    min_y = point.y - buffer_deg
    max_x = point.x + buffer_deg
    max_y = point.y + buffer_deg
    return box(min_x, min_y, max_x, max_y)


def create_visibility_graph(plaza_geometry, entry_points):
    """ create a visibility graph with all plaza and entry points """
    plaza_coords = get_polygon_coords(plaza_geometry)
    entry_coords = [(p.x, p.y) for p in entry_points]
    all_coords = set().union(plaza_coords, entry_coords)
    indexed_coords = {i: coords for i, coords in enumerate(all_coords)}
    edges = []
    for start_id, start_coords in indexed_coords.items():
        for end_id, end_coords in indexed_coords.items():
            if (start_id > end_id):
                line = LineString([start_coords, end_coords])
                if line_visible(line, plaza_geometry):
                    edges.append(line)
    return edges


def line_visible(line, plaza_geometry):
    """ check if the line is "visible", i.e. unobstructed through the plaza """
    return line.equals(plaza_geometry.intersection(line))


def get_polygon_coords(polygon):
    """ return a list of coordinates of all points in a multipolygon """
    coords = list(polygon.exterior.coords)
    for ring in polygon.interiors:
        coords.extend(ring.coords)
    return coords


def line_in_plaza_approx(line, plaza_geometry, buffer=0):
    """
    determines if a line's bounding box is in the bounding box of the plaza,
    with optional buffer in degrees (enlarged bounding box)
    """
    min_x1, min_y1, max_x1, max_y1 = plaza_geometry.bounds
    line_bbox = line.bounds
    min_x1 -= buffer / 2
    min_y1 -= buffer / 2
    max_x1 += buffer / 2
    max_y1 += buffer / 2
    return bounding_boxes_overlap(min_x1, min_y1, max_x1, max_y1, *line_bbox)


def bounding_boxes_overlap(min_x1, min_y1, max_x1, max_y1, min_x2, min_y2, max_x2, max_y2):
    """ takes two bounding boxes and checks if they overlap """
    if min_x1 <= min_x2 and max_x1 <= min_x2:
        return False
    if min_y1 <= min_y2 and max_y1 <= min_y2:
        return False
    if min_x1 >= max_x2 or min_y1 >= max_y2:
        return False

    return True


def point_in_plaza_bbox(point, plaza_geometry):
    """ determines whether a point is inside the bounding box of the plaza """
    min_x, min_y, max_x, max_y = plaza_geometry.bounds
    return point_in_bounding_box(point, min_x, min_y, max_x, max_y)


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
    return meters * 1/111701


if __name__ == '__main__':
    # osm_holder = importer.import_osm('data/helvetiaplatz_umfeld.osm')
    osm_holder = importer.import_osm('data/switzerland-exact.osm.pbf')
    preprocess_plazas(osm_holder)
