import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
from apis_core.apis_entities.models import TempEntityClass


@reversion.register(follow=["tempentityclass_ptr"])
class E1_Crm_Entity(TempEntityClass):
    """
    Base class for all entities.
    """

    # Set APIS_BIBSONOMY_FIELDS here when APIS_BIBSONOMY is
    # configured in settings. E.g.
    # APIS_BIBSONOMY_FIELDS = ["self", "name", "start_date_written"]

    class Meta:
        verbose_name = "entity"  # use lowercase for verbose names of classes
        verbose_name_plural = "entities"


# Example for how to define model classes for entities
@reversion.register(follow=["tempentityclass_ptr"])
class E55_Type(E1_Crm_Entity):
    """
    One-sentence summary of class goes here.

    Longer explanation of class goes here.
    Note that Docstrings of model classes are displayed to admin users on the
    admin frontend (on hover on an entity's name).
    """

    class Meta:
        verbose_name = "type"  # plural not needed for nouns with regular -s plural


def construct_properties():
    """
    Create relationships between entity classes.

    Regarding property definitions:
    - each "name" (and "name_reversed") may only be used once,
    - a relationship can connect more than two entities, i.e. can have more
    than just one Subject (subj_class) or just one Object (obj_class).
    """
    from apis_core.apis_relations.models import Property

    # Examples for how to define properties (a.k.a. relations)
    p2_has_type = Property.objects.get_or_create(
        name="p2 has type",
        name_reverse="p2i is type of",
    )[0]
    p2_has_type.subj_class.clear()
    p2_has_type.obj_class.clear()
    p2_has_type.subj_class.add(ContentType.objects.get(model=E1_Crm_Entity.__name__))
    p2_has_type.obj_class.add(ContentType.objects.get(model=E55_Type.__name__))

    work_type_has_broader_term = Property.objects.get_or_create(
        name="work type has broader term",
        name_reverse="work type has narrower term",
    )[0]
    work_type_has_broader_term.subj_class.clear()
    work_type_has_broader_term.obj_class.clear()
    work_type_has_broader_term.subj_class.add(
        ContentType.objects.get(model=E55_Type.__name__)
    )
    work_type_has_broader_term.obj_class.add(
        ContentType.objects.get(model=E55_Type.__name__)
    )
