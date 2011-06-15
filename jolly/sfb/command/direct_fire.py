"""Direct fire weapon commands."""

from jolly.command import CommandTemplate, FormalArgument, PreviouslyQueued
from jolly.system import System
from jolly.resource import ResourcePool
from sfb.chrono import get_moment

class LineOfSightBlocked(Exception):
    """The firing unit does not have a LOS to the target."""
class OutsideOfFiringArc(Exception):
    """The target is not in the firing arc of the weapon."""
class SystemNotReady(Exception):
    """Necessary conditions for using the system have not been met."""

class DecideDirectFire(CommandTemplate):

    def __init__(self):
        arguments = [FormalArgument('unit', System, upfront=True),
                     FormalArgument('weapon', System, upfront=True),
                     FormalArgument('target', System, upfront=True, can_change=True)]
        super(DecideDirectFire, self).__init__('decide-direct-fire', 'decide-direct-fire', arguments, True)

   
    def validate_for_queue(self, command, queue, env=None):
        super(DecideDirectFire, self).validate_for_queue(command, queue, env)

        if queue.is_duplicate(command, ['unit', 'weapon']):
            raise PreviouslyQueued(command)

    def validate_for_execute(self, command, env=None):
        super(DecideDirectFire, self).validate_for_execute(command, env)

        unit = command.arguments['unit']
        weapon = command.arguments['weapon']
        target = command.arguments['target']

        unit_position = unit.get_property('position')
        target_position = target.get_property('position')
        firing_arc = weapon.get_property('firing-arc')
        map = env.map
         
        if not weapon.use_as('frequency-restriction').can_use(command.time):
            raise SystemNotReady()

        if not map.has_line_of_sight(unit_position, target_position):
            raise LineOfSightBlocked()

        rel_location = get_relative_location(unit_position, target_position)
        if not rel_location in firing_arc:
            raise OutsideOfFiringArc()

        # weapon is powered
        # we'll need this when we have energy allocation


    def execute(self, command, env=None):
	actions = []

        unit = command.arguments['unit']
        weapon = command.arguments['weapon']
        target = command.arguments['target']

        # setup announce-direct-fire
        announce_moment = get_moment(command.time.turn, command.time.impulse, 'announce-direct-fire')
        announce_arguments = {'unit' : unit,
                              'weapon' : weapon,
                              'target' : target }
        announce_cmd = Command(command.owner, announce_direct_fire, announce_moment, announce_arguments)
        announce_cmd.insert_into_queue(command.queue, env)
	actions.append(command.create_action('queue-command', unit, "{0} queued 'Annouce Direct Fire' action".format(unit.id), {'weapon': weapon, 'target': target}, True))

        # setup resolve-weapon
        resolve_template = weapon.use_as('direct_fire').get_resolution_template()
        resolve_moment = get_moment(command.time.turn, command.time.impulse, resolve_template.step)
        resolve_arguments = {'unit' : unit,
                             'weapon' : weapon,
                             'target' : target }
        resolve_cmd = Command(command.owner, resolve_template, resolve_moment, resolve_arguments)
        resolve_cmd.insert_into_queue(command.queue, env)
	actions.append(command.create_action('queue-command', unit, "{0} queued 'Resolve Direct Fire' action".format(unit.id), {'weapon': weapon, 'target': target}, True)) 
	return actions

class AnnounceDirectFire(CommandTemplate):

    def __init__(self):
        arguments = [FormalArgument('unit', System, upfront=True),
                     FormalArgument('weapon', System, upfront=True),
                     FormalArgument('target', System, upfront=True)]
        super(AnnounceDirectFire, self).__init__('announce-direct-fire', 'announce-direct-fire', arguments)

    def execute(self, command, env=None):
        unit = command.arguments['unit']
        weapon = command.arguments['weapon']
        target = command.arguments['target']
	actions = [command.create_action('announce-direct-fire', unit, '{0} announces firing weapon {1} at {2}'.format(unit.id, weapon.id, target.id), {'weapon': weapon, 'target': target})]
	return actions

class ResolveOtherWeapons(CommandTemplate):

    def __init__(self):
        arguments = [FormalArgument('unit', System, upfront=True),
                     FormalArgument('weapon', System, upfront=True),
                     FormalArgument('target', System, upfront=True)]
        super(ResolveOtherWeapons, self).__init__('resolve-other-weapons', 'resolve-other-weapons', arguments)

    def execute(self, command, env=None):
        # this assumes that all the targeting is legit
        unit = command.arguments['unit']
        weapon = command.arguments['weapon']
        target = command.arguments['target']
        choice = env.choice
       
        source_position = unit.get_state('position')
        target_position = target.get_state('position')
        distance = distance(source_position, target_position)

	# TODO: figure out EW, lock-on, sensors, etc.
        moment = get_moment(command.time.turn, command.time.impulse, 'allocate-damage')
        def predicate(c):
            return c.time == moment and c.arguments['target'] == target and c.arguments['source'] == unit
        allocate_cmds = command.queue.find(predicate)
        total_damage = ResourcePool()
        for cmd in allocate_cmds:
            total_damage += cmd.arguments['damage']
        command.queue.remove(predicate)
 
        damage = weapon.use_as('direct-fire').get_damage(distance, choice)
	total_damage += damage
        weapon.use_as('frequency-restriction').record_use(command.time)
        #weapon.use_as('energy-consumer').consume()

        # setup allocate damage command
        arguments = {'target' : target, 
                     'source' : unit, 
                     'damage' : total_damage}
        cmd = Command(command.owner, AllocateDamage(), moment, arguments)
        cmd.insert_into_queue(command.queue, env)

	actions = [command.create_action('command_queued', unit, '{0} causes {1} points of damage to {2}'.format(unit.id, damage, target.id), {'target': target, 'damage': damage})]

	return actions
