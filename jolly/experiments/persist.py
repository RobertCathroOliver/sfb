
class System(db.Expando):
    id = db.StringProperty(required=True)
    prototype = db.StringProperty(required=True)

    def get_prototype(self):
        prototype = create_prototype(self.prototype) 
        return prototype

    def build(self):
        prototype = self.get_prototype()
        return prototype.create_systems(self.id, self.dynamic_properties())



registry = {}

def persist(object):
    return registry[object.__class__.__name__].persist(object)

def retrieve(id):
    data = db.get(id)
    return revive(data)

def revive(data):
    for k, v in data.items():
        if k[0] != '_':
            if 


result = { '_class' : self.__class__.__name__,
           'id' : self.id
           'prototype' : self._prototype.name
           'properties' : 

{ '_class' : 'Unit',
  'id' : '/g/1/unit/1'
  'prototype' : 'admin-shuttle',
  'properties' : { 'turn-mode' : 'shuttle',
                   'acceleration-limit' : { 'max-speed' : 6,
                                            'max-addition' : 6,
                                            'max-multiple' : 1 } },
                   'turn-mode-counter' : 0,
                   'sideslip-mode-counter' : 0,
                   'speed-plot' : { 'speeds' : { [0, 31] : 0 } }
                   'damage-rules', 'DAC_shuttle',
                   'position' : '0101A' },
  'systems' : ['/g/1/unit/1/system/1',
               '/g/1/unit/1/system/2',
               '/g/1/unit/1/system/3',
               '/g/1/unit/1/system/4',
               '/g/1/unit/1/system/5',
               '/g/1/unit/1/system/6',
               '/g/1/unit/1/system/7']
}

{ '_class' : 'System',
  'id' : '/g/1/unit/1/system/1',
  'prototype' : 'shuttle-hull',
  'properties' : { }
}, ...
{ '_class' : 'System',
  'id' : '/g/1/unit/1/system/7',
  'prototype' : 'shuttle-phaser-3',
  'properties' : { 'firing-arc' : 'ALL' } 
}
