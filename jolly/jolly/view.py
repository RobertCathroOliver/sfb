from django.conf import settings

import json

import jolly.http
import jolly.json_encode
from jolly.util import import_object, URLResolver


@jolly.http.content_negotiate
def root(request):
    urlresolver = import_object(settings.URL_RESOLVER)
    result = {'type': 'root',
              'games': {'type': 'collection', 'href': urlresolver.get_query_url_by_name('games')},
              'users': {'type': 'collection', 'href': urlresolver.get_query_url_by_name('users')}}
    return result

@jolly.http.authenticate
@jolly.http.content_negotiate
def get(request, root_id, *args, **kwargs):
    db = import_object(settings.DB)
    try:
        root = db.restore(root_id)
        doc_id = kwargs.get('doc_id', root_id)
        type_ = import_object(kwargs['doc_type'])
        path = kwargs.get('path', ())
        obj = db.get_obj(doc_id)
        if obj is None:
            return jolly.http.HttpResponseNotFound({'error': 'cannot restore 1'})

        def follow_path(obj):
            for p in path:
                obj = p(obj)
                if obj is None:
                    return obj
            return obj
        if isinstance(obj, list):
            obj = [follow_path(o) for o in obj]
            if any(o is None for o in obj):
                return jolly.http.HttpResponseNotFound({'error': 'cannot restore 2'})
        else:
            obj = follow_path(obj)
            if obj is None:
                return jolly.http.HttpResponseNotFound({'error': 'cannot restore 2'})
    except (KeyError, ImportError):
        return jolly.http.HttpResponseNotFound({'error': 'cannot restore 3'})

    if isinstance(obj, list):
        if any(not isinstance(o, type_) for o in obj):
            return jolly.http.HttpResponseNotFound({'error': 'bad type'})
    else:
        if not isinstance(obj, type_):
            return jolly.http.HttpResponseNotFound({'error': 'bad type'})

    user = request.user
    if kwargs.get('private_view', False):
        if isinstance(obj, list):
            if any(not user.is_owner(o) for o in obj):
                return jolly.http.HttpResponseUnauthorized(settings.AUTHENTICATION_REALM)
        else:
            if not user.is_owner(obj):
                return jolly.http.HttpResponseUnauthorized(settings.AUTHENTICATION_REALM)

    def is_visible(obj):
        return not getattr(obj, 'private', False) or user.is_owner(obj)

    out = import_object(settings.OUTPUT_CONVERTER)
    result = jolly.json_encode.encode(obj, out)

    return result

@jolly.http.authenticate
@jolly.http.content_negotiate
def get_many(request, *args, **kwargs):
    db = import_object(settings.DB)
    query = kwargs.get('query', [])
    where = []
    for k in query:
        if k in request.GET:
            where.extend([k, request.GET[k]])
    try:
	view_name = settings.QUERY_VIEWS[kwargs['doc_type']]
        objs = db.restore_view(view_name, where)
    except (KeyError, ImportError):
        return jolly.http.HttpResponseNotFound({'error': 'not found'})

    user = request.user
    if kwargs.get('private_view', False) and not all(user.is_owner(o) for o in obj):
        return jolly.http.HttpResponseUnauthorized(settings.AUTHENTICATION_REALM)

    def is_visible(obj):
        return not getattr(obj, 'private', False) or user.is_owner(obj)

    out = import_object(settings.OUTPUT_CONVERTER)
    result = jolly.json_encode.encode(objs, out)

    return result

@jolly.http.authenticate
@jolly.http.content_negotiate
def registry_get(request, name, doc_type, *args, **kwargs):
    registry = import_object(settings.REGISTRY)
    try:
        obj = registry.get(name, doc_type)
    except (KeyError,):
        return jolly.http.HttpResponseNotFound({'error': 'not found'})

    out = import_object(settings.OUTPUT_CONVERTER)
    result = jolly.json_encode.encode(obj, out)

    return result


