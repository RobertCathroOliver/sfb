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

import jolly.util

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

core_encoders = {
    'NoneType' : (lambda x: None),
    'int' : int,
    'str' : unicode,
    'unicode' : unicode,
    'list' : (lambda lst: [encode(l, core_encoders) for l in lst]),
    'dict' : (lambda dct: dict((k, encode(v, core_encoders)) for k, v in dct.items())),
}

def get_api_encoders(settings, api_property_encoders):
    identifier = jolly.util.import_object(settings.IDENTIFIER)
    urlresolver = jolly.util.import_object(settings.URL_RESOLVER)

    get_id = identifier.get_obj_id
    get_uri = urlresolver.get_url
    
    api_encoders = {
        'Game' : (lambda game: {'title': game.title,
                                'map': {'href': get_uri('map', root_id=get_id(game))},
                                'players': [encode(p, api_property_encoders) for p in game.players],
                                'time': encode(game.current_time, api_property_encoders),
                                'log': {'href': get_uri('game-log', root_id=get_id(game))}}),
        'Player' : (lambda player: {'name': player.name,
                                    'game': encode(player.game, api_property_encoders),
                                    'user': encode(player.owner, api_property_encoders),
                                    'units': [encode(u, api_property_encoders, 'Unit') for u in player.units],
                                    'log': {'href': get_uri('log', doc_id=get_id(player), root_id=get_id(player.game))},
                                    'status': {'href': get_uri('status', doc_id=get_id(player), root_id=get_id(player.game))},
                                    'queue': {'href': get_uri('command-queue',  doc_id=get_id(player), root_id=get_id(player.game))} }),
        'System' : (lambda system: {'id': unicode(system.id),
                                    'owner': encode(system.owner, api_property_encoders),
                                    'prototype': {'href': get_uri('system-prototype', name=system.prototype.name) },
                                    'properties': dict((k, encode(v, api_property_encoders)) for k, v in system.properties.items()),
                                    'subsystems': [encode(s, api_property_encoders) for s in system.subsystems] }),
        'User' : (lambda user: {'name': user.name,
                                'email': user.email}),
        'Map' : (lambda _map: {'game': encode(_map.game, api_property_encoders),
                               'width': int(_map.bounds[0]),
                               'height': int(_map.bounds[1]),
                               'units': [{'id': unicode(u.id),
                                          'href': get_uri('unit', doc_id=get_id(u), root_id=get_id(_map.game)),
                                          'position': encode(u.properties.get('position'), api_property_encoders)} for u in _map.game.units]}),
        'Status' : (lambda status: {'status': status.status,
                                    'details': encode(status.details, api_property_encoders)}),
        'ActionLog' : (lambda log: {'owner': encode(log.owner, api_property_encoders),
                                    'actions': encode(log.actions, api_property_encoders)}),
        'CommandQueue': (lambda queue: {'owner': encode(queue.owner, api_property_encoders),
                                        'commands': encode(queue.commands, api_property_encoders)}),
        'Command': (lambda command: {'owner': encode(command.owner, api_property_encoders),
                                     'template': encode(command.template, api_property_encoders),
                                     'time': encode(command.time, api_property_encoders),
                                     'status': command.status,
                                     'arguments': encode(command.arguments, api_property_encoders)}),
        'CommandTemplate': (lambda template: {'title': template.name,
                                              'type': 'object',
                                              'properties': {
                                                  'template': {
                                                      'type': 'string',
                                                      'required': True,
                                                      'format': 'uri',
                                                      'enum': [get_uri('command-template', name=template.name)]
                                                  },
                                                  'time': {
                                                      'type': 'string',
                                                      'required': True,
                                                      'format': 'moment[step={0}]'.format(template.step)
                                                  },
                                                  'arguments': {
                                                      'type': 'object',
                                                      'properties': dict((a.name, encode(a, api_property_encoders)) for a in template.arguments)
                                                      }
                                                  }
                                              }),
    }
    api_encoders.update(core_encoders)
    api_encoders['list'] = (lambda lst: [encode(l, api_property_encoders) for l in lst])
    api_encoders['dict'] = (lambda dct: dict((k, encode(v, api_property_encoders)) for k, v in dct.items()))
    return api_encoders

