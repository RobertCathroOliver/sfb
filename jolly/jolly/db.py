import uuid

from django.conf import settings
from couchdb.client import Server

from jolly.convert import (base_schema, ClassConversionRule, ConversionRule, 
                           Converter, SimpleConversionRule, MapConversionRule,
			   SequenceConversionRule)
from jolly.util import import_object

class Database(object):
    """CouchDB database interface."""

    def __init__(self, couchdb, identifier, serializer, deserializer):
	serializer_schema = {
            Ref: SimpleConversionRule(unicode),
	    Dict: MapConversionRule(),
	    List: SequenceConversionRule(),
	}
	serializer.update_schema(serializer_schema)
	serializer.nested_converter.update_schema(serializer_schema)

	def make_ref(doc_id):
            obj = self.get_object(doc_id)
            if obj and not isinstance(obj, Ref):
                return obj
	    return Ref(self, doc_id)

        deserialize_schema = {
            uuid.UUID: SimpleConversionRule(make_ref),
	    #lambda doc: Ref(self, doc)),
	    BackRef: SimpleConversionRule(lambda doc: make_ref(doc[8:])),
	    #lambda doc: Ref(self, doc[8:])),
            OwnedRef: SimpleConversionRule(lambda doc: self.restore_object(doc[6:]))
        }
        deserializer.update_schema(deserialize_schema)

        self.db = couchdb
        self.identifier = identifier
        self.serializer = serializer
        self.deserializer = deserializer

        # caches
        self.obj_cache = {}
        self.dirty_objs = set()
        self.revs = {}

    def truncate(self):
	"""Delete all the non-design documents from the database."""
	for doc_id in self.db:
	    if not '_design' in doc_id:
		del self.db[doc_id]

    def dirty(self, obj):
	"""Mark the object as dirty so it will be stored in the database."""
        doc_id = self.get_doc_id(obj)
        self.dirty_objs.add(doc_id)

    def dirty_all(self):
	"""Mark all stored objects as dirty."""
	for doc_id in self.obj_cache:
	    self.dirty_objs.add(doc_id)

    def store_object(self, obj):
        """Store obj in the database and return the document id."""

        doc_id = self.get_doc_id(obj)

        # if the object hasn't changed, do nothing
        if doc_id in self.obj_cache and not doc_id in self.dirty_objs:
            return doc_id

        # convert the object to its database representation
        doc = self.serializer.convert(obj)

        # maintain the correct _rev to avoid update conflicts
        rev = self.get_doc_rev(doc_id)
        if rev:
            doc['_rev'] = rev

        # actually store the document in the database
        self.db[doc_id] = doc

        # update the caches
        self.obj_cache[doc_id] = obj
        if doc_id in self.dirty_objs:
            self.dirty_objs.remove(doc_id)
        
        return doc_id

    def restore_object(self, doc_id):
        """Restore an object from the database given its document id."""
        # if we have the object and it is current, return it
        obj = self.get_object(doc_id)
        if obj:
            return obj

        # actually retrieve the document from the database
        doc = self.db[doc_id]

        obj = self.parse_doc(doc)
        return obj

    def delete_object(self, doc_id):
	"""Remove an object from the database given its document id."""
	if doc_id in self.obj_cache:
	    del self.obj_cache[doc_id]
	    del self.db[doc_id]

    def get_object(self, doc_id):
        """Return object if we have it and it is current."""
        if doc_id in self.obj_cache:
            obj = self.obj_cache[doc_id]
            if not doc_id in self.dirty_objs:
                return obj
        return None

    def parse_doc(self, doc):
        doc_id = doc['_id']

        # convert the document into its object representation
        obj = self.deserializer.convert(doc)

        # update the caches
        self.identifier.set_obj_id(obj, doc_id)
        self.obj_cache[doc_id] = obj
        if doc_id in self.dirty_objs:
            self.dirty_objs.remove(doc_id)
        self.revs[doc_id] = doc['_rev']

        return obj

    def restore_collection(self, name, filter=None):
        """Restore a collection of objects from the database."""
        if filter:
            view_results = self.db.view(name, key=filter)
        else:
            view_results = self.db.view(name)
        
        result = []
        for row in view_results:
            obj = self.get_object(row.id)
            if obj:
                result.append(obj)
            else:
                obj = self.parse_doc(row.value)
                result.append(obj)
        return result

    def get_doc_id(self, obj):
        """Return the document id of obj."""
        return self.identifier.get_obj_id(obj)

    def get_doc_rev(self, doc_id):
        """Return the document revision number."""
        return self.revs.get(doc_id, None)


