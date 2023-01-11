# Template for file for local Django settings.
#
# To be used as basis for new settings files for local development,
# to store keys/passwords, values for development databases etc.
#
# Resulting local settings files are not meant to be committed/versioned.

from .server_settings import *

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


# Bibsonomy example settings
APIS_BIBSONOMY = [{
    'type': 'zotero',
    'url': 'https://api.zotero.org/',
    'user': 'exmaple_user_id', # fill in the API user ID, not the user-name
    'API key': 'example_key',
}]
# Zotero example settings (note that code-wise the module and settings are 
# called bibsonomy eventhough they also support zotero)
APIS_BIBSONOMY = [{
    'type': 'bibsonomy',
    'url': 'https://www.bibsonomy.org/',
    'user': 'example_user',
    'API key': 'example_key',
}]
# then append the bibsonomy module:
INSTALLED_APPS.append("apis_bibsonomy")
