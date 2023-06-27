from collections.abc import Iterable
from dataclasses import dataclass
from typing import Union, Iterator

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
from apis_core.apis_entities.models import TempEntityClass
from apis_core.apis_relations.models import Property, Triple
from apis_core.utils import caching

from apis_ontology.helper_functions import remove_extra_spaces

# Entity categories


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
class Factoid(TempEntityClass):
    created_by = models.CharField(max_length=300)
    language = models.CharField(
        max_length=4,
        choices=(
            ("DE", "German"),
            ("LA", "Latin"),
            ("FR", "French"),
            ("NL", "Dutch"),
            ("IT", "Italian"),
        ),
    )


@reversion.register(follow=["tempentityclass_ptr"])
class Person(TempEntityClass):
    """Person: a real person, identified by a label and (one or more) URIs. All information about Persons derived from sources
    should be added as types of Statement, with the Person added as a Related Entity to the Statement."""

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Persons"

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


# TODO: sort out this focking hierarchy
@reversion.register(follow=["tempentityclass_ptr"])
class GroupOfPersons(TempEntityClass):
    """Group of persons identified by a label and URIs."""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Organisation(TempEntityClass):
    """Organisation: an organisation or other group, identified by a label and URIs."""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Foundation(Organisation):
    """Foundation: legally constituted entity, identified by a label and URIs."""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Family(TempEntityClass):  # TODO: should be group of persons subclass
    family_name = models.CharField(max_length=200, blank=True)


@reversion.register(follow=["tempentityclass_ptr"])
class ConceptualObject(TempEntityClass):
    """A Work of art, literature, music, etc. Where possible, use specific subtypes (Artistic Work, Music Work, etc.)"""

    __entity_group__ = CONCEPTUAL_OBJECTS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class CompositeConceptualObject(ConceptualObject):
    """A Work of art, literature, music, etc., comprised of individually identifiable sub-works"""

    __entity_group__ = CONCEPTUAL_OBJECTS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class PhysicalObject(TempEntityClass):
    """A physical object (rather than a conceptual object). Where possible, use specific subtypes (Work, Music Work, Armour)"""

    __entity_group__ = PHYSICAL_OBJECTS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class CompositePhysicalObject(PhysicalObject):
    """An object composed of more than one other objects"""

    __entity_group__ = PHYSICAL_OBJECTS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Role(TempEntityClass):
    """A Role in an Organisation, occupied by one or more Person in RoleOccupation, or assigned/removed via AssignmentToRole/RemovalFromRole"""

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Task(TempEntityClass):
    """A task, fulfilled by person, potentially as part of a Role"""

    __entity_group__ = GENERIC
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class FictionalPerson(ConceptualObject):
    __entity_type__ = ENTITY
    __entity_group__ = GENERIC


#### GENERIC STATEMENTS


@reversion.register(follow=["tempentityclass_ptr"])
class GenericStatement(TempEntityClass):
    """A Generic Statement about a Person (to be used when nothing else will work)."""

    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class Activity(GenericStatement):
    __entity_group__ = CONCEPTUAL_OBJECTS
    __entity_type__ = STATEMENT

    class Meta:
        verbose_name_plural = "Activities"


@reversion.register(follow=["tempentityclass_ptr"])
class OwnershipTransfer(Activity):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT


"""
@reversion.register(follow=["tempentityclass_ptr"])
class GiftGiving(OwnershipTransfer):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT
"""


@reversion.register(follow=["tempentityclass_ptr"])
class CreationCommission(Activity):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT


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


@reversion.register(follow=["tempentityclass_ptr"])
class Gendering(GenericStatement):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT

    GENDERS = (
        ("female", "Female"),
        ("male", "Male"),
        ("unknown", "Unknown"),
    )
    gender = models.CharField(
        max_length=9, choices=GENDERS, blank=True, verbose_name="gender types"
    )


@reversion.register(follow=["tempentityclass_ptr"])
class CreationAct(Activity):
    __entity_group__ = CONCEPTUAL_OBJECTS
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class CreationOfOrganisation(CreationAct):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class AssemblyOfCompositeObject(CreationAct):
    __entity_group__ = CONCEPTUAL_OBJECTS
    __entity_type__ = STATEMENT


# ARMOUR TYPES


@reversion.register(follow=["tempentityclass_ptr"])
class ArmourPiece(PhysicalObject):
    __entity_group__ = ARMOURING
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class ArmourSuit(CompositePhysicalObject):
    """Suit of armour, comprising possibly many pieces"""

    __entity_group__ = ARMOURING
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class ArmourCreationAct(CreationAct):
    __entity_group__ = ARMOURING
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class ArmourAssemblyAct(AssemblyOfCompositeObject):
    __entity_group__ = ARMOURING
    __entity_type__ = STATEMENT