class Ref(object):
    """A lazily loaded proxy object for a resource in the database."""

    def __init__(self, db, doc_id):
        self.db = db
        self.doc_id = doc_id
	self._doc_type = None

    def instantiate(self):
        obj = self.db.restore_object(self.doc_id)
        return obj

    def __getattr__(self, name):
	obj = self.instantiate()
	return getattr(obj, name)

    def __unicode__(self):
	return self.doc_id

class OwnedRef(Ref):
    """An object that should be stored by its referrer."""
    pass

class BackRef(Ref):
    """An object that should not be stored by its referrer."""

    def instantiate(self):
        """Explicit BackRefs should not be resolved."""
        return self

    def __unicode__(self):
	return 'backref:{0}'.format(self.doc_id)

class DocumentDeserializer(Converter):
    """A Converter for CouchDB documents."""

    def find_rule(self, doc):
        if self.is_uuid(doc):
            return self.schema[uuid.UUID]
        if self.is_backref(doc):
            return self.schema[BackRef]
        if self.is_deref(doc):
            return self.schema[OwnedRef]
        if hasattr(doc, '__contains__') and '*type' in doc:
            return self.schema[doc['*type']]
        return super(DocumentDeserializer, self).find_rule(doc)

    def is_uuid(self, doc):
        try:
            uuid.UUID(hex=doc)
            return True
        except (AttributeError, ValueError, TypeError):
            return False

    def is_backref(self, doc):
        try:
            return doc[0:8] == 'backref:' and self.is_uuid(doc[8:])
        except TypeError:
            return False
        return False

    def is_deref(self, doc):
        try:
            return doc[0:6] == 'deref:' and self.is_uuid(doc[6:])
        except TypeError:
            return False
        return False

class Dict(dict):

    def get(self, key, default=None):
	try:
	    return self[key]
	except KeyError:
	    pass
	return default

    def __getitem__(self, key):
	value = super(Dict, self).__getitem__(key)
	if isinstance(value, Ref):
	    return value.instantiate()
	return value

class List(list):

    def __getitem__(self, index):
	value = super(List, self).__getitem__(index)
	if isinstance(value, Ref):
	    return value.instantiate()
	return value

class DocumentRestorationRule(ConversionRule):
    """Converts a CouchDB document to an object."""

    def __init__(self, obj_class, field_rules):
        self.obj_class = obj_class
        self.field_rules = field_rules

    def convert(self, doc, converter, is_accessible):
        obj_type = import_object(self.obj_class)
        obj = object.__new__(obj_type)

        lazy_fields = {}
        for name, field_rule in self.field_rules.items():
            if callable(field_rule):
                field = field_rule(doc)
            else:
                field = converter.convert(doc[name], is_accessible)
            if isinstance(field, Ref):
                lazy_fields[name] = field
            else:
                setattr(obj, name, field)
        if lazy_fields:
            obj._jolly_lazy_fields = lazy_fields
            def __getattr__(s, name):
                if '_jolly_lazy_fields' in s.__dict__ and name in s._jolly_lazy_fields:
                    field = s._jolly_lazy_fields[name].instantiate()
                    s.__dict__[name] = field
                    del s._jolly_lazy_fields[name]
                    if not s._jolly_lazy_fields:
                        del s._jolly_lazy_fields
                    return field
                error_msg = "'{0}' object has no attribute '{1}'"
                raise AttributeError(error_msg.format(type(s).__name__, name))
            obj.__class__.__getattr__ = __getattr__
        return obj

