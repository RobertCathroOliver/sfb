import sqlalchemy
from sfb.persist import column_types, create_type

import sfb.firing_arc
import jolly.map
import jolly.chrono
import sfb.chrono

column_types[jolly.map.LocationMask] = \
        create_type(jolly.map.LocationMask, 
                    lambda x: getattr(x, 'name', None),
                    lambda x: getattr(sfb.firing_arc, x or '', None))

def serialize_duration(duration):
    return duration._impulses + (0.0 if duration._turns_only else 0.5)

def deserialize_duration(value):
    duration = sfb.chrono.Duration(0, int(value))
    duration._turns_only = value % 1 == 0.0
    return duration

column_types[sfb.chrono.Duration] = \
        create_type(sfb.chrono.Duration,
                    serialize_duration,
                    deserialize_duration,
                    sqlalchemy.Float)

def serialize_moment(moment):
    if moment.impulse:
        return '%d.%d.%s' % (moment.turn, moment.impulse, moment.step)
    return '%d.%s' % (moment.turn, moment.step)

def deserialize_moment(value):
    elements = value.split('.')
    impulse = None if len(elements) == 2 else int(elements[1])
    return sfb.chrono.get_moment(int(elements[0]), impulse, elements[-1])

column_types[jolly.chrono.Moment] = \
        create_type(jolly.chrono.Moment,
		    serialize_moment,
                    deserialize_moment)