# Print


@reversion.register(follow=["tempentityclass_ptr"])
class Image(ConceptualObject):
    __entity_type__ = CONCEPTUAL_OBJECTS
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Woodcut(Image):
    __entity_group__ = PRINT
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class PrintedWork(CompositePhysicalObject):
    __entity_group__ = PRINT
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Leaflet(PrintedWork):
    __entity_group__ = PRINT
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Book(PrintedWork):
    __entity_group__ = PRINT
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Manuscript(CompositePhysicalObject):
    __entity_group__ = PRINT
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class TextualWork(ConceptualObject):
    __entity_group__ = PRINT
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Poem(TextualWork):
    __entity_group__ = PRINT
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class CompositeTextualWork(CompositeConceptualObject):
    __entity_group__ = PRINT
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Preface(TextualWork):
    __entity_group__ = PRINT
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class DedicatoryText(TextualWork):
    __entity_group__ = PRINT
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class Dedication(GenericStatement):
    __entity_group__ = PRINT
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class TextualCreationAct(CreationAct):
    __entity_group__ = PRINT
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class Authoring(TextualCreationAct):
    __entity_group__ = PRINT
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class Printing(TextualCreationAct):
    __entity_group__ = PRINT
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class SecretarialAct(TextualCreationAct):
    __entity_group__ = PRINT
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class Redacting(TextualCreationAct):
    __entity_group__ = PRINT
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class PreparationOfConceptualText(TextualCreationAct):
    __entity_group__ = PRINT
    __entity_type__ = STATEMENT


# Base Work subtypes


@reversion.register(follow=["tempentityclass_ptr"])
class MusicWork(ConceptualObject):
    """A piece of music"""

    __entity_group__ = MUSIC
    __entity_type__ = ENTITY


@reversion.register(follow=["tempentityclass_ptr"])
class ArtisticWork(PhysicalObject):
    """A work of art"""

    __entity_group__ = ART
    __entity_type__ = ENTITY


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


@reversion.register(follow="tempentityclass_ptr")
class OrganisationLocation(GenericStatement):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT


@reversion.register(follow="tempentityclass_ptr")
class AcceptanceOfStatement(GenericStatement):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class Election(GenericStatement):
    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    position = models.CharField(
        max_length=200, blank=True, verbose_name="Position elected to"
    )


@reversion.register(follow=["tempentityclass_ptr"])
class PerformanceOfTask(Activity):
    __entity_group__ = GENERIC
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class PerformanceOfWork(Activity):
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
        verbose_name_plural = "Assignments to Role"

    __entity_group__ = ROLE_ORGANISATIONS
    __entity_type__ = STATEMENT

    description = models.CharField(max_length=200)


@reversion.register(follow=["tempentityclass_ptr"])
class RemovalFromRole(GenericStatement):
    """Describes the removal from a Role of a Person (role occupier), by an Person (remover)"""

    class Meta:
        verbose_name_plural = "Removals from Role"

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
    SIBLING_TYPE = (
        ("brother", "Brother"),
        ("sister", "Sister"),
        ("half-brother", "Half-Brother"),
        ("step-brother", "Step-Brother"),
        ("half-sister", "Half-Sister"),
        ("step-sister", "Step-Sister"),
        ("unknown", "Unknown"),
    )

    sibling_type = models.CharField(
        max_length=12, choices=SIBLING_TYPE, blank=True, verbose_name="sibling types"
    )


@reversion.register(follow=["tempentityclass_ptr"])
class MarriageBeginning(FamilialRelation):
    __entity_group__ = LIFE_FAMILY
    __entity_type__ = STATEMENT


@reversion.register(follow=["tempentityclass_ptr"])
class MarriageEnd(FamilialRelation):
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
class ArtworkCreationAct(CreationAct):
    __entity_group__ = ART
    __entity_type__ = STATEMENT


""" REMOVED: adds nothing above Acquisition
@reversion.register(follow=["tempentityclass_ptr"])
class ArtworkAcquisition(Acquisition):
    __entity_group__ = ART_STATEMENTS
"""

