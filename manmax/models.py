from collections.abc import Iterable
from dataclasses import dataclass
from typing import Union, Iterator

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
from apis_core.apis_entities.models import TempEntityClass
from apis_core.apis_relations.models import Property, Triple, AbstractReification
from apis_core.helper_functions import caching

from apis_ontology.helper_functions import remove_extra_spaces

# Entity categories

BASE_ENTITIES = "Base Entities"
BASE_STATEMENTS = "Base Statements"
ART_ENTITIES = "Art Entities"
ART_STATEMENTS = "Art Statements"
MUSIC_ENTITIES = "Music Entities"
MUSIC_STATEMENTS = "Music Statements"
OTHER = "Other"

group_order = [
    BASE_ENTITIES,
    BASE_STATEMENTS,
    ART_ENTITIES,
    ART_STATEMENTS,
    MUSIC_ENTITIES,
    MUSIC_STATEMENTS,
    OTHER,
]


@reversion.register(follow=["tempentityclass_ptr"])
class Person(TempEntityClass):
    """Person: a real person, identified by a label and (one or more) URIs. All information about Persons derived from sources
    should be added as types of Statement, with the Person added as a Related Entity to the Statement."""

    class Meta:
        verbose_name = "Person"

    __entity_group__ = BASE_ENTITIES

    def update_label_from_namings(self):
        """Get all Naming objects which are subjects of Triples where self is the object, and combine the values"""
        naming_triples = self.triple_set_from_obj.filter(
            prop__name="is naming of",
            subj__self_contenttype=caching.get_contenttype_of_class(Naming),
        ).all()
        if "|" in self.name:
            new_label = self.name.split(" | ")[0]
        else:
            new_label = self.name
        other_names = " | ".join(
            f"{nt.subj.forename} {nt.subj.surname} {nt.subj.role_name} {nt.subj.add_name}"
            for nt in naming_triples
        )
        if other_names:
            new_label += " | " + other_names
        self.name = remove_extra_spaces(new_label)
        self.save()


@reversion.register(follow=["tempentityclass_ptr"])
class Place(TempEntityClass):
    """Place: a real place, identified by a label and (one or more) URIS."""

    __entity_group__ = BASE_ENTITIES


@reversion.register(follow=["tempentityclass_ptr"])
class Organisation(TempEntityClass):
    """Organisation: a real person, identified by a label and (one or more) URIS."""

    __entity_group__ = BASE_ENTITIES


@reversion.register(follow=["tempentityclass_ptr"])
class GenericWork(TempEntityClass):
    """A Work of art, literature, music, etc. Where possible, use specific subtypes (Artistic Work, Music Work, etc.)"""

    __entity_group__ = BASE_ENTITIES


@reversion.register(follow=["tempentityclass_ptr"])
class GenericItem(TempEntityClass):
    """An item which is not (as far as this project is concerned) created by a Person — in which case, use Generic Work — but
    which may be owned or exchanged."""

    __entity_group__ = BASE_ENTITIES


# Base Work subtypes


@reversion.register(follow=["tempentityclass_ptr"])
class MusicWork(GenericWork):
    """A piece of music"""

    __entity_group__ = MUSIC_ENTITIES


@reversion.register(follow=["tempentityclass_ptr"])
class ArtWork(GenericWork):
    """A work of art"""

    __entity_group__ = ART_ENTITIES


# Base Statements


@reversion.register(follow=["tempentityclass_ptr"])
class GenericStatement(TempEntityClass):
    """A Generic Statement about a Person (to be used when nothing else will work)."""

    __entity_group__ = BASE_STATEMENTS


@reversion.register(follow=["tempentityclass_ptr"])
class Naming(GenericStatement):
    __entity_group__ = BASE_STATEMENTS

    forename = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Forename",
        help_text="contains a forename, given or baptismal name (for multiple, separate with a space)",
    )
    surname = models.CharField(
        max_length=200,
        blank=True,
        help_text="contains a family (inherited) name, as opposed to a given, baptismal, or nick name (for multiple, separate with a space)",
    )
    role_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="contains a name component which indicates that the referent has a particular role or position in society, such as an official title or rank.",
    )
    add_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="(additional name) contains an additional name component, such as a nickname, epithet, or alias, or any other descriptive phrase used within a personal name.",
    )


@receiver(post_save, sender=Triple)
def update_person_label_on_adding_naming_triple(sender, instance: Triple, **kwargs):
    """On saving of a triple where subj=Naming and obj=Person, call Person.update_label_from_names
    to update the Person label"""
    if isinstance(instance.subj, Naming) and isinstance(instance.obj, Person):
        instance.obj.update_label_from_namings()


@receiver(post_save, sender=Naming)
def update_person_label_on_naming_change(sender, instance: Naming, **kwargs):
    """On saving of a naming, get all related Persons and call Person.update_label_from_names
    to update the Person label"""
    naming_triples = instance.triple_set_from_subj.all()
    for nt in naming_triples:
        person: Person = nt.obj
        person.update_label_from_namings()


@reversion.register(follow=["tempentityclass_ptr"])
class Birth(GenericStatement):
    __entity_group__ = BASE_STATEMENTS


@reversion.register(follow=["tempentityclass_ptr"])
class Death(GenericStatement):
    __entity_group__ = BASE_STATEMENTS


