import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'test.settings'
from django.conf import settings
from jolly.util import import_object
value_resolver = import_object(settings.VALUE_RESOLVER)