# Music Statements


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

    print("PROPERTY_NAME", name)
    prop.subj_class.clear()
    if isinstance(subj_class, Iterable):
        print("SUBJCLASS", subj_class)
        for sclass in subj_class:

            prop.subj_class.add(ContentType.objects.get_for_model(sclass))

    else:
        prop.subj_class.add(ContentType.objects.get_for_model(subj_class))

    prop.obj_class.clear()
    if isinstance(obj_class, Iterable):
        print("objclass", obj_class)
        for oclass in set(obj_class):

            prop.obj_class.add(ContentType.objects.get_for_model(oclass))

    else:
        prop.obj_class.add(ContentType.objects.get_for_model(obj_class))
    return prop


def subclasses(model: TempEntityClass):
    sc = [model]
    for subclass in model.__subclasses__():
        sc += [subclass, *subclasses(subclass)]
    return set(sc)


def construct_properties():
    # Generic Statement attached to Factoid

    is_part_of_factoid = build_property(
        "has statement", "is part of factoid", Factoid, subclasses(GenericStatement)
    )

    activity_has_place = build_property(
        "location of activity", "activity took place in", subclasses(Activity), Place
    )

    creation_act_carried_out_by_person_or_org = build_property(
        "carried out by person",
        "person carried out",
        subclasses(CreationAct),
        [Person, Organisation],
    )

    text_authored = build_property(
        "text authored", "was authored in", Authoring, subclasses(TextualWork)
    )

    printed_work_printed = build_property(
        "work printed", "was printed in", Printing, subclasses(PrintedWork)
    )

    secretarial_act_contributed_to = build_property(
        "work concerned",
        "was concerned in secretarial act",
        SecretarialAct,
        subclasses(TextualWork),
    )

    redacting_contributed_to = build_property(
        "work concerned",
        "was concerned in redacting",
        Redacting,
        subclasses(TextualWork),
    )

    preparation_of_conceptual_text_of = build_property(
        "was prepared as conceptual text",
        "prepared as conceptual text in",
        PreparationOfConceptualText,
        subclasses(TextualWork),
    )

    assembly_of_composite_object = build_property(
        "object assembled",
        "was assembled in",
        AssemblyOfCompositeObject,
        [*subclasses(CompositeConceptualObject), *subclasses(CompositePhysicalObject)],
    )

    ownership_transfer_what = build_property(
        "thing transferred",
        "had ownership transferred in",
        subclasses(OwnershipTransfer),
        subclasses(PhysicalObject),
    )
    ownership_transfer_from_whom = build_property(
        "transferred from",
        "was previous owner in transfer",
        subclasses(OwnershipTransfer),
        [Person, *subclasses(Organisation)],
    )
    ownership_transfer_to_whom = build_property(
        "transferred to",
        "new owner in transfer",
        subclasses(OwnershipTransfer),
        [Person, *subclasses(Organisation)],
    )

    naming_of_person = build_property("person named", "was named in", Naming, Person)

    gendering_of_person = build_property(
        "person has gender", "was gendered in", Gendering, Person
    )

    dedication_to_dedicatory_text = build_property(
        "dedication found in", "contains dedication", Dedication, DedicatoryText
    )
    dedication_to_person = build_property(
        "person receiving dedication", "has dedication", Dedication, Person
    )

    birth_of_person = build_property("has birth event", "was born in", Birth, Person)
    place_of_birth = build_property("occurred in", "is location of birth", Birth, Place)

    death_of_person = build_property("has death event", "died in", Death, Person)
    place_of_death = build_property("occurred in", "is location of death", Death, Place)

    organisation_location_organisation = build_property(
        "organisation located",
        "was located in",
        OrganisationLocation,
        subclasses(Organisation),
    )
    organisation_location_place = build_property(
        "has location", "is location of organisation", OrganisationLocation, Place
    )

    organisation_creation_creates_organisation = build_property(
        "organisation created", "was created by", CreationOfOrganisation, Organisation
    )

    election_to_role = build_property(
        "role elected to", "was occupied by election", Election, Role
    )
    election_of_person = build_property(
        "person elected", "was elected in", Election, Person
    )
    election_leads_to_role_occupation = build_property(
        "role occupation begun by", "was begun by election", Election, RoleOccupation
    )

    performance_of_task_task = build_property(
        "task performed", "was performed in", PerformanceOfTask, Task
    )
    performance_of_task_person_group = build_property(
        "performed task",
        "involved in task performance",
        PerformanceOfTask,
        [Person, *subclasses(Organisation)],
    )

    performance_of_work_work = build_property(
        "work performed", "was performed in", PerformanceOfWork, [MusicWork, Poem]
    )
    performance_of_work_person_group = build_property(
        "performed work",
        "involved in performance of work",
        PerformanceOfWork,
        [Person, *subclasses(Organisation)],
    )

    role_occupation_role = build_property(
        "role occupied", "role occupied in", RoleOccupation, Role
    )
    role_occupation_person = build_property(
        "person occupying role", "has role occupation", RoleOccupation, Person
    )

    assignment_to_role_role = build_property(
        "role assigned", "was assigned in", AssignmentToRole, Role
    )
    assignment_to_role_assigner = build_property(
        "assigned role to person",
        "assigned role to person in",
        AssignmentToRole,
        [Person, *subclasses(Organisation)],
    )
    assignment_to_role_assignee = build_property(
        "person to whom role assigned", "was assigned role in", AssignmentToRole, Person
    )
    assignment_to_role_starts_role_occupation = build_property(
        "role occupation started by assignment",
        "was started by",
        AssignmentToRole,
        RoleOccupation,
    )

    removal_from_role_role = build_property(
        "role removed from", "was removed from person in", RemovalFromRole, Role
    )
    removal_from_role_remover = build_property(
        "person removing role",
        "removed role in",
        RemovalFromRole,
        [Person, *subclasses(Organisation)],
    )
    removal_from_role_removee = build_property(
        "person removed from role", "removed from role in", RemovalFromRole, Person
    )
    removal_from_role_ends_role_occupation = build_property(
        "role occupation ended by removal",
        "was ended by",
        RemovalFromRole,
        RoleOccupation,
    )

    parental_relation_parent = build_property(
        "parent in relationship", "is parent in relationship", ParentalRelation, Person
    )
    parental_relation_child = build_property(
        "child in relationship", "is child in relationship", ParentalRelation, Person
    )

    sibling_relation_person_a = build_property(
        "person having sibling", "has sibling in relationship", SiblingRelation, Person
    )
    sibling_relation_person_b = build_property(
        "is sibling", "has sibling_in_relationship", SiblingRelation, Person
    )

    marriage_beginning_person = build_property(
        "persons married", "has marriage beginning in", MarriageBeginning, Person
    )
    marriage_beginning_place = build_property(
        "place of marriage", "is place of marriage", MarriageBeginning, Place
    )

    marriage_end_person = build_property(
        "persons married", "has marriage ending in", MarriageEnd, Person
    )

    family_membership = build_property(
        "family member", "is member of family", Family, Person
    )

    payment_for_entity = build_property(
        "payment for",
        "was paid for in",
        Payment,
        [
            PerformanceOfTask,
            PerformanceOfWork,
            RoleOccupation,
            CreationAct,
            PhysicalObject,
            OwnershipTransfer,
        ],
    )
    payment_by_person = build_property(
        "payment by", "made payment in", Payment, [Person, *subclasses(Organisation)]
    )
    payment_to_person = build_property(
        "payment to",
        "received payment in",
        Payment,
        [Person, *subclasses(Organisation)],
    )

    order_for = build_property(
        "thing ordered",
        "was ordered in",
        subclasses(Order),
        [
            Poem,
            Preface,
            DedicatoryText,
            MusicWork,
            *subclasses(PhysicalObject),
            PerformanceOfTask,
            MusicPerformance,
            *subclasses(CreationAct),
            *subclasses(CreationCommission),
            Death,
            AssignmentToRole,
            RemovalFromRole,
            Payment,
            Order,
        ],
    )
    ordered_by = build_property(
        "order given by", "gave order", Order, [Person, *subclasses(Organisation)]
    )
    order_received_by = build_property(
        "order received by",
        "received order",
        Order,
        [Person, *subclasses(Organisation)],
    )

    armour_creation_act_armour = build_property(
        "armour created", "was created in", ArmourCreationAct, [ArmourPiece, ArmourSuit]
    )
    armour_assembly_act_armour_pieces = build_property(
        "armour assembled from",
        "was assembled to suit in",
        ArmourAssemblyAct,
        ArmourPiece,
    )
    armour_assembly_act_armour_suit = build_property(
        "assembled into", "was assembled in", ArmourAssemblyAct, ArmourSuit
    )

    creation_commission_creation_act_commissions = build_property(
        "creation act commissions",
        "was commissioned in",
        CreationCommission,
        subclasses(CreationAct),
    )

    acceptance_of_statement_generic_statement = build_property(
        "thing accepted",
        "was accepted in",
        AcceptanceOfStatement,
        subclasses(GenericStatement),
    )
    acceptance_of_statement_by_person = build_property(
        "person accepting statement",
        "was accepted by",
        AcceptanceOfStatement,
        [Person, Organisation, GroupOfPersons],
    )
