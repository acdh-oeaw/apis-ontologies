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


GENERIC = "Generic"
ROLE_ORGANISATIONS = "Roles/Organisations"
LIFE_FAMILY = "Life/Family"
ART = "Art"
MUSIC = "Music"
ARMOURING = "Armouring"
OTHER = "Other"



ENTITY = "Entities"
STATEMENT = "Statements"

group_order = [

    GENERIC,
    LIFE_FAMILY,
    ROLE_ORGANISATIONS,
    ART,
    MUSIC,
    OTHER,
]


@reversion.register(follow=["tempentityclass_ptr"])
class Factoid(TempEntityClass):
    
    
    created_by = models.CharField(max_length=300)

@reversion.register(follow=["tempentityclass_ptr"])
class Person(TempEntityClass):
    """Person: a real person, identified by a label and (one or more) URIs. All information about Persons derived from sources
    should be added as types of Statement, with the Person added as a Related Entity to the Statement."""

    class Meta:
        verbose_name = "Person"

    __entity_group__ = GENERIC
    __entity_type__ = ENTITY

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
    """Place: a real place, identified by a label and URIs."""

    __entity_group__ = GENERIC
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Organisation(TempEntityClass):
    """Organisation: an organisation or other group, identified by a label and URIs."""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class ConceptualObject(TempEntityClass):
    """A Work of art, literature, music, etc. Where possible, use specific subtypes (Artistic Work, Music Work, etc.)"""

    __entity_group__ = GENERIC
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class PhysicalObject(TempEntityClass):
    """A physical object (rather than a conceptual object). Where possible, use specific subtypes (Work, Music Work, Armour)"""

    __entity_group__ = GENERIC
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Role(TempEntityClass):
    """A Role in an Organisation, occupied by one or more Person in RoleOccupation, or assigned/removed via AssignmentToRole/RemovalFromRole"""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY

# Base Armour subtypes



# Base Work subtypes


@reversion.register(follow=["tempentityclass_ptr"])
class MusicWork(ConceptualObject):
    """A piece of music"""

    __entity_group__ = MUSIC
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class ArtWork(ConceptualObject):
    """A work of art"""

    __entity_group__ = ART
    __entity_type__ = ENTITY


# Base Statements


@reversion.register(follow=["tempentityclass_ptr"])
class GenericStatement(TempEntityClass):
    """A Generic Statement about a Person (to be used when nothing else will work)."""

    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT
    

@reversion.register(follow=["tempentityclass_ptr"])
class PropertyExchange(TempEntityClass):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT
    
    description_of_property_exchanged = models.CharField(max_length=300, blank=True)


@reversion.register(follow=["tempentityclass_ptr"])
class Naming(GenericStatement):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

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
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class Death(GenericStatement):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class Election(GenericStatement):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    position = models.CharField(
        max_length=200, blank=True, verbose_name="Position elected to"
    )

@reversion.register(follow="tempentityclass_ptr")
class OrganisationLocation(GenericStatement):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class Performance(GenericStatement):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class RoleOccupation(GenericStatement):
    """Describes the occupation of a Role by a Person"""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class AssignmentToRole(GenericStatement):
    """Describes the assignment of a Role to a Person (assignee), by an Person (assigner)"""

    class Meta:
        verbose_name_plural = "Assignments to Role Occupation"

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    description = models.CharField(max_length=200)


@reversion.register(follow=["tempentityclass_ptr"])
class RemovalFromRole(GenericStatement):
    """Describes the removal from a Role of a Person (role occupier), by an Person (remover)"""

    class Meta:
        verbose_name_plural = "Removals from Role Occupation"

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    description = models.CharField(max_length=200)


@reversion.register(follow=["tempentityclass_ptr"])
class FamilialRelation(GenericStatement):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class ParentalRelation(FamilialRelation):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT
    PARENTAL_TYPES = (
        ("mother", "Mother"),
        ("father", "Father"),
        ("unknown", "Unknown"),
    )
    parental_type = models.CharField(
        max_length=9, choices=PARENTAL_TYPES, blank=True, verbose_name="parental types"
    )


@reversion.register(follow=["tempentityclass_ptr"])
class SiblingRelation(FamilialRelation):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class Payment(GenericStatement):
    """Payment of money for Item, Work, Acquisition, or other Activity"""

    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT

    amount = models.IntegerField(blank=True)


@reversion.register(follow=["tempentityclass_ptr"])
class Order(GenericStatement):
    """An order given by someone to do something"""

    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class Acquisition(GenericStatement):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT


# Art Statements


@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkCreation(GenericStatement):
    __entity_group__ = ART
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkCommission(GenericStatement):
    __entity_group__ = ART
    __entity_type__ = STATEMENT


""" REMOVED: adds nothing above Acquisition
@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkAcquisition(Acquisition):
    __entity_group__ = ART_STATEMENTS
"""

# Music Statements


@reversion.register(follow=["tempentityclass_ptr"])
class MusicCreation(GenericStatement):
    __entity_group__ = MUSIC
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name = "Music Creation"


