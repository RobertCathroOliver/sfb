"""Convert objects to other representations."""

class Converter(object):
    """Converts objects to another representation according a schema."""

    def __init__(self, schema, nested_converter=None):
	"""Initializer the converter with a schema.

	schema - a map of data types to conversion rules
	nested_converter - a Converter to use on nested data values (e.g. in dicts)
	"""
	self.schema = {}
	self.update_schema(schema)
	self.nested_converter = nested_converter or self

    def update_schema(self, schema):
	"""Update the schema with a dict of conversion rules."""
	self.schema.update(schema)

    def find_rule(self, obj):
	"""Return the conversion rule for obj."""
        for c in obj.__class__.__mro__:
	    if c in self.schema:
		return self.schema[c]
	raise TypeError('no conversion rule for {0} objects'.format(obj.__class__))

    def convert(self, obj, is_accessible=None):
	"""Return the conversion of obj according the schema.

	obj - the object to be converted
	is_accessible - a function indicating whether a resource can be used
        """
	rule = self.find_rule(obj)
	is_accessible = is_accessible or (lambda x: True)
	return rule.convert(obj, self.nested_converter, is_accessible)


class ConversionRule(object):
    """Base class for conversion rules."""
    def convert(self, obj, converter, is_accessible):
        return obj if is_accessible(obj) else None


class SimpleConversionRule(ConversionRule):
    """Converts an object using a cast."""
    def __init__(self, cast):
	self.cast = cast
    def convert(self, obj, converter, is_accessible):
	if not is_accessible(obj):
	    return None
	return self.cast(obj)


class ClassConversionRule(ConversionRule):
    """Converts a class by converting its attributes."""
    def __init__(self, key_values):
        self.key_values = key_values
    def convert(self, obj, converter, is_accessible):
        if not is_accessible(obj):
            return None
	def attr(getter):
	    if callable(getter):
		return getter(obj)
	    return getattr(obj, getter, None)
	def get_key(key):
	    if callable(key):
                return key(obj)
	    return key
        result = dict((get_key(k), converter.convert(attr(v), is_accessible))
                      for k, v in self.key_values.items() if get_key(k))
        return result


class SequenceConversionRule(ConversionRule):
    """Converts a sequence (e.g. list, tuple) by converting its items."""
    def __init__(self, constructor=list):
	self.constructor = constructor
    def convert(self, obj, converter, is_accessible):
	if not is_accessible(obj):
	    return None
	result = self.constructor(r for r in 
		  (converter.convert(o, is_accessible) for o in obj) 
		  if r is not None)
	return result


class MapConversionRule(ConversionRule):
    """Converts a map (e.g. dict) by converting its items."""
    def __init__(self, constructor=dict):
	self.constructor = constructor
    def convert(self, obj, converter, is_accessible):
	if not is_accessible(obj):
	    return None
	result = self.constructor((k, v) for k, v in 
		                    ((k, converter.convert(v, is_accessible)) 
			              for k, v in obj.items()) 
		                  if v is not None)
	return result

base_schema = {
    type(None): SimpleConversionRule(lambda obj: None),
    int: SimpleConversionRule(int),
    str: SimpleConversionRule(unicode),
    unicode: SimpleConversionRule(unicode),
    bool: SimpleConversionRule(bool),
    float: SimpleConversionRule(float),
    list: SequenceConversionRule(),
    tuple: SequenceConversionRule(),
    dict: MapConversionRule()
}

