import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
# from apis_core.apis_entities.models import AbstractEntity
from apis_core.apis_entities.models import TempEntityClass



@reversion.register(follow=["tempentityclass_ptr"])
class Xml_File(TempEntityClass):

    file_path = models.CharField(max_length=1024, blank=True, null=True)
    file_content = models.TextField(blank=True)


@reversion.register(follow=["tempentityclass_ptr"])
class E1_Crm_Entity(TempEntityClass):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class E40_Legal_Body(E1_Crm_Entity):

    # for institutions and publishers
    institution_id = models.CharField(max_length=1024, blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class E55_Type(E1_Crm_Entity):
    pass


@reversion.register(follow=["tempentityclass_ptr"])
class F1_Work(E1_Crm_Entity):

    untertitel = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Untertitel")
    idno = models.CharField(max_length=1024, blank=True, null=True)
    index_in_chapter = models.IntegerField(blank=True, null=True)
    gnd_url = models.URLField(blank=True, null=True)
    genre = models.CharField(max_length=1024, blank=True, null=True)

    anmerkung = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name="Anmerkung"
    )

    short = models.CharField(max_length=1024, blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class F3_Manifestation_Product_Type(E1_Crm_Entity):

    idno = models.CharField(max_length=1024, blank=True, null=True)
    bibl_id = models.CharField(max_length=1024, blank=True, null=True) # TODO __sresch__ : Maybe replace with idno?
    note = models.CharField(max_length=1024, blank=True, null=True)
    series = models.CharField(max_length=1024, blank=True, null=True)
    edition = models.CharField(max_length=1024, blank=True, null=True)
    ref_target = models.URLField(blank=True, null=True)
    ref_accessed = models.CharField(max_length=1024, blank=True, null=True)
    text_language = models.CharField(max_length=1024, blank=True, null=True)
    short = models.CharField(max_length=1024, blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class F9_Place(E1_Crm_Entity):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class F10_Person(E1_Crm_Entity):

    # TODO: Find a solution for if no name is given, but surname and forename exist

    role =  models.CharField(max_length=1024, blank=True, null=True) # TODO : remove this, use appropriate relation
    pers_id = models.CharField(max_length=1024, blank=True, null=True)
    gnd_url = models.URLField(blank=True, null=True)

    forename = models.CharField(
        max_length=255,
        help_text="The persons´s forename. In case of more then one name...",
        blank=True,
        null=True,
        verbose_name="Vorname"
    )

    surname = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nachname"
    )

    name_generisch = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Name generisch"
    )

    vorname_zweitansetzung = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Vorname (Zweitansetzung)"
    )

    nachname_zweitansetzung = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nachname (Zweitansetzung)"
    )

    name_generisch_zweitansetzung = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Name generisch (Zweitansetzung)"
    )

    GENDER_CHOICES = (("female", "female"), ("male", "male"), ("third gender", "third gender"))
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, blank=True)


