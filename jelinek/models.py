import reversion
from django.contrib.contenttypes.models import ContentType
from django.db import models
# from apis_core.apis_entities.models import AbstractEntity
from apis_core.apis_entities.models import TempEntityClass



class XmlFile(TempEntityClass):

    file_path = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Untertitel")

@reversion.register(follow=["tempentityclass_ptr"])
class E1_Crm_Entity(TempEntityClass):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class E40_Legal_Body(E1_Crm_Entity):

    # for institutions and publishers

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class E55_Type(E1_Crm_Entity):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class F1_Work(E1_Crm_Entity):

    untertitel = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Untertitel")
    idno = models.CharField(max_length=1024, blank=True, null=True)

    anmerkung = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name="Anmerkung"
    )


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


@reversion.register(follow=["tempentityclass_ptr"])
class F9_Place(E1_Crm_Entity):

    pass


@reversion.register(follow=["tempentityclass_ptr"])
class F10_Person(E1_Crm_Entity):

    # TODO: Find a solution for if no name is given, but surname and forename exist

    role =  models.CharField(max_length=1024, blank=True, null=True)
    pers_id = models.CharField(max_length=1024, blank=True, null=True)

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

    note = models.CharField(max_length=1024, blank=True, null=True)

    # TODO: consider changing this to a e55 relation
    category = models.CharField(max_length=1024, blank=True, null=True)


@reversion.register(follow=["tempentityclass_ptr"])
class Chapter(TempEntityClass):

    chapter_number = models.CharField(max_length=1024, blank=True, null=True)


def construct_properties():

    from apis_core.apis_relations.models import Property
    from apis_core.apis_metainfo.models import RootObject

    RootObject.objects.all().delete()

    data_read_from = Property.objects.create(
        name="data read from file",
        name_reverse="provides data to",
    )
    data_read_from.subj_class.add(ContentType.objects.get(model=E1_Crm_Entity.__name__))
    data_read_from.obj_class.add(ContentType.objects.get(model=XmlFile.__name__))

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
    is_director_of.obj_class.add(ContentType.objects.get(model=F20_Performance_Work.__name__))
    is_director_of.save()

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
    has_been_performed_at.subj_class.add(ContentType.objects.get(model=F20_Performance_Work.__name__))
    has_been_performed_at.obj_class.add(ContentType.objects.get(model=E40_Legal_Body.__name__))
    has_been_performed_at.save()

    contains = Property.objects.create(
        name="contains",
        name_reverse="is contained in",
    )
    contains.subj_class.add(ContentType.objects.get(model=F17_Aggregation_Work.__name__))
    contains.obj_class.add(ContentType.objects.get(model=F1_Work.__name__))
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


