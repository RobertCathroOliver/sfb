admin_shuttle =\
unit('admin-shuttle', prototypes)\
                     .has(system('shuttle-hull') * 6)\
                     .has(system('shuttle-phaser-3')\
                            .property('firing-arc', 'firing_arc.ALL'))\
                     .does('Movement()')\
                     .property('turn-mode', 'turn_mode.shuttle')\
                     .property('acceleration-limit', 'AccelerationLimit(6,3,1)')\
                     .property('damage-rules', 'DAC_shuttle')\
                     .create()
print admin_shuttle.required_properties

p1 = Position(Location(1, 1), Compass['D'])
p2 = Position(Location(10, 10), Compass['A'])
unit1 = admin_shuttle.create_system('unit-1', {'position' : p1 })
unit2 = admin_shuttle.create_system('unit-2', {'position' : p2 })

class System(object):
    def __init__(self, id, prototype, properties=None, services=None, systems=None):
        self._id = id
        self._prototype = prototype
        self._properties = properties || {}
        self._services = services || []
        self._systems = systems || []

class Prototype(object):
    def __init__(self, name, properties=None):
        self._name = name
        self._properties = properties || {}
    def create_system(self, id, properties):
	properties = dict(self._properties).update(properties)
	return System(id, self, properties)

prototypes = {'shuttle-hull' : Prototype('shuttle-hull'),
              'shuttle-phaser-3' : Prototype('shuttle-phaser-3')}

class unit(object):
    def __init__(self, name, prototypes):
        self._name = name
        self._systems = []
        self._services = []
        self._properties = {}
        self._prototypes = prototypes
        self._id = 0
    def has(self, system):
        systems = system.instantiate(self._id, self._prototypes)
        self._id = 1 + max(self._id, *[s['id'] for s in systems])
        self._systems.extend(systems)
        return self
    def does(self, service):
        self._services.append(service)
        return self
    def property(self, name, value):
        self._properties[name] = value
        return self
    def create(self):
        prototype = {'name' : self._name, 'systems' : self._systems, 'services' : self._services, 'properties' : self._properties } #UnitPrototype(self._name, self._systems, self._services, self._properties)
        return prototype

class system(object):
    def __init__(self, name):
        self._name = name
        self._quantity = 1
        self._properties = {}
        self._id = None
    def instantiate(self, id, prototypes):
        prototype = prototypes[self._name]
        id = self._id or id
        systems = [prototype.create_system(i, self._properties) for i in range(id, id + self._quantity)]
        return systems
    def __mul__(self, quantity):
        self._quantity *= int(quantity)
        return self
    def property(self, name, value):
        self._properties[name] = value
        return self
    def id(self, id):
        self._id = id
        return self