@reversion.register(follow=["tempentityclass_ptr"])
class MusicPerformance(GenericStatement):
    __entity_group__ = MUSIC
    __entity_type__ = STATEMENT


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
    # Generic Statement attached to Factoid
    for sc in list(GenericStatement.__subclasses__()):
    
        is_part_of_factoid = build_property("has statement", "is part of factoid", Factoid, sc)
    
    # Property Exchange
    giver = build_property("giver of property", "gave property in property exchange" , PropertyExchange, [Person, Organisation])
    receiver = build_property("receiver of property", "received property in property exchange" , PropertyExchange, [Person, Organisation])
    is_part_of_factoid = build_property("has statement", "is part of factoid", Factoid, PropertyExchange)
    
    # Place located within
    place_located_in_place = build_property("located within", "contains place", Place, Place)

    # Naming
    naming_of_person = build_property("is naming of", "has naming", Naming, Person)

    # Birth to person and location
    birth_event_of_person = build_property("is birth of", "has birth", Birth, Person)
    birth_event_in_location = build_property(
        "has location", "is location of birth", Birth, Place
    )

    # Death to person and location
    death_event_of_person = build_property("is death of", "has death", Death, Person)
    death_event_in_location = build_property(
        "has location", "is location of death", Death, Place
    )

    # Organisation has location
    organisation_location_place = build_property("organisation located in", "organisation location", OrganisationLocation, Place)
    organisation_location_organisation = build_property("organisation with location", "organisation location", OrganisationLocation, Organisation)

    # Role in organisation
    role_in_organisation = build_property(
        "role in organisation", "organisation has role", Role, Organisation
    )

    # Role occupied by person with role occupation
    role_occupied = build_property(
        "role occupied",
        "role occupation",
        RoleOccupation,
        Role,
    )
    role_occupation_occupied_by_person = build_property(
        "person occupying role", "occupies role", RoleOccupation, Person
    )
    # Assignment of role
    assignment_to_role_role = build_property(
        "role assigned", "role assigned in", Role, AssignmentToRole
    )
    assignment_to_role_assigner = build_property(
        "assigns role", "role assignment by", Person, AssignmentToRole
    )
    assignment_to_role_assignee = build_property(
        "person assigned role", "role assigned to", Person, AssignmentToRole
    )
    assignment_to_role_leads_to_role_occupation = build_property(
        "leads to role occupation",
        "result of role assignment",
        AssignmentToRole,
        RoleOccupation,
    )

    # Removal from role
    removal_from_role_role = build_property(
        "role removed from", "removal of role via", Role, RemovalFromRole
    )
    removal_from_role_remover = build_property(
        "removes from role", "role removal by", Person, RemovalFromRole
    )
    removal_from_role_person_removed = build_property(
        "removed from role", "was removed by from role via", Person, RemovalFromRole
    )
    removal_from_role_ends_role_occupation = build_property(
        "causes end of role occupation",
        "ends as a result of removal",
        RemovalFromRole,
        RoleOccupation,
    )

    # Parental relation to person-parent and person-child
    parental_relation_parent = build_property(
        "has parent", "is parent in relation", ParentalRelation, Person
    )
    parental_relation_child = build_property(
        "has child", "is child in relation", ParentalRelation, Person
    )

    payment_payer = build_property("has payer", "is payer of", Payment, Person)
    payment_payee = build_property("has payee", "is payee of", Payment, Person)
    payment_for = build_property(
        "payment for",
        "result of payment",
        Payment,
        [
            Acquisition,
            ArtworkCommission,
            ArtworkCreation,
            ArtWork,
            Performance,
            MusicPerformance,
        ],
    )

    election_of_person = build_property(
        "is election of", "person elected", Election, Person
    )
    location_of_election = build_property(
        "has location", "is location of election", Election, Place
    )
    role_to_which_elected = build_property(
        "role elected to", "role filled via election", Election, Role
    )
    role_occupation_to_which_elected = build_property(
        "role occupation resulting from", "resulted from", Election, RoleOccupation
    )

    order_given_by_person = build_property(
        "order given by", "gave order", Order, Person
    )
    thing_ordered = build_property(
        "thing ordered",
        "was result of order",
        Order,
        [
            Payment,
            Death,
            Acquisition,
            Order,
            AssignmentToRole,
            RemovalFromRole,
            ArtworkCommission,
            ArtworkCreation,
            MusicCreation,
            MusicPerformance,
            PropertyExchange
        ],
    )

    ownership_by_start = build_property(
        "previous owner", "is previous owner of", Acquisition, [Person, Organisation]
    )
    ownership_by_end = build_property(
        "new owner", "is new owner of", Acquisition, [Person, Organisation]
    )
    ownership_of_entity = build_property(
        "thing changing ownership", "changed ownership by", Acquisition, [ArtWork, GenericItem]
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

    artwork_created_in_artwork_creation = build_property(
        "artwork created", "is result of creation", ArtworkCreation, ArtWork
    )
    artwork_created_by_person = build_property(
        "created by", "person created artwork", ArtworkCreation, Person
    )
    artwork_creation_result_of_commission = build_property(
        "resulted from commission",
        "was result of commission",
        ArtworkCreation,
        ArtworkCommission,
    )
    artwork_result_of_commission = build_property(
        "resulted from commission",
        "was result of commission",
        ArtWork,
        ArtworkCommission,
    )

    music_created = build_property(
        "music work created", "is result of creation", MusicCreation, MusicWork
    )
    music_created_by = build_property(
        "created by", "person created music work", MusicCreation, Person
    )

    music_performance_of_music_work = build_property("music perfmored", "has performance", MusicPerformance, MusicWork)