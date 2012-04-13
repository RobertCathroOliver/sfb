"""Utility functions."""

import re
import sys
import uuid

def import_object(name):
    try:
        module_name, obj_name = name.rsplit('.', 1)
        __import__(module_name)
        obj = getattr(sys.modules[module_name], obj_name)
    except (ImportError, ValueError):
        raise ImportError('Unable to import object "{0}"'.format(name))
    return obj

class Identifier(object):

    def __init__(self, resource_types=None):
        # the double lookup is used so that unhashable objects can be stored
        self.id_cache = {}
        self.obj_cache = []
        self.rev_cache = {}
        self.resource_types = resource_types or []

    def get_obj_id(self, obj):
        has_id = False
        for _class in obj.__class__.__mro__:
            if _class.__name__ in self.resource_types:
                has_id = True
                break
        if not has_id:
            return None

        try:
            index = self.obj_cache.index(obj)
            obj_id = self.id_cache[index]
        except (ValueError, KeyError):
            obj_id = self.gen_obj_id()
            self.set_obj_id(obj, obj_id)
        return obj_id

    def set_obj_id(self, obj, obj_id):
        try:
            index = self.obj_cache.index(obj)
        except ValueError:
            index = len(self.obj_cache)
            self.obj_cache.append(obj)
        self.id_cache[index] = obj_id
        self.rev_cache[obj_id] = obj

    def gen_obj_id(self):
        return uuid.uuid4().hex

    def get_obj(self, obj_id):
        return self.rev_cache.get(obj_id)
    

class URLResolver(object):

    def __init__(self, urlconf, identifier):
        import django.core.urlresolvers
        self.resolver = django.core.urlresolvers.get_resolver(urlconf)
        self.identifier = identifier
        self.url_names = {}

    def get_doc_id(self, obj):
        return self.identifier.get_obj_id(obj)

    def get_url(self, url_name, **kwargs):
        return self.get_url_by_name(url_name, kwargs)

    def get_url_by_name(self, url_name, kwargs):
        return '{0}'.format(self.resolver.reverse(url_name, **kwargs))

    def get_query_url_by_name(self, url_name, query=None):
        query = query or {}
        qs = '&'.join('{0}={1}'.format(k, v) for k, v in query.items())
        if qs:
            qs = '?{0}'.format(qs)
        return '{0}{1}'.format(self.resolver.reverse(url_name), qs)

class Range(object):
    """A closed range."""

    def __init__(self, begin, end=None):
        end = end or begin
        self.begin = min(begin, end)
        self.end = max(begin, end)

    def __contains__(self, value):
        return self.begin <= value <= self.end

class RangeDict(object):
    """A dictionary with Range objects as keys"""

    def __init__(self, dictionary):
        self.ranges = dictionary

    def __contains__(self, value):
        return any(value in range_ for range_ in self.ranges)

    def __getitem__(self, key):
        for range_, value in self.ranges.items():
            if key in range_: 
                return value
        raise KeyError(key)

    def items(self):
        return self.ranges.items()


class ValueResolver(object):
    """Resolves string values to their equivalent object values."""

    def __init__(self, rules):
        """rules is an iterable of 2-or-3 tuples.
           The first value is a regular expression specifying a value type.
           The second value is a constructor for the value.
           The third value is the type of the result. It is optional but 
             must be unique."""
        self.rules = [(re.compile(r[0]), r[1]) for r in rules]
        self.types = dict((r[2], i) for i, r in enumerate(rules) if len(r) > 2)

    def resolve(self, value, expected_type=None):
        """Return the value object represented by value."""
        value = str(value)
        # ensure that the expected type is tested first
        rules = self.rules[:]
        if expected_type in self.types:
            rules.insert(0, self.rules[self.types[expected_type]])
        # test each type in turn
        for pattern, func in rules:
            match = pattern.search(value)
            if match:
        	try:
        	    resolved_value = func(*match.groups())
        	    return resolved_value
        	except Exception:
        	    # always continue to try the next option
        	    pass
        raise ValueError('Unrecognized value: {0}'.format(value))