def serializer():
    import jolly.action
    import jolly.chrono
    import jolly.command
    import jolly.core
    import jolly.map
    import jolly.system
    import jolly.util
    import sfb.damage
    import sfb.movement
    import sfb.chrono

    schema = {}
    schema.update(base_schema)
    schema.update({
        # jolly.map types
        jolly.map.Position: ClassConversionRule(
            {'*type': (lambda obj: 'position'), 
             'location': 'location', 
             'facing': 'facing'}),
        jolly.map.HexLocation: ClassConversionRule(
            {'*type': (lambda obj: 'hexlocation'), 
             'coordinates': 'coordinates'}),
        jolly.map.Direction: ClassConversionRule(
            {'*type': (lambda obj: 'direction'), 
             'name': 'name'}),
        jolly.map.LocationMask: ClassConversionRule(
            {'*type': (lambda obj: 'location-mask'), 
             'name': 'name'}),
        jolly.map.Bearing: ClassConversionRule(
            {'*type': (lambda obj: 'bearing'), 
             'offset_direction': 'offset_direction', 
             'rotation_direction': 'rotation_direction'}),

        # jolly.system types
        jolly.system.System: ClassConversionRule(
            {'*type': (lambda obj: 'system'), 
             'id': 'id', 
             'prototype': 'prototype', 
             'properties': 'properties', 
             'subsystems': 'subsystems'}),
        jolly.system.Prototype: ClassConversionRule(
            {'*type': (lambda obj: 'prototype'), 
             'name': 'name'}),

        # jolly.command types
        jolly.command.CommandTemplate: ClassConversionRule(
            {'*type': (lambda obj: 'command-template'), 
             'name': 'name'}),

        # jolly.core types
        jolly.core.User: ClassConversionRule(
            {'*type': (lambda obj: 'user'), 
             'name': 'name', 
             'email': 'email', 
             'password': 'password'}),

	
        # jolly.chrono types
        jolly.chrono.Moment: ClassConversionRule(
            {'*type': (lambda obj: 'moment'), 
             'name': 'name', 
             'description': 'description', 
             'path': 'path', 
             'multiple': 'multiple'}),

        # other types
        sfb.damage.DamageAllocationChart: ClassConversionRule(
            {'*type': (lambda obj: 'damage-allocation-chart'), 
             'name': 'name'}),
        sfb.damage.RuleSet: ClassConversionRule(
            {'*type': (lambda obj: 'rule-set'), 
             'system_types': 'system_types'}),
        sfb.movement.SpeedPlot: ClassConversionRule(
            {'*type': (lambda obj: 'speed-plot'), 
             'speeds': 'speeds'}),
        sfb.movement.AccelerationLimit: ClassConversionRule(
            {'*type': (lambda obj: 'acceleration-limit'), 
             'max_speed': 'max_speed', 
             'max_addition': 'max_addition', 
             'max_multiple': 'max_multiple'}),
        sfb.movement.TurnMode: ClassConversionRule(
            {'*type': (lambda obj: 'turn-mode'), 
             'name': 'name'}),
        sfb.chrono.Duration: ClassConversionRule(
            {'*type': (lambda obj: 'duration'), 
             'turns_only': 'turns_only', 
             'impulses': 'impulses'}),
        jolly.util.RangeDict: ClassConversionRule(
            {'*type': (lambda obj: 'range-dict'), 
             'ranges': (lambda obj: [[r.begin, r.end, v] for r, v in obj.ranges.items()])}),
    })

    value_schema = {}
    value_schema.update(schema)

    ref_schema = {}
    ref_schema.update(schema)

    serializer = Converter(value_schema, Converter(ref_schema))
    return serializer

