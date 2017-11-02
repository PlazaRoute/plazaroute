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


class Leg(colander.MappingSchema):
    departure = colander.SchemaNode(colander.String(), missing=None)
    stopid = colander.SchemaNode(colander.String())
    name = colander.SchemaNode(colander.String(), missing=None)
    line = colander.SchemaNode(colander.String(), missing=None)
    line_type = colander.SchemaNode(colander.String(), name='type', missing=None)
    exit = colander.SchemaNode(ExitType(), missing=[])


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
        return SearchChResponse().deserialize(json.loads(response))
    except colander.Invalid as e:
        raise RuntimeError(e.asdict())
    except:
        raise ValueError('connections cannot be parsed')
