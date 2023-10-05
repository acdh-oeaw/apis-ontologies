"""
Deletes properties that are no longer required
"""
import logging

from apis_core.apis_relations.models import Property, TempTriple, Triple
from apis_ontology.models import Instance, Person, Place, Work
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


def run():
    """see doctstring"""
    OLD_PROPS = ["father of", "mother of"]
    for p in OLD_PROPS:
        matches = Property.objects.filter(name__icontains=p)
        for m in matches:
            matches.delete()

    NEW_PROPS = [
        {
            "subj_class": Person.__name__,
            "name": "cites",
            "name_reverse": "is cited by",
            "obj_class": Work.__name__,
        },
        {
            "subj_class": Work.__name__,
            "name": "names",
            "name_reverse": "is named in",
            "obj_class": Person.__name__,
        },
        {
            "subj_class": Work.__name__,
            "name": "names",
            "name_reverse": "is named in",
            "obj_class": Work.__name__,
        },
    ]
    for p in NEW_PROPS:
        new_prop, _ = Property.objects.get_or_create(
            name=p["name"], name_reverse=p["name_reverse"]
        )
        new_prop.subj_class.add(ContentType.objects.get(model=p["subj_class"]))
        new_prop.obj_class.add(ContentType.objects.get(model=p["obj_class"]))
