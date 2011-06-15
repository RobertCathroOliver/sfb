
class Converter(object):

    def __init__(self):
	pass

    def convert(self, obj, rule=None, is_included=None):
	rule = rule or self.find_rule(obj)
	is_included = is_included or (lambda x: True)

class ConversionRule(object):

    def __init__(self, constructor, attributes=None):
        self.constructor = constructor
        self.attributes = attributes

    def convert(self, obj, converter, is_included):
        if not is_included(obj):
            return None
        if not self.attributes:
            return self.constructor(obj)
        result = self.constructor()
        for get_key, get_attr, format in self.attributes:
            key = get_key(obj) if callable(get_key) else get_key
            attr = get_attr(obj)
            if is_included(attr):
                value = format(attr) if callable(format) else converter.convert(attr, format, is_included)
                result[key] = value
        return result   

def make_href(obj):
    return {'href': urlresolver.get_url(obj)}

def list_of(rule):
    def iterate(attr):
        return [converter.convert(a, rule, is_included) for a in attr]
    return iterate

def dict_of(rule):
    def iterate(attr):
        return dict((k, converter.convert(v, rule, is_included)) for k, v in attr)
    return iterate

def prefer_ref(obj):
    try:
        return make_href(obj)
    except:
        rule = '.'.join(getattr(type

rules = {
    'jolly.map.Map': ConversionRule(dict,
        (('width', lambda o: o.bounds[0], int),
         ('height', lambda o: o.bounds[1], int),
         ('game', operator.attrgetter('game'), make_href),
         ('tokens', operator.attrgetter('tokens'), list_of('jolly.map.Token')))),
    'jolly.map.Token': ConversionRule(dict,
        (('position', operator.attrgetter('position'), unicode),
         ('href', operator.attrgetter('item'), get_url))),
    'jolly.map.Direction': ConversionRule(unicode),
    'jolly.map.Location': ConversionRule(unicode),
    'jolly.map.Position': ConversionRule(unicode),
    'jolly.map.LocationMask': ConversionRule(make_href)
    'jolly.map.Bearing': ConversionRule(lambda o: '{0} - {1}'.format(o.offset_direction, o.rotation_direction)),

    'jolly.core.Game': ConversionRule(dict,
        (('title', operator.attrgetter('title'), unicode),
         ('players', operator.attrgetter('players'), list_of('jolly.core.Player')),
         ('map', operator.attrgetter('map'), make_href),
         ('time', operator.attrgetter('last_command'), unicode))),
    'jolly.core.User': ConversionRule(dict,
        (('name', operator.attrgetter('name'), unicode),)),
    'jolly.system.System': ConversionRule(dict,
        (('id', operator.attrgetter('id'), unicode),
         (lambda o: 'player' if obj.subsystems else 'unit', operator.attrgetter('owner'), make_href),
         ('prototype', operator.attrgetter('prototype'), lambda o: {'href': 'prototype/{0}'.format(o.name)}),
         ('properties', operator.attrgetter('properties'), dict_of(prefer_ref)),
         ('subsystems', operator.attrgetter('subsystems'), list_of('jolly.system.System')),
    'jolly.chrono.Moment': ConversionRule(unicode),
    'jolly.command.Command': ConversionRule(dict,
        (('owner', operator.attrgetter('owner'), make_href),
         ('template', operator.attrgetter('template'), lambda o: {'href': 'command-template/{0}'.format(o.name)}),
         ('time', operator.attrgetter('time'), unicode),
         ('status', operator.attrgetter('status'), unicode),
         ('arguments', operator.attrgetter('arguments'), dict_of(prefer_ref)),
         ('queue', operator.attrgetter('queue'), make_href))),
    'jolly.command.CommandQueue': ConversionRule(dict,
        (('player', operator.attrgetter('owner'), make_href),
         ('commands', lambda o: o, list_of(make_href))),
}
