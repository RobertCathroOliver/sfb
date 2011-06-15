"""Canonization is the process of converting user-defined classes to built-in
   Python datatypes.
"""

class Reference(object):

    def __init__(self, url_mapper, field_name=''):
	self.url_mapper = url_mapper
	self.field_name = field_name 

    def evaluate(self, obj, canonizer, user):
	field = getattr(obj, self.field_name, obj)
	if getattr(field, 'private', False) or user.is_owner(field):
	    return self.url_mapper.get_url(field)
	return None

class Value(object):

    def __init__(self, field_name):
	self.field_name = field_name

    def evaluate(self, obj, canonizer, user):
	field = getattr(obj, self.field_name)
	if getattr(field, 'private', False) and not user.is_owner(field)):
	    return None
	try:
	    return canonizer.summarize(field, user)
	except KeyError:
	    return str(field)

class Collection(object):

    def __init__(self, field_name):
	self.field_name = field_name

    def evaluate(self, obj, canonizer, user):
	collection = getattr(obj, self.field_name)
	result = [canonizer.summarize(o, user) for o in collection]
	if all(r for r in result if r is None):
	    return None
	return result

class Canonizer(object):

    def __init__(self):
	self.short_canon = {}
	self.full_canon = {}

    def set_short_canon(self, class_, canon):
	self.short_canon[class_] = canon

    def get_short_canon(self, obj):
	for c in obj.__class__.__mro__:
	    if c in self.short_canon:
		return self.short_canon[c]
	raise KeyError(obj.__class__)

    def set_full_canon(self, class_, canon):
	self.full_canon[class_] = canon

    def get_full_canon(self, obj):
	for c in obj.__class__.__mro__:
	    if c in self.full_canon:
		return self.full_canon[c]
	raise KeyError(obj.__class__)

    def canonize(self, obj, user):
	canon = self.get_full_canon(obj)
	result = dict((k, v.evaluate(obj, self, user)) for k, v in canon.items())
	return dict((k, v) for k, v in result.items() if v is not None)
	return result

    def summarize(self, obj, user):
	canon = self.get_short_canon(obj)
	result = dict((k, v.evaluate(obj, self, user)) for k, v in canon.items())
	return dict((k, v) for k, v in result.items() if v is not None)
