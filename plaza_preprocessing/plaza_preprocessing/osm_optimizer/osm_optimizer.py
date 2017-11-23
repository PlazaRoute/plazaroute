import logging
from shapely.geometry import Point, MultiPolygon, Polygon, LineString, box
from typing import List
from plaza_preprocessing.osm_optimizer import utils
from plaza_preprocessing.osm_optimizer import shortest_paths
from plaza_preprocessing.osm_optimizer.graphprocessor.graphprocessor import GraphProcessor
from plaza_preprocessing.osm_importer import OSMHolder

logger = logging.getLogger('plaza_preprocessing.osm_optimizer')

# TODO: Make configurable
OBSTACLE_BUFFER = 2  # buffer in meters to circumvent obstacles


def preprocess_plazas(osm_holder: OSMHolder, process_strategy: GraphProcessor):
    """ preprocess all plazas from osm_importer """
    logger.info(f"Start processing {len(osm_holder.plazas)} plazas")
    plaza_processor = PlazaPreprocessor(osm_holder, process_strategy)
    processed_plazas = plaza_processor.process_plazas()

    logger.info(f"Finished processing {len(processed_plazas)} plazas (rest were discarded)")
    return processed_plazas


class PlazaPreprocessor:

    def __init__(self, osm_holder: OSMHolder, graph_processor: GraphProcessor):
        self.plazas = osm_holder.plazas
        self.lines = osm_holder.lines
        self.buildings = osm_holder.buildings
        self.points = osm_holder.points
        self.graph_processor = graph_processor

    def process_plazas(self):
        """ process all plazas in the osm holder"""
        processed_plazas = []
        for plaza in self.plazas:
            logger.info(f"Processing plaza {plaza['osm_id']}")
            processed_plaza = self._process_plaza(plaza)
            if processed_plaza is not None:
                processed_plazas.append(processed_plaza)

        return processed_plazas

    def _process_plaza(self, plaza):
        """ process a single plaza """

        intersecting_lines = self._find_intersescting_lines(plaza['geometry'])

        entry_points = self._calc_entry_points(plaza['geometry'], intersecting_lines)

        if len(entry_points) < 2:
            logger.debug(f"Discarding Plaza {plaza['osm_id']} - it has fewer than 2 entry points")
            return None

        entry_lines = self._map_entry_lines(intersecting_lines, entry_points)

        plaza_geom_without_obstacles = self._calc_obstacle_geometry(plaza, buffer_m=OBSTACLE_BUFFER)

        if not plaza_geom_without_obstacles:
            logger.debug(f"Discarding Plaza {plaza['osm_id']}: completely obstructed by obstacles")
            return None

        graph_edges = self.get_graph_edges(entry_points, plaza['geometry'], plaza_geom_without_obstacles)

        if not graph_edges:
            logger.debug(f"Discarding Plaza {plaza['osm_id']}: no graph could be constructed")
            return None

        plaza['geometry'] = plaza_geom_without_obstacles
        plaza['entry_points'] = entry_points
        plaza['entry_lines'] = entry_lines
        plaza['graph_edges'] = graph_edges

        return plaza

    def get_graph_edges(self, entry_points: List[Point], plaza_geom: Polygon,
                        plaza_geom_without_obstacles: Polygon) -> List[LineString]:
        """ create graph with shortest paths between entry points """
        graph_edges = self.graph_processor.create_graph_edges(plaza_geom_without_obstacles, entry_points)
        graph = shortest_paths.create_graph(graph_edges)
        shortest_path_lines = shortest_paths.compute_astar_shortest_paths(graph, entry_points)
        optimized_lines = self.graph_processor.optimize_lines(plaza_geom, shortest_path_lines, OBSTACLE_BUFFER)
        return optimized_lines

    def _calc_entry_points(self, plaza_geometry, intersecting_lines):
        """
        calculate points where lines intersect with the outer ring of the plaza
        """
        intersection_coords = set()
        for line in intersecting_lines:
            line_geom = line['geometry']
            intersection = line_geom.intersection(plaza_geometry)
            intersection_coords = intersection_coords.union(
                utils.unpack_geometry_coordinates(intersection))

        intersection_points = list(map(Point, intersection_coords))

        entry_points = [
            p for p in intersection_points if plaza_geometry.touches(p)]

        return entry_points

    def _map_entry_lines(self, intersecting_lines, entry_points):
        """ map entry lines to entry points """
        entry_lines = []
        for line in intersecting_lines:
            matching_entry_points = list(filter(
                lambda p: (p.x, p.y) in line['geometry'].coords, entry_points))
            if matching_entry_points:
                entry_lines.append({
                    'way_id': line['id'],
                    'entry_points': matching_entry_points
                })
        return entry_lines

    def _find_intersescting_lines(self, plaza_geometry):
        """ return every line that intersects with the plaza """
        # filtering is slower than checking every line
        # bbox_buffer = 5 * 10**-3  # about 500m
        # lines_in_approx = list(
        #     filter(lambda l: line_in_plaza_approx(l, plaza_geometry, buffer=bbox_buffer), lines))
        intersecting_lines = []
        for line in self.lines:
            if plaza_geometry.intersects(line['geometry']):
                intersecting_lines.append(line)
        return intersecting_lines

    def _calc_obstacle_geometry(self, plaza, buffer_m):
        """ cuts out holes for obstacles on the plaza geometry """
        intersecting_buildings = self._find_intersecting_buildings(plaza)

        geometry_without_buildings = plaza['geometry']
        for building in intersecting_buildings:
            geometry_without_buildings = geometry_without_buildings.difference(building)

        points_on_plaza = self._get_points_inside_plaza(plaza)
        point_obstacles = list(
            map(lambda p: self._create_point_obstacle(p, buffer_m), points_on_plaza))

        geometry_without_obstacles = geometry_without_buildings
        for point_obstacle in point_obstacles:
            geometry_without_obstacles = geometry_without_obstacles.difference(point_obstacle)

        if isinstance(geometry_without_obstacles, MultiPolygon):
            logger.debug(
                f"Plaza {plaza['osm_id']}: Multipolygon after cut out, discarding smaller polygon")
            # take the largest of the polygons
            largest_geometry_without_obstacles = max(
                geometry_without_obstacles, key=lambda p: p.area)
            # if cut out is less than 5% the area of the original, it's discarded
            if largest_geometry_without_obstacles.area < plaza['geometry'].area * 0.05:
                return None
            return largest_geometry_without_obstacles

        return geometry_without_obstacles

    def _find_intersecting_buildings(self, plaza):
        """ finds all buildings on the plaza that have not been cut out"""
        return list(filter(plaza['geometry'].intersects, self.buildings))

    def _get_points_inside_plaza(self, plaza):
        """ finds all points that are on the plaza geometry """
        return list(filter(plaza['geometry'].intersects, self.points))

    def _create_point_obstacle(self, point, buffer_m):
        """ create a polygon around a point with a buffer in meters """
        buffer_deg = utils.meters_to_degrees(buffer_m)
        min_x = point.x - buffer_deg
        min_y = point.y - buffer_deg
        max_x = point.x + buffer_deg
        max_y = point.y + buffer_deg
        return box(min_x, min_y, max_x, max_y)

    def _line_in_plaza_approx(self, line, plaza_geometry, buffer=0):
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
        return utils.bounding_boxes_overlap(min_x1, min_y1, max_x1, max_y1, *line_bbox)

    def _point_in_plaza_bbox(self, point, plaza_geometry):
        """ determines whether a point is inside the bounding box of the plaza """
        min_x, min_y, max_x, max_y = plaza_geometry.bounds
        return utils.point_in_bounding_box(point, min_x, min_y, max_x, max_y)
