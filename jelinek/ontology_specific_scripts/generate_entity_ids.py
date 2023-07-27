from apis_ontology.models import *

def generate_ids():
    classes_to_check = [
        [E40_Legal_Body, "institution_id"],
        [F1_Work, "idno"],
        [Honour, "honour_id"],
        [F3_Manifestation_Product_Type, "bibl_id"],
        [F9_Place, "place_id"],
        [F10_Person, "pers_id"],
        [F26_Recording, "broadcast_id"],
        [F31_Performance, "performance_id"],
        [Keyword, "keyword_id"]
    ]
    for [ontology_class, property] in classes_to_check:
        print("Adding entity_id for all objects of class {}".format(ontology_class.__class__))
        for obj in ontology_class.objects.all():
            obj.entity_id = getattr(obj, property)
            obj.save()


def run(*args, **options):
    def main_run():
        generate_ids()
    main_run()