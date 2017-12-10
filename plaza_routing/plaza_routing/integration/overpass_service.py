from typing import Tuple
import logging
import overpy
import math

from plaza_routing import config
from plaza_routing.integration.util.exception_util import ValidationError, ServiceError

INITIAL_STOP_BOUNDING_BOX_BUFFER_METERS = 100

API = overpy.Overpass(url=config.overpass['overpass_api'])

logger = logging.getLogger('plaza_routing.overpass_service')


def get_public_transport_stops(start_position: tuple) -> dict:
    """ retrieves all public transport stops for a specific location in a given range """
    bbox = _parse_bounding_box(*start_position, config.overpass['public_transport_search_radius'])
    query_str = f"""
        [bbox:{bbox}];
        node["public_transport"="stop_position"];node["highway"="bus_stop"];
        out body;
        rel["type"="public_transport"];
        out center;
        """

    public_transport_stops = _query(query_str)

    filtered_public_transport_stops_nodes = filter(
        lambda node: 'uic_ref' in node.tags, public_transport_stops.nodes)
    filtered_public_transport_stops_relations = filter(
        lambda rel: 'uic_ref' in rel.tags, public_transport_stops.relations)

    public_transport_stop_nodes = {stop.tags['uic_ref']: (float(stop.lon), float(stop.lat))
                                   for stop in filtered_public_transport_stops_nodes}
    public_transport_stop_rels = {stop.tags['uic_ref']: (float(stop.center_lon), float(stop.center_lat))
                                  for stop in filtered_public_transport_stops_relations}

    public_transport_refs = {**public_transport_stop_nodes, **public_transport_stop_rels}

    if len(public_transport_refs) == 0:
        raise ValidationError(f'no public transport stops found for the given location {start_position} and range')

    return public_transport_refs


def get_connection_coordinates(lookup_position: tuple, start_uic_ref: str, exit_uic_ref: str, line: str,
                               fallback_start_position: tuple, fallback_exit_position: tuple) -> Tuple[tuple, tuple]:
    """
    Retrieves the start public transport stop position (longitude, latitude)
    for a specific uic_ref (start_uic_ref) and the corresponding exit node in the connection based on the exit_uic_ref.
    Both will be returned as tuple.

    OSM returns multiple public transport stops for a given uic_ref. We'll have to retrieve the right start and
    exit node based on the ordering of the nodes (with ref start_uic_ref or exit_uic_ref)
    in the relation (ex. bus lines) that serves the start stop.
    If the node with ref exit_uic_ref comes after the node with ref start_uic_ref
    in the relation, we've got the public transport stop in the right direction of travel.

    Returns the fallback_start_position and fallback_exit_position if all retrieval options from Overpass fail.
    """
    logger.debug(f'Retrieving start and exit stop position for start_uic_ref {start_uic_ref}, '
                 f'exit_uic_ref {exit_uic_ref} and line {line}')
    try:
        return _retrieve_start_exit_stop_position(lookup_position, start_uic_ref, exit_uic_ref, line)
    except (ValueError, ServiceError):
        return fallback_start_position, fallback_exit_position


def _retrieve_start_exit_stop_position(lookup_position: tuple, start_uic_ref: str, exit_uic_ref: str,
                                       line: str) -> Tuple[tuple, tuple]:
    """
    Retrieves the start and exit public transport stop position with Overpass.
    Recovery Block pattern is used to deal with inconsistent OSM data.
    """
    try:
        logger.debug("First try retrieving start and exit stop position")
        lines = _get_public_transport_lines(lookup_position, start_uic_ref, exit_uic_ref, line)
    except ValueError as fallback_1:
        logger.debug(fallback_1)
        try:
            logger.debug("Second try retrieving start and exit stop position")
            lines = _get_public_transport_lines_fallback(lookup_position, start_uic_ref, exit_uic_ref, line)
        except ValueError as fallback_2:
            logger.debug(fallback_2)
            fallback_message = f"Start and exit stop position cannot be retrieved with the current OSM data " \
                               f"for the start_uic_ref {start_uic_ref}, exit_uic_ref {exit_uic_ref} and line {line}, " \
                               f"returning fallback coordinates"
            logger.debug(fallback_message)
            raise ValueError(fallback_message)

    return _get_public_transport_stop_node(lines)