def get_api_property_encoders(settings):
    identifier = jolly.util.import_object(settings.IDENTIFIER)
    urlresolver = jolly.util.import_object(settings.URL_RESOLVER)

    get_id = identifier.get_obj_id
    get_uri = urlresolver.get_url
    
    def encode_argument(arg):
        import numbers
        result = {'required': arg.mandatory}
        if arg.klass.__name__ in identifier.resource_types:
            result['type'] = 'string'
            result['format'] = 'uri'
        elif isinstance(arg.klass, numbers.Integral):
            result['type'] = 'integer'
        else:
            result['type'] = 'string'
        return result

    api_property_encoders = {}
    api_property_encoders.update({
        'Game' : (lambda game: {'title': game.title, 'href': get_uri('game', root_id=get_id(game))}),
        'Player' : (lambda player: {'name': player.name, 'href': get_uri('player', doc_id=get_id(player), root_id=get_id(player.game))}),
        'System' : (lambda system: encode(system, api_property_encoders, 'Unit') if system.is_unit() else {'id': unicode(system.id), 'href': get_uri('system', doc_id=get_id(system), unit_id=get_id(system.owner), root_id=get_id(system.owner.owner.game))}),
        'Unit' : (lambda unit: {'id': unicode(unit.id), 'href': get_uri('unit', doc_id=get_id(unit), root_id=get_id(unit.owner.game))}),
        'User': (lambda user: {'name': user.name, 'href': get_uri('user', root_id=get_id(user))}),
        'Command': (lambda command: {'href': get_uri('command', doc_id=get_id(command), player_id=get_id(command.owner), root_id=get_id(command.owner.game)),
                                     'time': encode(command.time, api_property_encoders),
                                     'template': encode(command.template, api_property_encoders)}),
        'Action': (lambda action: {'action-type': action.action_type,
                                   'time': encode(action.time, api_property_encoders),
                                   'target': encode(action.target, api_property_encoders),
                                   'description': encode(action.description, api_property_encoders),
                                   'details': encode(action.details, api_property_encoders),
                                   'owner': encode(action.owner, api_property_encoders)}),
        'CommandTemplate' : (lambda template: {'name': template.name,
                                               'href': get_uri('command-template', name=template.name)}),
        'FormalArgument' : encode_argument,
        'Fraction' : (lambda f: int(f) if f.denominator == 1 else str(f)),
        'Position' : unicode,
        'Location' : unicode,
        'Direction' : unicode,
        'LocationMask' : unicode,
        'Moment' : unicode,
        'RangeDict' : (lambda rdict: [[r.begin, r.end, v] for r, v in rdict.ranges.items()]),
    })
    api_property_encoders.update(core_encoders)
    api_property_encoders['list'] = (lambda lst: [encode(l, api_property_encoders) for l in lst])
    api_property_encoders['dict'] = (lambda dct: dict((k, encode(v, api_property_encoders)) for k, v in dct.items()))
    return api_property_encoders

