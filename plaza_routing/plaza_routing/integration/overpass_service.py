import overpy
import math

OVERPASS_API_URL = 'http://overpass.osm.ch/api/interpreter'
BOUNDING_BOX_BUFFER_METERS = 1000

API = overpy.Overpass(url=OVERPASS_API_URL)


def get_public_transport_stops(start_position):
    """ retrieves all public transport stop names for a specific location in a given range """
    bbox = _parse_bounding_box(*start_position)
    query_str = f"""
        [bbox:{bbox}];
        (
        node["public_transport"="stop_position"];
        );
        out body;
        """

    public_transport_stops = API.query(query_str)
    if not public_transport_stops.nodes:
        raise ValueError('no public transport stops found for the given location and range')

    return set(stop.tags.get('uic_name') for stop in public_transport_stops.nodes)


def get_initial_public_transport_stop_position(start_position, line,
                                               start_uic_ref, exit_uic_ref):
    """
    Retrieves the initial public transport stop position (latitude, longitude)
    for a specific uic_ref (start_uic_ref). OSM returns multiple public transport
    stops for a given uic_ref. We'll have to retrieve the right one
    based on the ordering of the nodes (with ref start_uic_ref or exit_uic_ref)
    in the relation (ex. bus lines) that serves the stop.
    If the node with ref exit_uic_ref comes after the node with ref start_uic_ref
    in the relation, we've got the public transport stop in the right direction of travel.
    """
    try:
        lines = _get_public_transport_lines(start_position, line, start_uic_ref, exit_uic_ref)
    except ValueError:
        try:
            lines = _get_public_transport_lines_fallback(start_position, line, start_uic_ref)
        except ValueError:
            print(f'initial public transport stop position cannot be retrieved with the current OSM data, '
                  f'the line {line} with start_uic_ref {start_uic_ref} should be skipped.')
            raise RuntimeError("initial public transport stop position cannot be retrieved")

    start_node = _get_public_transport_stop_node(lines)
    return float(start_node.lat), float(start_node.lon)


def _get_public_transport_lines(start_position, line,
                                start_uic_ref, exit_uic_ref):
    """
    Retrieves all public transport lines (relations) that serve the public transport stop node
    with ref start_uic_ref. We'll get more than one one for a specific uic_ref (for each
    direction of travel). The nodes (with ref start_uic_ref or exit_uic_ref)
    will be assigned to the relation (public transport lines)
    that have the node as a member. We'll also get multiple ones for each node.
    The exit nodes are necessary to retrieve the line in the right direction of travel
    in a later step.
    """
    bbox = _parse_bounding_box(*start_position)
    query_str = f"""
        node(r:"stop")["uic_ref"={start_uic_ref}]({bbox});
        rel({bbox})["type"="route"]["ref"={line}]->.lines;
        (.lines;);
        out;
        node(r.lines:"stop")["uic_ref"~"{start_uic_ref}|{exit_uic_ref}"];
        out;
        """
    result = API.query(query_str)
    return _merge_nodes_with_corresponding_relation(
        result.nodes, result.relations, start_uic_ref)


def _get_public_transport_lines_fallback(start_position, line,
                                         start_uic_ref):
    """
    Same motivation as in _get_public_transport_lines().
    Some public transport stops are not mapped with an uic_ref, so we'll use the Recovery Block pattern to provide
    an alternative possibility to retrieve the public transport lines.

    To achieve that, we'll retrieve the start and destination nodes separately.
    This results in two requests to Overpass and thus a longer response time.
    """
    start_stops, lines = _get_start_stops_and_lines(start_position, line, start_uic_ref)
    destination_stops = _get_destination_stops(start_position, line, start_uic_ref)
    return _merge_nodes_with_corresponding_relation_fallback(start_stops, destination_stops, lines)


def _get_start_stops_and_lines(start_position, line, start_uic_ref):
    """
    Returns the start public transport stops and the corresponding line that serves the stop
    based on the provided line and uic_ref.

    Use this method if it is not possible to retrieve nodes with the uic_ref.
    In that case the nodes and lines will retrieved based on the relation with the given uic_ref.
    stop_area (relation) are also mapped with the uic_ref.
    """
    bbox = _parse_bounding_box(*start_position)
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
    result = API.query(query_str)
    return result.nodes, result.relations