def _get_public_transport_lines(start_position: tuple, start_uic_ref: str, exit_uic_ref: str, line: str) -> list:
    """
    Retrieves all public transport lines (relations) that serve the public transport stop node
    with ref start_uic_ref. We'll get more than one one for a specific uic_ref (for each
    direction of travel). The nodes (with ref start_uic_ref or exit_uic_ref)
    will be assigned to the relation (public transport lines) that have the node as a member.
    The exit nodes are necessary to retrieve the line in the right direction of travel
    in a later step.
    """
    bbox = _parse_bounding_box(*start_position, INITIAL_STOP_BOUNDING_BOX_BUFFER_METERS)
    query_str = f"""
        node(r:"stop")["uic_ref"={start_uic_ref}]({bbox});
        rel({bbox})["type"="route"]["ref"={line}]->.lines;
        (.lines;);
        out;
        node(r.lines:"stop")["uic_ref"~"{start_uic_ref}|{exit_uic_ref}"];
        out;
        """

    result = _query(query_str)
    if not result.nodes or not result.relations:
        raise ValueError(f"No start and exit nodes or relations could be retrieved for {start_uic_ref}, "
                         f"fallback to more complex retrieval")
    return _merge_nodes_with_corresponding_relation(result.nodes, result.relations, start_uic_ref)


def _get_public_transport_lines_fallback(start_position: tuple, start_uic_ref: str, exit_uic_ref: str,
                                         line: str) -> list:
    """
    Same motivation as in _get_public_transport_lines().
    Some public transport stops are not mapped with an uic_ref, so we'll use the Recovery Block pattern to provide
    an alternative possibility to retrieve the public transport lines.

    To achieve that, we'll retrieve the start and exit nodes separately.
    This results in two requests to Overpass and thus a longer response time.
    """
    start_stops, lines = _get_start_stops_and_lines(start_position, start_uic_ref, line)
    exit_stops = _get_exit_stops(start_position, start_uic_ref, exit_uic_ref, line)
    return _merge_nodes_with_corresponding_relation_fallback(start_stops, exit_stops, lines)


def _get_start_stops_and_lines(start_position: tuple, start_uic_ref: str, line: str) -> Tuple[list, list]:
    """
    Returns the start public transport stops and the corresponding line that serves the stop
    based on the provided line and uic_ref.

    Use this method if it is not possible to retrieve nodes with the uic_ref.
    In that case the nodes and lines will retrieved based on the relation with the given uic_ref.
    stop_area (relation) are also mostly mapped with the uic_ref.
    """
    bbox = _parse_bounding_box(*start_position, INITIAL_STOP_BOUNDING_BOX_BUFFER_METERS)
    query_str = f"""
            rel({bbox})["uic_ref"={start_uic_ref}];
            node(r)["public_transport"="stop_position"]->.initialstops;
            rel(bn.initialstops)["ref"={line}]->.lines;
            (.lines;);
            out;
            node(r.lines);
            node.initialstops._->.startstops;
            (.startstops;);
            out;
            """

    result = _query(query_str)
    if not result.nodes or not result.relations:
        raise ValueError(f"No start nodes or relations could be retrieved for {start_uic_ref}")
    return result.nodes, result.relations


def _get_exit_stops(start_position: tuple, start_uic_ref: str, exit_uic_ref: str, line: str) -> list:
    """
    Returns the exit public transport stops based on the exit_uic_ref.
    The relations for the line are loaded based on the line and the start_uic_ref.
    start_uic_ref is needed because the bounding box includes only relations with the start_uic_ref.
    For the loaded relations all public transport stop nodes are selected. Based on these nodes all
    parent relations with the exit_uic_ref are retrieved. This could for our advantage include platform relations.
    We are now able to select the public transport stops that are member of this relation.

    Same reason to use as in _get_start_stops_and_lines().
    """
    bbox = _parse_bounding_box(*start_position, INITIAL_STOP_BOUNDING_BOX_BUFFER_METERS)
    query_str = f"""
                rel({bbox})["uic_ref"={start_uic_ref}];
                node(r)["public_transport"="stop_position"]->.initialstartstops;
                rel(bn.initialstartstops)["ref"={line}]->.lines;
                node(r.lines:"stop");
                rel(bn)["uic_ref"={exit_uic_ref}]->.stoprelations;
                node(r.stoprelations)["public_transport"="stop_position"]->.initialstops;
                node(r.lines)->.stops;
                node.initialstops.stops->.exitstops;
                (.exitstops;);
                out;
                """

    result = _query(query_str)
    if not result.nodes:
        raise ValueError(f"No exit nodes could be retrieved for {exit_uic_ref}")
    return result.nodes


