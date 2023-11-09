import datetime
import re
import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.postgres.search import SearchVectorField
# from apis_core.apis_entities.models import AbstractEntity
from apis_core.apis_entities.models import TempEntityClass, TempTriple
import django_filters



@reversion.register(follow=["tempentityclass_ptr"])
class Xml_File(TempEntityClass):
    file_path = models.CharField(max_length=1024, blank=True, null=True)
    file_content = models.TextField(blank=True)

@reversion.register(follow=["tempentityclass_ptr"])
class Xml_Content_Dump(TempEntityClass):
    file_content = models.TextField(blank=True)


@reversion.register(follow=["tempentityclass_ptr"])
class E1_Crm_Entity(TempEntityClass):
    entity_id = models.CharField(max_length=1024, blank=True, null=True)
    date_hidden = models.BooleanField(blank=True, null=True)
    title_hidden = models.BooleanField(blank=True, null=True)
    vector_column_e1_set = SearchVectorField(null=True)
    vector_related_f10_set = SearchVectorField(null=True)
    vector_related_E40_set = SearchVectorField(null=True)
    vector_related_xml_content_dump_set = SearchVectorField(null=True)
    vector_related_xml_note_set = SearchVectorField(null=True)

    def get_entity_list_filter():
        class AdHocEntityListFilter(django_filters.FilterSet):
            class Meta:
                model = E1_Crm_Entity
                exclude = ["vector_column_e1_set", "vector_related_f10_set", "vector_related_E40_set", "vector_related_xml_content_dump_set", "vector_related_xml_note_set"]
        return AdHocEntityListFilter
    
    def save(self, *args, **kwargs):
        if self.start_date_written is not None and "/" in self.start_date_written:
            regex_match = re.match(r"^([0-9]{4})/([0-9]{4})$", self.start_date_written)
            if regex_match is not None:
                try:
                    if int(regex_match.group(2)) == int(regex_match.group(1)) + 1:
                        self.start_date = datetime.datetime(year=int(regex_match.group(1)), month=12, day=31)
                        super(E1_Crm_Entity, self).save(parse_dates=False, *args, **kwargs)
                        return
                
                except:
                    pass

        if self.start_date is not None:
            if isinstance(self.start_date, str):
                regex_match = re.match(r"^([0-9]{4})-([0-9]{2})$", self.start_date)
                if regex_match is not None:
                    try:
                        self.start_date = datetime.datetime(year=int(regex_match.group(1)), month=int(regex_match.group(2)), day=1)                    
                    except:
                        pass
            if isinstance(self.start_date, datetime.datetime):
                super(E1_Crm_Entity, self).save(parse_dates=False, *args, **kwargs)
                return

        super(E1_Crm_Entity, self).save(*args, **kwargs)



