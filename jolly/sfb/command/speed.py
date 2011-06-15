from django.conf import settings

from jolly.action import Action
from jolly.command import (Command, CommandTemplate, FormalArgument, 
	                   InvalidArgument)
from jolly.system import System
from jolly.util import import_object

from sfb.chrono import get_moment
from sfb.movement import SpeedPlot

class AnnounceInitialSpeed(CommandTemplate):

    def __init__(self):
        arguments = [FormalArgument('unit', System, upfront=True)]
        super(AnnounceInitialSpeed, self).__init__('announce-initial-speed', 'announce-initial-speed', arguments)

    def execute(self, command, env=None):
        unit = command.arguments['unit']
        speed_plot = unit.get_property('speed-plot')
        speed = speed_plot.get_speed(0)
	actions = [command.create_action('announce-initial-speed', unit, '{0} announces initial speed of {1}'.format(unit.id, speed), {'speed': speed})]
	return actions

class AnnounceSpeedChange(CommandTemplate):

    def __init__(self):
        arguments = [FormalArgument('unit', System, upfront=True)]
        super(AnnounceSpeedChange, self).__init__('announce-speed-change', 'announce-speed-change', arguments)

    def execute(self, command, env=None):
        unit = command.arguments['unit']
        speed_plot = unit.get_property('speed-plot')
        speed = speed_plot.get_speed(command.impulse)
	actions = [command.create_action('announce-speed-change', unit, '{0} announces speed change to {1}'.format(unit.id, speed), {'speed': speed})]
	return actions

class ShuttleDetermineInitialSpeed(AnnounceInitialSpeed):

    def __init__(self):
        arguments = [FormalArgument('unit', System, upfront=True),
                     FormalArgument('speed-plot', SpeedPlot, can_change=True)]
        super(AnnounceInitialSpeed, self).__init__('shuttle-determine-initial-speed', 'announce-initial-speed', arguments, required=True)

    def validate_for_execute(self, command, env=None):
        super(ShuttleDetermineInitialSpeed, self).validate_for_execute(command, env)
        unit = command.arguments['unit']
        speed_plot = command.arguments['speed-plot']
        acceleration_limit = unit.get_property('acceleration-limit')
        prev_speed_plot = unit.get_property('prev-speed-plot') if unit.has_property('prev-speed-plot') else None
        if not speed_plot.is_valid(acceleration_limit, prev_speed_plot):
            raise InvalidArgument('speed-plot')

    def execute(self, command, env=None):
        unit = command.arguments['unit']
        speed_plot = command.arguments['speed-plot']
	unit.properties['speed-plot'] = speed_plot
	actions = [command.create_action('property-change', unit, '{0} changes speed plot'.format(unit.id), {'speed-plot': speed_plot}, True)]
        actions.extend(super(ShuttleDetermineInitialSpeed, self).execute(command, env))
	registry = import_object(settings.REGISTRY)
	move = registry.get('move')
	for impulse in speed_plot:
	    time = get_moment(command.time.turn, impulse, move.step)
	    cmd = Command(command.owner, move, time, {'unit': unit})
	    cmd.insert_into_queue(command.queue)
	    actions.append(command.create_action('queue-command', unit, "{0} queued 'Move' command at {1}".format(unit.id, time), {'command': cmd}, True))
	return actions

class EmergencyDeceleration(CommandTemplate):

    def __init__(self):
        arguments = [FormalArgument('unit', System, upfront=True)]
        super(EmergencyDeceleration, self).__init__('emergency-deceleration', 'emergency-deceleration', arguments)

    def execute(self, command, env=None):
        unit = command.arguments['unit']
        speed_plot = unit.get_property('speed-plot')
        new_speed_plot = speed_plot.get_altered_speed_plot(0, command.impulse)
	unit.properties['speed-plot'] = new_speed_plot

	actions = [command.create_action('property-change', unit, '{0} changes speed plot'.format(unit.id), {'speed-plot': new_speed_plot}, True)]
	actions.append(command.create_action('property-change', unit, '{0} changes speed to {1}'.format(unit.id), {'speed': 0}))

        # need to also figure out energy to reinforcement
	return actions

class AnnounceEmergencyDeceleration(CommandTemplate):

    def __init__(self):
        arguments = [FormalArgument('unit', System, upfront=True)]
        super(AnnounceEmergencyDeceleration, self).__init__('announce-emergency-deceleration', 'announce-emergency-deceleration', arguments)

    def execute(self, command, env=None):
        unit = command.arguments['unit']
        delay = command.time + Duration(0, 2)
        moment = get_moment(delay.turn, delay.impulse, 'emergency-deceleration')
        cmd = Command(command, emergency_deceleration, moment, {'unit' : System})
	cmd.insert_into_queue(command.queue, env)

        actions = [command.create_action('emergency-deceleration', unit, '{0} announces emergency deceleration'.format(unit.id))]
	return actions
