import os
import sys

sys.path.insert(0, "/home/hostinger_username/root_folder/krs_mekbat")
os.environ['DJANGO_SETTINGS_MODULE'] = 'krs_mekbat.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()