@reversion.register(follow=["tempentityclass_ptr"])
class Election(GenericStatement):
    __entity_group__ = BASE_STATEMENTS
    position = models.CharField(
        max_length=200, blank=True, verbose_name="Position elected to"
    )


@reversion.register(follow=["tempentityclass_ptr"])
class Membership(GenericStatement):
    __entity_group__ = BASE_STATEMENTS
    role = models.CharField(blank=True, max_length=500)


@reversion.register(follow=["tempentityclass_ptr"])
class ParentalRelation(GenericStatement):
    __entity_group__ = BASE_STATEMENTS
    PARENTAL_TYPES = (
        ("mother", "Mother"),
        ("father", "Father"),
        ("unknown", "Unknown"),
    )
    parental_type = models.CharField(
        max_length=9, choices=PARENTAL_TYPES, blank=True, verbose_name="parental types"
    )


@reversion.register(follow=["tempentityclass_ptr"])
class Payment(GenericStatement):
    __entity_group__ = BASE_STATEMENTS
    amount = models.IntegerField(blank=True)
    payment_for = models.CharField(blank=True, max_length=500)


@reversion.register(follow=["tempentityclass_ptr"])
class Order(GenericStatement):
    """An order given by someone to do something"""

    __entity_group__ = BASE_STATEMENTS


@reversion.register(follow=["tempentityclass_ptr"])
class Acquisition(GenericStatement):
    __entity_group__ = BASE_STATEMENTS


# Art Statements


@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkCreation(GenericStatement):
    __entity_group__ = ART_STATEMENTS


@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkCommission(GenericStatement):
    __entity_group__ = ART_STATEMENTS


@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkExchange(Acquisition):
    __entity_group__ = ART_STATEMENTS


# Music Statements


@reversion.register(follow=["tempentityclass_ptr"])
class MusicCreation(GenericStatement):
    __entity_group__ = MUSIC_STATEMENTS

    class Meta:
        verbose_name = "Music Creation"


@reversion.register(follow=["tempentityclass_ptr"])
class MusicPerformance(GenericStatement):
    __entity_group__ = MUSIC_STATEMENTS


class IdentificationOfEntity(AbstractReification):
    identified_by = models.CharField(max_length=100, choices=(
        ("explicit_in_source", "Explicit in Source"), 
        ("implicit_in_source", "Implicit in Source"), 
        ("inferred_from_other_source", "Inferred from Other Source"), 
        ("guess", "Guess"),
    ))

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



    birth_event_to_identification = build_property("is birth of", "has birth", Birth, IdentificationOfEntity)
    identification_to_person = build_property("has birth identification", "is identification of", IdentificationOfEntity, Person)




    birth_event_in_location = build_property(
        "has location", "is location of birth", Birth, Place
    )

    death_event_of_person = build_property("is death of", "has death", Death, Person)
    death_event_in_location = build_property(
        "has location", "is location of death", Death, Place
    )

    membership_concerns_person = build_property(
        "membership concerns person", "has membership", Membership, Person
    )
    membership_of_organisation = build_property(
        "membership organisation",
        "organisation of membership",
        Membership,
        Organisation,
    )

    parental_relation_parent = build_property(
        "has parent", "is parent in relation", ParentalRelation, Person
    )
    parental_relation_child = build_property(
        "has child", "is child in relation", ParentalRelation, Person
    )

    payment_payer = build_property("has payer", "is payer of", Payment, Person)
    payment_payee = build_property("has payee", "is payee of", Payment, Person)
    payment_acquisition = build_property(
        "for acquisition", "payment for", Payment, Acquisition
    )

    election_of_person = build_property(
        "is election of", "person elected", Election, Person
    )
    location_of_election = build_property(
        "has location", "is location of election", Election, Place
    )
    organisation_to_which_elected = build_property(
        "organisation_elected_to", "organisation_of_election", Election, Organisation
    )

    ordered_by_person = build_property("order given by", "gave order", Order, Person)
    thing_ordered = build_property(
        "thing ordered", "was result of order", Order, [Payment, Death, Acquisition]
    )

    ownership_by_person_start = build_property(
        "start owner", "is start owner of", Acquisition, [Person, Organisation]
    )
    ownership_by_person_start = build_property(
        "end owner", "is end owner of", Acquisition, [Person, Organisation]
    )
    ownership_of_entity = build_property(
        "thing owned", "is thing owned", Acquisition, [ArtWork, GenericItem]
    )

    artwork_comissioned = build_property(
        "artwork commissioned", "is result of commission", ArtworkCommission, ArtWork
    )
    artwork_commissioned_by = build_property(
        "commissioned by", "person commissioned artwork", ArtworkCommission, Person
    )
    artwork_commissioned_of_person = build_property(
        "person commissioned for artwork",
        "received commission for artwork",
        ArtworkCommission,
        Person,
    )

    artwork_created = build_property(
        "artwork created", "is result of creation", ArtworkCreation, ArtWork
    )
    artwork_created_by = build_property(
        "created by", "person created artwork", ArtworkCreation, Person
    )
    artwork_creation_result_of_commission = build_property(
        "resulted from commission",
        "was result of commission",
        ArtworkCreation,
        ArtworkCommission,
    )

    music_created = build_property(
        "music work created", "is result of creation", MusicCreation, MusicWork
    )
    music_created_by = build_property(
        "created by", "person created music work", MusicCreation, Person
    )