def get_db_encoders(settings):
    identifier = jolly.util.import_object(settings.IDENTIFIER)
    get_id = identifier.get_obj_id

    def encode_command_argument(argument, db_encoders):
        encoded = encode(argument, db_encoders)
        if isinstance(encoded, dict) and '_id' in encoded:
            return encoded['_id']
        return encoded

    db_encoders = {
        'Game' : (lambda game: {'_id': get_id(game),
                                '$class': 'jolly.core.Game',
                                'title': game.title,
                                'players': encode(game.players, db_encoders),
                                'map': encode(game.map, db_encoders),
                                'log': encode(game.log, db_encoders),
                                'queue': encode(game.queue, db_encoders),
                                'last_actions': encode(game.last_actions, db_encoders)}),
        'Map' : (lambda map: {'bounds': map.bounds,
                              '$class': 'jolly.map.Map'}),
        'Player' : (lambda player: {'_id': get_id(player),
                                    '$class': 'jolly.core.Player',
                                    'name': player.name,
                                    'owner': get_id(player.owner),
                                    'units': encode(player.units, db_encoders),
                                    'breakpoints': encode(player.breakpoints, db_encoders),
                                    'queue': encode(player.queue, db_encoders),
                                    'status': encode(player.status, db_encoders) }), 
        'System' : (lambda system: {'_id': get_id(system),
                                    '$class': 'jolly.system.System',
                                    'id': system.id,
                                    'prototype': {'$lookup': system.prototype.name},
                                    'properties': encode(system.properties, db_encoders),
                                    'subsystems': encode(system.subsystems, db_encoders) }),
        'User' : (lambda user: {'_id': get_id(user),
                                '$class': 'jolly.core.User',
                                'name': user.name,
                                'email': user.email,
                                'password': user.password}),
        'Status' : (lambda status: {'$class': 'jolly.core.Status',
                                    'owner': get_id(status.owner),
                                    'status': status.status,
                                    'details': encode(status.details, db_encoders)}),
        'ActionLog' : (lambda log: {'$class': 'jolly.core.ActionLog',
                                    'owner': get_id(log.owner),
                                    'actions': encode(log.actions, db_encoders) }),
        'Action' : (lambda action: {'$class': 'jolly.action.Action',
                                    'owner': get_id(action.owner),
                                    'action-type': action.action_type,
                                    'time': encode(action.time, db_encoders),
                                    'target': get_id(action.target),
                                    'description': action.description,
                                    'details': encode(action.details, db_encoders),
                                    'private': action.private }),
        'BreakPoint' : (lambda breakpoint: {'_id': get_id(breakpoint),
                                            '$class': 'jolly.breakpoint.BreakPoint',
                                            'owner': get_id(breakpoint.owner),
                                            'action-type': breakpoint.action_type }),
        'SequenceOfPlayBreakPoint' : (lambda breakpoint: {'_id': get_id(breakpoint),
                                                          '$class': 'jolly.breakpoint.SequenceOfPlayBreakPoint',
                                                          'owner': get_id(breakpoint.owner),
                                                          'time': encode(breakpoint.time, db_encoders) }),
        'PropertyChangeBreakPoint' : (lambda breakpoint: {'_id': get_id(breakpoint),
                                                          '$class': 'jolly.breakpoint.PropertyChangeBreakPoint',
                                                          'owner': get_id(breakpoint.owner),
                                                          'system' : get_id(breakpoint.system),
                                                          'property-name': breakpoint.property_name }),
        'CommandQueue' : (lambda queue: {'$class': 'jolly.command.CommandQueue',
                                         'commands': encode(queue.commands, db_encoders),
                                         'owner': get_id(queue.owner)}),
        'Command' : (lambda command: {'_id': get_id(command),
                                      '$class': 'jolly.command.Command',
                                      'owner': get_id(command.owner),
                                      'template': {'$lookup': command.template.name},
                                      'arguments': dict((k, encode_command_argument(v, db_encoders)) for k, v in command.arguments.items()),
                                      'time': encode(command.time, db_encoders),
                                      'done': command.done,
                                      'cancelled': command.cancelled }),
                                  
        'Position' : unicode,
        'Location' : unicode,
        'Direction' : unicode,
        'LocationMask' : unicode,
        'Moment' : unicode,
        'RangeDict' : (lambda rdict: {'$class': 'jolly.util.RangeDict',
                                  'dictionary': rdict.ranges}),
        'Range' : (lambda range: {'$class': 'jolly.util.Range',
                                  'begin': range.begin,
                                  'end': range.end}),
    }
    db_encoders.update(core_encoders)
    db_encoders['list'] = (lambda lst: [encode(l, db_encoders) for l in lst])
    db_encoders['dict'] = (lambda dct: dict((k, encode(v, db_encoders)) for k, v in dct.items()))
    return db_encoders