# Old ontology, defined by Daniel's google doc (either update the doc to reality of tei files, or vice versa)
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Inszenierung(TempEntityClass):
#
#     pass
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Auffuehrung(TempEntityClass):
#
#     pass
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Ereignis(TempEntityClass):
#
#     pass
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Kapitel(TempEntityClass):
#
#     cidoc_id = "F50"
#
#     kapitel_nummer = models.CharField(max_length=255, null=True, blank=True)
#
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Publisher(TempEntityClass):
#
#     pass
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Textausschnitt(TempEntityClass):
#
#     pass
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Aufzeichnung(TempEntityClass):
#
#     pass
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Thema(TempEntityClass):
#
#     pass
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Einteiliges_Work(TempEntityClass):
#
#     pass
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Sammelwerk(TempEntityClass):
#
#     pass
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Performatives_Work(TempEntityClass):
#
#     pass
#
#
# @reversion.register(follow=["tempentityclass_ptr"])
# class Genre(TempEntityClass):
#
#     kapitelnummer = models.CharField(max_length=30, blank=True, null=True)
#
#
# def construct_properties():
#
#     hat_genre = Property.objects.create(
#         name="hat Genre",
#         name_reverse="ist Genre von"
#     )
#     hat_genre.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     hat_genre.obj_class.add(ContentType.objects.get(model=Genre.__name__))
#     hat_genre.cidoc_id = "P2"
#     hat_genre.save()
#
#
#     klasse = VocabsBaseClass.objects.create(name="Klasse")
#     einstelliges_Work = VocabsBaseClass.objects.create(name="Einstelliges Work", parent_class=klasse)
#     einstelliges_Work.cidoc_id = "F14"
#     sammelWork = VocabsBaseClass.objects.create(name="SammelWork", parent_class=klasse)
#     sammelWork.cidoc_id = "F17"
#     performatives_Work = VocabsBaseClass.objects.create(name="Performatives Work", parent_class=klasse)
#     performatives_Work.cidoc_id = "F20"
#
#     hat_klasse = Property.objects.create(
#         name="hat Klasse",
#         name_reverse="ist Klasse von"
#     )
#     hat_klasse.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     hat_klasse.obj_class.add(ContentType.objects.get(model=klasse.__class__.__name__))
#     hat_klasse.save()
#
#     Workkategorie = VocabsBaseClass.objects.create(name="Workkategorie")
#     originaltext = VocabsBaseClass.objects.create(name="Originaltext", parent_class=Workkategorie)
#     bearbeitung = VocabsBaseClass.objects.create(name="Bearbeitung", parent_class=klasse)
#     uebersetzung = VocabsBaseClass.objects.create(name="Übersetzung", parent_class=klasse)
#
#     hat_Workkategorie = Property.objects.create(
#         name="hat Workkategorie",
#         name_reverse="ist Workkategorie von"
#     )
#     hat_Workkategorie.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     hat_Workkategorie.obj_class.add(ContentType.objects.get(model=Workkategorie.__class__.__name__))
#
#
#     kommentar = TextType.objects.create(name="Kommentar", entity="F1_Work")
#     personal = TextType.objects.create(name="Personal", entity="F1_Work")
#
#     hat_urheber = Property.objects.create(
#         name="hat Urheber",
#         name_reverse="ist Urheber von"
#     )
#     hat_urheber.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     hat_urheber.obj_class.add(ContentType.objects.get(model=Person.__name__))
#     hat_urheber.save()
#
#     wurde_durchgefuehrt_von = Property.objects.create(
#         name="wurde durchgeführt von",
#         name_reverse="führte"
#     )
#     wurde_durchgefuehrt_von.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     wurde_durchgefuehrt_von.obj_class.add(ContentType.objects.get(model=Person.__name__))
#     wurde_durchgefuehrt_von.save()
#
#     wurde_durchgefuehrt_mit = Property.objects.create(
#         name="wurde durchgeführt mit",
#         name_reverse="führte mit"
#     )
#     wurde_durchgefuehrt_mit.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     wurde_durchgefuehrt_mit.obj_class.add(ContentType.objects.get(model=Person.__name__))
#     wurde_durchgefuehrt_mit.save()
#
#     hat_strukturellen_teil = Property.objects.create(
#         name="hat strukturellen Teil",
#         name_reverse="ist struktureller Teil von"
#     )
#     hat_strukturellen_teil.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     hat_strukturellen_teil.obj_class.add(ContentType.objects.get(model=Work.__name__))
#     hat_strukturellen_teil.cidoc_id = "P148"
#     hat_strukturellen_teil.save()
#
#     ist_adaptiert_in = Property.objects.create(
#         name="ist adaptiert in",
#         name_reverse="ist Adaption von"
#     )
#     ist_adaptiert_in.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     ist_adaptiert_in.obj_class.add(ContentType.objects.get(model=Work.__name__))
#     ist_adaptiert_in.save()
#
#     ist_uebersetzung_von = Property.objects.create(
#         name="ist Übersetzung von",
#         name_reverse="verarbeitet"
#     )
#     ist_uebersetzung_von.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     ist_uebersetzung_von.obj_class.add(ContentType.objects.get(model=Work.__name__))
#     ist_uebersetzung_von.cidoc_id = "F1-R2->F1->R2.1"
#     ist_uebersetzung_von.save()
#
#     wurde_inszeniert_in = Property.objects.create(
#         name="wurde inszeniert in",
#         name_reverse="ist Instenzierung von"
#     )
#     wurde_inszeniert_in.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     wurde_inszeniert_in.obj_class.add(ContentType.objects.get(model=Work.__name__))
#     wurde_inszeniert_in.cidoc_id = "R25"
#     wurde_inszeniert_in.save()
#
#     ist_teil_von_kapitel = Property.objects.create(
#         name="enthält",
#         name_reverse="ist Teil von Kapitel"
#     )
#     ist_teil_von_kapitel.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     ist_teil_von_kapitel.obj_class.add(ContentType.objects.get(model=Kapitel.__name__))
#     ist_teil_von_kapitel.cidoc_id = "R1"
#     ist_teil_von_kapitel.save()
#
#     steht_in_zusammenhang_mit = Property.objects.create(
#         name="steht in Zusammenhang mit",
#         name_reverse="steht in Zusammenhang mit"
#     )
#     steht_in_zusammenhang_mit.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     steht_in_zusammenhang_mit.obj_class.add(ContentType.objects.get(model=Ereignis.__name__))
#     steht_in_zusammenhang_mit.save()
#
#     wird_thematisiert_in = Property.objects.create(
#         name="wird thematisiert in",
#         name_reverse="thematisiert"
#     )
#     wird_thematisiert_in.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     wird_thematisiert_in.obj_class.add(ContentType.objects.get(model=Work.__name__))
#     wird_thematisiert_in.save()
#
#     hat_textbeispiel_in = Property.objects.create(
#         name="hat Textbeispiel in",
#         name_reverse="ist Beispiel für"
#     )
#     hat_textbeispiel_in.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     hat_textbeispiel_in.obj_class.add(ContentType.objects.get(model=Textausschnitt.__name__))
#     hat_textbeispiel_in.save()
#
#     ist_realisiert_in = Property.objects.create(
#         name="ist realisiert in",
#         name_reverse="realisiert"
#     )
#     ist_realisiert_in.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     ist_realisiert_in.obj_class.add(ContentType.objects.get(model=Expression.__name__))
#     ist_realisiert_in.cidoc_id = "R3"
#     ist_realisiert_in.save()
#
#     verbreitet_durch = Property.objects.create(
#         name="verbreitet durch",
#         name_reverse="verbreitet"
#     )
#     verbreitet_durch.subj_class.add(ContentType.objects.get(model=Expression.__name__))
#     verbreitet_durch.obj_class.add(ContentType.objects.get(model=Publikation.__name__))
#     verbreitet_durch.cidoc_id = "R4"
#     verbreitet_durch.save()
#
#     inkorporiert = Property.objects.create(
#         name="inkorporiert",
#         name_reverse="ist inkorporiert in"
#     )
#     inkorporiert.subj_class.add(ContentType.objects.get(model=Expression.__name__))
#     inkorporiert.obj_class.add(ContentType.objects.get(model=Expression.__name__))
#     inkorporiert.cidoc_id = "P165"
#     inkorporiert.save()
#
#     publikations_typ = VocabsBaseClass.objects.create(name="Publikationstyp")
#     erstdruck = VocabsBaseClass.objects.create(name="Erstdruck", parent_class=publikations_typ)
#
#
#     hat_publikations_typ = Property.objects.create(
#         name="hat Publikationstyp",
#         name_reverse="ist Publikationstyp von"
#     )
#     hat_publikations_typ.subj_class.add(ContentType.objects.get(model=Work.__name__))
#     hat_publikations_typ.obj_class.add(ContentType.objects.get(model=publikations_typ.__class__.__name__))
#     hat_publikations_typ.cidoc_id = "P2"
#     hat_publikations_typ.save()
#
#     ist_spielstaette_von = Property.objects.create(
#         name="ist Spielstätte von",
#         name_reverse="hat Spielstätte"
#     )
#     ist_spielstaette_von.subj_class.add(ContentType.objects.get(model=Ort.__name__))
#     ist_spielstaette_von.obj_class.add(ContentType.objects.get(model=Koerperschaft.__name__))
#     ist_spielstaette_von.save()
#
#     befindet_sich_in = Property.objects.create(
#         name="befindet sich in",
#         name_reverse="hat"
#     )
#     befindet_sich_in.subj_class.add(ContentType.objects.get(model=Koerperschaft.__name__))
#     befindet_sich_in.obj_class.add(ContentType.objects.get(model=Ort.__name__))
#     befindet_sich_in.save()
#
#     fand_statt_in = Property.objects.create(
#         name="fand statt in",
#         name_reverse="ist Veranstaltungsort von"
#     )
#     fand_statt_in.subj_class.add(ContentType.objects.get(model=Inszenierung.__name__))
#     fand_statt_in.obj_class.add(ContentType.objects.get(model=Ort.__name__))
#     fand_statt_in.save()
#
#     fuehrte_auf = Property.objects.create(
#         name="führte auf",
#         name_reverse="wurde aufgeführt von"
#     )
#     fuehrte_auf.subj_class.add(ContentType.objects.get(model=Koerperschaft.__name__))
#     fuehrte_auf.obj_class.add(ContentType.objects.get(model=Inszenierung.__name__))
#     fuehrte_auf.save()
#
#     hat_subgenre = Property.objects.create(
#         name="hat Subgenre",
#         name_reverse="ist Subgenre von",
#     )
#     hat_subgenre.subj_class.add(ContentType.objects.get(model=Genre.__name__))
#     hat_subgenre.obj_class.add(ContentType.objects.get(model=Genre.__name__))
#     hat_subgenre.save()
#
#     g = Genre.objects.create(name="Worke", kapitelnummer="1")
#     g = Genre.objects.create(name="Lyrik", kapitelnummer="1.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Buchpublikationen", kapitelnummer="1.1.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Einzelne Gedichtabdrucke", kapitelnummer="1.1.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Weitere Abdrucke von Gedichtenaus den Buchpublikationen", kapitelnummer="1.1.2.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.1.2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Weitere Gedichte (ausschließlich als Einzelabdrucke)", kapitelnummer="1.1.2.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.1.2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Romane", kapitelnummer="1.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Kurzprosa", kapitelnummer="1.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Theatertexte", kapitelnummer="1.4")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sammelbände", kapitelnummer="1.4.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.4").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Einzelne Worke", kapitelnummer="1.4.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.4").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Hörspiele", kapitelnummer="1.5")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Drehbücher und Texte für Filme", kapitelnummer="1.6")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Kompositionen", kapitelnummer="1.7")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Texte für Kompositionen", kapitelnummer="1.8")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Libretti | Oper", kapitelnummer="1.9")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Libretti | Ballett", kapitelnummer="1.10")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Essayistische Texte, Reden und Statements", kapitelnummer="1.11")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sammelbände", kapitelnummer="1.11.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Persönliches und Biographisches", kapitelnummer="1.11.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zum Schwerpunkt bei den Salzburger Festspielen 1998", kapitelnummer="1.11.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zum Aufführungsverbot 2000", kapitelnummer="1.11.4")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zu eigenen Worken", kapitelnummer="1.11.5")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Lyrik", kapitelnummer="1.11.5.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Romane", kapitelnummer="1.11.5.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Theatertexte", kapitelnummer="1.11.5.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sonstiges zu Mode und Modeschöpfern", kapitelnummer="")
#     g = Genre.objects.create(name="Hörspiele (eigene und Bearbeitungen von anderen)", kapitelnummer="1.11.5.4")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Drehbücher (eigene und Bearbeitungen von anderen)", kapitelnummer="1.11.5.5")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Kompositionen, Texte für Musik, Libretti(eigene und Bearbeitungen von anderen)", kapitelnummer="1.11.5.6")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Essayistische Texte", kapitelnummer="1.11.5.7")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Übersetzungen", kapitelnummer="1.11.5.8")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Installationen", kapitelnummer="1.11.5.9")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Allgemein über ihr Schreiben und ihre Ästhetik (Schreibtradition, Schreibverfahren)", kapitelnummer="1.11.6")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Dankesreden anlässlich von Preisen [ Seklit. S.] (Schreibtradition, Schreibverfahren)", kapitelnummer="1.11.7")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zur Literatur", kapitelnummer="1.11.8")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zu einzelnen AutorInnen (KünstlerIn)", kapitelnummer="1.11.8.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.8").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sonstiges zur Literatur", kapitelnummer="1.11.8.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.8").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Rezensionen für den Sender Freies Berlin", kapitelnummer="1.11.8.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.8").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Rezensionen für Extrablatt", kapitelnummer="1.11.8.4")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.8").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zum Theater", kapitelnummer="1.11.9")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zu einzelnen Theaterleuten (Theaterästhetik)", kapitelnummer="1.11.9.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.9").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sonstiges zum Theater (Theaterästhetik)", kapitelnummer="1.11.9.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.9").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zum Film", kapitelnummer="1.11.10")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zu einzelnen RegisseurInnen und SchauspielerInnen (KünstlerIn)", kapitelnummer="1.11.10.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.10").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zur bildenden Kunst, Architektur und Fotografie", kapitelnummer="1.11.11")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zu einzelnen KünstlerInnen (KünstlerIn)", kapitelnummer="1.11.11.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sonstiges zur bildenden Kunst, Architektur und Fotografie", kapitelnummer="1.11.11.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zu Mode und Modeschöpfern", kapitelnummer="1.11.12")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zur Musik", kapitelnummer="1.11.13")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zu einzelnen MusikerInnen (KünstlerIn)", kapitelnummer="1.11.13.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.13").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sonstiges zur Musik", kapitelnummer="1.11.13.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.13").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zur Wissenschaft und Psychoanalyse", kapitelnummer="1.11.14")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zur internationalen Politik und Gesellschaft", kapitelnummer="1.11.15")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zur österreichischen Politik und Gesellschaft (Österreich)", kapitelnummer="1.11.16")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Essays, Beiträge", kapitelnummer="1.11.16.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.16").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Demoreden, Reden, vorgetragene Texte", kapitelnummer="1.11.16.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.16").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Flugblätter, offene Briefe", kapitelnummer="1.11.16.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.16").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Leserbriefe", kapitelnummer="1.11.16.4")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.16").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Wahlempfehlungen", kapitelnummer="1.11.16.5")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.16").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Statements", kapitelnummer="1.11.16.6")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.16").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zu Frauenfragen", kapitelnummer="1.11.17")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zu Medien", kapitelnummer="1.11.18")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zur * Kronen Zeitung", kapitelnummer="1.11.18.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.18").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sonstiges zu Medien", kapitelnummer="1.11.18.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11.18").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Diverses", kapitelnummer="1.11.19")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.11").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Übersetzungen", kapitelnummer="1.12")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Lyrik", kapitelnummer="1.12.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.12").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Prosatexte", kapitelnummer="1.12.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.12").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Theaterstücke", kapitelnummer="1.12.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.12").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Texte für Installationen und Projektionen, Fotoarbeiten", kapitelnummer="1.13")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Herausgeberin- und Redaktionstätigkeit", kapitelnummer="1.14")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Buchpublikationen", kapitelnummer="1.14.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.14").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Zeitschriften", kapitelnummer="1.14.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.14").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Internetprojekte", kapitelnummer="1.14.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="1.14").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Übersetzte Worke", kapitelnummer="2")
#     g = Genre.objects.create(name="Lyrik", kapitelnummer="2.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sammelbän de", kapitelnummer="2.1.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2.1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Einzelne Gedichte", kapitelnummer="2.1.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2.1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Romane", kapitelnummer="2.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sammelbän de", kapitelnummer="2.2.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2.2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Einzelne Romane", kapitelnummer="2.2.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2.2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Kurzprosa", kapitelnummer="2.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Theatertexte", kapitelnummer="2.4")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Sammelbände", kapitelnummer="2.4.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2.4").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Einzelne Theatertexte", kapitelnummer="2.4.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2.4").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Hörspiele", kapitelnummer="2.5")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Drehbücher und Texte für Filme", kapitelnummer="2.6")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Libretti", kapitelnummer="2.7")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Übersetzungen", kapitelnummer="2.8")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Theaterstücke", kapitelnummer="2.8.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="2.8").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Interviews", kapitelnummer="3")
#     g = Genre.objects.create(name="Über Persönliches und Biographisches", kapitelnummer="3.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Über Preise", kapitelnummer="3.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Literaturnobelpreis [ Preise S.]", kapitelnummer="3.2.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.2").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Deutschsprachige Interviews", kapitelnummer="3.2.1.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.2.1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Fremdsprachige Interviews", kapitelnummer="3.2.1.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.2.1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Über den Schwerpunkt bei den Salzburger Festspielen 1998", kapitelnummer="3.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Über die politische und/oder kulturelle Situation", kapitelnummer="3.4")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Über allgemein Workspezifisches", kapitelnummer="3.5")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Beziehungen zu anderen KünstlerInnen", kapitelnummer="3.5.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Begegnungen", kapitelnummer="3.5.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Über Work und Schreibweise im Allgemeinen", kapitelnummer="3.5.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.5").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Über einzelne Gattungen und Worke", kapitelnummer="3.6")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Romane", kapitelnummer="3.6.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Allgemeines zu den Romanen", kapitelnummer="3.6.1.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6.1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Über einzelne Romane", kapitelnummer="3.6.1.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6.1").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Kurzprosa", kapitelnummer="3.6.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Theatertexte", kapitelnummer="3.6.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Allgemeines zu den Theatertexten", kapitelnummer="3.6.3.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6.3").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Über einzelne Theatertexte", kapitelnummer="3.6.3.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6.3").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Hörspiele", kapitelnummer="3.6.4")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Drehbücher", kapitelnummer="3.6.5")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Libretti", kapitelnummer="3.6.6")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Übersetzungen", kapitelnummer="3.6.7")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Bearbeitungen von anderen", kapitelnummer="3.6.8")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Hörspiele", kapitelnummer="3.6.8.1")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6.8").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Filme", kapitelnummer="3.6.8.2")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6.8").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Opern", kapitelnummer="3.6.8.3")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3.6.8").first(), obj=g, prop=hat_subgenre)
#     g = Genre.objects.create(name="Über die Rezeption", kapitelnummer="3.7")
#     Triple.objects.create(subj=Genre.objects.filter(kapitelnummer="3").first(), obj=g, prop=hat_subgenre)