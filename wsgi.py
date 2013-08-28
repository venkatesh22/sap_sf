# imports
import os
import sys
import settings
#activate_this = os.path.join("/home/ubuntu/venv", "bin/activate_this.py")
#execfile(activate_this, dict(__file__=activate_this))
# Sets the path for WSGI to read the Django app properly
sys.path.append('/home/ubuntu/sap_sf/')
#sys.path.append('/home/ubuntu/gconnect-sap/sap_sync/')

# "djangoproj" should be the subdirectory within your root where the Django project's root is.
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "/home/ubuntu/sap_sf.settings")
os.environ['PATH'] = '/home/ubuntu/venv/bin:' + os.environ['PATH']
# another import--should really be at the top, but whatever
import django.core.handlers.wsgi

djangoapplication = django.core.handlers.wsgi.WSGIHandler()


# DotCloud WSGI stack sets the SCRIPT_NAME variable in the WSGI environment. This variable is required by some frameworks, but it confuses Django. Therefore, our wsgi.py wrapper unsets the variable to avoid unwanted side effects.
def application(environ, start_response):
        if 'SCRIPT_NAME' in environ:
                del environ['SCRIPT_NAME']
        return djangoapplication(environ, start_response)

