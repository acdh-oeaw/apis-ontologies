# Template for file for local Django settings.
#
# To be used as basis for new settings files for local development,
# to store keys/passwords, values for development databases etc.
#
# Resulting local settings files are not meant to be committed/versioned.

from .server_settings import *

# SECRET_KEY must not be empty or Django won't run.
# Use a unique, unpredictable value,
# see: https://docs.djangoproject.com/en/4.0/ref/settings/#secret-key
SECRET_KEY = ""

# DEBUG, DEV_VERSION are optional variables which override defaults
# for production environments set in server_settings.py
# Comment them out if/when they are not needed.
DEBUG = True
DEV_VERSION = False

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