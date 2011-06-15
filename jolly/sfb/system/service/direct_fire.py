import jolly.command
from jolly.system import Service, PropertyDefinition
from jolly.map import LocationMask as FiringArc
from jolly.resource import ResourcePool
from sfb.damage import damage
from sfb import registry

class DirectFire(Service):
    """Provides the ability to fire as a direct fire weapon."""

    def __init__(self, damage_lookup, damage_type=damage, 
	    resolution_template=None):
	resolution_template = resolution_template or registry.get('resolve-other-weapons', jolly.command.CommandTemplate)
        props = [PropertyDefinition('firing-arc', FiringArc)]
        super(DirectFire, self).__init__('direct-fire', props, exposed_commands=[registry.get('decide-direct-fire', jolly.command.CommandTemplate)])
        self._damage_lookup = damage_lookup
        self._damage_type = damage_type
        self._resolution_template = resolution_template

    def get_resolution_template(self, system):
        return self._resolution_template

    def can_target(self, system, location):
        firing_arc = system.get_property('firing-arc')
        if firing_arc is None or firing_arc.contains(location):
            return abs(location) in self._damage_lookup
        return False

    def get_damage(self, system, distance, choice):
        return ResourcePool(self._damage_type, choice(self._damage_lookup[location]))
