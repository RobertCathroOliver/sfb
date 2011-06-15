import pickle

from google.appengine.ext import db

class System(db.Expando):
    id = db.StringProperty(required=True)
    prototype = db.StringProperty(required=True)
    unit = db.ReferenceProperty(Unit)

    def to_object(self, prototypes):
        prototype = prototypes[self.prototype]
        properties = dict((p, pickle.loads(getattr(self, p))) for p in self.dynamic_properties())
        result = prototype.create_system(self.id, prototype, properties)
        return result

    @classmethod
    def from_object(cls, system, unit):
        result = System(id=system.id, prototype=system.prototype.name, unit=unit)
        for k, v in system.properties.items():
            setattr(result, k, pickle.dumps(v))
        return result

class Unit(db.Expando):
    id = db.StringProperty(required=True)
    prototype = db.StringProperty(required=True)

    def to_object(self, prototypes):
        prototype = prototypes[self.prototype]
        systems = [s.to_object(prototypes) for s in self.system_set]
        properties = dict((p, pickle.loads(getattr(self, p))) for p in self.dynamic_properties())
        result = prototype.create_system(self.id, prototype, systems, properties)
        return result

    @classmethod
    def from_object(cls, unit):
        result = Unit(id=unit.id, prototype=unit.prototype.name)
        for s in unit.systems:
            result.system_set.add(System.from_object(s, result))
        for k, v in unit.properties.items():
            setattr(result, k, pickle.dumps(v))
        return result

