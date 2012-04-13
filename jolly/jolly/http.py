"""Utilities for dealing with HTTP responses using the Django framework."""
import mimeparse
import json

from django.conf import settings
from django.http import (HttpResponse, HttpResponseNotAllowed, 
                         HttpResponseRedirect, HttpResponseBadRequest,
                         HttpResponseNotFound, HttpResponseForbidden)
from django.utils.importlib import import_module

import jolly.util

__all__ = ['HttpResponse', 'HttpResponseNotAllowed', 'HttpResponseUnauthorized',
           'HttpResponseRedirect', 'HttpResponseBadRequest', 
           'MultiResponse', 'HttpResponseNotFound', 'HttpResponseForbidden',
           'MethodDispatcher', 'authenticate', 'content_negotiate']

def authenticate(view):
    def wrapper(request, *args, **kwargs):
        import jolly.core
        request.user = jolly.core.User('anonymous', '', '')

        if 'HTTP_AUTHORIZATION' in request.META:
            authentication = request.META.get('HTTP_AUTHORIZATION', '')
            auth_method, auth = authentication.split(' ', 1)
            if 'basic' == auth_method.lower():
                username, password = auth.strip().decode('base64').split(':', 1)
                db = jolly.util.import_object(settings.DB)
                users = db.restore_view(settings.QUERY_VIEWS['login'], username)
                if len(users) == 1:
                    if users[0].authenticate(password):
                        request.user = users[0]
        return view(request, *args, **kwargs)
    return wrapper

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

    def __init__(self, realm):
        HttpResponse.__init__(self)
        self['WWW-Authenticate'] = 'Basic realm={realm}'.format(realm=realm)


class MultiResponse(object):
    """Post-process view output based on HTTP Content-Type."""

    def __init__(self, method_map, charset):
        self.methods = method_map
        self.charset = charset

    def __call__(self, view_func):
        def wrapper(request, *args, **kwargs):
            content_type = mimeparse.best_match(self.methods.keys(),
                                                request.META['HTTP_ACCEPT'])
            method = self.methods[content_type]
            content_type = "{content_type}; charset={charset}".format(content_type=content_type, charset=self.charset)
            view_result = view_func(request, *args, **kwargs)

            if isinstance(view_result, HttpResponse):
                content = method(view_result._container[0] if view_result._is_string else view_result._container)
                response = view_result
                response.content = content
                response['Content-Type'] = content_type
            else:
                content = method(view_result)
                response = HttpResponse(content, content_type=content_type)
            return response
        return wrapper


class MethodDispatcher(object):
    """Dispatch to different methods based on HTTP verb."""

    def __init__(self, method_map):
        self.methods = {}
        self.default = None
        for k, v in method_map.items():
            if k == '__default__':
                self.default = v
            elif isinstance(k, basestring):
                self.methods[k] = v
            else:
                for e in k:
                    self.methods[e] = v
    
    def __call__(self, request, *args, **kwargs):
        view_func = self.methods.get(request.method, self.default)
        if view_func:
            return view_func(request, *args, **kwargs)
        return HttpResponseNotAllowed(self.methods.keys())

content_negotiate = MultiResponse(
    {'application/json': json.dumps,
     'text/plain': str},
    'utf-8')
