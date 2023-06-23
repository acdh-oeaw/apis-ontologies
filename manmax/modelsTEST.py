from apis_core.apis_entities.models import TempEntityClass
from apis_core.apis_relations.models import Property, Triple
from apis_core.utils import caching


import reversion

from typing import Union, Iterator, Iterable


GENERIC = "Generic"
CONCEPTUAL_OBJECTS = "Conceptual Objects"
PHYSICAL_OBJECTS = "Physical Objects"
ROLE_ORGANISATIONS = "Roles/Organisations"
LIFE_FAMILY = "Life/Family"
ART = "Art"
MUSIC = "Music"
ARMOURING = "Armouring"
PRINT = "Print"
OTHER = "Other"



ENTITY = "Entities"
STATEMENT = "Statements"


group_order = [

    GENERIC,
    CONCEPTUAL_OBJECTS,
    PHYSICAL_OBJECTS,
    LIFE_FAMILY,
    ROLE_ORGANISATIONS,
    ART,
    MUSIC,
    ARMOURING,
    PRINT,
    OTHER,
]

@reversion.register(follow=["tempentityclass_ptr"])
class Person(TempEntityClass):
    __entity_group__ = GENERIC
    __entity_type__ = ENTITY

@reversion.register(follow=["tempentityclass_ptr"])
class Place(TempEntityClass):
    __entity_group__ = GENERIC
    __entity_type__ = ENTITY


def build_property(
    name: str,
    name_reverse: str,
    subj_class: Property,
    obj_class: Union[Property, Iterator[Property]],
):
    """Convenience function for defining properties"""
    
    prop = Property.objects.get_or_create(
        name=name,
        name_reverse=name_reverse,
    )[0]
    
    print(name)
    prop.subj_class.clear()
    if isinstance(subj_class, Iterable):
        #print(subj_class)
        for sclass in subj_class:
            
            prop.subj_class.add(caching.get_contenttype_of_class(sclass))
            #print('error here')
    else:
        prop.subj_class.add(caching.get_contenttype_of_class(subj_class))
        
    prop.obj_class.clear()
    if isinstance(obj_class, Iterable):
        print(obj_class)
        for oclass in set(obj_class):
            print(oclass)
            prop.obj_class.add(caching.get_contenttype_of_class(oclass))
    else:
        prop.obj_class.add(caching.get_contenttype_of_class(obj_class))
    return prop

def construct_properties():
    # Generic Statement attached to Factoid
    
    
    person_born_in_place = build_property("was born in place", "has_place_of_birth", Person, Place)