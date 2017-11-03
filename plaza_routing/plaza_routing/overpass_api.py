import overpy
import math

OVERPASS_API_URL = 'http://overpass.osm.ch/api/interpreter'
BOUNDING_BOX_BUFFER_METERS = 1000

API = overpy.Overpass(url=OVERPASS_API_URL)


def get_public_transport_stops(latitude, longitude):
    """ retrieves all public transport stop names for a specific location in a given range """
    bbox = _parse_bounding_box(latitude, longitude)
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
    based on the ordering of the nodes (with start_uic_ref and exit_uic_ref)
    in the relation (ex. bus lines) that serves the stop.
    If the node with ref exit_uic_ref comes after the node with ref start_uic_ref
    in the relation, we've got the public transport stop in the right direction of travel.
    """

    lines = _get_public_transport_lines(start_position,
                                        line, start_uic_ref, exit_uic_ref)
    start_node = _get_public_transport_stop_node(lines)
    # TODO work with Decimal objects or parse to floats
    return (float(start_node.lat), float(start_node.lon))


def _get_public_transport_lines(start_position,
                                line, start_uic_ref, exit_uic_ref):
    """
    Retrieves all public transport lines (relations) that serve the public transport stop node
    with ref start_uic_ref. We'll get more than one one for a specific uic_ref.
    The nodes will be assigned to the relation (public transport lines) that have
    the node as a member. The exit nodes are necessary to retrieve the line
    in the right direction of travel in a later step.
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


def _merge_nodes_with_corresponding_relation(nodes, relations, start_uic_ref):
    """ merge nodes to relations based on the members in the relation """
    lines = []
    for relation in relations:
        for node in nodes:
            for member in relation.members:
                if node.id == member.ref:
                    if node.tags.get('uic_ref') == start_uic_ref:
                        start_node = node
                    else:
                        exit_node = node
        lines.append({'rel': relation, 'start': start_node, 'exit': exit_node})
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
    raise RuntimeError("Start node of transport lines not found")


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
