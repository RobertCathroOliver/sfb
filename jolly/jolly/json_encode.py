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

def encode(obj, encoders):
    for klass in type(obj).__mro__:
        encoder = encoders.get(klass.__name__)
        if not encoder is None:
            return encoder(obj)
    raise TypeError('{0} is not encodeable'.format(repr(obj)))

def get_id(obj):
    return 'id'

def get_uri(obj):
    return 'uri'

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
                            'map': {'href': get_uri(game.map)},
                            'players': [encode(p, api_property_encoders) for p in game.players],
                            'time': encode(game.current_time, api_property_encoders)}),
    'Player' : (lambda player: {'name': player.name,
                                'game': encode(player.game, api_property_encoders),
                                'user': encode(player.user, api_property_encoders),
                                'units': [encode(u, api_property_encoders) for u in player.units],
                                'log': {'href': get_uri(player.log)},
                                'status': {'href': get_uri(player.status)},
                                'queue': {'href': get_uri(player.queue)} }),
    'System' : (lambda system: {'id': system.id,
                                'prototype': {'href': get_uri(system.prototype) },
                                'properties': encode(system.properties, api_property_encoders),
                                'subsystems': [encode(s, api_property_encoders) for s in system.subsystems] }),
}
api_encoders.update(core_encoders)

api_property_encoders = {
    'Game' : (lambda game: {'title': game.title, 'href': get_uri(game)}),
    'Player' : (lambda player: {'name': player.name, 'href': get_uri(player)}),
    'System' : (lambda system: {'id': system.id, 'href': get_uri(system)}),
    'User': (lambda user: {'name': user.name, 'href': get_uri(user)}),
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
    game = Game(doc['title'], sequence_of_play, map_, players, choice)
    game.last_actions = last_actions
    return game

def decode_player(doc):
    units = [decode_system(u) for u in doc['units']]
    player = Player(doc['name'], units)
    player.status = status

def decode_system(doc):
    prototype = registry.get(doc['prototype'], Prototype)
    subsystems = [decode_system(s) for s in doc['subsystems']]
    properties = dict((k, decode_property(v)) for k, v in doc['properties'])
    system = System(id, prototype, 

db_encoders = {
    'Game' : (lambda game: {'_id': get_id(game),
                            'title': game.title,
                            'players': [encode(p, db_encoders) for p in game.players],
                            'map': encode(game.map, db_encoders),
                            'last_actions': [encode(a, db_encoders) for a in game.last_actions] }),
    'Player' : (lambda player: {'name': player.name,
                                'units': [encode(u, db_encoders) for u in player.units],
                                'status': encode(player.status, db_encoders) }), 
    'System' : (lambda system: {'id': system.id,
                                'prototype': system.prototype.name,
                                'properties': dict((k, encode(v, db_encoders)) for k, v in system.properties.items()),
                                'subsystems': [encode(s, db_encoders) for s in system.subsystems] }),
    'User' : (lambda user: {'name': user.name,
                            'email': user.email,
                            'password': user.password}),
    'Status' : (lambda status: {'status': status.status,
                                'details': [encode(d, db_encoders) for d in status.details] }),
    'Action' : (lambda action: {'action_type': action.action_type,
                                'time': encode(action.time, db_encoders),
                                'target': get_id(action.target),
                                'description': action.description,
                                'details': dict((k, encode(v, db_encoders)) for k, v in action.details.items()),
                                'private': action.private }),
    'BreakPoint' : (lambda breakpoint: {'owner': get_id(breakpoint.owner),
                                        'action_type': breakpoint.action_type }),
    'SequenceOfPlayBreakpoint' : (lambda breakpoint: {'owner': get_id(breakpoint.owner),
                                                      'action_type': breakpoint.action_type,
                                                      'time': encode(breakpoint.time, db_encoders) }),
    'PropertyChangeBreakPoint' : (lambda breakpoint: {'owner': get_id(breakpoint.owner),
                                                      'action_type': breakpoint.action_type,
                                                      'system' : get_id(breakpoint.system),
                                                      'property_name': breakpoint.property_name }),
    'Command' : (lambda command: {'owner': get_id(command.owner),
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

