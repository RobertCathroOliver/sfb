import jolly.command
from jolly.system import Service, PropertyDefinition
from jolly.map import Position
from sfb.movement import TurnMode, SpeedPlot, AccelerationLimit, make_speed_plot
from sfb import registry

class Movement(Service):
    """Provide the ability for a Unit to move on a map."""

    def __init__(self):
        props = [PropertyDefinition('turn-mode', TurnMode),
                 PropertyDefinition('acceleration-limit', AccelerationLimit, True),
                 PropertyDefinition('turn-mode-counter', int, True, 0),
                 PropertyDefinition('sideslip-mode-counter', int, True, 0),
                 PropertyDefinition('speed-plot', SpeedPlot, True, make_speed_plot(0)),
                 PropertyDefinition('prev-speed-plot', SpeedPlot, False),
                 PropertyDefinition('position', Position, True)]
        super(Movement, self).__init__('movement', props, [registry.get('shuttle-determine-initial-speed', jolly.command.CommandTemplate), registry.get('announce-emergency-deceleration', jolly.command.CommandTemplate)])

    def can_move(self, system, impulse, bearing):
        speed_plot = system.get_property('speed-plot')
        speed = speed_plot.get_speed(impulse)
        if bearing.is_rotation():
            turn_mode = system.get_property('turn-mode')
            turn_mode_counter = system.get_property('turn-mode-counter')
            return turn_mode.is_fulfilled(turn_mode_counter, speed)
        if bearing.is_straight(system.get_property('position')):
            sideslip_mode_counter = system.get_property('sideslip-mode-counter')
            return sideslip_mode_counter > 0
        return True

    def get_destination(self, system, bearing):
        return system.get_property('position') + bearing