@jolly.http.authenticate
@jolly.http.content_negotiate
def delete_command(request, doc_id, *args, **kwargs):
    import jolly.command

    db = jolly.db.create_database()
    try:
        command = db.restore_object(doc_id)
    except KeyError:
        return jolly.http.HttpResponseNotFound({'error': 'cannot restore'})

    if not isinstance(command, jolly.command.Command):
        return jolly.http.HttpResponseNotFound({'error': 'bad type'})

    user = request.user
    if not user.is_owner(command):
        return jolly.http.HttpResponseUnauthorized(settings.AUTHENTICATION_REALM)

    try:
	queue = command.queue
        command.cancel()
    except jolly.command.PreviouslyCancelled:
        pass # DELETE is idempotent
    except jolly.command.CannotCancel:
        return jolly.http.HttpResponseForbidden({'error': 'command cannot be cancelled'})
    except jolly.command.PreviouslyExecuted:
        return jolly.http.HttpResponseForbidden({'error': 'command has already be executed'})
    else:
        game = command.owner.game
        game.advance()

        db.dirty_all()
        db.store_object(game)

    return jolly.http.HttpResponseRedirect(doc_id)

@jolly.http.authenticate
@jolly.http.content_negotiate
def put_command(request, doc_id, *args, **kwargs):
    import jolly.command

    db = jolly.db.create_database()
    try:
        command = db.restore_object(doc_id)
    except KeyError:
        return jolly.http.HttpResponseNotFound({'error': 'cannot restore'})

    if not isinstance(command, jolly.command.Command):
        return jolly.http.HttpResponseNotFound({'error': 'bad type'})

    user = request.user
    if not user.is_owner(command):
        return jolly.http.HttpResponseUnauthorized(settings.AUTHENTICATION_REALM)

    # Convert the data from JSON to a Python dict
    try:
        data = json.loads(request.raw_post_data)
        request_arguments = data['arguments']
    except (KeyError, ValueError):
        return jolly.http.HttpResponseBadRequest()

    # Determine the arguments
    value_resolver = import_object(settings.VALUE_RESOLVER)
    arguments = {}
    for pname, pvalue in request_arguments.items():
        try:
            arguments[pname] = value_resolver.resolve(pvalue)
        except ValueError: 
            pass

    try:
        command.update_arguments(arguments)
    except jolly.command.ArgumentException as e:
        return jolly.http.HttpResponseBadRequest({'error': str(e.problems.keys())})
    else:
        game = command.owner.game
        game.advance()

        db.dirty_all()
        db.store_object(game)
 
    return jolly.http.HttpResponseRedirect(doc_id)

@jolly.http.authenticate
@jolly.http.content_negotiate
def post_command(request, doc_id, *args, **kwargs):
    import jolly.command

    db = jolly.db.create_database()
    try:
        queue = db.restore_object(doc_id)
    except KeyError:
        return jolly.http.HttpResponseNotFound({'error': 'cannot restore'})

    if not isinstance(queue, jolly.command.CommandQueue):
        return jolly.http.HttpResponseNotFound({'error': 'bad type'})

    user = request.user
    if not user.is_owner(queue):
        return jolly.http.HttpResponseUnauthorized(settings.AUTHENTICATION_REALM)

    # Convert the data from XML/JSON to a Python dict
    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return jolly.http.HttpResponseBadRequest()

    value_resolver = import_object(settings.VALUE_RESOLVER)

    # Ensure that a valid template is present
    try:
	template = value_resolver.resolve(data['template'])
	if not isinstance(template, jolly.command.CommandTemplate):
            return jolly.http.HttpResponseBadRequest({'error': 'template'})
    except KeyError:
        return jolly.http.HttpResponseBadRequest({'error': 'template'})

    # Determine the parameters that have been set
    try:
        request_arguments = data['arguments']
    except KeyError:
        request_arguments = {}
    response_arguments = {}

    # Determine the time
    try:
        time = value_resolver.resolve(request_arguments['time'])
        response_arguments['time'] = time
        del request_arguments['time']
    except KeyError:
        response_arguments['time'] = None
    except ValueError:
        response_arguments['time'] = None
        del request_arguments['time']

    # Determine the issuer
    issuer = queue.owner

    # Determine the arguments
    arguments = {}
    for pname, pvalue in request_arguments.items():
        try:
            arguments[pname] = value_resolver.resolve(pvalue)
            response_arguments[pname] = arguments[pname]
        except ValueError: 
            pass

    command = jolly.command.Command(issuer, template, time, arguments)
    try:
        command.insert_into_queue(queue)
    except jolly.command.CommandException as e:
        return jolly.http.HttpResponseBadRequest({'error': str(e.problems.keys())})
    else:
        db.dirty(queue)
        db.store_object(queue)

    url_resolver = import_object(settings.URL_RESOLVER)
    return jolly.http.HttpResponseRedirect(url_resolver.get_url(command))

