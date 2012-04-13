from django.conf import settings
from django.core.urlresolvers import get_resolver

import jolly.couch
import jolly.util
import jolly.map
import fractions

import sfb.map
import sfb.chrono
import sfb.json_encode

from random import Random

__all__ = ['choice', 'identifier', 'urlresolver', 'out', 'value_resolver']

choice = Random().choice
identifier = jolly.util.Identifier(['Game', 'Player', 'User', 'System', 'BreakPoint', 'Command'])
urlresolver = jolly.util.URLResolver(settings.ROOT_URLCONF, identifier)
out = sfb.json_encode.get_api_encoders(settings)

def _lookup_reference(url):
    resolver = get_resolver(settings.ROOT_URLCONF)
    _, _, kwargs = resolver.resolve(url)
    name = kwargs['name']
    doc_type = kwargs['doc_type']
    registry = jolly.util.import_object(settings.REGISTRY)
    return registry.get(name, doc_type)

def _make_reference(url):
    db = jolly.db.create_database()
    resolver = get_resolver(settings.ROOT_URLCONF)
    _, _, kwargs = resolver.resolve(url)
    doc_id = kwargs['doc_id']
    obj = db.restore_object(doc_id)
    return obj

def _make_direction(value):
    try:
	result = sfb.map.compass.get(value)
    except IndexError:
	raise ValueError()
    return result

def _make_position(location_value, direction_value):
    location = sfb.map.Location.parse(location_value)
    direction = _make_direction(direction_value)
    result = jolly.map.Position(location, direction)
    return result

def _make_moment(turn_value, impulse_value, step_value=None):
    if step_value is None:
	step_value, impulse_value = impulse_value, None
    else:
	impulse_value = int(impulse_value)
    result = sfb.chrono.get_moment(int(turn_value), impulse_value, step_value)
    return result

def _make_bearing(offset_value, rotation_value):
    offset = _make_direction(offset_value)
    result = jolly.map.Bearing(offset, rotation_value)
    return result

_rules = ((r'^([-+]?[0-9]+(?:(?:/|.)[0-9]+)?)$', fractions.Fraction),
	  (r'^([A-F])$', _make_direction, jolly.map.Direction),
	  (r'^(\d\d\d\d)$', sfb.map.Location.parse, sfb.map.Location),
	  (r'^(\d\d\d\d)([A-F])$', _make_position, jolly.map.Position),
	  (r'^(\d+)\.(\d+)\.([-\w]+)$', _make_moment, sfb.chrono.Moment),
          (r'^([A-F]) - (self|cw|ccw|opposite)$', _make_bearing, jolly.map.Bearing),
	  (r"^{\s*u'href'\s*:\s*u'([^']*)'\s*}$", _lookup_reference),
	  (r"^{\s*u'href'\s*:\s*u'([^']*)'\s*}$", _make_reference),
	  (r'^$', str),
	  (r'^(.*)$', str))

value_resolver = jolly.util.ValueResolver(_rules)

db = jolly.couch.Database(settings)
