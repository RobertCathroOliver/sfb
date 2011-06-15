class URLMapper(object):

    def __init__(self, url_map):
	self.url_map = dict((k, re.compile(v)) for k, v in url_map.items())
	self.ids = {}

    def get_id(self, obj):
	return self.ids[id(obj)]

    def set_id(self, obj, id_):
	self.ids[id(obj)] = id_

    def get_url(self, obj):
	id_ = self.get_id(obj)
	pattern = self.get_pattern(obj)
	return pattern.sub(r'\1', id_)

    def reverse(self, url):
	for class_, pattern in self.url_map.items():
            match = pattern.search(url)
	    if match:
		return class_, match.group()
	raise KeyError(url)

    def get_pattern(self, obj):
	for c in obj.__class__.__mro__:
	    if c in self.url_map:
		return self.url_map[c]
	raise KeyError(obj.__class__)
	

class Persistence(object):

    def __init__(self, url_mapper, loaders, savers):
	"""url_mapper is a URLMapper object.
	   loaders is a dict with class keys and load function values.
	   savers is a dict with class keys and save function values."""
	self.url_mapper = url_mapper
	self.loaders = loaders
	self.savers = savers

    def save(self, obj):
	save = self.savers[obj.__class__]
	id_ = save(obj, self.url_mapper.get_id(obj))
	self.url_mapper.set_id(obj, id_)

    def load(self, url):
	class_, id_ = self.url_mapper.reverse(url)
	load = self.loaders[class_]
	obj = load(id_)
	self.url_mapper.set_id(obj, id_)
	return obj
