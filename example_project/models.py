import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
from apis_core.apis_entities.models import TempEntityClass


@reversion.register(follow=["tempentityclass_ptr"])
class E1_Crm_Entity(TempEntityClass):
    class Meta:
        verbose_name = "E1 CRM Entity"

    APIS_BIBSONOMY_FIELDS = ["self", "name", "start_date_written"]


@reversion.register(follow=["tempentityclass_ptr"])
class E55_Type(E1_Crm_Entity):
    class Meta:
        verbose_name = "E55 Type"

    pass


def construct_properties():

    from apis_core.apis_vocabularies.models import TextType
    from apis_core.apis_metainfo.models import Collection
    from apis_core.apis_relations.models import Property
    from apis_highlighter.models import AnnotationProject, Project
    from django.contrib.auth.models import User

    TextType.objects.all().delete()
    tt = TextType.objects.create(entity="E1_Crm_Entity")
    # tt.collections.add(Collection.objects.get_or_create(name="manually created entity"))

    AnnotationProject.objects.create(name="test__annotation_project_1")
    Project.objects.create(name="test__project_1", user=User.objects.first())

    Property.objects.all().delete()

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
