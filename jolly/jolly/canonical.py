"""Define canonical representations of objects and encode such objects."""

def register(registry, canonical):
    registry[canonical.name] = canonical

def encode(registry, object):
    for class_ in type(object).__mro__:
        try:
            return dict((registry[class_.__name__](object),))
        except KeyError:
            pass
    raise TypeError("unrecognized type '{name}'".format(type(object).__name__))

class Object(object):
    """A canonical representation of an object."""

    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def __call__(self, obj):
	return {self.name: [f(obj) for f in self.fields]}


class Field(Object):
    """The canonical representation of an object attribute."""

    def __init__(self, name, field_name=None, serialize=None):
        self.name = name
        self.field_name = field_name or name
        self.serialize = serialize or (lambda x: x)

    def __call__(self, obj):
        field = getattr(obj, self.field_name)
        return {self.name: self.serialize(field)}

class Collection(Object):
    """The canonical representation of a collection of objects."""

    def __init__(self, name, collect, fields):
        self.name = name
        self.collect = collect
        self.fields = fields

    def __call__(self, obj):
        return [{self.name: [f(o) for f in self.fields]} for o in self.collect(obj)]

#class Self(Object):
   #"""The canonical representation of an opaque object."""

    #def __init__(self, name, encode):
        #self._name = name
        #self._encode = encode or (lambda x: x)

    #def __call__(self, object):
        #return self.key, self._encode(object)
   
