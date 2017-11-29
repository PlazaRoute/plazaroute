import json
import colander
import logging


logger = logging.getLogger('plaza_routing.search_ch_parser')


class Exit(colander.MappingSchema):
    stopid = colander.SchemaNode(colander.String(), missing=None)
    name = colander.SchemaNode(colander.String(), missing=None)
    arrival = colander.SchemaNode(colander.String())
    x = colander.SchemaNode(colander.Int())
    y = colander.SchemaNode(colander.Int())


class LegType(colander.SchemaType):
    """
    Search.ch returns walking legs (type=walk) that will be skipped with colander.drop.
    The leg with a missing type is either the last leg or a an address with isaddress=True (if the destination that is
    passed to search.ch is an address). Both are of no use and will be skipped.
    """
    def serialize(self, node, appstruct):
        raise NotImplementedError()

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.drop
        if cstruct.get('type', '') == 'walk' or cstruct.get('type', '') == '':
            return colander.drop
        return Leg().deserialize(cstruct)


class Stopovers(colander.SequenceSchema):
    stop = Exit()


class Leg(colander.MappingSchema):
    departure = colander.SchemaNode(colander.String(), missing=None)
    stopid = colander.SchemaNode(colander.String())
    name = colander.SchemaNode(colander.String(), missing=None)
    line_type = colander.SchemaNode(colander.String(), name='type', missing=None)
    line = colander.SchemaNode(colander.String(), missing=None)
    track = colander.SchemaNode(colander.String(), missing='')
    terminal = colander.SchemaNode(colander.String(), missing=None)
    exit = Exit()
    x = colander.SchemaNode(colander.Int())
    y = colander.SchemaNode(colander.Int())
    stops = Stopovers()


class Legs(colander.SequenceSchema):
    leg = colander.SchemaNode(LegType())


class Connection(colander.MappingSchema):
    start = colander.SchemaNode(colander.String(), name='from')
    departure = colander.SchemaNode(colander.String())
    to = colander.SchemaNode(colander.String())
    arrival = colander.SchemaNode(colander.String())
    duration = colander.SchemaNode(colander.Float())
    legs = Legs()


class Connections(colander.SequenceSchema):
    connection = Connection()


class SearchChResponse(colander.MappingSchema):
    connections = Connections()


def parse_connections(response):
    """ parses a search.ch response to a suitable data structure """
    try:
        parsed_response = SearchChResponse().deserialize(json.loads(response))
        _add_calculated_values(parsed_response['connections'])
        return parsed_response
    except colander.Invalid as e:
        logger.debug(f'colander failed with {e.asdict()} for response {response}')
        raise RuntimeError(e.asdict())


def _add_calculated_values(connections):
    for connection in connections:
        connection['number_of_legs'] = len(connection['legs'])