def update_serializer(db):

    import jolly.action
    import jolly.breakpoint
    import jolly.command
    import jolly.core
    import jolly.map
    import jolly.system

    def make_backref(attr):
        def backref(obj):
            if not hasattr(obj, attr):
                return None
	    value = getattr(obj, attr)
	    if value is None:
		return None
            return 'backref:{0}'.format(
                db.get_doc_id(value))
        return backref

    ref_schema = {
        jolly.map.Map: SimpleConversionRule(db.store_object),
        jolly.system.System: SimpleConversionRule(db.store_object),
        jolly.command.Command: SimpleConversionRule(db.store_object),
        jolly.command.CommandQueue: SimpleConversionRule(db.store_object),
        jolly.core.Player: SimpleConversionRule(db.store_object),
        jolly.core.User: SimpleConversionRule(db.store_object),
        jolly.core.Game: SimpleConversionRule(db.store_object),
	jolly.action.Action: SimpleConversionRule(db.store_object),
	jolly.breakpoint.BreakPoint: SimpleConversionRule(db.store_object),
	jolly.core.ActionLog: SimpleConversionRule(db.store_object),
	jolly.core.Status: SimpleConversionRule(db.store_object),
    }

    def make_unowned_dict(attr):
        def unowned_dict(obj):
            if not hasattr(obj, attr):
                return None
	    attr_value = getattr(obj, attr)
	    if not isinstance(attr_value, dict):
		return None
            values = attr_value.items()
            return dict((k, BackRef(db, db.get_doc_id(v)) 
                            if type(v) in ref_schema else v) for k, v in values)
        return unowned_dict

    def make_unowned_list(attr):
	def unowned_list(obj):
	    if not hasattr(obj, attr):
		return None
	    values = getattr(obj, attr)
	    if not isinstance(values, (list, tuple)):
		return None
	    return [BackRef(db, db.get_doc_id(v)) if type(v) in ref_schema else v for v in values]
	return unowned_list

    value_schema = {
        jolly.map.Token: ClassConversionRule(
            {'*type': (lambda obj: 'token'), 
             'item': make_backref('item'), 
             'position': 'position'}),
        jolly.map.Map: ClassConversionRule(
           {'*type': (lambda obj: 'map'), 
            'bounds': 'bounds', 
            'tokens': 'tokens', 
            'game': make_backref('game')}),
        jolly.core.Player: ClassConversionRule(
            {'*type': (lambda obj: 'player'), 
             'name': 'name', 
             'units': 'units', 
	     'breakpoints': 'breakpoints',
	     'log': 'log',
	     'status': 'status',
             'game': make_backref('game'), 
             'owner': make_backref('owner'),
             'queue': 'queue'}),
        jolly.core.Game: ClassConversionRule(
            {'*type': (lambda obj: 'game'), 
             'map': 'map', 
             'players': 'players', 
	     'game_queue': 'game_queue',
             'last_command': make_backref('last_command'), 
	     'current_time': 'current_time',
	     'last_actions': make_unowned_list('last_actions'),
	     'log': 'log',
             'title': 'title'}),
	jolly.action.Action: ClassConversionRule(
	    {'*type': (lambda obj: 'action'),
	     'action_type': 'action_type',
	     'description': 'description',
	     'details': make_unowned_dict('details'),
	     'target': make_backref('target'),
	     'owner': make_backref('owner'),
	     'time': 'time',
	     'private': 'private'}),
	jolly.core.ActionLog: ClassConversionRule(
	    {'*type': (lambda obj: 'action-log'),
	     'owner': make_backref('owner'),
	     'actions': 'actions'}),
	jolly.core.Status: ClassConversionRule(
	    {'*type': (lambda obj: 'status'),
	     'owner': make_backref('owner'),
	     'status': 'status',
	     'details': make_unowned_list('details')}),
        jolly.system.System: ClassConversionRule(
            {'*type': (lambda obj: 'system'), 
             'id': 'id', 
             'prototype': 'prototype', 
             'properties': make_unowned_dict('properties'),
             'subsystems': 'subsystems', 
             'owner': make_backref('owner')}),
        jolly.command.Command: ClassConversionRule(
            {'*type': (lambda obj: 'command'), 
             'owner': make_backref('owner'),
             'template': 'template', 
             'time': 'time', 
             'arguments': make_unowned_dict('arguments'),
             'queue': make_backref('queue'),
             'done': 'done', 
             'cancelled': 'cancelled'}),
        jolly.command.CommandQueue: ClassConversionRule(
            {'*type': (lambda obj: 'command-queue'), 
             'commands': 'commands', 
             'owner': make_backref('owner')}),
	jolly.breakpoint.BreakPoint: ClassConversionRule(
	    {'*type': (lambda obj: 'breakpoint'),
	     'owner': make_backref('owner'),
	     'action_type': 'action_type'}),
	jolly.breakpoint.SequenceOfPlayBreakPoint: ClassConversionRule(
	    {'*type': (lambda obj: 'sequence-of-play-breakpoint'),
	     'owner': make_backref('owner'),
	     'action_type': 'action_type',
	     'time': 'time'}),
	jolly.breakpoint.PropertyChangeBreakPoint: ClassConversionRule(
	    {'*type': (lambda obj: 'property-change-breakpoint'),
	     'owner': make_backref('owner'),
	     'action_type': 'action_type',
	     'system': make_backref('system'),
	     'property_name': 'property_name'}),
    }

    db.serializer.update_schema(value_schema)
    db.serializer.nested_converter.update_schema(ref_schema)
    other_refs = {
        jolly.map.Token: ClassConversionRule(
            {'*type': (lambda obj: 'token'), 
             'item': make_backref('item'), 
             'position': 'position'}),
    }
    db.serializer.nested_converter.update_schema(other_refs)

    return db