def _get_destination_stops(start_position, line, start_uic_ref):
    """
    Returns all possible public transport stops that are reachable
    based on the provided line and start_uic_ref.
    We are not able to retrieve only the nodes at the destination because of some public stop relations
    that do not hold an uic_ref.

    Same reason to use as in _get_start_stops_and_lines().
    """
    bbox = _parse_bounding_box(*start_position)
    query_str = f"""
                rel({bbox})["uic_ref"={start_uic_ref}];
                node(r)["public_transport"="stop_position"]->.initialstartstops;
                rel(bn.initialstartstops)["ref"={line}]->.lines;
                node(r.lines:"stop");
                rel(bn)->.stoprelations;
                node(r.stoprelations)["public_transport"="stop_position"]->.initialstops;
                node(r.lines)->.stops;
                node.initialstops.stops->.destinationstops;
                (.destinationstops; - .initialstartstops;);
                out;
                """
    result = API.query(query_str)
    return result.nodes


def _merge_nodes_with_corresponding_relation(nodes, relations, start_uic_ref):
    """
    Merges nodes to relations based on the members in the relation.
    start_uic_ref is required to differ between start and exit nodes.
    """
    lines = []
    start_node = None
    exit_node = None
    for relation in relations:
        for node in nodes:
            for member in relation.members:
                if node.id == member.ref:
                    if node.tags.get('uic_ref') == start_uic_ref:
                        start_node = node
                    else:
                        exit_node = node
        lines.append({'rel': relation, 'start': start_node, 'exit': exit_node})
    if start_node is None or exit_node is None:
        raise ValueError("Could not retrieve start and exit node based on the uic_ref, fallback to more complex "
                         "retrieval")
    return lines


def _merge_nodes_with_corresponding_relation_fallback(start_nodes, destination_nodes, relations):
    """
    Merges nodes to relations based on the members in the relation.
    """
    lines = []
    for relation in relations:
        start_node = None
        destination_node = None
        for member in relation.members:
            for temp_start_node in start_nodes:
                if temp_start_node.id == member.ref:
                    start_node = temp_start_node
                    break
            for temp_destination_node in destination_nodes:
                """
                We do not mind that the selected destination node does not correlate with our desired destination.
                We are using this node to determine the right direction of travel thus it is not of interest if
                the selected node is the last node in the relation or one in the middle.
                """
                if temp_destination_node.id == member.ref:
                    destination_node = temp_destination_node
                    break
        lines.append({'rel': relation, 'start': start_node, 'exit': destination_node})
    return lines


def _get_public_transport_stop_node(lines):
    """
    OSM returns multiple nodes for a given uic_ref. Based on a
    start node and exit node, it's possible to retrieve the node that belongs
    to the public transport line in the right direction of travel based on the order
    of the start and exit node in the relation.
    """
    for line in lines:
        for member in line['rel'].members:
            if member.ref == line['start'].id:
                start_node = line['start']
                return start_node
            elif member.ref == line['exit'].id:
                break
    raise ValueError("Could not retrieve start and exit node based on the id, no retrieval is possible in this case")


def _parse_bounding_box(latitude, longitude):
    """ calculates the bounding box for a specific location and a given buffer """
    buffer_degrees = _meters_to_degrees(BOUNDING_BOX_BUFFER_METERS)

    # divide by 2 to add only half on each side
    buffer_latitude = buffer_degrees / 2
    buffer_longitude = buffer_degrees * (1 / math.cos(math.radians(longitude))) / 2

    south = latitude - buffer_latitude
    west = longitude - buffer_longitude
    north = latitude + buffer_latitude
    east = longitude + buffer_longitude

    return f'{south},{west},{north},{east}'


def _meters_to_degrees(meters):
    """ convert meters to approximate degrees """
    # meters * 360 / (2 * PI * 6400000)
    # multiply by (1/cos(lat) for longitude)
    return meters * 1 / 111701
