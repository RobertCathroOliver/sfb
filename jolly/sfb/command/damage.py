"""Damage application commands."""

from jolly.command import CommandTemplate, FormalArgument
from jolly.system import System
from jolly.resource import ResourceType, ResourcePool
from sfb.map import Location
from sfb.damage import Allocator

class AllocateDamage(CommandTemplate):

    def __init__(self):
        arguments = [FormalArgument('target', System, upfront=True),
                     FormalArgument('source', System, upfront=True),
                     FormalArgument('damage', ResourcePool, upfront=True, can_change=True)]
        super(AllocateDamage, self).__init__('allocate-damage', 'allocate-damage', arguments)

    def execute(self, command, env=None):
        target = command.arguments['target']
        source = command.arguments['source']
        damage = command.arguments['damage']
        damage_rules = target.get_property('damage-rules')
        choice = env.choice

        incident = get_relative_location(source.get_property('position'), target.get_property('position'))
        allocator = Allocator(damage_rules, choice)
	actions = []
        for damage_type in damage:
            systems = allocator.find_target(target, incident, damage_type)
            system = systems[0] # must get user input if more than one (different) option
            allocator.allocate(system)
	    actions.append(command.create_action('property-change', system, '{0} damaged'.format(system.id)))
            # check for destruction
	return actions
