from jolly.command import (CommandTemplate, FormalArgument, InvalidTime, 
	                   InvalidArgument)
from jolly.map import Bearing
from jolly.system import System

class Move(CommandTemplate):

    def __init__(self):
        arguments = [FormalArgument('unit', System, upfront=True),
                     FormalArgument('bearing', Bearing, can_change=True)]
        super(Move, self).__init__('move', 'move', arguments)

    def validate_for_queue(self, command, queue, env=None):
        super(Move, self).validate_for_queue(command, queue, env)
        unit = command.arguments['unit']
        if not unit.get_property('speed-plot').has_move(command.time.impulse):
            raise InvalidTime(command.time)

    def validate_for_execute(self, command, env=None):
        super(Move, self).validate_for_execute(command, env)
        unit = command.arguments['unit']
        bearing = command.arguments['bearing']
        if not unit.use_as('movement').can_move(command.time.impulse, bearing):
            raise InvalidArgument('bearing')

    def execute(self, command, env=None):
        unit = command.arguments['unit']
        bearing = command.arguments['bearing']
        position = unit.use_as('movement').get_destination(bearing)
	actions = [command.create_action('property-change', unit, '{0} moves to {1}'.format(unit.id, position), {'position': position})]
        unit.properties['position'] = position
	return actions
        # turn and slip modes should be updated
