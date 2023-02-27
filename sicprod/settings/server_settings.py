from apis.settings.base import *
import re
import dj_database_url
import os


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
APIS_BASE_URI = "https://sicprod.acdh.oeaw.ac.at/"
# APIS_OEBL_BIO_COLLECTION = "ÖBL Biographie"

APIS_SKOSMOS = {
    "url": os.environ.get("APIS_SKOSMOS", "https://vocabs.acdh-dev.oeaw.ac.at"),
    "vocabs-name": os.environ.get("APIS_SKOSMOS_THESAURUS", "apisthesaurus"),
    "description": "Thesaurus of the APIS project. Used to type entities and relations.",
}

APIS_BIBSONOMY = [{
   'type': 'zotero', #or zotero
   'url': 'https://api.zotero.org', #url of the bibsonomy instance or zotero.org
   'user': os.environ.get('APIS_BIBSONOMY_USER'), #for zotero use the user id number found in settings
   'API key': os.environ.get('APIS_BIBSONOMY_PASSWORD'),
   'group': '4853010'
}]
APIS_BIBSONOMY_FIELDS = ['self']
APIS_AUTOCOMPLETE_SETTINGS = "apis_ontology.settings.autocomplete_settings"

ALLOWED_HOSTS = re.sub(
    r"https?://",
    "",
    os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,sicprod.acdh-dev.oeaw.ac.at"),
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

#DATABASES["default"] = dj_database_url.parse(os.environ['DATABASE_LOCAL'], conn_max_age=600)
DATABASES["default"] = dj_database_url.config(conn_max_age=600)

MAIN_TEXT_NAME = "ÖBL Haupttext"

LANGUAGE_CODE = "de"

INSTALLED_APPS += ["apis_bibsonomy"]

#STATICFILES_DIRS = [BASE_DIR + "/member_images"]

# APIS_COMPONENTS = ['deep learning']

# APIS_BLAZEGRAPH = ('https://blazegraph.herkules.arz.oeaw.ac.at/metaphactory-play/sparql', 'metaphactory-play', 'KQCsD24treDY')


APIS_RELATIONS_FILTER_EXCLUDE += ["annotation", "annotation_set_relation"]

#INSTALLED_APPS.append("apis_highlighter")
APIS_ENTITIES = {
    "Salary": {
        "search": ["name"]
    },
    "Function": {
        "search": ["name", "alternative_label"]
    },
    "Court": {
        "search": ["name", "alternative_label"]
    },
    "Place": {
        "merge": True,
        "search": ["name", "alternative_label"],
        "form_order": ["name", "kind", "lat", "lng", "status", "collection"],
        "table_fields": ["name"],
        "additional_cols": ["id", "lat", "lng", "part_of"],
        "list_filters": [
            {"name": {"method": "name_label_filter"}},
            {"collection": {"label": "Collection"}},
            {"kind": {"label": "Kind of Place"}},
            "related_entity_name",
            "related_relationtype_name",
            "lat",
            "lng",
        ],
    },
    "Person": {
        "merge": True,
        "search": ["name", "first_name", "alternative_label"],
        "form_order": [
            "first_name",
            "name",
            "start_date_written",
            "end_date_written",
            "profession",
            "status",
            "collection",
        ],
        "table_fields": [
            "name",
            "first_name",
            "start_date_written",
            "end_date_written",
            "alternative_label",
            "status",
        ],
        "additional_cols": ["id", "profession", "gender"],
        "list_filters": [
            "name",
            {"gender": {"label": "Gender"}},
            {"start_date": {"label": "Date of Birth"}},
            {"end_date": {"label": "Date of Death"}},
            {"profession": {"label": "Profession"}},
            {"title": {"label": "Title"}},
            {"collection": {"label": "Collection"}},
            "related_entity_name",
            "related_relationtype_name",
        ],
    },
    "Institution": {
        "merge": True,
        "search": ["name", "alternative_label"],
        "form_order": [
            "name",
            "start_date_written",
            "end_date_written",
            "kind",
            "status",
            "collection",
        ],
        "additional_cols": [
            "id",
            "kind",
        ],
        "list_filters": [
            {"name": {"label": "Name or label of institution"}},
            {"kind": {"label": "Kind of Institution"}},
            {"start_date": {"label": "Date of foundation"}},
            {"end_date": {"label": "Date of termination"}},
            {"collection": {"label": "Collection"}},
            "related_entity_name",
            "related_relationtype_name",
        ],
    },
    "Work": {
        "merge": True,
        "search": ["name"],
        "additional_cols": [
            "id",
            "kind",
        ],
        "list_filters": [
            {"name": {"label": "Name of work"}},
            {"kind": {"label": "Kind of Work"}},
            {"start_date": {"label": "Date of creation"}},
            {"collection": {"label": "Collection"}},
            "related_entity_name",
            "related_relationtype_name",
        ],
    },
    "Event": {
        "merge": True,
        "search": ["name", "alternative_label"],
        "additional_cols": [
            "id",
        ],
        "list_filters": [
            {"name": {"label": "Name of event"}},
            {"kind": {"label": "Kind of Event"}},
            {"start_date": {"label": "Date of beginning"}},
            {"end_date": {"label": "Date of end"}},
            {"collection": {"label": "Collection"}},
            "related_entity_name",
            "related_relationtype_name",
        ],
    },
}