def make_object_decoder(field_map, decoder):
    def decode_object(doc, references=None):
        args = dict((v, decoder.decode(doc[k], references)) for k, v in field_map.items())
        if '_id' in doc:
            obj = references.get(doc['_id'])
            obj.__init__(**args)
            decoder.set_obj(doc['_id'], obj)
            return obj
        _class = jolly.util.import_object(doc['$class'])
        return _class(**args)
    return decode_object

def make_game_decoder(settings, decoder):
    sequence_of_play = jolly.util.import_object(settings.SEQUENCE_OF_PLAY)
    randomizer = jolly.util.import_object(settings.RANDOMIZER)
    def decode_game(doc, references=None):
        title = doc['title']
        players = decoder.decode(doc['players'], references)
        map_ = decoder.decode(doc['map'], references)
        log = decoder.decode(doc['log'], references)
        queue = decoder.decode(doc['queue'], references)
        last_actions = decoder.decode(doc['last_actions'], references)

        game = references.get(doc['_id'])
        game.__init__(title, sequence_of_play, map_, players, randomizer, log, queue)
        game.last_actions = last_actions
        decoder.set_obj(doc['_id'], game)
        return game
    return decode_game

def make_command_decoder(decoder):
    decode_object = make_object_decoder({'owner': 'owner',
                                         'template': 'template',
                                         'time': 'time',
                                         'arguments': 'arguments'}, decoder)
    def decode_command(doc, references=None):
        command = decode_object(doc, references)
        command.done = decoder.decode(doc['done'], references)
        command.cancelled = decoder.decode(doc['cancelled'], references)
        return command
    return decode_command

def get_db_decoders(settings, decoder):
    db_decoders = {
        'jolly.core.Game' : make_game_decoder(settings, decoder),
        'jolly.map.Map' : make_object_decoder({'bounds': 'bounds'}, decoder),
        'jolly.core.Player' : make_object_decoder({'name': 'name',
                                                   'units': 'units',
                                                   'breakpoints': 'breakpoints',
                                                   'owner': 'owner',
                                                   'status': 'status',
                                                   'queue': 'queue'}, decoder),
        'jolly.system.System' : make_object_decoder({'id': 'id',
                                                     'prototype': 'prototype',
                                                     'properties': 'properties',
                                                     'subsystems': 'subsystems'}, decoder),
        'jolly.core.Status' : make_object_decoder({'owner': 'owner',
                                                   'status': 'status',
                                                   'details': 'details'}, decoder),
        'jolly.core.User' : make_object_decoder({'name': 'name',
                                                 'email': 'email',
                                                 'password': 'password'}, decoder),
        'jolly.core.ActionLog' : make_object_decoder({'owner': 'owner',
                                                      'actions': 'actions'}, decoder),
        'jolly.action.Action' : make_object_decoder({'action-type': 'action_type',
                                                     'time': 'time',
                                                     'target': 'target',
                                                     'description': 'description',
                                                     'details': 'details',
                                                     'owner': 'owner',
                                                     'private': 'private'}, decoder),
        'jolly.breakpoint.BreakPoint' : make_object_decoder({'owner': 'owner',
                                                             'action-type': 'action_type'}, decoder),
        'jolly.breakpoint.SequenceOfPlayBreakPoint' : make_object_decoder({'owner': 'owner',
                                                                           'time': 'time'}, decoder),
        'jolly.breakpoint.PropertyChangeBreakPoint' : make_object_decoder({'owner': 'owner',
                                                                           'system': 'system',
                                                                           'property-name': 'property_name'}, decoder),
        'jolly.command.CommandQueue' : make_object_decoder({'commands': 'commands',
                                                            'owner': 'owner'}, decoder),
        'jolly.command.Command' : make_command_decoder(decoder),
        'jolly.util.RangeDict': make_object_decoder({'dictionary': 'dictionary'}, decoder),
        'jolly.util.Range': make_object_decoder({'begin': 'begin', 'end': 'end'}, decoder),
    }
    return db_decoders
