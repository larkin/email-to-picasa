"""
settings.py

Config stuff.

"""

import os

from secret_keys import CSRF_SECRET_KEY, SESSION_KEY

DEBUG_MODE = False

REQUEST_SCOPE = 'https://picasaweb.google.com/data/'
RETURN_URL = 'https://email-to-picasa.appspot.com/auth/auth_return'
# set return url to development version if on dev server.
if 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'] \
                                         .startswith('Dev'):
    RETURN_URL = 'http://email-to-picasa.pete-richards.com:8080/auth/auth_return'

# Auto-set debug mode based on App Engine dev environ
if 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'] \
                                         .startswith('Dev'):
    DEBUG_MODE = True

DEBUG = DEBUG_MODE
# Set secret keys for CSRF protection
SECRET_KEY = CSRF_SECRET_KEY
CSRF_SESSION_KEY = SESSION_KEY

CSRF_ENABLED = True


