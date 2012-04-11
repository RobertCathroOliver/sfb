"""
encoding/decoding

encode = Python -> JSON
decode = JSON -> Python

database encode = for storage in database (private)
api encode = for public consumption (prettier)

questions
 - how can we recognize values of a given type?
   - annotation e.g. __class__ member
   - regex matching
   - expectations (e.g. game.players is expected to be a list of Player objects)

- use annotation in database
- too ugly for api
- also, we are mostly encoding
- decode only select objects e.g. Command objects which have expected values

"""
import json
import util
import test.settings

def encode(obj, encoders, key=None):
    if key:
        encoder = encoders.get(key)
        if not encoder is None:
            return encoder(obj)
        raise TypeError('{0} is not encodeable'.format(repr(obj)))
   
    for klass in type(obj).__mro__:
        encoder = encoders.get(klass.__name__)
        if not encoder is None:
            return encoder(obj)
    raise TypeError('{0} is not encodeable'.format(repr(obj)))

identifier = util.Identifier(['Game', 'Player', 'User', 'System'])
resolver = util.URLResolver(test.settings.ROOT_URLCONF, identifier)
def get_id(obj):
    return identifier.get_obj_id(obj)

def get_uri(view_name, **kwargs):
    return resolver.get_url(view_name, **kwargs)

core_encoders = {
    'NoneType' : (lambda x: None),
    'int' : int,
    'str' : unicode,
    'unicode' : unicode,
    'list' : (lambda lst: [encode(l, core_encoders) for l in lst]),
    'dict' : (lambda dct: dict((k, encode(v, core_encoders)) for k, v in dct.items())),
}

api_encoders = {
    'Game' : (lambda game: {'title': game.title,
                            'map': {'href': get_uri('map', game_id=get_id(game))},
                            'players': [encode(p, api_property_encoders) for p in game.players],
                            'time': encode(game.current_time, api_property_encoders)}),
    'Player' : (lambda player: {'name': player.name,
                                'game': encode(player.game, api_property_encoders),
                                'user': encode(player.owner, api_property_encoders),
                                'units': [encode(u, api_property_encoders, 'Unit') for u in player.units],
                                #'log': {'href': get_uri(player.log, player_id=get_id(player), game_id=get_id(player.game))},
                                'status': {'href': get_uri('status', player_id=get_id(player), game_id=get_id(player.game))},
                                'queue': {'href': get_uri('command-queue',  player_id=get_id(player), game_id=get_id(player.game))} }),
    'System' : (lambda system: {'id': system.id,
                                'prototype': {'href': get_uri('system-prototype', name=system.prototype.name) },
                                'properties': dict((k, encode(v, api_property_encoders)) for k, v in system.properties.items()),
                                'subsystems': [encode(s, api_property_encoders) for s in system.subsystems] }),
    'User' : (lambda user: {'name': user.name,
                            'email': user.email}),
                          
}
api_encoders.update(core_encoders)
api_encoders['list'] = (lambda lst: [encode(l, api_property_encoders) for l in lst])
api_encoders['dict'] = (lambda dct: dict((k, encode(v, db_encoders)) for k, v in dct.items()))

api_property_encoders = {
    'Game' : (lambda game: {'title': game.title, 'href': get_uri('game', game_id=get_id(game))}),
    'Player' : (lambda player: {'name': player.name, 'href': get_uri('player', player_id=get_id(player), game_id=get_id(player.game))}),
    'System' : (lambda system: {'id': system.id, 'href': get_uri('system', system_id=get_id(system), unit_id=get_id(system.owner), game_id=get_id(system.owner.owner.game))}),
    'Unit' : (lambda unit: {'id': unit.id, 'href': get_uri('unit', unit_id=get_id(unit), game_id=get_id(unit.owner.game))}),
    'User': (lambda user: {'name': user.name, 'href': get_uri('user', user_id=get_id(user))}),
    'Position' : unicode,
    'Location' : unicode,
    'Direction' : unicode,
    'LocationMask' : unicode,
    'Moment' : unicode,
    'RangeDict' : (lambda rdict: [[r.begin, r.end, v] for r, v in rdict.ranges.items()]),
# SFB specific
    'DamageAllocationChart' : (lambda dac: dac.name),
    'SpeedPlot' : (lambda speedplot: 'speedplot'),
    'AccelerationLimit' : (lambda limit: {'maximum-speed': limit.max_speed,
                                          'maximum-addition': limit.max_addition,
                                          'maximum-multiplication': limit.max_multiple}),
    'TurnMode' : (lambda turnmode: turnmode.name),
    'Duration' : (lambda duration: {'turns': 'turns', 'impulses': duration.impulses})
}
api_property_encoders.update(core_encoders)

def decode_game(doc):
    players = [decode_player(p) for p in doc['players']]
    map_ = decode_map(doc['map'])
    last_actions = [decode_action(a) for a in doc['last_actions']]
    import jolly.core
    from jolly.util import import_object
    import test.settings as settings
    sequence_of_play = import_object(settings.SEQUENCE_OF_PLAY)
    choice = None
    game = jolly.core.Game(doc['title'], sequence_of_play, map_, players, choice)
    game.last_actions = last_actions
    return game