def output_converter(urlresolver):

    import jolly.action
    import jolly.breakpoint
    import jolly.chrono
    import jolly.command
    import jolly.core
    import jolly.db
    import jolly.map
    import jolly.system
    import jolly.util

    import sfb.chrono
    import sfb.damage
    import sfb.movement

    def make_href(url):
	return {'href': url}

    schema = {
        # jolly.map types
	jolly.map.Map: ClassConversionRule(
            {'width': (lambda obj: obj.bounds[0]), 
             'height': (lambda obj: obj.bounds[1]),
             'game': 'game',
	     'tokens': 'tokens'}),
        jolly.map.Token: ClassConversionRule(
            {'href': 'item',
             'position': 'position'}),
        jolly.map.Direction: SimpleConversionRule(unicode),
        jolly.map.Location: SimpleConversionRule(unicode),
        jolly.map.Position: SimpleConversionRule(unicode),
	jolly.map.LocationMask: SimpleConversionRule(lambda obj: make_href('firing-arc/{0}'.format(obj.name))),
	jolly.map.Bearing: SimpleConversionRule(lambda obj: '{0} - {1}'.format(obj.offset_direction, obj.rotation_direction)),

        # jolly.core types
        jolly.core.Game: ClassConversionRule(
            {'title': 'title',
             'players': (lambda obj: make_href(urlresolver.get_query_url_by_name('players', {'g': urlresolver.get_doc_id(obj)}))),
             'map': 'map',
	     'log': (lambda obj: make_href(urlresolver.get_url_by_name('gamelog', urlresolver.get_doc_id(obj.log)))),
	     'time': 'current_time'}),
        jolly.core.Player: ClassConversionRule(
            {'name': 'name',
             'user': 'owner',
	     'game': 'game',
	     'log': (lambda obj: make_href(urlresolver.get_url_by_name('log', urlresolver.get_doc_id(obj.log)))),
	     'status': 'status',
             'breakpoints': (lambda obj: make_href(urlresolver.get_query_url_by_name('breakpoints', {'player': urlresolver.get_doc_id(obj)}))),
	     'queue': (lambda obj: obj.queue),
	     'units': 'units'}),
        jolly.core.User: ClassConversionRule(
            {'name': 'name',
             'players': (lambda obj: make_href(urlresolver.get_query_url_by_name('players', {'user': urlresolver.get_doc_id(obj)})))}),
	jolly.core.ActionLog: ClassConversionRule(
	    {(lambda obj: 'player' if isinstance(obj.owner, jolly.core.Player) else 'game'): 'owner',
             'actions': 'actions'}),
	jolly.core.Status: ClassConversionRule(
	    {'player': 'owner',
	     'status': 'status',
	     (lambda obj: 'details' if obj.details else None): 'details'}),

        # jolly.system Types
        jolly.system.System: ClassConversionRule(
            {'id': 'id',
            (lambda obj: 'player' if obj.subsystems else None): 'owner',
            (lambda obj: 'unit' if not obj.subsystems else None): 'owner',
             'prototype': 'prototype',
             'properties': 'properties',
             'subsystems': 'subsystems'}),
        jolly.system.Prototype: SimpleConversionRule(lambda obj: make_href('prototype/{0}'.format(obj.name))),

        # jolly.chrono Types
        jolly.chrono.Moment: SimpleConversionRule(unicode),

	# jolly.command Types
	jolly.command.Command: ClassConversionRule(
	    {'owner': 'owner',
	     'template': 'template',
             'time': 'time',
             'status': 'status',
             'arguments': 'arguments',
	     'queue': (lambda obj: obj.queue)}),
        jolly.command.CommandTemplate: SimpleConversionRule(lambda obj: make_href('command-template/{0}'.format(obj.name))),
        jolly.command.CommandQueue: ClassConversionRule(
            {'player': 'owner',
             'commands': (lambda obj: [o for o in obj if not o.cancelled])}),

        # other Types
	jolly.action.Action: ClassConversionRule(
	    {'action-type': 'action_type',
	     'time': 'time',
	     'target': 'target',
	     'description': 'description',
	     (lambda obj: 'details' if obj.details else None): 'details',
	     (lambda obj: 'player' if obj.owner else None): 'owner'}),
	jolly.breakpoint.BreakPoint: ClassConversionRule(
	    {'player': 'owner',
	     'action-type': 'action_type'}),
	jolly.breakpoint.SequenceOfPlayBreakPoint: ClassConversionRule(
	    {'player': 'owner',
	     'action-type': 'action_type',
	     'time': 'time'}),
	jolly.breakpoint.PropertyChangeBreakPoint: ClassConversionRule(
	    {'player': 'owner',
	     'action-type': 'action_type',
	     'system': 'system',
	     'property': 'property_name'}),
        sfb.damage.DamageAllocationChart: SimpleConversionRule(lambda obj: {'href': 'damage-allocation-chart/{0}'.format(obj.name)}),
	jolly.util.Range: SimpleConversionRule(lambda obj: [obj.begin, obj.end]),
	jolly.util.RangeDict: SimpleConversionRule(lambda obj: [{'start': k.begin, 'end': k.end, 'value': v} for k, v in obj.ranges.items()]),
	sfb.movement.SpeedPlot: SimpleConversionRule(lambda obj: [{'start': k.begin, 'end': k.end, 'value': v} for k, v in obj.speeds.ranges.items()]),
	sfb.movement.AccelerationLimit: SimpleConversionRule(lambda obj: {'max-speed': obj.max_speed, 'max-additional-speed': obj.max_addition, 'max-speed-multiple': obj.max_multiple}),
	sfb.movement.TurnMode: SimpleConversionRule(lambda obj: {'href': 'turn-mode/{0}'.format(obj.name)}),
	sfb.chrono.Duration: SimpleConversionRule(lambda obj: obj.impulses),
	jolly.db.Ref: SimpleConversionRule(lambda obj: make_href(urlresolver.get_url(obj.instantiate()))),
	jolly.db.BackRef: SimpleConversionRule(lambda obj: make_href(urlresolver.get_url_by_name(obj.type_, obj.doc_id))),
    }

    value_schema = {}
    value_schema.update(base_schema)
    value_schema.update(schema)

    def get_url(obj):
	url = urlresolver.get_url(obj)
	return make_href(url)

    ref_schema = {}
    ref_schema.update(base_schema)
    ref_schema.update(schema)
    ref_schema.update({
        jolly.map.Map: SimpleConversionRule(get_url),
	jolly.system.System: SimpleConversionRule(get_url),
	jolly.command.Command: SimpleConversionRule(get_url),
	jolly.command.CommandQueue: SimpleConversionRule(get_url),
        jolly.core.Player: SimpleConversionRule(get_url),
	jolly.core.User: SimpleConversionRule(get_url),
	jolly.core.Game: SimpleConversionRule(get_url),
	jolly.core.ActionLog: SimpleConversionRule(get_url),
	jolly.core.Status: SimpleConversionRule(get_url),
	jolly.breakpoint.BreakPoint: SimpleConversionRule(get_url),
	jolly.breakpoint.SequenceOfPlayBreakPoint: SimpleConversionRule(get_url),
	jolly.breakpoint.PropertyChangeBreakPoint: SimpleConversionRule(get_url),
    })
    converter = Converter(value_schema, Converter(ref_schema))
    return converter

