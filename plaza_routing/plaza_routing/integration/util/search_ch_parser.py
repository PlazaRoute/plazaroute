import json
import colander


class ExitType(colander.SchemaType):
    """
    The exit attribute is not always defined and there is no other
    solution to define a default value for a colander.MappingSchema.
    """
    def serialize(self, node, appstruct):
        raise NotImplementedError()

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null
        return Exit().deserialize(cstruct)


class Exit(colander.MappingSchema):
    stopid = colander.SchemaNode(colander.String(), missing=None)
    name = colander.SchemaNode(colander.String(), missing=None)
    arrival = colander.SchemaNode(colander.String())
    x = colander.SchemaNode(colander.Int())
    y = colander.SchemaNode(colander.Int())


class Leg(colander.MappingSchema):
    departure = colander.SchemaNode(colander.String(), missing=None)
    stopid = colander.SchemaNode(colander.String())
    name = colander.SchemaNode(colander.String(), missing=None)
    line = colander.SchemaNode(colander.String(), missing=None)
    line_type = colander.SchemaNode(colander.String(), name='type', missing=None)
    terminal = colander.SchemaNode(colander.String(), missing=None)
    exit = colander.SchemaNode(ExitType(), missing=[])
    x = colander.SchemaNode(colander.Int())
    y = colander.SchemaNode(colander.Int())


class Legs(colander.SequenceSchema):
    leg = Leg()


class Connection(colander.MappingSchema):
    start = colander.SchemaNode(colander.String(), name='from')
    departure = colander.SchemaNode(colander.String())
    to = colander.SchemaNode(colander.String())
    arrival = colander.SchemaNode(colander.String())
    duration = colander.SchemaNode(colander.Int())
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
        print(f'colander failed with {e.asdict()} for response {response}')
        raise RuntimeError(e.asdict())


def _add_calculated_values(connections):
    for connection in connections:
        connection['number_of_legs'] = len(connection['legs'])
