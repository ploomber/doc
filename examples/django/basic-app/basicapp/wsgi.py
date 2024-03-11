"""
WSGI config for basicapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "basicapp.settings")


# allow serving static files in development mode (ok for low-traffic sites)
application = StaticFilesHandler(get_wsgi_application())

# if you encounter performance issues, you can use a separate server for static files
# and do:
# application = get_wsgi_application()