@reversion.register(follow=["tempentityclass_ptr"])
class E40_Legal_Body(E1_Crm_Entity):
    # for institutions and publishers
    institution_id = models.CharField(max_length=1024, blank=True, null=True)
    institution_type = models.CharField(max_length=1024, blank=True, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_id = self.institution_id


@reversion.register(follow=["tempentityclass_ptr"])
class E55_Type(E1_Crm_Entity):
    pass


@reversion.register(follow=["tempentityclass_ptr"])
class F1_Work(E1_Crm_Entity):
    
    untertitel = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Untertitel")
    idno = models.CharField(max_length=1024, blank=True, null=True)
    index_in_chapter = models.IntegerField(blank=True, null=True)
    index_desc = models.CharField(max_length=1024, blank=True, null=True)
    gnd_url = models.URLField(blank=True, null=True)
    genre = models.CharField(max_length=1024, blank=True, null=True)
    
    anmerkung = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name="Anmerkung"
    )
    
    short = models.CharField(max_length=1024, blank=True, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_id = self.idno

@reversion.register(follow=["tempentityclass_ptr"])
class Honour(E1_Crm_Entity):
    honour_id = models.CharField(max_length=1024, blank=True, null=True)
    index_in_chapter = models.IntegerField(blank=True, null=True)
    short = models.CharField(max_length=1024, blank=True, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_id = self.honour_id

@reversion.register(follow=["tempentityclass_ptr"])
class F3_Manifestation_Product_Type(E1_Crm_Entity):
    idno = models.CharField(max_length=1024, blank=True, null=True)
    bibl_id = models.CharField(max_length=1024, blank=True, null=True) # TODO __sresch__ : Maybe replace with idno?
    note = models.TextField(blank=True, null=True)
    series = models.CharField(max_length=1024, blank=True, null=True)
    edition = models.CharField(max_length=1024, blank=True, null=True)
    page = models.CharField(max_length=1024, blank=True, null=True)
    issue = models.CharField(max_length=1024, blank=True, null=True)
    volume = models.CharField(max_length=1024, blank=True, null=True)
    ref_target = models.URLField(max_length=1024, blank=True, null=True)
    ref_accessed = models.CharField(max_length=1024, blank=True, null=True)
    text_language = models.CharField(max_length=1024, blank=True, null=True)
    short = models.CharField(max_length=1024, blank=True, null=True)
    untertitel = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Untertitel")
    scope_style = models.CharField(max_length=1024, blank=True, null=True)
    koha_id = models.CharField(max_length=1024, blank=True, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_id = self.bibl_id
    def filtered_triples_from_obj(self):
        return self.triple_set_from_obj.exclude(prop__name="has host")
    def filtered_triples_from_subj(self):
        return self.triple_set_from_subj.exclude(prop__name__in=["data read from file"])

@reversion.register(follow=["tempentityclass_ptr"])
class F9_Place(E1_Crm_Entity):
    place_id = models.CharField(max_length=1024, blank=True, null=True)
    country = models.CharField(max_length=1024, blank=True, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_id = self.place_id
    


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_id = self.pers_id


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
class F26_Recording(E1_Crm_Entity):
    note = models.TextField(blank=True, null=True)
    airing_date = models.CharField(max_length=1024, blank=True, null=True)
    broadcast_id = models.CharField(max_length=1024, blank=True, null=True)
    recording_type = models.CharField(max_length=1024, blank=True, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_id = self.broadcast_id


@reversion.register(follow=["tempentityclass_ptr"])
class F31_Performance(E1_Crm_Entity):
    note = models.TextField(blank=True, null=True)
    performance_id = models.CharField(max_length=1024, blank=True, null=True)
    performance_type = models.CharField(max_length=1024, blank=True, null=True)
    short = models.CharField(max_length=1024, blank=True, null=True)
    # TODO: consider changing this to a e55 relation
    category = models.CharField(max_length=1024, blank=True, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_id = self.performance_id
    def filtered_triples_from_subj(self):
        return self.triple_set_from_subj.exclude(prop__name__in=["data read from file"])


@reversion.register(follow=["tempentityclass_ptr"])
class Chapter(TempEntityClass):
    chapter_number = models.CharField(max_length=1024, blank=True, null=True)
    chapter_type = models.CharField(max_length=1024, blank=True, null=True)

@reversion.register(follow=["tempentityclass_ptr"])
class Keyword(TempEntityClass):
    keyword_id = models.CharField(max_length=1024, blank=True, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_id = self.keyword_id

@reversion.register(follow=["tempentityclass_ptr"])
class XMLNote(TempEntityClass):
    content = models.TextField(blank=True, null=True)
    context = models.CharField(max_length=1024, blank=True, null=True)
    rendition = models.CharField(max_length=1024, blank=True, null=True)
    type = models.CharField(max_length=1024, blank=True, null=True)

@reversion.register(follow=["tempentityclass_ptr"])
class E38_Image(E1_Crm_Entity):
    image_id = models.CharField(max_length=1024, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    alt_text = models.CharField(max_length=1024, blank=True, null=True)
    filename = models.CharField(max_length=1024, blank=True, null=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_id = self.image_id

@reversion.register(follow=["temptriple_ptr"])
class InChapterTriple(TempTriple):
    index_in_chapter = models.IntegerField(blank=True, null=True)

@reversion.register(follow=["temptriple_ptr"])
class RenditionTriple(TempTriple):
    rendition_hidden = models.BooleanField(blank=True, null=True)

def construct_properties():
    
    from apis_core.apis_vocabularies.models import TextType
    from apis_core.apis_metainfo.models import Collection
    from apis_core.apis_relations.models import Property
    # from apis_highlighter.models import AnnotationProject, Project
    from django.contrib.auth.models import User
    
    # TextType.objects.all().delete()
    # tt = TextType.objects.create(entity="E1_Crm_Entity")
    #tt.collections.add(Collection.objects.get_or_create(name="manually created entity"))
    
    # AnnotationProject.objects.create(name="test__annotation_project_1")
    # Project.objects.create(name="test__project_1", user=User.objects.first())
    
    Property.objects.all().delete()
    
    data_read_from = Property.objects.create(
        name="data read from file",
        name_reverse="provides data to",
    )
    data_read_from.subj_class.add(ContentType.objects.get_for_model(model=E1_Crm_Entity))
    data_read_from.subj_class.add(ContentType.objects.get_for_model(model=Chapter))
    data_read_from.subj_class.add(ContentType.objects.get_for_model(model=Keyword))
    data_read_from.subj_class.add(ContentType.objects.get_for_model(model=XMLNote))
    data_read_from.obj_class.add(ContentType.objects.get_for_model(model=Xml_File))
    
    
    was_defined_primarily_in = Property.objects.create(
        name="was defined primarily in",
        name_reverse="defined primarily",
    )
    was_defined_primarily_in.subj_class.add(ContentType.objects.get_for_model(model=E1_Crm_Entity))
    was_defined_primarily_in.subj_class.add(ContentType.objects.get_for_model(model=XMLNote))
    was_defined_primarily_in.obj_class.add(ContentType.objects.get_for_model(model=Xml_File))
    
    p2_has_type = Property.objects.create(
        name="p2 has type",
        name_reverse="p2i is type of",
    )
    p2_has_type.subj_class.add(ContentType.objects.get_for_model(model=E1_Crm_Entity))
    p2_has_type.obj_class.add(ContentType.objects.get_for_model(model=E55_Type))
    p2_has_type.save()
    
    p127_has_broader_term = Property.objects.create(
        name="p127 has broader term",
        name_reverse="p127i has narrower term",
    )
    p127_has_broader_term.subj_class.add(ContentType.objects.get_for_model(model=E55_Type))
    p127_has_broader_term.obj_class.add(ContentType.objects.get_for_model(model=E55_Type))
    p127_has_broader_term.save()
    
    host = Property.objects.create(
        name="has host",
        name_reverse="is host"
    )
    host.subj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    host.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    host.save()
    
    is_author_of = Property.objects.create(
        name="is author of",
        name_reverse="has been written by",
    )
    is_author_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_author_of.subj_class.add(ContentType.objects.get_for_model(model=E40_Legal_Body))
    is_author_of.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_author_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_author_of.save()
    
    is_interviewer_of = Property.objects.create(
        name="is interviewer of",
        name_reverse="has been interviewed by",
    )
    is_interviewer_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_interviewer_of.subj_class.add(ContentType.objects.get_for_model(model=E40_Legal_Body))
    is_interviewer_of.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_interviewer_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_interviewer_of.save()
    
    is_interviewee_of = Property.objects.create(
        name="is interviewee of",
        name_reverse="has interviewee",
    )
    is_interviewee_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_interviewee_of.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_interviewee_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_interviewee_of.save()
    
    is_adaptioner_of = Property.objects.create(
        name="is adaptioner of",
        name_reverse="has adaptioner",
    )
    is_adaptioner_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_adaptioner_of.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_adaptioner_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_adaptioner_of.save()
    
    is_translator_of = Property.objects.create(
        name="is translator of",
        name_reverse="has been translated by",
    )
    is_translator_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_translator_of.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_translator_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    # is_translator_of.obj_class.add(ContentType.objects.get_for_model(model=F20_Performance_Work))
    is_translator_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_translator_of.save()
    
    is_translator_of = Property.objects.create(
        name_reverse="is translation of",
        name="is original for translation",
    )
    is_translator_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_translator_of.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_translator_of.save()
    
    is_editor_of = Property.objects.create(
        name="is editor of",
        name_reverse="has been edited by",
    )
    is_editor_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_editor_of.subj_class.add(ContentType.objects.get_for_model(model=E40_Legal_Body))
    is_editor_of.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_editor_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_editor_of.save()
    
    is_publisher_of = Property.objects.create(
        name="is publisher of",
        name_reverse="has been published by",
    )
    is_publisher_of.subj_class.add(ContentType.objects.get_for_model(model=E40_Legal_Body))
    is_publisher_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_publisher_of.save()
    
    is_posessor_of = Property.objects.create(
        name="is posessor of",
        name_reverse="is possessed by",
    )
    is_posessor_of.subj_class.add(ContentType.objects.get_for_model(model=E40_Legal_Body))
    is_posessor_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_posessor_of.save()
    
    is_director_of = Property.objects.create(
        name="is director of",
        name_reverse="has been directed by",
    )
    is_director_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_director_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_director_of.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_director_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_director_of.save()
    
    is_contributor_of = Property.objects.create(
        name="is contributor of",
        name_reverse="has been contributed by",
    )
    is_contributor_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_contributor_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_contributor_of.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_contributor_of.save()
    
    is_composer_of = Property.objects.create(
        name="is composer of",
        name_reverse="has been composed by",
    )
    is_composer_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_composer_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_composer_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_composer_of.save()
    
    is_voice_actor_of = Property.objects.create(
        name="is voice actor of",
        name_reverse="has been voice acted by",
    )
    is_voice_actor_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_voice_actor_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_voice_actor_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_voice_actor_of.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_voice_actor_of.save()
    
    is_actor_of = Property.objects.create(
        name="is actor of",
        name_reverse="has been acted by",
    )
    is_actor_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_actor_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_actor_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_actor_of.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_actor_of.save()
    
    is_musician_of = Property.objects.create(
        name="is musician of",
        name_reverse="has been musically accompanied by",
    )
    is_musician_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_musician_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_musician_of.save()
    
    is_singer_of = Property.objects.create(
        name="is singer of",
        name_reverse="has been sung by",
    )
    is_singer_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_singer_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_singer_of.save()
    
    is_musical_director_of = Property.objects.create(
        name="is musical director of",
        name_reverse="has been musically directed by",
    )
    is_musical_director_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_musical_director_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_musical_director_of.save()
    
    is_choreographer_of = Property.objects.create(
        name="is choreographer of",
        name_reverse="has choreographer",
    )
    is_choreographer_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_choreographer_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_choreographer_of.save()

    is_redactor_of = Property.objects.create(
        name="is redactor of",
        name_reverse="has redactor",
    )
    is_redactor_of.subj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_redactor_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_redactor_of.save()
    
    was_published_in = Property.objects.create(
        name="was published in",
        name_reverse="is publication place of",
    )
    was_published_in.subj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    was_published_in.obj_class.add(ContentType.objects.get_for_model(model=F9_Place))
    was_published_in.save()
    
    has_been_performed_at = Property.objects.create(
        name="has been performed at",
        name_reverse="has had performance",
    )
    has_been_performed_at.subj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    has_been_performed_at.subj_class.add(ContentType.objects.get_for_model(model=F26_Recording))
    has_been_performed_at.obj_class.add(ContentType.objects.get_for_model(model=E40_Legal_Body))
    has_been_performed_at.save()
    
    is_organizer_of = Property.objects.create(
        name="is organizer of",
        name_reverse="has organizer",
    )
    is_organizer_of.subj_class.add(ContentType.objects.get_for_model(model=E40_Legal_Body))
    is_organizer_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_organizer_of.obj_class.add(ContentType.objects.get_for_model(model=F26_Recording))
    is_organizer_of.obj_class.add(ContentType.objects.get_for_model(model=Honour))
    is_organizer_of.save()
    
    is_broadcaster_of = Property.objects.create(
        name="is broadcaster of",
        name_reverse="has broadcaster",
    )
    is_broadcaster_of.subj_class.add(ContentType.objects.get_for_model(model=E40_Legal_Body))
    is_broadcaster_of.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_broadcaster_of.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    is_broadcaster_of.obj_class.add(ContentType.objects.get_for_model(model=F26_Recording))
    is_broadcaster_of.obj_class.add(ContentType.objects.get_for_model(model=Honour))
    is_broadcaster_of.save()
    
    has_been_performed_in = Property.objects.create(
        name="has been performed in",
        name_reverse="was performance of",
    )
    has_been_performed_in.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    has_been_performed_in.obj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    has_been_performed_in.save()
    
    contains = Property.objects.create(
        name="contains",
        name_reverse="is contained in",
    )
    contains.subj_class.add(ContentType.objects.get_for_model(model=F17_Aggregation_Work))
    contains.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    contains.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    contains.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    contains.save()
    
    is_expressed_in = Property.objects.create(
        name="is expressed in",
        name_reverse="expresses",
    )
    is_expressed_in.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_expressed_in.subj_class.add(ContentType.objects.get_for_model(model=F17_Aggregation_Work))
    is_expressed_in.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_expressed_in.save()
    
    is_expressed_in = Property.objects.create(
        name="is reported in",
        name_reverse="reports",
    )
    is_expressed_in.subj_class.add(ContentType.objects.get_for_model(model=Honour))
    is_expressed_in.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
    is_expressed_in.save()
    
    is_in_chapter = Property.objects.create(
        name="is in chapter",
        name_reverse="contains work",
    )
    is_in_chapter.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_in_chapter.subj_class.add(ContentType.objects.get_for_model(model=Honour))
    is_in_chapter.obj_class.add(ContentType.objects.get_for_model(model=Chapter))
    
    is_in_chapter = Property.objects.create(
        name="is sub chapter of",
        name_reverse="contains chapter",
    )
    is_in_chapter.subj_class.add(ContentType.objects.get_for_model(model=Chapter))
    is_in_chapter.obj_class.add(ContentType.objects.get_for_model(model=Chapter))
    
    r13_is_realised_in = Property.objects.create(
        name="R13 is realised in",
        name_reverse="R13i realises",
    )
    r13_is_realised_in.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    r13_is_realised_in.obj_class.add(ContentType.objects.get_for_model(model=F26_Recording))
    
    has_keyword = Property.objects.create(
        name="has keyword",
        name_reverse="is keyword of",
    )
    has_keyword.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    has_keyword.subj_class.add(ContentType.objects.get_for_model(model=Honour))
    has_keyword.obj_class.add(ContentType.objects.get_for_model(model=Keyword))
    
    has_note = Property.objects.create(
        name="has note",
        name_reverse="is note of",
    )
    has_note.subj_class.add(ContentType.objects.get_for_model(model=E1_Crm_Entity))
    has_note.obj_class.add(ContentType.objects.get_for_model(model=XMLNote))
    
    is_about = Property.objects.create(
        name="is about",
        name_reverse="is discussed in",
    )
    is_about.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_about.subj_class.add(ContentType.objects.get_for_model(model=Chapter))
    is_about.obj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    is_about.obj_class.add(ContentType.objects.get_for_model(model=F10_Person))
    is_about.obj_class.add(ContentType.objects.get_for_model(model=E40_Legal_Body))
    is_about.obj_class.add(ContentType.objects.get_for_model(model=Honour))
    is_about.obj_class.add(ContentType.objects.get_for_model(model=Chapter))
    
    is_about = Property.objects.create(
        name="took place in",
        name_reverse="was venue of",
    )
    is_about.subj_class.add(ContentType.objects.get_for_model(model=Honour))
    is_about.obj_class.add(ContentType.objects.get_for_model(model=F9_Place))
    
    is_located_in = Property.objects.create(
        name="is located in",
        name_reverse="is location of",
    )
    is_located_in.subj_class.add(ContentType.objects.get_for_model(model=E40_Legal_Body))
    is_located_in.obj_class.add(ContentType.objects.get_for_model(model=F9_Place))

    data_read_from_dump = Property.objects.create(
        name="data read from dump",
        name_reverse="is dump of",
    )
    data_read_from_dump.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    data_read_from_dump.obj_class.add(ContentType.objects.get_for_model(model=Xml_Content_Dump))

    has_image = Property.objects.create(
        name="has image",
        name_reverse="is image of",
    )
    has_image.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    has_image.subj_class.add(ContentType.objects.get_for_model(model=Honour))
    has_image.obj_class.add(ContentType.objects.get_for_model(model=E38_Image))

    has_image = Property.objects.create(
        name="has image for translation",
        name_reverse="is translation image of",
    )
    has_image.subj_class.add(ContentType.objects.get_for_model(model=F1_Work))
    has_image.subj_class.add(ContentType.objects.get_for_model(model=Honour))
    has_image.obj_class.add(ContentType.objects.get_for_model(model=E38_Image))

    has_recording_artefact = Property.objects.create(
        name="has recording artefact",
        name_reverse="is recording event"
    )
    has_recording_artefact.subj_class.add(ContentType.objects.get_for_model(model=F31_Performance))
    has_recording_artefact.obj_class.add(ContentType.objects.get_for_model(model=F3_Manifestation_Product_Type))
