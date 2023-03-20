from collections.abc import Iterable
from dataclasses import dataclass
from typing import Union, Iterator

import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
from apis_core.apis_entities.models import TempEntityClass
from apis_core.apis_relations.models import Property
from apis_core.helper_functions import caching

BASE_ENTITIES = "Base Entities"
BASE_STATEMENTS = "Base Statements"
ART_ENTITIES = "Art Entities"
ART_STATEMENTS = "Art Statements"
MUSIC_ENTITIES = "Music Entities"
MUSIC_STATEMENTS = "Music Statements"
OTHER = "Other"

group_order = [BASE_ENTITIES, BASE_STATEMENTS, ART_ENTITIES, ART_STATEMENTS, MUSIC_ENTITIES,  MUSIC_STATEMENTS, OTHER]



@reversion.register(follow=["tempentityclass_ptr"])
class Person(TempEntityClass):
    __entity_group__ = BASE_ENTITIES

    

@reversion.register(follow=["tempentityclass_ptr"])
class Location(TempEntityClass):
    __entity_group__ = BASE_ENTITIES

@reversion.register(follow=["tempentityclass_ptr"])
class Organisation(TempEntityClass):
    __entity_group__ = BASE_ENTITIES

@reversion.register(follow=["tempentityclass_ptr"])
class GenericWork(TempEntityClass):
    __entity_group__ = BASE_ENTITIES

@reversion.register(follow=["tempentityclass_ptr"])
class GenericStatement(TempEntityClass):
    __entity_group__ = BASE_STATEMENTS



# Generic Work subtypes

@reversion.register(follow=["tempentityclass_ptr"])
class MusicWork(GenericWork):
    __entity_group__ = MUSIC_ENTITIES

@reversion.register(follow=["tempentityclass_ptr"])
class ArtWork(GenericWork):
    __entity_group__ = ART_ENTITIES


# Generic Statements

@reversion.register(follow=["tempentityclass_ptr"])
class Naming(GenericStatement):
    __entity_group__ = BASE_STATEMENTS
    
    forename = models.CharField(max_length=200, blank=True, verbose_name="First Name", help_text="(forename) contains a forename, given or baptismal name.")
    surname = models.CharField(max_length=200, blank=True, help_text="(surname) contains a family (inherited) name, as opposed to a given, baptismal, or nick name.")
    role_name = models.CharField(max_length=200, blank=True, help_text="(role name) contains a name component which indicates that the referent has a particular role or position in society, such as an official title or rank.")
    add_name = models.CharField(max_length=200, blank=True, help_text="(additional name) contains an additional name component, such as a nickname, epithet, or alias, or any other descriptive phrase used within a personal name.")


@reversion.register(follow=["tempentityclass_ptr"])
class Birth(GenericStatement):
    __entity_group__ = BASE_STATEMENTS

@reversion.register(follow=["tempentityclass_ptr"])
class Death(GenericStatement):
    __entity_group__ = BASE_STATEMENTS

@reversion.register(follow=["tempentityclass_ptr"])
class Election(GenericStatement):
    __entity_group__ = BASE_STATEMENTS
    position = models.CharField(max_length=200, blank=True, verbose_name="Position elected to")

@reversion.register(follow=["tempentityclass_ptr"])
class Membership(GenericStatement):
    __entity_group__ = BASE_STATEMENTS
    role = models.CharField(blank=True, max_length=500)

@reversion.register(follow=["tempentityclass_ptr"])
class ParentalRelation(GenericStatement):
    __entity_group__ = BASE_STATEMENTS
    PARENTAL_TYPES = (("mother", "Mother"), ("father", "Father"), ("unknown", "Unknown"), )
    parental_type = models.CharField(max_length=9, choices=PARENTAL_TYPES, blank=True, verbose_name="parental types")

@reversion.register(follow=["tempentityclass_ptr"])
class Payment(GenericStatement):
    __entity_group__ = BASE_STATEMENTS
    amount = models.IntegerField(blank=True)
    payment_for = models.CharField(blank=True, max_length=500)

@reversion.register(follow=["tempentityclass_ptr"])
class Order(GenericStatement):
    """An order given by someone to do something"""
    __entity_group__ = BASE_STATEMENTS


# Art Statements

@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkCreation(GenericStatement):
    __entity_group__ = ART_STATEMENTS

@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkCommission(GenericStatement):
    __entity_group__ = ART_STATEMENTS

@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkExchange(GenericStatement):
    __entity_group__ = ART_STATEMENTS

# Music Statements

@reversion.register(follow=["tempentityclass_ptr"])
class MusicCreation(GenericStatement):
    __entity_group__ = MUSIC_STATEMENTS

@reversion.register(follow=["tempentityclass_ptr"])
class MusicPerformance(GenericStatement):
    __entity_group__ = MUSIC_STATEMENTS



def build_property(name: str=None, name_reverse: str=None, subj_class: Property=None, obj_class: Union[Property, Iterator[Property]]=None):
    prop = Property.objects.get_or_create(
        name=name,
        name_reverse=name_reverse,
    )[0]
    prop.subj_class.clear()
    prop.subj_class.add(caching.get_contenttype_of_class(subj_class))
    prop.obj_class.clear()
    if isinstance(obj_class, Iterable):
        for oclass in obj_class:
            prop.obj_class.add(caching.get_contenttype_of_class(oclass))
    else:
        prop.obj_class.add(caching.get_contenttype_of_class(obj_class))
    return prop

def construct_properties():

    naming_of_person = build_property("is naming of", "has naming", Naming, Person)

    birth_event_of_person = build_property("is birth of", "has birth", Birth, Person)
    birth_event_in_location = build_property("has location", "is location of birth", Birth, Location)

    death_event_of_person = build_property("is death of", "has death", Death, Person)
    death_event_in_location = build_property("has location", "is location of death", Death, Location)

    membership_concerns_person = build_property("membership concerns person", "has membership", Membership, Person)
    membership_of_organisation = build_property("membership organisation", "organisation of membership", Membership, Organisation)

    parental_relation_parent = build_property("has parent", "is parent in relation", ParentalRelation, Person)
    parental_relation_child = build_property("has child", "is child in relation", ParentalRelation, Person)

    payment_payer = build_property("has payer", "is payer of", Payment, Person)
    payment_payee = build_property("has payee", "is payee of", Payment, Person)

    election_of_person = build_property("is election of", "person elected", Election, Person)
    location_of_election = build_property("has location", "is location of election", Election, Location)
    organisation_to_which_elected = build_property("organisation_elected_to", "organisation_of_election", Election, Organisation)

    ordered_by_person = build_property("order given by", "gave order", Order, Person)
    thing_ordered = build_property("thing ordered", "was result of order", Order, [Payment, Death])