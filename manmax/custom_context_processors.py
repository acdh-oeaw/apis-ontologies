from collections import defaultdict

from apis_core.helper_functions.caching import get_all_entity_classes
from apis_ontology.models import group_order


def get_entity_groups():
    entity_groups = defaultdict(lambda: defaultdict(list))
    for cls in get_all_entity_classes():
        group = getattr(cls, "__entity_group__", "Other")
        entity_type = getattr(cls, "__entity_type__", "Entity")
        entity_groups[group][entity_type].append((cls.__name__.lower(), cls._meta.verbose_name_plural.title(), cls.__doc__))
    return entity_groups



def grouped_menus(request):
    entity_groups = get_entity_groups()
    groups = {}
    for key in group_order:
        if len(entity_groups[key]) > 0:
            groups[key] = entity_groups[key]
    return {"entity_groups": groups, "request": request}

