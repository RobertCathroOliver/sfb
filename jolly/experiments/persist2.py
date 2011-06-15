import functools
import operator

top_level_schemas = {}
base_schemas = {}

base_schemas = {
  jolly.sfb.firing_arc.FiringArc : str,
  jolly.sfb.movement.TurnMode : str,
  jolly.sfb.movement.AccelerationLimit : {'max_speed' : str,
                                          'max_addition' : str,
                                          'max_multiple' : str},
  jolly.sfb.chrono.Duration : {'turns' : str, 'impulses' : str},
  jolly.sfb.movement.SpeedPlot : 
  jolly.map.Position : str,
  str : str,
  int : str


def register_schema(schemas, schema):
    schemas[schema.key] = schema

class Schema(object):
    """A template for serializing an object of a given class."""

    def __init__(self, class_, fields):
        self._class = class_
        self._fields = fields

    @property
    def key(self):
        return self._class

    def serialize(self, object, registry):
        return dict((f.name, f.serialize(object, registry)) for f in self._fields)

class SchemaField(object):
    
    def __init__(self, name, accessor, serializer):
        self._name = name
        self._accessor = accessor
        self._serializer = serializer

    @property
    def name(self):
        return self._name

    def serialize(self, object, registry):
        return self._serializer(self._accessor(object), registry)

def serialize_list_with(serializer):
    @functools.wraps(serializer)
    def wrapper(*args, **kwargs):
        return [serializer(arg) for arg in args]
    return wrapper

def serialize_dict_with(serializer):
    @functools.wraps(serializer)
    def wrapper(*args, **kwargs):
        return dict((k, serializer(v)) for (k, v) in args[0].items())
    return wrapper

string_serializer = lambda value, registry: str(value)
reference_serializer = lambda value, registry: 
string_list_serializer = serialize_list_with(str)
reference_list_serializer = serialize_list_with(get_uri)
string_dict_serializer = serialize_dict_with(str)
reference_dict_serializer = serialize_dict_with(get_uri)

field_accessor = operator.attrgetter
self_accessor = lambda x: x

## e.g. System

register_schema(schemas, 
                Schema(jolly.System,
                  SchemaField('id', self_accessor, get_uri),
                  SchemaField('prototype', field_accessor('_prototype'),
                      get_uri),
                  SchemaField('properties', field_accessor('_properties'),






