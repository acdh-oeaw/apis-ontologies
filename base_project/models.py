import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
from apis_core.apis_entities.models import TempEntityClass


@reversion.register(follow=["tempentityclass_ptr"])
class E1_Crm_Entity(TempEntityClass):
    """
    Base class for all entities.
    """

    # Set APIS_BIBSONOMY_FIELDS here when APIS_BIBSONOMY is configured in settings.
    # APIS_BIBSONOMY_FIELDS = ["self", "name", "start_date_written"]


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
        verbose_name = "typ"  # user lowercase for verbose names of classes
        verbose_name_plural = "typen"  # plural not needed for nouns pluralised with -s


def construct_properties():
    """
    Create relationships between entity classes.

    Important note: On rerunning this function, all existing properties/relations are
    removed, which means that all relations previously created between entity objects
    are deleted as well.

    Regarding property definitions:
    - each "name" (and "name_reversed") may only be used once
    - a relationship can connect more than two entities, i.e. have more than just
    one Subject (subj_class) or just one Object (obj_class)
    """
    from apis_core.apis_vocabularies.models import TextType
    from apis_core.apis_relations.models import Property
    from apis_core.apis_metainfo.models import Collection
    from apis_highlighter.models import AnnotationProject, Project
    from django.contrib.auth.models import User

    TextType.objects.all().delete()
    Property.objects.all().delete()

    tt = TextType.objects.create(entity="E1_Crm_Entity")
    tt.collections.add(
        (Collection.objects.get_or_create(name="manually created entity"))[0]
    )

    AnnotationProject.objects.create(name="test__annotation_project_1")
    Project.objects.create(name="test__project_1", user=User.objects.first())

    # Examples for how to define properties (aka relations)
    p2_has_type = Property.objects.create(
        name="p2 has type",
        name_reverse="p2i is type of",
    )
    p2_has_type.subj_class.add(ContentType.objects.get(model=E1_Crm_Entity.__name__))
    p2_has_type.obj_class.add(ContentType.objects.get(model=E55_Type.__name__))
    p2_has_type.save()

    p127_has_broader_term = Property.objects.create(
        name="p127 has broader term",
        name_reverse="p127i has narrower term",
    )
    p127_has_broader_term.subj_class.add(
        ContentType.objects.get(model=E55_Type.__name__)
    )
    p127_has_broader_term.obj_class.add(
        ContentType.objects.get(model=E55_Type.__name__)
    )
    p127_has_broader_term.save()
