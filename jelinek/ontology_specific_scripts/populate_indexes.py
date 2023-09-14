
from apis_ontology.models import E1_Crm_Entity
from django.contrib.postgres.search import SearchVector
from django.db.models import Value


def populate_indexes():
    count = 0
    total = E1_Crm_Entity.objects.all().count()
    for ent in E1_Crm_Entity.objects_inheritance.select_subclasses("f1_work", "f3_manifestation_product_type", "honour", "f31_performance").all():
        count += 1
        print("Processing entity {} of {}".format(count, total))
        txt_e1 = ""
        txt_pers = ""
        txt_e40 = ""
        txt_xml_content = ""
        txt_xml_note = ""
        check = False
        for attr in ["name", "content", "file_content", "note", "short"]:
            if hasattr(ent, attr):
                if getattr(ent, attr) is not None:
                    txt_e1 += getattr(ent, attr) + " "
                    check = True
        if len(txt_e1) > 0:
            ent.vector_column_e1 = SearchVector(Value(txt_e1), config='german')
        for triple in ent.triple_set_from_subj.filter(obj__self_contenttype_id=37):
            txt_pers += triple.obj.name + " "
        for triple in ent.triple_set_from_obj.filter(subj__self_contenttype_id=37):
            txt_pers += triple.subj.name + " "
        if len(txt_pers) > 0:
            check = True
            ent.vector_related_f10 = SearchVector(Value(txt_pers))
        for triple in ent.triple_set_from_subj.filter(obj__self_contenttype_id=35):
            txt_e40 += triple.obj.name + " "
        for triple in ent.triple_set_from_obj.filter(subj__self_contenttype_id=35):
            txt_e40 += triple.subj.name + " "
        if len(txt_e40) > 0:
            check = True
            ent.vector_related_E40 = SearchVector(Value(txt_e40))
        for triple in ent.triple_set_from_subj.filter(obj__self_contenttype_id=97):
            txt_xml_content += triple.obj.file_content + " "
        if len(txt_xml_content) > 0:
            check = True
            ent.vector_related_xml_content_dump = SearchVector(Value(txt_xml_content), config='german')
        for triple in ent.triple_set_from_subj.filter(obj__self_contenttype_id=47):
            txt_xml_note += triple.obj.content + " "
        for triple in ent.triple_set_from_obj.filter(subj__self_contenttype_id=47):
            txt_xml_note += triple.subj.content + " "
        if len(txt_xml_note) > 0:
            check = True
            ent.vector_related_xml_note = SearchVector(Value(txt_xml_note), config='german')
        if check:
            ent.save()


def run(*args, **options):
    def main_run():
        populate_indexes()
    main_run()