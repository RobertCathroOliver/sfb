import jolly.util
import jolly.map
import fractions

import sfb.map
import sfb.chrono

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

_rules = ((r'^([-+]?[0-9]+(?:(?:/|.)[0-9]+)?)$', fractions.Fraction),
	  (r'^([A-F])$', _make_direction, jolly.map.Direction),
	  (r'^(\d\d\d\d)$', sfb.map.Location.parse, sfb.map.Location),
	  (r'^(\d\d\d\d)([A-F])$', _make_position, jolly.map.Position),
	  (r'^(\d+)\.(\d+)\.([-\w]+)$', _make_moment, sfb.chrono.Moment),
	  (r'^$', str),
	  (r'^(.*)$', str))

value_resolver = jolly.util.ValueResolver(rules)

__all__ = [value_resolver]