def decode_action(doc):
    import jolly.action
    action = jolly.action.Action(doc['action_type'], doc['time'], doc['target'], doc['description'], doc['details'], None, doc['private'])
    return action

def decode_map(doc):
    import jolly.map
    map = jolly.map.Map(doc['bounds'])
    return map

def decode_player(doc):
    units = [decode_system(u) for u in doc['units']]
    import jolly.core
    player = jolly.core.Player(doc['name'], units)
    #player.status = status
    return player

def decode_system(doc):
    from jolly.util import import_object
    import test.settings as settings
    registry = import_object(settings.REGISTRY)
    import jolly.system
    prototype = registry.get(doc['prototype'], jolly.system.Prototype)
    subsystems = [decode_system(s) for s in doc['subsystems']]
    properties = dict((k, decode_property(v)) for k, v in doc['properties'].items())
    system = jolly.system.System(id, prototype, properties, subsystems)
    return system

def decode_property(doc):
    return doc

db_encoders = {
    'Game' : (lambda game: {'_id': get_id(game),
                            'title': game.title,
                            'players': [encode(p, db_encoders) for p in game.players],
                            'map': encode(game.map, db_encoders),
                            'log': encode(game.log, db_encoders),
                            'last_actions': [encode(a, db_encoders) for a in game.last_actions] }),
    'Map' : (lambda map: {'bounds': map.bounds}),
    'Player' : (lambda player: {'_id': get_id(player),
                                'name': player.name,
                                'units': [encode(u, db_encoders) for u in player.units],
                                'status': encode(player.status, db_encoders) }), 
    'System' : (lambda system: {'_id': get_id(system),
                                'id': system.id,
                                'prototype': system.prototype.name,
                                'properties': dict((k, encode(v, db_encoders)) for k, v in system.properties.items()),
                                'subsystems': [encode(s, db_encoders) for s in system.subsystems] }),
    'User' : (lambda user: {'_id': get_id(user),
                            'name': user.name,
                            'email': user.email,
                            'password': user.password}),
    'Status' : (lambda status: {'status': status.status,
                                'details': [encode(d, db_encoders) for d in status.details] }),
    'ActionLog' : (lambda log: {'actions': encode(log.actions, db_encoders) }),
    'Action' : (lambda action: {'action_type': action.action_type,
                                'time': encode(action.time, db_encoders),
                                'target': get_id(action.target),
                                'description': action.description,
                                'details': encode(action.details, db_encoders),
                                'private': action.private }),
    'BreakPoint' : (lambda breakpoint: {'_id': get_id(breakpoint),
                                        'owner': get_id(breakpoint.owner),
                                        'action_type': breakpoint.action_type }),
    'SequenceOfPlayBreakpoint' : (lambda breakpoint: {'_id': get_id(breakpoint),
                                                      'owner': get_id(breakpoint.owner),
                                                      'action_type': breakpoint.action_type,
                                                      'time': encode(breakpoint.time, db_encoders) }),
    'PropertyChangeBreakPoint' : (lambda breakpoint: {'_id': get_id(breakpoint),
                                                      'owner': get_id(breakpoint.owner),
                                                      'action_type': breakpoint.action_type,
                                                      'system' : get_id(breakpoint.system),
                                                      'property_name': breakpoint.property_name }),
    'Command' : (lambda command: {'_id': get_id(command),
                                  'owner': get_id(command.owner),
                                  'template': command.template.name,
                                  'time': encode(command.time, db_encoders),
                                  'done': command.done,
                                  'cancelled': command.cancelled }),
                                  
    'Position' : unicode,
    'Location' : unicode,
    'Direction' : unicode,
    'LocationMask' : unicode,
    'Moment' : unicode,
    'RangeDict' : (lambda rdict: [[r.begin, r.end, v] for r, v in rdict.ranges.items()]),
# these are SFB specific
    'DamageAllocationChart' : (lambda dac: dac.name),
    'SpeedPlot' : (lambda speedplot: 'speedplot'),
    'AccelerationLimit' : (lambda limit: {'maximum-speed': limit.max_speed,
                                          'maximum-addition': limit.max_addition,
                                          'maximum-multiplication': limit.max_multiple}),
    'TurnMode' : (lambda turnmode: turnmode.name),
    'Duration' : (lambda duration: {'turns': 'turns', 'impulses': duration.impulses})
}
db_encoders.update(core_encoders)
db_encoders['list'] = (lambda lst: [encode(l, db_encoders) for l in lst])
db_encoders['dict'] = (lambda dct: dict((k, encode(v, db_encoders)) for k, v in dct.items()))

def decode_command(doc):
    owner = get_obj(doc['owner'])
    template = registry.get(doc['template'])
    arguments = {}
    for formal_arg in template.arguments:
        arguments[formal_arg.name] = decode(doc['arguments'][formal_arg.name], formal_arg.klass)
    time = decode(doc['time'], 'Moment')
    done = doc['done']
    cancelled = doc['cancelled']
    command = Command(owner, template, time, arguments)
    command.done = doc['done']
    command.cancelled = doc['cancelled']
    return command

