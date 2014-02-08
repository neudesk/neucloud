import logging
import os
import sys
import django.core.handlers.wsgi
from django.conf import settings

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/var/www/neucloud/.venv/local/lib/python2.7/site-packages')

# Add this file path to sys.path in order to import settings
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'openstack_dashboard.settings'
sys.stdout = sys.stderr

DEBUG = False

activate_env=os.path.expanduser("/var/www/neucloud/.venv/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

application = django.core.handlers.wsgi.WSGIHandler()

