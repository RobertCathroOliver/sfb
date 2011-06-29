import json

def json_encode(obj):
    for klass in type(obj).__mro__:
        encoder = json_encoders.get(klass.__name__)
        if not encoder is None:
            return encoder(obj)
    raise TypeError('{0} is not JSON serializable'.format(repr(obj)))

def get_id(obj):
    return 'id'

json_encoders = {
    'NoneType' : (lambda x: None),
    'int' : int,
    'str' : unicode,
    'unicode' : unicode,
    'list' : (lambda lst: [json_encode(l) for l in lst]),
    'dict' : (lambda dct: dict((k, json_encode(v)) for k, v in dct.items())),
    'Game' : (lambda game: {'type': 'game',
                            '_id': get_id(game),
                            'title': game.title,
                            'players': json_encode(game.players) }),
    'Player' : (lambda player: {'type': 'player',
                                'id': get_id(player),
                                'name': player.name,
                                'units': json_encode(player.units) }),
    'System' : (lambda system: {'id': system.id,
                                'prototype': system.prototype.name,
                                'properties': json_encode(system.properties),
                                'subsystems': json_encode(system.subsystems) }),
    'Position' : unicode,
    'Location' : unicode,
    'Direction' : unicode,
    'LocationMask' : unicode,
    'Moment' : unicode,
    'DamageAllocationChart' : (lambda dac: dac.name),
    'SpeedPlot' : (lambda speedplot: 'speedplot'),
    'AccelerationLimit' : (lambda limit: {'maximum-speed': limit.max_speed,
                                          'maximum-addition': limit.max_addition,
                                          'maximum-multiplication': limit.max_multiple}),
    'TurnMode' : (lambda turnmode: turnmode.name),
    'Duration' : (lambda duration: {'turns': 'turns', 'impulses': duration.impulses}),
    'RangeDict' : (lambda rdict: [[r.begin, r.end, v] for r, v in rdict.ranges.items()])
}

