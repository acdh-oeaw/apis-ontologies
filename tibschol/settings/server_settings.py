import os
import re

import dj_database_url
from apis.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# REDMINE_ID = "14590"
APIS_LIST_VIEWS_ALLOWED = False
APIS_DETAIL_VIEWS_ALLOWED = False
FEATURED_COLLECTION_NAME = "FEATURED"
# MAIN_TEXT_NAME = "ÖBL Haupttext"
BIRTH_REL_NAME = "geboren in"
DEATH_REL_NAME = "verstorben in"
APIS_LOCATED_IN_ATTR = ["located in"]
APIS_BASE_URI = "https://tibschol.acdh-dev.oeaw.ac.at/"
# APIS_OEBL_BIO_COLLECTION = "ÖBL Biographie"

APIS_SKOSMOS = {
    "url": os.environ.get("APIS_SKOSMOS", "https://vocabs.acdh-dev.oeaw.ac.at"),
    "vocabs-name": os.environ.get("APIS_SKOSMOS_THESAURUS", "apisthesaurus"),
    "description": "Thesaurus of the APIS project. Used to type entities and relations.",
}

ALLOWED_HOSTS = re.sub(
    r"https?://",
    "",
    os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,paas.acdh-dev.oeaw.ac.at"),
).split(",")
# You need to allow '10.0.0.0/8' for service health checks.

ALLOWED_CIDR_NETS = ["10.0.0.0/8", "127.0.0.0/8"]

REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (
    # "rest_framework.permissions.DjangoModelPermissions",
    "rest_framework.permissions.IsAuthenticated",
    # "rest_framework.permissions.DjangoObjectPermissions",
    # use IsAuthenticated for every logged in user to have global edit rights
)

# HAYSTACK_DEFAULT_OPERATOR = "OR"

DEBUG = True
DEV_VERSION = False

SPECTACULAR_SETTINGS["COMPONENT_SPLIT_REQUEST"] = True
SPECTACULAR_SETTINGS["COMPONENT_NO_READ_ONLY_REQUIRED"] = True

DATABASES = {}

DATABASES["default"] = dj_database_url.config(conn_max_age=600)

MAIN_TEXT_NAME = "ÖBL Haupttext"

LANGUAGE_CODE = "de"

APIS_AUTOCOMPLETE_SETTINGS = "apis_ontology.settings.autocomplete_settings"

# STATICFILES_DIRS = [BASE_DIR + "/member_images"]

# APIS_COMPONENTS = ['deep learning']

# APIS_BLAZEGRAPH = ('https://blazegraph.herkules.arz.oeaw.ac.at/metaphactory-play/sparql', 'metaphactory-play', 'KQCsD24treDY')
# INSTALLED_APPS += ["apis_ontology"]

APIS_RELATIONS_FILTER_EXCLUDE += ["annotation", "annotation_set_relation"]

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from apis_ontology.filters import name_filter, instance_name_filter, work_name_filter

sentry_sdk.init(
    dsn="https://26617c9eabdc4fb7b54a8d8d2037c67d@o4504360778661888.ingest.sentry.io/4504360943484928",
    integrations=[
        DjangoIntegration(),
    ],
    environment="production",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)

APIS_RELATIONS_FILTER_EXCLUDE += ["annotation", "annotation_set_relation"]

APIS_ENTITIES = {
    "Instance": {
        "relations_per_page": 100,
        "search": ["name", "alternative_names", "tibschol_ref", "external_link"],
        "list_filters": {
            "name": {
                "method": instance_name_filter,
                "label": "Name or reference",
            },
        },
        "table_fields": [
            "id",
            "tibschol_ref",
            "name",
            "external_link",
        ],
    },
    "Person": {
        "relations_per_page": 100,
        "search": ["name", "alternative_names", "external_link"],
        "list_filters": {
            "name": {
                "method": name_filter,
                "label": "Name or reference",
            },
        },
        "table_fields": [
            "id",
            "name",
            "start_date_written",
            "end_date_written",
            "external_link",
        ],
    },
    "Work": {
        "relations_per_page": 100,
        "search": ["name", "alternative_names", "sde_dge_ref", "external_link"],
        "list_filters": {
            "name": {
                "method": work_name_filter,
                "label": "Name or reference",
            },
        },
        "table_fields": ["id", "name", "sde_dge_ref"],
    },
    "Place": {
        "relations_per_page": 100,
        "search": ["name", "alternative_names", "external_link"],
        "list_filters": {
            "name": {
                "method": name_filter,
                "label": "Name or reference",
            },
        },
        "table_fields": [
            "id",
            "name",
            "longitude",
            "latitude",
            "external_link",
        ],
    },
}

ONTOLOGY_DIR = os.path.dirname(os.path.dirname(__file__))
for template in TEMPLATES:
    template["DIRS"].append(os.path.join(ONTOLOGY_DIR, "templates"))
