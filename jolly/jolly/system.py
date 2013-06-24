"""Systems and Services define the functionality of units in the game."""

import copy

def register(registry, prototype):
    """Register prototype in the registry."""
    registry[prototype.name] = prototype

class MissingParameter(Exception):
    """A parameter attribute is missing."""
class InvalidParameter(Exception):
    """The parameter value is not the correct type."""

class System(object):
    """A modular component of a unit.  This follows the composite pattern."""

    def __init__(self, id, prototype, properties=None, subsystems=None):
	self.id = id
        self.prototype = prototype
        self.properties = properties or {}
        self.subsystems = subsystems or []
	for s in self.subsystems:
	    s.owner = self
	self.owner = None

    def is_unit(self):
        return not isinstance(self.owner, System)

    def has_service(self, service_name):
        """Determine whether this system has a given service."""
        return not self.prototype.get_service(service_name) is None

    def use_as(self, service_name):
        """Use one of this system's services."""
        return self.prototype.bind_service(self, service_name)

    def has_property(self, name):
        """Determine whether this system has a given property."""
        return name in self.properties

    def get_property(self, name):
        """Return the specified property."""
        return self.properties[name]

    def filter(self, predicate, include_self=False):
        """Return a list of all systems such that predicate(system) is true."""
        return [s for s in self.subsystems + 
                           ([self] if include_self else []) 
                  if predicate(s)]

    @property
    def exposed_commands(self):
        """Return a set of commands available to this System."""
        return self.prototype.exposed_commands

    def __deepcopy__(self, memo):
	subsystems = copy.deepcoppy(self.subsystems)
        properties = copy.deepcopy(self.properties)
        result = System(self.prototype, properties, subsystems)
	result.owner = self.owner
        memo[id(self)] = result
        return result


class Prototype(object):
    """Definition of the common functionality of systems of a given type."""

    system_class = System

    def __init__(self, name, services=None, properties=None, subsystems=None):
        self.name = name
        self.services = dict((s.name, s) for s in services or [])
        self.properties = properties or {}
        self.subsystems = subsystems or []

    @property
    def required_properties(self):
        """Return the required properties for Systems with this Prototype."""
        return set(p for s in self.services.values()
                     for p in s.required_properties)

    @property
    def exposed_commands(self):
        """Return a set of Commands available to this System."""
        return set.union(reduce(set.union, [s.exposed_commands for s in self.services.values()], set()), reduce(set.union, [s.prototype.exposed_commands for s in self.subsystems],  set()))

    def get_service(self, name):
        """Return the Service with the given name."""
        return self.services[name]

    def bind_service(self, system, service_name):
        """Return an object that curries the system into the first argument 
           of the service methods."""
        return BoundService(system, self.get_service(service_name))

    def prepare_properties(self, properties=None):
        props = copy.deepcopy(self.properties)
        props.update(properties or {})
        for service in self.services.values():
            props.update(service.resolve_properties(props))
            service.validate_properties(props)
	return props

    def create_system(self, id, properties=None):
        """Create a system using this prototype."""
	properties = self.prepare_properties(properties)
        subsystems = [s.prototype.create_system(s.id, 
	                copy.deepcopy(s.properties)) 
		      for s in self.subsystems]
        system = self.system_class(id, self, properties, subsystems)
	for s in subsystems:
	    s.owner = system
        return system

        
class Service(object):
    """Provider of functionality to systems."""

    def __init__(self, name, property_definitions=None, exposed_commands=None):
        self.name = name
        self.property_definitions = set(property_definitions or [])
	self.exposed_commands = set(exposed_commands or [])

    @property
    def required_properties(self):
        """Return a set of the properties that are required for this Service."""
        return set(p for p in self.property_definitions if p.mandatory and not p.default)

    def resolve_properties(self, values):
        """Update and return values using defaults where required."""
	results = {}
        for definition in self.property_definitions:
            results[definition.name] = (values.get(definition.name) or
                                        copy.deepcopy(definition.default))
        return results

    def validate_properties(self, values):
        """Determine whether values are valid for this Service's parameters."""
        for definition in self.property_definitions:
            definition.validate(values[definition.name])

class BoundService(object):
    """A service bound to a system."""

    def __init__(self, system, service):
        self.system = system
        self.service = service

    def __getattr__(self, name):
        attribute = getattr(self.service, name)
        if not callable(attribute):
            return attribute
        def call_attribute(*args, **kwargs):
            """Call attribute with the given arguments."""
            return attribute(self.system, *args, **kwargs)
        return call_attribute


class PropertyDefinition(object):
    """Requirements definition for a service property."""

    def __init__(self, name, required_class, mandatory=True, default=None, private=False, validator=None):
        self.name = name
        self.required_class = required_class
        self.mandatory = mandatory
        self.default = default
	self.private = private
        self.validator = validator or (lambda x: True)

    def validate(self, value):
        """Determine whether the given value is valid for this parameter."""
        if value is None:
            if self.mandatory:
                raise MissingParameter(self.name)
	elif isinstance(self.required_class, list):
	    if not isinstance(value, list):
		raise InvalidParameter(self.name)
	    for v in value:
		if not isinstance(v, self.required_class[0]):
		    raise InvalidParameter(self.name)
        elif not isinstance(value, self.required_class):
            raise InvalidParameter(self.name)
        elif not self.validator(value):
            raise InvalidParameter(self.name)
