from plaza_preprocessing import osm_importer as importer
from plaza_preprocessing.osm_merger import geojson_writer
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon


def preprocess_plazas(osm_holder):
    """ preprocess all plazas from osm_importer """
    # test for helvetiaplatz
    # plaza = next(p for p in osm_holder.plazas if p['osm_id'] == 4533221)
    # process_plaza(plaza, osm_holder.lines, osm_holder.buildings)
    for plaza in osm_holder.plazas:
        process_plaza(plaza, osm_holder.lines, osm_holder.buildings)


def process_plaza(plaza, lines, buildings):
    """ process a single plaza """
    print(f"processing plaza {plaza['osm_id']}")
    entry_points = calc_entry_points(plaza['geometry'], lines)
    if not entry_points:
        print(f"Plaza {plaza['osm_id']} has no entry points")
        return
    create_obstacle_geometry(plaza['geometry'], buildings)
    


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
    # lines_in_approx = list(filter(lambda l: line_in_plaza_bbox(l, plaza_geometry, buffer=bbox_buffer), lines))
    return list(filter(plaza_geometry.intersects, lines))


def create_obstacle_geometry(plaza_geometry, buildings):
    """ create a geometry that contains every obstacle on the plaza """
    intersecting_buildings = find_intersecting_buildings(plaza_geometry, buildings)
    geojson_writer.write_geojson(intersecting_buildings, 'buildings.geojson')
    # TODO: Add point cutouts


def find_intersecting_buildings(plaza_geometry, buildings):
    """ finds all buildings on the plaza that have not been cut out"""
    return list(filter(plaza_geometry.intersects, buildings))



def line_in_plaza_bbox(line, plaza_geometry, buffer=0):
    """
    determines if any node of a line is in the bounding box of the plaza,
    with optional buffer in degrees (enlarged bounding box)
    """
    min_x, min_y, max_x, max_y = plaza_geometry.bounds
    min_x -= buffer / 2
    min_y -= buffer / 2
    max_x += buffer / 2
    max_y += buffer / 2
    for p in line.coords:
        if point_in_bounding_box(Point(p), min_x, min_y, max_x, max_y):
            return True
    return False


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

if __name__ == '__main__':
    osm_holder = importer.import_osm('data/helvetiaplatz_umfeld.osm')
    # osm_holder = importer.import_osm('data/switzerland-exact.osm.pbf')
    preprocess_plazas(osm_holder)
