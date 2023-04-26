"""
Template for file for local Django settings.

To be used as basis for new settings file(s) for local development,
to store keys/passwords, configs for development databases etc.

Resulting local settings files are not meant to be committed/versioned.
"""
from .server_settings import *

# DEBUG, DEV_VERSION are optional variables which override defaults for
# production environments which are set in server_settings.py
# DEBUG = True
# DEV_VERSION = False

# Database settings for MySQL / MariaDB
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "",
        "USER": "",
        "PASSWORD": "",
        "HOST": "localhost",  # use "localhost" or the IP address your DB is hosted on
        "PORT": "3306",
    }
}

# For local development, override project-specific APIS_BASE_URI
APIS_BASE_URI = ""
