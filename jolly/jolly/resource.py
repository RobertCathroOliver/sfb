"""Representations of resources and collections of resources."""

import collections

class ResourceUnavailable(Exception):
    """Insufficient quantities of a given resource type are available."""

class ResourceType(object):
    """A category of resource and its substitutability."""

    def __init__(self, name, usable_as=None):
        self.name = name
        self.usable_as = usable_as or []
        self.usable_as.append(self)

    def is_usable_as(self, resource_type):
        """Can this ResourceType substitute for resource_type?"""
        return resource_type in self.usable_as

    def substitutes(self):
        """Return an iterator of increasingly general substitutes."""
        return reversed(self.usable_as)

    def __lt__(self, other):
        """More specialized ResourceTypes are considered less."""
        if not isinstance(other, ResourceType):
            return NotImplemented
        return self.is_usable_as(other)

    def __gt__(self, other):
        """More specialized ResourceTypes are considered less."""
        if not isinstance(other, ResourceType):
            return NotImplemented
        return other.is_usable_as(self)

    def __str__(self):
        return self.name

class ResourcePool(object):
    """Generic bags of semi-substitutable resources."""

    def __init__(self, resource_type=None, quantity=0):
        self.resources = collections.defaultdict(lambda: 0)
        if not resource_type is None: 
            self.resources[resource_type] = quantity

    def __iter__(self):
        for resource_type in sorted(self._resources.keys()):
            for _ in range(self._resources[resource_type]):
                yield resource_type

    def __getitem__(self, key):
        return self.resources[key]

    def quantity(self, resource_type):
        """Return the number of resources that can be used as resource_type."""
        return sum(v for k, v in self.resources.items() if k.is_usable_as(resource_type))

    def add(self, pool):
        """Add the resources of pool to self."""
        if not isinstance(pool, self.__class__):
            raise TypeError(pool)
        for resource_type in pool:
            self.resources[resource_type] += 1

    def subtract(self, pool):
        """Subtract the resources of pool from self."""
        if not isinstance(pool, self.__class__):
            raise TypeError(pool)
        for resource_type in pool:
            if self.quantity(resource_type) == 0:
                raise ResourceUnavailable(resource_type)
            for substitute in resource_type.subsitutes():
                if self.resources[substitute] > 0:
                    self.resources[resource_type] -= 1
                    break

    def __add__(self, other):
        result = ResourcePool()
        result.add(self)
        result.add(other)
        return result

    def __sub__(self, other):
        result = ResourcePool()
        result.add(self)
        result.subtract(other)
        return result

    def __str__(self):
        return ','.join(['{0}: {1}'.format(k.name, v) for k, v in self.resources.items()])
        
