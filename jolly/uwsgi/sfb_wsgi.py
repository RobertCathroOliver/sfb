import os
import sys
sys.path.append('/home/robert/projects/jolly/src/jolly')

os.environ['DJANGO_SETTINGS_MODULE'] = 'test.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
