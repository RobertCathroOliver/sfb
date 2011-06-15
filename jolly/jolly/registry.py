"""For organizing those objects that are stored in a registry by lookup."""

from jolly.util import import_object

class Registry(object):

    def __init__(self):
	self.registry = {}
	self.lookup = {}

    def set(self, key, item, class_=None):
        self.registry.setdefault(class_ or type(item), {})[key] = item
	self.lookup.setdefault(key, set()).add(item)

    def get(self, key, class_=None):
	if class_:
	    if isinstance(class_, basestring):
                 class_ = import_object(class_)
	    return self.registry[class_][key]
	items = self.lookup[key]
	if len(items) == 1:
	    return list(items)[0]
