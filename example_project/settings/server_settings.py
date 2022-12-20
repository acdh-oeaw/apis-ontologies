from apis.settings.base import *
import re
import dj_database_url
import os

# General Django settings

# DEV_VERSION must not be set True for production. Leave as-is.
# Use env variables or local settings file to override for local development.
DEBUG = False
DEV_VERSION = False

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    # host name(s) your app will be available on (subdomain and domain name
    # only, without protocol or trailing slash), e.g.
    # "my-project.some-subdomain.oeaw.ac.at",
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


# Project-specific settings

# APIS_BASE_URI is used to construct URIs to resources (allows access to
# individual objects via the API). Should be set to full web address
# where app is hosted, needs to end with a trailing slash. Example:
# APIS_BASE_URI = "https://my-project.subdomain.oeaw.ac.at/"
APIS_BASE_URI = ""
REDMINE_ID = ""
MAIN_TEXT_NAME = ""

LANGUAGE_CODE = "de"
TIME_ZONE = "CET"

APIS_AUTOCOMPLETE_SETTINGS = "apis_ontology.settings.autocomplete_settings"

APIS_RELATIONS_FILTER_EXCLUDE.append("annotation")

APIS_DEFAULT_COLLECTION = "manual"

# To add new template files or to override existing shared templates, point
# CUSTOM_TEMPLATES_DIR to a custom templates directory within your app. E.g.
# CUSTOM_TEMPLATES_DIR = "templates"
# Otherwise, leave set to None.
CUSTOM_TEMPLATES_DIR = None

if CUSTOM_TEMPLATES_DIR:
    ONTOLOGY_DIR = os.path.dirname(os.path.dirname(__file__))
    for item in TEMPLATES:
        item["DIRS"].append(os.path.join(ONTOLOGY_DIR, CUSTOM_TEMPLATES_DIR))


# Use APIS_ENTITIES to configure display settings and functionality for
# individual fields of any entity class in models.py. Example:
APIS_ENTITIES = {
    "MyEntity": {
        "search": [
            "field_1",
            "field_2",
        ],
        "form_order": [  # field order in web form (create/edit view)
            "field_3",
            "field_1",
            "field_2",
        ],
        "table_fields": [  # fields to display as table columns (list view)
            "field_1",
            "field_3",
        ],
        "additional_cols": [  # fields by which list table can be extended
            "field_2",
        ],
        "list_filters": [  # fields by which to allow filtering of list table
            {"field_1": {"method": "name_label_filter"}},
            "field_2",
        ],
    },
}
