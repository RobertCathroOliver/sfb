from jolly.system import Prototype
from sfb.system.service import DamageTarget

class Hull(Prototype):
    """Defines systems that function as hull."""

    def __init__(self, name, damaged_as):
        services = [DamageTarget(damaged_as)]
        super(Hull, self).__init__(name, services)

forward_hull = Hull('forward-hull', 
                    ('forward-hull', 'any-hull', 'excess-damage'))

center_hull = Hull('center-hull',
                   ('center-hull', 'any-hull', 'excess-damage'))

aft_hull = Hull('aft-hull',
                ('aft-hull', 'any-hull', 'excess-damage'))

shuttle_hull = Hull('shuttle-hull',
                    ('shuttle-hull',))
