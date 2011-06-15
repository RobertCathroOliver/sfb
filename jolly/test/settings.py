# Django settings for mysite project.

DEBUG = True

DATABASE = {
    'NAME': 'sfb',
    'SERIALIZER': 'jolly.db.serializer',
    'DESERIALIZER': 'jolly.db.deserializer',
    'POST_PROCESS': 'jolly.db.update_serializer',
}

QUERY_VIEWS = {
    'jolly.core.Player': 'query/players',
    'jolly.core.Game': 'query/games',
    'jolly.core.User': 'query/users',
    'jolly.breakpoint.BreakPoint': 'query/breakpoints',
    'login': 'login/by_name',
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = '74u8i9*gg0z2xglq#62j1x6d$*5k-pa-pyfz3-^fb12*m3ja4e'

AUTHENTICATION_REALM = 'sfb'

IDENTIFIER = 'sfb.config.identifier'
REGISTRY = 'sfb.registry'
SEQUENCE_OF_PLAY = 'sfb.chrono.SOP'
RANDOMIZER = 'sfb.config.choice'
VALUE_RESOLVER = 'sfb.config.value_resolver'

ROOT_URLCONF = 'sfb.urls'

URL_RESOLVER = 'sfb.config.urlresolver'
OUTPUT_CONVERTER = 'sfb.config.out'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
)
TEMPLATE_DIRS = (
    "C:/Users/rcathro-oliver/Documents/jolly/static",
)