@jolly.http.authenticate
@jolly.http.content_negotiate
def post_breakpoint(request, *args, **kwargs):
    import jolly.core

    player_doc_id = request.GET['player']
    db = jolly.db.create_database()
    try:
        player = db.restore_object(player_doc_id)
    except KeyError:
        return jolly.http.HttpResponseNotFound({'error': 'cannot restore'})

    if not isinstance(player, jolly.core.Player):
        return jolly.http.HttpResponseNotFound({'error': 'bad type'})

    user = request.user
    if not user.is_owner(player):
        return jolly.http.HttpResponseUnauthorized(settings.AUTHENTICATION_REALM)

    # Convert the data from XML/JSON to a Python dict
    try:
        data = json.loads(request.raw_post_data)
    except ValueError:
        return jolly.http.HttpResponseBadRequest()

    value_resolver = import_object(settings.VALUE_RESOLVER)

    breakpoint_types = dict((getattr(v, 'action_type'), v) 
                           for v in dict((n, getattr(jolly.breakpoint, n)) 
	                   for n in dir(jolly.breakpoint)).values() 
		               if isinstance(v, type) 
		               and hasattr(v, 'action_type'))
    try:
	type_ = breakpoint_types.setdefault(data['action-type'],
		                            jolly.breakpoint.BreakPoint)
	import inspect
	args = inspect.getargspec(type_.__init__).args[2:]
	parsed_args = {}
	for arg in args:
	    parsed_args[arg] = value_resolver.resolve(data[arg.replace('_', '-')])
	breakpoint = type_(player, **parsed_args)
    except KeyError as exc:
        return jolly.http.HttpResponseBadRequest({'error': str(exc)})

    player.breakpoints.append(breakpoint)
    db.dirty(player)
    db.store_object(player)

    url_resolver = import_object(settings.URL_RESOLVER)
    return jolly.http.HttpResponseRedirect(url_resolver.get_url(breakpoint))

@jolly.http.authenticate
@jolly.http.content_negotiate
def delete_breakpoint(request, doc_id, *args, **kwargs):
    import jolly.breakpoint

    db = jolly.db.create_database()
    try:
        breakpoint = db.restore_object(doc_id)
    except KeyError:
        return jolly.http.HttpResponseNotFound({'error': 'cannot restore'})

    if not isinstance(breakpoint, jolly.breakpoint.BreakPoint):
        return jolly.http.HttpResponseNotFound({'error': 'bad type'})

    user = request.user
    if not user.is_owner(breakpoint):
        return jolly.http.HttpResponseUnauthorized(settings.AUTHENTICATION_REALM)

    try:
	breakpoint.owner.breakpoints.remove(breakpoint)
    except ValueError:
        pass # DELETE is idempotent
    else:
	db.delete_object(doc_id)
        game = breakpoint.owner.game
        game.advance()

        db.dirty_all()
        db.store_object(game)

    url_resolver = import_object(settings.URL_RESOLVER)
    return jolly.http.HttpResponseRedirect('/{0}'.format(url_resolver.get_query_url_by_name('breakpoints', {'player': db.get_doc_id(breakpoint.owner)})))
