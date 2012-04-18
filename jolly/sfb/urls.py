import operator

from django.conf.urls.defaults import patterns
from django.views.generic.simple import direct_to_template

from jolly.http import MethodDispatcher
from jolly.view import (root, get, get_many, registry_get,
	                delete_command, put_command, post_command,
			delete_breakpoint, post_breakpoint)

urlpatterns = patterns('',
    (r'^$', MethodDispatcher({'GET': root})),
    (r'^g$', 
        MethodDispatcher({'GET': get_many}), 
        {'doc_type': 'jolly.core.Game'}, 
        'games'),
    (r'^g/(?P<root_id>[0-9a-f]{32})$', 
        MethodDispatcher({'GET': get}), 
        {'doc_type': 'jolly.core.Game'}, 
        'game'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/map$', 
        MethodDispatcher({'GET': get}), 
        {'doc_type': 'jolly.map.Map', 'path': (operator.attrgetter('map'),)}, 
        'map'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/player$', 
        MethodDispatcher({'GET': get_many}), 
        {'doc_type': 'jolly.core.Player'},
        'players'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/player/(?P<doc_id>[0-9a-f]{32})$', 
        MethodDispatcher({'GET': get}), 
        {'doc_type': 'jolly.core.Player'}, 
        'player'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/unit/(?P<doc_id>[0-9a-f]{32})$', 
        MethodDispatcher({'GET': get}), 
        {'doc_type': 'jolly.system.System'}, 
        'unit'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/unit/(?P<unit_id>[0-9a-f]{32})/system/(?P<doc_id>[0-9a-f]{32})$', 
        MethodDispatcher({'GET': get}), 
        {'doc_type': 'jolly.system.System'}, 
        'system'),
    (r'^user$', 
        MethodDispatcher({'GET': get_many}), 
        {'doc_type': 'jolly.core.User'}, 
        'users'),
    (r'^user/(?P<root_id>[0-9a-f]{32})$', 
        MethodDispatcher({'GET': get}), 
        {'doc_type': 'jolly.core.User'}, 
        'user'),
    (r'^user/(?P<root_id>[0-9a-f]{32})/player$', 
        MethodDispatcher({'GET': get_many}), 
        {'doc_type': 'jolly.core.Player'},
        'players'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/player/(?P<doc_id>[0-9a-f]{32})/queue$', 
        MethodDispatcher({'GET': get,
                          'POST': post_command}), 
        {'doc_type': 'jolly.command.CommandQueue', 'private_view': True, 'path': (operator.attrgetter('queue'),)}, 
        'command-queue'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/queue$', 
        MethodDispatcher({'GET': get}), 
        {'doc_type': 'jolly.command.CommandQueue', 'private_view': True, 'path': (operator.attrgetter('queue'),)}, 
        'game-command-queue'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/player/(?P<player_id>[0-9a-f]{32})/command/(?P<doc_id>[0-9a-f]{32})$', 
        MethodDispatcher({'GET': get, 
                          'DELETE': delete_command,
                          'PUT': put_command}), 
        {'doc_type': 'jolly.command.Command', 'private_view': True}, 
        'command'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/player/(?P<doc_id>[0-9a-f]{32})/log$', 
    MethodDispatcher({'GET': get}), 
        {'doc_type': 'jolly.core.ActionLog', 'private_view': True, 'path': (operator.attrgetter('log'),)}, 
        'log'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/log$', 
    MethodDispatcher({'GET': get}), 
        {'doc_type': 'jolly.core.ActionLog', 'path': (operator.attrgetter('log'),)},
        'game-log'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/player/(?P<doc_id>[0-9a-f]{32})/status$', 
        MethodDispatcher({'GET': get}), 
        {'doc_type': 'jolly.core.Status', 'private_view': True, 'path': (operator.attrgetter('status'),)}, 
        'status'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/player/(?P<player_id>[0-9a-f]{32})/breakpoint$', 
        MethodDispatcher({'GET': get_many,
	                  'POST': post_breakpoint}), 
	{'doc_type': 'jolly.breakpoint.BreakPoint', 'private_view': True}, 
        'breakpoints'),
    (r'^g/(?P<root_id>[0-9a-f]{32})/player/(?P<player_id>[0-9a-f]{32})/breakpoint/(?P<doc_id>[0-9a-f]{32})$', 
        MethodDispatcher({'GET': get,
	                  'DELETE': delete_breakpoint}), 
	{'doc_type': 'jolly.breakpoint.BreakPoint', 'private_view': True}, 
        'breakpoint'),
#    (r'^scenario/(?P<doc_id>[0-9a-f]{32})$', 
#        MethodDispatcher({'GET': get}), 
#        {'doc_type': 'jolly.core.Scenario'}, 
#        'scenario'),
    (r'^system-prototype/(?P<name>[a-zA-Z-]+)$',
        MethodDispatcher({'GET': direct_to_template}),
        {'doc_type': 'jolly.system.Prototype',
         'template': ''},
	'system-prototype'),
    (r'^command-template/(?P<name>[a-zA-Z-]+)$',
        MethodDispatcher({'GET': registry_get}),
        {'doc_type': 'jolly.command.CommandTemplate',
         'template': ''},
	'command-template'),
    (r'^test/test_ajax.html', 
        direct_to_template, 
        {'template': 'test_ajax.html'}),
    (r'^test/test_window.html', 
        direct_to_template, 
        {'template': 'test_window.html'}),
    (r'^test/test_map.html', 
        direct_to_template, 
        {'template': 'test_map.html'}),
    (r'^window.js', 
        direct_to_template, 
        {'template': 'window.js'}),
    (r'^map.js', 
        direct_to_template, 
        {'template': 'map.js'}),
    (r'^sfb.js', 
        direct_to_template, 
        {'template': 'sfb.js'}),
)