def deserializer():

    import jolly.map
    import jolly.util

    registry = import_object(settings.REGISTRY)
    sequence_of_play = import_object(settings.SEQUENCE_OF_PLAY)
    choice = import_object(settings.RANDOMIZER)

    schema = {}
    deserializer = DocumentDeserializer(schema)

    def make_deref_sequence(attr):
        def deref_sequence(doc):
            if not attr in doc:
                return None
            sequence = doc[attr]
            return List(deserializer.convert('deref:{0}'.format(v) if deserializer.is_uuid(v) else v) for v in sequence)
        return deref_sequence

    def make_deref_dict(attr):
        def deref_dict(doc):
            if not attr in doc:
                return None
            values = doc[attr].items()
            return Dict((k, deserializer.convert('deref:{0}'.format(v) if deserializer.is_uuid(v) else v)) for k, v in values)
        return deref_dict

    schema.update(base_schema)
    schema.update({
	list: SequenceConversionRule(List),
	tuple: SequenceConversionRule(List),
	dict: MapConversionRule(Dict),
        # jolly.map Types
        'map': DocumentRestorationRule('jolly.map.Map',
            {'bounds': 'bounds',
             'tokens': 'tokens',
             'game': 'game'}),
        'token': DocumentRestorationRule('jolly.map.Token', 
            {'item': 'item', 
             'position': 'position'}),
        'position': DocumentRestorationRule('jolly.map.Position', 
            {'location': 'location', 
             'facing': 'facing'}),
        'hexlocation': DocumentRestorationRule('jolly.map.HexLocation', 
            {'coordinates': 'coordinates'}),
        'direction': SimpleConversionRule(
            lambda doc: jolly.map.hexcompass.get(doc['name'])),
        'location-mask': SimpleConversionRule(
            lambda doc: registry.get(doc['name'], 'jolly.map.LocationMask')),
        'bearing': DocumentRestorationRule('jolly.map.Bearing', 
            {'offset_direction': 'offset_direction', 
             'rotation_direction': 'rotation_direction'}),

	# jolly.breakpoint Types
	'breakpoint': DocumentRestorationRule('jolly.breakpoint.BreakPoint',
	    {'owner': 'owner',
	     'action_type': 'action_type'}),
	'sequence-of-play-breakpoint': DocumentRestorationRule('jolly.breakpoint.SequenceOfPlayBreakPoint',
	    {'owner': 'owner',
	     'action_type': 'action_type',
	     'time': 'time'}),
	'property-change-breakpoint': DocumentRestorationRule('jolly.breakpoint.PropertyChangeBreakPoint',
	    {'owner': 'owner',
	     'action_type': 'action_type',
	     'system': 'system',
	     'property_name': 'property_name'}),

	# jolly.action Types
	'action': DocumentRestorationRule('jolly.action.Action',
	    {'action_type': 'action_type',
	     'time': 'time',
	     'description': 'description',
	     'details': 'details',
	     'target': 'target',
	     'owner': 'owner',
	     'private': 'private'}),

        # jolly.system types
        'system': DocumentRestorationRule('jolly.system.System', 
            {'id': 'id', 
             'prototype': 'prototype', 
             'properties': make_deref_dict('properties'), 
             'subsystems': make_deref_sequence('subsystems'), 
             'owner': 'owner'}),
        'prototype': SimpleConversionRule(
            lambda doc: registry.get(doc['name'], 'jolly.system.Prototype')),

        # jolly.command types
        'command': DocumentRestorationRule('jolly.command.Command', 
            {'owner': 'owner', 
             'template': 'template', 
             'time': 'time', 
             'arguments': make_deref_dict('arguments'), 
             'queue': 'queue', 
             'done': 'done', 
             'cancelled': 'cancelled'}),
        'command-template': SimpleConversionRule(
            lambda doc: registry.get(doc['name'], 
                                     'jolly.command.CommandTemplate')),
        'command-queue': DocumentRestorationRule('jolly.command.CommandQueue', 
            {'commands': make_deref_sequence('commands'), 
             'owner': 'owner'}),

        # jolly.core types
        'player': DocumentRestorationRule('jolly.core.Player', 
            {'name': 'name', 
             'units': make_deref_sequence('units'), 
             'game': 'game', 
             'owner': 'owner', 
             'queue': 'queue',
	     'log': 'log',
	     'status': 'status',
	     'breakpoints': 'breakpoints'}),
        'user': DocumentRestorationRule('jolly.core.User', 
            {'name': 'name', 
             'email': 'email', 
             'password': 'password'}),
        'game': DocumentRestorationRule('jolly.core.Game', 
            {'sequence_of_play': (lambda obj: sequence_of_play), 
             'choice': (lambda obj: choice), 
             'map': 'map', 
	     'game_queue': 'game_queue',
             'players': make_deref_sequence('players'), 
             'last_command': 'last_command', 
	     'log': 'log',
	     'current_time': 'current_time',
	     'last_actions': 'last_actions',
             'title': 'title'}),
	'action-log': DocumentRestorationRule('jolly.core.ActionLog',
            {'owner': 'owner',
	     'actions': make_deref_sequence('actions')}),
	'status': DocumentRestorationRule('jolly.core.Status',
	    {'owner': 'owner',
	     'status': 'status',
	     'details': 'details'}),

        # jolly.chrono types
        'moment': DocumentRestorationRule('jolly.chrono.Moment', 
            {'name': 'name', 
             'description': 'description', 
             'path': 'path', 
             'multiple': 'multiple'}),

        # other types
        'damage-allocation-chart': SimpleConversionRule(
            lambda doc: registry.get(doc['name'], 
                                     'sfb.damage.DamageAllocationChart')),
        'rule-set': DocumentRestorationRule('sfb.damage.RuleSet', 
            {'system_types': 'system_types'}),
        'speed-plot': DocumentRestorationRule('sfb.movement.SpeedPlot', 
            {'speeds': 'speeds'}),
        'acceleration-limit': DocumentRestorationRule('sfb.movement.AccelerationLimit', 
            {'max_speed': 'max_speed', 
             'max_addition': 'max_addition', 
             'max_multiple': 'max_multiple'}),
        'turn-mode': SimpleConversionRule(
            lambda doc: registry.get(doc['name'], 'sfb.movement.TurnMode')),
        'duration': DocumentRestorationRule('sfb.chrono.Duration', 
            {'turns_only': 'turns_only', 
             'impulses': 'impulses'}),
        'range-dict': DocumentRestorationRule('jolly.util.RangeDict', 
            {'ranges': (lambda doc: dict((jolly.util.Range(v[0], v[1]), v[2]) for v in doc['ranges']))}),
    })

    deserializer = DocumentDeserializer(schema)
    return deserializer


def create_database():
    server = Server()
    database = server[settings.DATABASE['NAME']]
    identifier = import_object(settings.IDENTIFIER)
    serializer = import_object(settings.DATABASE['SERIALIZER'])()
    deserializer = import_object(settings.DATABASE['DESERIALIZER'])()

    db = Database(database, identifier, serializer, deserializer)

    import_object(settings.DATABASE['POST_PROCESS'])(db)

    return db