def _merge_nodes_with_corresponding_relation(nodes: list, relations: list, start_uic_ref: str) -> list:
    """
    Merges nodes to relations based on the members in the relation.
    start_uic_ref is required to differ between start and exit nodes.
    """
    lines = []
    for relation in relations:
        start_node = None
        start_node_modify_counter = 0
        exit_node = None
        for node in nodes:
            for member in relation.members:
                if node.id == member.ref:
                    if node.tags.get('uic_ref') == start_uic_ref:
                        start_node = node
                        start_node_modify_counter += 1
                    else:
                        exit_node = node

        if start_node is None or exit_node is None:
            continue
        if start_node_modify_counter > 1:
            raise ValueError(f"Start node with uic_ref {start_uic_ref} was set {start_node_modify_counter} times, "
                             f"thus one relation is used to map both direction of travels, "
                             f"fallback to more complex retrieval")
        lines.append({'rel': relation, 'start': start_node, 'exit': exit_node})
    if not lines:
        raise ValueError(f"Could not merge start and exit node to a relation based on the uic_ref {start_uic_ref}, "
                         f"fallback to more complex retrieval")
    return lines


def _merge_nodes_with_corresponding_relation_fallback(start_nodes: list, exit_nodes: list, relations: list) -> list:
    """ merges start nodes und exit nodes to relations based on the members in the relation """
    lines = []
    for relation in relations:
        start_node = None
        exit_node = None
        for member in relation.members:
            for temp_start_node in start_nodes:
                if temp_start_node.id == member.ref:
                    start_node = temp_start_node
                    break
            for temp_exit_node in exit_nodes:
                if temp_exit_node.id == member.ref:
                    exit_node = temp_exit_node
                    break
        if start_node is None or exit_node is None:
            continue
        lines.append({'rel': relation, 'start': start_node, 'exit': exit_node})
    if not lines:
        fallback_message = "Could not merge start and exit node to a relation based on the provided relation," \
                           "start nodes and exit nodes, return fallback coordinates"
        logger.debug(fallback_message)
        raise ValueError(fallback_message)
    return lines


def _get_public_transport_stop_node(lines: list) -> tuple:
    """
    OSM returns multiple nodes for a given uic_ref. Based on a
    start node and exit node, it's possible to retrieve the start and exit node that belong
    to the public transport line in the right direction of travel based on the order
    of the start and exit node in the relation.
    """
    start_node = None
    start_node_modify_counter = 0
    exit_node = None
    for line in lines:
        for member in line['rel'].members:
            if member.ref == line['start'].id:
                if start_node and start_node != line['start']:
                    start_node_modify_counter += 1
                start_node = line['start']
                exit_node = line['exit']
            elif member.ref == line['exit'].id:
                break

    """
    Should fail if the start node is modified multiple times or is not set at all.
    Both cases result from the fact that the order of the nodes in the relation is not correct.
    """
    if start_node_modify_counter > 1 or not start_node or not exit_node:
        raise ValueError("Could not retrieve start and exit node because of an incorrect order in the relation")
    else:
        return (float(start_node.lon), float(start_node.lat)), \
               (float(exit_node.lon), float(exit_node.lat))


def _parse_bounding_box(longitude: float, latitude: float, buffer_meters) -> str:
    """ calculates the bounding box for a specific location and a given buffer """
    buffer_degrees = _meters_to_degrees(buffer_meters)

    # divide by 2 to add only half on each side
    buffer_latitude = buffer_degrees / 2
    buffer_longitude = buffer_degrees * (1 / math.cos(math.radians(longitude))) / 2

    south = latitude - buffer_latitude
    west = longitude - buffer_longitude
    north = latitude + buffer_latitude
    east = longitude + buffer_longitude

    return f'{south},{west},{north},{east}'


def _meters_to_degrees(meters: int) -> float:
    """ convert meters to approximate degrees """
    # meters * 360 / (2 * PI * 6400000)
    # multiply by (1/cos(lat) for longitude)
    return meters * 1 / 111701


def _query(query: str) -> overpy.Result:
    """ handles the communication with overpass and provides error handling """
    try:
        return API.query(query)
    except BaseException as exception:
        msg = f'overpass is not running correctly: {exception}'
        logger.error(msg)
        raise ServiceError(msg) from None
