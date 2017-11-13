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


def get_initial_public_transport_stop_position(lookup_position, start_uic_ref, exit_uic_ref, line,
                                               fallback_initial_stop_position):
    """
    Retrieves the initial public transport stop position (latitude, longitude)
    for a specific uic_ref (start_uic_ref). OSM returns multiple public transport
    stops for a given uic_ref. We'll have to retrieve the right one
    based on the ordering of the nodes (with ref start_uic_ref or exit_uic_ref)
    in the relation (ex. bus lines) that serves the stop.
    If the node with ref exit_uic_ref comes after the node with ref start_uic_ref
    in the relation, we've got the public transport stop in the right direction of travel.

    Returns the fallback_initial_stop_position if all retrieval options from Overpass fail.
    """
    try:
        return _retrieve_initial_public_transport_stop_position(lookup_position, start_uic_ref, exit_uic_ref, line)
    except ValueError:
        return fallback_initial_stop_position


def _retrieve_initial_public_transport_stop_position(lookup_position, start_uic_ref, exit_uic_ref, line):
    """
    Retrieves the initial public transport stop position with Overpass.
    Recovery Block pattern is used to deal with inconsistent OSM data.
    """
    try:
        lines = _get_public_transport_lines(lookup_position, start_uic_ref, exit_uic_ref, line)
    except ValueError:
        try:
            lines = _get_public_transport_lines_fallback(lookup_position, start_uic_ref, exit_uic_ref, line)
        except ValueError:
            print(f'initial public transport stop position cannot be retrieved with the current OSM data '
                  f'for the uic_ref {start_uic_ref} and line {line}')
            raise ValueError(f'initial public transport stop position cannot be retrieved with the current OSM data '
                             f'for the uic_ref {start_uic_ref} and line {line}')

    start_node = _get_public_transport_stop_node(lines)
    return float(start_node.lat), float(start_node.lon)


def _get_public_transport_lines(start_position, start_uic_ref, exit_uic_ref, line):
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
    return _merge_nodes_with_corresponding_relation(result.nodes, result.relations, start_uic_ref)


def _get_public_transport_lines_fallback(start_position, start_uic_ref, exit_uic_ref, line):
    """
    Same motivation as in _get_public_transport_lines().
    Some public transport stops are not mapped with an uic_ref, so we'll use the Recovery Block pattern to provide
    an alternative possibility to retrieve the public transport lines.

    To achieve that, we'll retrieve the start and destination nodes separately.
    This results in two requests to Overpass and thus a longer response time.
    """
    start_stops, lines = _get_start_stops_and_lines(start_position, start_uic_ref, line)
    destination_stops = _get_destination_stops(start_position, start_uic_ref, exit_uic_ref, line)
    return _merge_nodes_with_corresponding_relation_fallback(start_stops, destination_stops, lines)


def _get_start_stops_and_lines(start_position, start_uic_ref, line):
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


def _get_destination_stops(start_position, start_uic_ref, exit_uic_ref, line):
    """
    Returns the destination public transport stops based on the exit_uic_ref.
    The relations for the line are loaded based on the line and the start_uic_ref.
    start_uic_ref is needed because the bounding box includes only relations with the start_uic_ref.
    For the loaded relations all public transport stop nodes are selected. Based on these nodes all
    parent relations with the exit_uic_ref are retrieved. This could for our advantage include platform relations.
    We are now able to select the public transport stops that are member of this relation.

    Same reason to use as in _get_start_stops_and_lines().
    """
    bbox = _parse_bounding_box(*start_position)
    query_str = f"""
                rel({bbox})["uic_ref"={start_uic_ref}];
                node(r)["public_transport"="stop_position"]->.initialstartstops;
                rel(bn.initialstartstops)["ref"={line}]->.lines;
                node(r.lines:"stop");
                rel(bn)["uic_ref"={exit_uic_ref}]->.stoprelations;
                node(r.stoprelations)["public_transport"="stop_position"]->.initialstops;
                node(r.lines)->.stops;
                node.initialstops.stops->.destinationstops;
                (.destinationstops;);
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
    for relation in relations:
        start_node = None
        exit_node = None
        for node in nodes:
            for member in relation.members:
                if node.id == member.ref:
                    if node.tags.get('uic_ref') == start_uic_ref:
                        start_node = node
                    else:
                        exit_node = node

        if start_node is None or exit_node is None:
            raise ValueError("Could not retrieve start and exit node based on the uic_ref, fallback to more complex "
                             "retrieval")
        lines.append({'rel': relation, 'start': start_node, 'exit': exit_node})
    return lines


def _merge_nodes_with_corresponding_relation_fallback(start_nodes, destination_nodes, relations):
    """ merges start nodes und destination nodes to relations based on the members in the relation """
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
                if temp_destination_node.id == member.ref:
                    destination_node = temp_destination_node
                    break
        if start_node is None or destination_node is None:
            raise ValueError("Could not retrieve start and exit node based on the provided relation, start nodes and "
                             "destination nodes, return fallback coordinate")
        lines.append({'rel': relation, 'start': start_node, 'exit': destination_node})
    return lines


def _get_public_transport_stop_node(lines):
    """
    OSM returns multiple nodes for a given uic_ref. Based on a
    start node and exit node, it's possible to retrieve the node that belongs
    to the public transport line in the right direction of travel based on the order
    of the start and exit node in the relation.
    """
    start_node = None
    start_node_modify_counter = 0
    for line in lines:
        for member in line['rel'].members:
            if member.ref == line['start'].id:
                start_node = line['start']
                start_node_modify_counter += 1
            elif member.ref == line['exit'].id:
                break

    """
    Should fail if the start node is modified multiple times or is not set at all.
    Both cases result from the fact that the order of the nodes in the relation is not correct.
    """
    if start_node_modify_counter > 1 or not start_node:
        raise ValueError("Could not retrieve start and exit node because of an incorrect order in the relation")
    else:
        return start_node


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
