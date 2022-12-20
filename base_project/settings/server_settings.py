"""
Django main settings.

Changes to this file affect both deployed and locally run applications.

Code for this app is public. Make sure not to include any secrets/keys/other
sensitive information; use CI/CD variables instead!

To override configurations for local development, use a local settings file
(see local_settings_template.py) or local env variables as needed.
"""
from apis.settings.base import *
import re
import dj_database_url
import os

# General Django settings

# SECRET_KEY must not be empty or Django won't run.
# Use a unique, unpredictable value,
# see: https://docs.djangoproject.com/en/4.0/ref/settings/#secret-key
SECRET_KEY = ""

# DEBUG, DEV_VERSION must not be set True for production. Leave as-is.
DEBUG = False
DEV_VERSION = False

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    # "project-name.subdomain.oeaw.ac.at",  # add URI of website where app gets deployed
]

if "ALLOWED_HOSTS" in os.environ:
    try:
        ALLOWED_HOSTS = re.sub(r"https?://", "", os.environ.get("ALLOWED_HOSTS")).split(
            ","
        )
    except Exception as e:
        print(e)
        print(
            "Invalid environment variable value for ALLOWED_HOSTS.\n"
            "Falling back to default ALLOWED_HOSTS defined in settings."
        )

DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

# STATICFILES_DIRS = [BASE_DIR + "/member_images"]


# Django third-party apps, plugins

# Django Allow CIDR
# see https://github.com/mozmeao/django-allow-cidr
# address '10.0.0.0/8' needs to be allowed for service health checks
ALLOWED_CIDR_NETS = ["10.0.0.0/8", "127.0.0.0/8"]

# Django REST framework permissions
# see https://www.django-rest-framework.org/api-guide/permissions/
REST_FRAMEWORK.update(
    {
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    }
)

# drf-spectacular
# see https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS.update(
    {"COMPONENT_SPLIT_REQUEST": True, "COMPONENT_NO_READ_ONLY_REQUIRED": True}
)

# Haystack
# see https://django-haystack.readthedocs.io/en/v2.1.0/settings.html
# HAYSTACK_DEFAULT_OPERATOR defaults to 'AND', can be set to 'OR'
# HAYSTACK_DEFAULT_OPERATOR = 'OR'


# Project-specific settings

# APIS_BASE_URI needs to be set to full website address where app is hosted.
# Used to construct URLs to individual data items (for access via APIS api),
# should be overridden for local development! Needs to end with a trailing slash.
# e.g. "https://my-project.subdomain.oeaw.ac.at/"
APIS_BASE_URI = ""
REDMINE_ID = ""
MAIN_TEXT_NAME = ""

LANGUAGE_CODE = "de"

APIS_RELATIONS_FILTER_EXCLUDE.append("annotation")

FEATURED_COLLECTION_NAME = "FEATURED"
APIS_DEFAULT_COLLECTION = "manual"
APIS_LOCATED_IN_ATTR = ["located in"]
BIRTH_REL_NAME = "geboren in"
DEATH_REL_NAME = "verstorben in"
# APIS_OEBL_BIO_COLLECTION = "ÖBL Biographie"


# Other APIS apps/modules to use with this app

APIS_AUTOCOMPLETE_SETTINGS = "apis_ontology.settings.autocomplete_settings"

APIS_SKOSMOS = {
    "url": os.environ.get("APIS_SKOSMOS", "https://vocabs.acdh-dev.oeaw.ac.at"),
    "vocabs-name": os.environ.get("APIS_SKOSMOS_THESAURUS", "apisthesaurus"),
    "description": "Thesaurus of the APIS project. Used to type entities and relations.",
}

# APIS_COMPONENTS.append('deep learning')

# APIS_BLAZEGRAPH = (
# 'https://blazegraph.herkules.arz.oeaw.ac.at/metaphactory-play/sparql',
# 'metaphactory-play',
# 'KQCsD24treDY'
# )

INSTALLED_APPS.append("apis_highlighter")
