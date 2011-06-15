"""Utilities for converting between URLs and objects."""

import re, inspect, fractions
from sqlalchemy.orm import join
from django.core.urlresolvers import get_resolver, NoReverseMatch
from django.conf.urls.defaults import url
from jolly.utils import uncamelize, unnest

__all__ = ['build_urls', 'evaluate_argument', 
           'get_url', 'get_object', 'get_object_list']


def build_urls(klass, key_name='id', key_pattern=r'\d+', plural_too=True):
    """Build the url pattern(s) for the given class."""
    name = uncamelize(klass.__name__, '-')
    plural_name = '%ss' % name
    singular = url(r'^%s/(?P<%s>%s)/$' % (plural_name, key_name, key_pattern),
                    'detail', {'klass': klass}, name=name)
    if plural_too:
        plural = url(r'^%s/$' % plural_name, 
                      'showall', {'klass': klass}, name=plural_name)
        return singular, plural
    return singular,

def evaluate_argument(arg, session, urlconf):
    """Determine the value of the given argument."""
    try:
        return fractions.Fraction(arg) # number
    except ValueError:
        pass
    try:
        return get_object(arg, session, urlconf) # object from url
    except: # catch all exceptions
        return arg # string default

def get_url(object, urlconf):
    """Retrieve the URL of an object."""
    view_name, pattern, possibilities = _get_possible_urls(object.__class__, urlconf)
    
    for result, params in possibilities:
        kwargs = {}
        if view_name in params:
            kwargs[view_name] = str(object)
            params.remove(view_name)
        for p in reversed(params):
            o, value, x = _find_attribute(object, p)
            if value: kwargs[p] = value
        if len(kwargs) < len(params): continue
        candidate = result % kwargs
        if re.search(u'^%s' % pattern, candidate, re.UNICODE):
            return candidate
    raise NoReverseMatch("Reverse for '{view_name}' with keyword arguments '{kwargs} not found.".format(view_name=view_name, kwargs=kwargs))


def get_object(url, session, urlconf):
    """Retrieve an object by URL."""
    return _get_by_url(url, session, urlconf, True)


def get_object_list(url, session, urlconf):
    """Retrieve a list of objects by URL."""
    return _get_by_url(url, session, urlconf, False)


### The following functions are helpers.

def _get_view_name(class_):
    """Determine the name of a view based on the name of a class."""
    return uncamelize(class_.__name__)


def _get_possible_urls(class_, urlconf):
    """Return the view_name, pattern and possible URLs for a given class."""
    resolver = get_resolver(urlconf)
    for view_name in (_get_view_name(c) for c in class_.__mro__):
        all = resolver.reverse_dict.getlist(view_name)
        if all: 
            possibilities, pattern = all[0]
            # sort in descending order of number of params
            possibilities.sort(cmp=lambda x, y: len(y[1]) - len(x[1]))
            return view_name, pattern, possibilities
    raise NoReverseMatch("Reverse for '{view_name}' not found.".format(view_name=get_view_name(class_)))


def _find_attribute(object, attr):
    """Find the attr attribute recursively in object or its attributes.
       Note: an underscore in attr may indicate that the desired value
             is the attribute named by the string after the underscore in the 
             attribute named by the string before the underscore.
             e.g. attr = 'game_id' may indicate that the desired value is
                  object.game.id
       Returns (object attribute found in, the attribute, the attribute name)"""
    if hasattr(object, attr):
        return object, getattr(object, attr), attr
    try:
        # the attribute might be on a subobject as specified in the docstring.
        uindex = attr.index('_')
        subobject = unnest(getattr(object, attr[:uindex]))
        return subobject, getattr(object, attr[uindex+1:]), attr[uindex+1:]
    except (ValueError, AttributeError):
        pass # the attribute is not on a subobject
    # look for the attribute within object's attributes recursively
    for subobject in [o for o in dir(object) if not callable(o)]:
        o, value, subattr = _find_attribute(subobject, attr)
        if value: return o, value, subattr
    return None, None, None

# TODO: move this to db functions
def _build_object_query(session, class_, **kwargs):
    """Create an SQLAlchemy query for objects of type 'class_' filtering based
       on the provided kwargs.
       Note: there is required to be at least row in the database for type
             'class_'"""
    object = session.query(class_).first()

    query = session.query(class_)
    selectables, filters = [class_], []
    for k, v in kwargs.iteritems():
        o, x, a = _find_attribute(object, k)
        selectables.append(type(o))
        filters.append((getattr(type(o), a), v))
    if filters:
        query = query.select_from(join(*selectables))
        for f, v in filters:
            query = query.filter(f == v)
    return query

# TODO: move this to persistance functions
def _build_object(factory, **kwargs):
    """Use a factory function and kwargs to create an object."""
    return factory(**dict((k, v) for k, v in kwargs.iteritems() if k in inspect.getargspec(factory).args))


def _get_by_url(url, session, urlconf, individual=True):
    """Retrieve an object or list by URL."""
    x, y, kwargs = get_resolver(urlconf).resolve(url)

    # build our using the provided factory
    if 'factory' in kwargs:
        return _build_object(kwargs['factory'], **kwargs)
    # retrieve from the database
    else:
        class_ = kwargs['klass']
        del kwargs['klass']
        query = _build_object_query(session, class_, **kwargs)
        result = query.one() if individual else query.all()
    return result
