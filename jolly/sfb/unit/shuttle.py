"""Shuttle unit prototypes."""
from jolly.system import Prototype, System
from sfb.system.service import Movement
from sfb.movement import turn_mode, AccelerationLimit
from sfb import firing_arc, registry
from sfb.damage import DAC_shuttle

admin_shuttle = Prototype('admin-shuttle',
                              [Movement()],
                              {'turn-mode' : turn_mode.shuttle,
                               'acceleration-limit' : AccelerationLimit(6, 3, 1),
                               'damage-rules' : DAC_shuttle},
                              [System(i+1, registry.get('shuttle-hull')) for i in range(6)] +
                              [System(7, registry.get('shuttle-phaser-1'),
                                      {'firing-arc' : firing_arc.ALL})])
                               