@reversion.register(follow=["tempentityclass_ptr"])
class F17_Aggregation_Work(F1_Work):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class F20_Performance_Work(F1_Work):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class F21_Recording_Work(F1_Work):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class F26_Recording(F1_Work):
    note = models.CharField(max_length=1024, blank=True, null=True)
    airing_date = models.CharField(max_length=1024, blank=True, null=True)
    broadcast_id = models.CharField(max_length=1024, blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class F31_Performance(E1_Crm_Entity):

    note = models.CharField(max_length=1024, blank=True, null=True)
    performance_id = models.CharField(max_length=1024, blank=True, null=True)
    performance_type = models.CharField(max_length=1024, blank=True, null=True)

    # TODO: consider changing this to a e55 relation
    category = models.CharField(max_length=1024, blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class Chapter(TempEntityClass):

    chapter_number = models.CharField(max_length=1024, blank=True, null=True)
    chapter_type = models.CharField(max_length=1024, blank=True, null=True)

@reversion.register(follow=["tempentityclass_ptr"])
class Keyword(TempEntityClass):
    pass


def construct_properties():

    from apis_core.apis_vocabularies.models import TextType
    from apis_core.apis_metainfo.models import Collection
    from apis_core.apis_relations.models import Property
    from apis_highlighter.models import AnnotationProject, Project
    from django.contrib.auth.models import User

    TextType.objects.all().delete()
    tt = TextType.objects.create(entity="E1_Crm_Entity")
    #tt.collections.add(Collection.objects.get_or_create(name="manually created entity"))

    AnnotationProject.objects.create(name="test__annotation_project_1")
    Project.objects.create(name="test__project_1", user=User.objects.first())

    Property.objects.all().delete()

    data_read_from = Property.objects.create(
        name="data read from file",
        name_reverse="provides data to",
    )
    data_read_from.subj_class.add(ContentType.objects.get(model=E1_Crm_Entity.__name__))
    data_read_from.subj_class.add(ContentType.objects.get(model=Chapter.__name__))
    data_read_from.subj_class.add(ContentType.objects.get(model=Keyword.__name__))
    data_read_from.obj_class.add(ContentType.objects.get(model=Xml_File.__name__))

    was_defined_primarily_in = Property.objects.create(
        name="was defined primarily in",
        name_reverse="defined primarily",
    )
    was_defined_primarily_in.subj_class.add(ContentType.objects.get(model=E1_Crm_Entity.__name__))
    was_defined_primarily_in.obj_class.add(ContentType.objects.get(model=Xml_File.__name__))

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
    p127_has_broader_term.subj_class.add(ContentType.objects.get(model=E55_Type.__name__))
    p127_has_broader_term.obj_class.add(ContentType.objects.get(model=E55_Type.__name__))
    p127_has_broader_term.save()

    host = Property.objects.create(
        name="host",
    )
    host.subj_class.add(ContentType.objects.get(model=F3_Manifestation_Product_Type.__name__))
    host.obj_class.add(ContentType.objects.get(model=F3_Manifestation_Product_Type.__name__))
    host.save()

    is_author_of = Property.objects.create(
        name="is author of",
        name_reverse="has been written by",
    )
    is_author_of.subj_class.add(ContentType.objects.get(model=F10_Person.__name__))
    is_author_of.obj_class.add(ContentType.objects.get(model=F1_Work.__name__))
    is_author_of.obj_class.add(ContentType.objects.get(model=F3_Manifestation_Product_Type.__name__))
    is_author_of.save()

    is_translator_of = Property.objects.create(
        name="is translator of",
        name_reverse="has been translated by",
    )
    is_translator_of.subj_class.add(ContentType.objects.get(model=F10_Person.__name__))
    is_translator_of.obj_class.add(ContentType.objects.get(model=F1_Work.__name__))
    is_translator_of.obj_class.add(ContentType.objects.get(model=F3_Manifestation_Product_Type.__name__))
    is_translator_of.obj_class.add(ContentType.objects.get(model=F20_Performance_Work.__name__))
    is_translator_of.obj_class.add(ContentType.objects.get(model=F31_Performance.__name__))
    is_translator_of.save()

    is_translator_of = Property.objects.create(
        name="is translation of",
        name_reverse="is original for translation",
    )
    is_translator_of.subj_class.add(ContentType.objects.get(model=F3_Manifestation_Product_Type.__name__))
    is_translator_of.obj_class.add(ContentType.objects.get(model=F1_Work.__name__))
    is_translator_of.save()

    is_editor_of = Property.objects.create(
        name="is editor of",
        name_reverse="has been edited by",
    )
    is_editor_of.subj_class.add(ContentType.objects.get(model=F10_Person.__name__))
    is_editor_of.subj_class.add(ContentType.objects.get(model=E40_Legal_Body.__name__))
    is_editor_of.obj_class.add(ContentType.objects.get(model=F1_Work.__name__))
    is_editor_of.obj_class.add(ContentType.objects.get(model=F3_Manifestation_Product_Type.__name__))
    is_editor_of.save()

    is_publisher_of = Property.objects.create(
        name="is publisher of",
        name_reverse="has been published by",
    )
    is_publisher_of.subj_class.add(ContentType.objects.get(model=E40_Legal_Body.__name__))
    is_publisher_of.obj_class.add(ContentType.objects.get(model=F3_Manifestation_Product_Type.__name__))
    is_publisher_of.save()

    is_director_of = Property.objects.create(
        name="is director of",
        name_reverse="has been directed by",
    )
    is_director_of.subj_class.add(ContentType.objects.get(model=F10_Person.__name__))
    is_director_of.obj_class.add(ContentType.objects.get(model=F31_Performance.__name__))
    is_director_of.save()

    is_composer_of = Property.objects.create(
        name="is composer of",
        name_reverse="has been composed by",
    )
    is_composer_of.subj_class.add(ContentType.objects.get(model=F10_Person.__name__))
    is_composer_of.obj_class.add(ContentType.objects.get(model=F31_Performance.__name__))
    is_composer_of.save()

    is_musician_of = Property.objects.create(
        name="is musician of",
        name_reverse="has been musically accompanied by",
    )
    is_musician_of.subj_class.add(ContentType.objects.get(model=F10_Person.__name__))
    is_musician_of.obj_class.add(ContentType.objects.get(model=F31_Performance.__name__))
    is_musician_of.save()

    is_singer_of = Property.objects.create(
        name="is singer of",
        name_reverse="has been sung by",
    )
    is_singer_of.subj_class.add(ContentType.objects.get(model=F10_Person.__name__))
    is_singer_of.obj_class.add(ContentType.objects.get(model=F31_Performance.__name__))
    is_singer_of.save()

    was_published_in = Property.objects.create(
        name="was published in",
        name_reverse="is publication place of",
    )
    was_published_in.subj_class.add(ContentType.objects.get(model=F3_Manifestation_Product_Type.__name__))
    was_published_in.obj_class.add(ContentType.objects.get(model=F9_Place.__name__))
    was_published_in.save()

    has_been_performed_at = Property.objects.create(
        name="has been performed at",
        name_reverse="has had performance",
    )
    has_been_performed_at.subj_class.add(ContentType.objects.get(model=F31_Performance.__name__))
    has_been_performed_at.subj_class.add(ContentType.objects.get(model=F26_Recording.__name__))
    has_been_performed_at.obj_class.add(ContentType.objects.get(model=E40_Legal_Body.__name__))
    has_been_performed_at.save()

    has_been_performed_in = Property.objects.create(
        name="has been performed in",
        name_reverse="was performance of",
    )
    has_been_performed_in.subj_class.add(ContentType.objects.get(model=F1_Work.__name__))
    has_been_performed_in.obj_class.add(ContentType.objects.get(model=F31_Performance.__name__))
    has_been_performed_in.save()

    contains = Property.objects.create(
        name="contains",
        name_reverse="is contained in",
    )
    contains.subj_class.add(ContentType.objects.get(model=F17_Aggregation_Work.__name__))
    contains.subj_class.add(ContentType.objects.get(model=F1_Work.__name__))
    contains.obj_class.add(ContentType.objects.get(model=F1_Work.__name__))
    contains.obj_class.add(ContentType.objects.get(model=F3_Manifestation_Product_Type.__name__))
    contains.save()

    is_expressed_in = Property.objects.create(
        name="is expressed in",
        name_reverse="expresses",
    )
    is_expressed_in.subj_class.add(ContentType.objects.get(model=F1_Work.__name__))
    is_expressed_in.subj_class.add(ContentType.objects.get(model=F17_Aggregation_Work.__name__))
    is_expressed_in.obj_class.add(ContentType.objects.get(model=F3_Manifestation_Product_Type.__name__))
    is_expressed_in.save()

    is_in_chapter = Property.objects.create(
        name="is in chapter",
        name_reverse="contains work",
    )
    is_in_chapter.subj_class.add(ContentType.objects.get(model=F1_Work.__name__))
    is_in_chapter.obj_class.add(ContentType.objects.get(model=Chapter.__name__))

    is_in_chapter = Property.objects.create(
        name="is sub chapter of",
        name_reverse="contains chapter",
    )
    is_in_chapter.subj_class.add(ContentType.objects.get(model=Chapter.__name__))
    is_in_chapter.obj_class.add(ContentType.objects.get(model=Chapter.__name__))

    r13_is_realised_in = Property.objects.create(
        name="R13 is realised in",
        name_reverse="R13i realises",
    )
    r13_is_realised_in.subj_class.add(ContentType.objects.get(model=F21_Recording_Work.__name__))
    r13_is_realised_in.obj_class.add(ContentType.objects.get(model=F26_Recording.__name__))

    has_keyword = Property.objects.create(
        name="has keyword",
        name_reverse="is keyword of",
    )
    has_keyword.subj_class.add(ContentType.objects.get(model=F1_Work.__name__))
    has_keyword.obj_class.add(ContentType.objects.get(model=Keyword.__name__))
