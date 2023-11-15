
from apis_ontology.models import E1_Crm_Entity, E40_Legal_Body, F10_Person, XMLNote, Xml_Content_Dump
from django.contrib.postgres.search import SearchVector
from django.contrib.contenttypes.models import ContentType
from django.db.models import Value


def populate_indexes():
    count = 0
    total = E1_Crm_Entity.objects.all().count()
    contenttype_f10 = ContentType.objects.get_for_model(model=F10_Person)
    contenttype_e40 = ContentType.objects.get_for_model(model=E40_Legal_Body)
    contenttype_content_dump = ContentType.objects.get_for_model(model=Xml_Content_Dump)
    contenttype_note = ContentType.objects.get_for_model(model=XMLNote)
    for ent in E1_Crm_Entity.objects_inheritance.select_subclasses("f1_work", "f3_manifestation_product_type", "honour", "f31_performance").all():
        count += 1
        print("Processing entity {} of {}".format(count, total))
        txt_e1 = ""
        txt_pers = ""
        txt_e40 = ""
        txt_xml_content = ""
        txt_xml_note = ""
        check = False
        for attr in ["name", "content", "file_content"]:
            if hasattr(ent, attr):
                if getattr(ent, attr) is not None:
                    txt_e1 += getattr(ent, attr) + " "
                    check = True
        if len(txt_e1) > 0:
            ent.vector_column_e1_set = SearchVector(Value(txt_e1), config='german')
        for triple in ent.triple_set_from_subj.filter(obj__self_contenttype_id=contenttype_f10):
            txt_pers += triple.obj.name + " "
            if triple.obj.entity_id is not None:
                txt_pers += triple.obj.entity_id + " "
        for triple in ent.triple_set_from_obj.filter(subj__self_contenttype_id=contenttype_f10):
            txt_pers += triple.subj.name + " "
            if triple.subj.entity_id is not None:
                txt_pers += triple.subj.entity_id + " "
        if len(txt_pers) > 0:
            check = True
            ent.vector_related_f10_set = SearchVector(Value(txt_pers))
        for triple in ent.triple_set_from_subj.filter(obj__self_contenttype_id=contenttype_e40):
            txt_e40 += triple.obj.name + " "
            if triple.obj.entity_id is not None:
                txt_e40 += format(triple.obj.entity_id.replace("_", "")) + " "
        for triple in ent.triple_set_from_obj.filter(subj__self_contenttype_id=contenttype_e40):
            txt_e40 += triple.subj.name + " "
            if triple.subj.entity_id is not None:
                txt_e40 += format(triple.subj.entity_id.replace("_", "")) + " "
        if len(txt_e40) > 0:
            check = True
            ent.vector_related_E40_set = SearchVector(Value(txt_e40))
        for triple in ent.triple_set_from_subj.filter(obj__self_contenttype_id=contenttype_content_dump):
            txt_xml_content += triple.obj.file_content + " "
        if len(txt_xml_content) > 0:
            check = True
            ent.vector_related_xml_content_dump_set = SearchVector(Value(txt_xml_content), config='german')
        for triple in ent.triple_set_from_subj.filter(obj__self_contenttype_id=contenttype_note):
            txt_xml_note += triple.obj.content + " "
        for triple in ent.triple_set_from_obj.filter(subj__self_contenttype_id=contenttype_note):
            txt_xml_note += triple.subj.content + " "
        if len(txt_xml_note) > 0:
            check = True
            ent.vector_related_xml_note_set = SearchVector(Value(txt_xml_note), config='german')
        if check:
            ent.save()


def run(*args, **options):
    def main_run():
        populate_indexes()
    main_run()