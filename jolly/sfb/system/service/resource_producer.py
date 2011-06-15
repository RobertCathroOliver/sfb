from jolly.system import Service, PropertyDefinition
from jolly.resource import ResourcePool

class ResourceProducer(Service):
    """Provides the ability to produce a resource."""

    def __init__(self, resource_type):
        name = '{0}-producer'.format(resource_type.name)
        props = [PropertyDefinition('{0}-quantity-produced'.format(resource_type.name), int, True, 1)]
        super(ResourceProducer, self).__init__(name, props)
        self._resource_type = resource_type

    def get_resource(self, system):
        quantity = system.get_property('{0}-quantity-produced'.format(self._resource_type.name))
        return ResourcePool(self._resource_type, quantity)
