request
URL dispatcher

to GET/POST/PUT/DELETE handler or 404

from functools import update_wrapper
import mimeparse

class MultiResponse(object):
    def __init__(self, encoder_mapping):
	self._encoder_mapping = encoder_mapping
    def __call__(self, view_func):
	def wrapper(request, *args, **kwargs):
	    result = view_func(request, *args, **kwargs)
	    content_type = mimeparse.best_match(self._encoder_mapping.keys(),
		                                request.META['HTTP_ACCEPT'])
	    response = self._encoder_mapping[content_type](result)
	    return HttpResponse(response, content_type=content_type)
        update_wrapper(wrapper, view_func)
	return wrapper

content_negotiate = MultiResponse({'xml' : to_xml, 'json' : to_json })


@content_negotiate
def public_get_handler(request):
    id_ = request.path

    # retrieve the relevant information
    try:
        object = sfb.persist.load(id_)
    except KeyError:
        raise Http404

    result = sfb.canonize(object, public=True)
    return result


@content_negotiate
def private_get_handler(request):
    id_ = request.path

    # retrieve the relevant information
    try:
        object = sfb.persist.load(id_)
    except KeyError:
        raise Http404

    # determine permissions
    if request.user.owns(object):
        result = sfb.canonize(object, public=False)
    else:
        raise HttpPermissionDenied

    return result
