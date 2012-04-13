from django.conf import settings
from jolly.util import import_object

import jolly.core
import jolly.map

import sfb.movement

import setup

value_resolver = import_object(settings.VALUE_RESOLVER)
registry = import_object(settings.REGISTRY)
sequence_of_play = import_object(settings.SEQUENCE_OF_PLAY)
choice = import_object(settings.RANDOMIZER)

u = jolly.core.User('user1', 'user1@example.com', 'password1')
s = registry.get('admin-shuttle').create_system('shuttle1', {'speed-plot': sfb.movement.make_speed_plot(6), 'position': jolly.map.Position(jolly.map.HexLocation.parse('1012'), jolly.map.hexcompass.get('A'))})
p = jolly.core.Player('player1', [s])
p.owner = u
m = jolly.map.Map([42, 30])
g = jolly.core.Game('Test Game', sequence_of_play, m, [p], choice)

import sfb.command
import jolly.map
import sfb.chrono
import jolly.command
import jolly.breakpoint

ct1 = registry.get('shuttle-determine-initial-speed')
c1 = jolly.command.Command(p, ct1, sfb.chrono.get_moment(0, None, ct1.step), {'unit': s, 'speed-plot': sfb.movement.make_speed_plot(6)})
c1.insert_into_queue(p.queue, g)

del p.breakpoints[0]
bp1 = jolly.breakpoint.PropertyChangeBreakPoint(p, s, 'position')
p.breakpoints.append(bp1)
bp2 = jolly.breakpoint.SequenceOfPlayBreakPoint(p, sfb.chrono.get_moment(1, 10, 'move'))
p.breakpoints.append(bp2)

g.advance()

import jolly.couch
import sfb.json_encode

db = jolly.couch.Database(settings)

