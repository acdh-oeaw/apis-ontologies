from apis_core.apis_relations.models import Property
from apis_ontology.models import *
from django.db.models import OuterRef,Exists,Q

def generate_publisher_relations_for_journals_with_existing_e40():
    journals = E40_Legal_Body.objects.filter(Exists(F3_Manifestation_Product_Type.objects.filter(name=OuterRef('name'), triple_set_from_obj__prop__name="has host", triple_set_from_subj__obj__name__in=["journal", "newspaper"]).exclude(name="")))
    print("{} entries with matching e40".format(journals.count()))
    counter = 1
    for j in journals:
        matching_f3 = F3_Manifestation_Product_Type.objects.filter(name=j.name)
        child_manifestations = [triple.subj for host in matching_f3 for triple in host.triple_set_from_obj.filter(prop__name="has host")]
        for c in child_manifestations:
            RenditionTriple.objects.get_or_create(subj=j, obj=c, prop=Property.objects.get(name="is publisher of"), rendition_hidden=True)
        print("{}/{}   {}: {}".format(counter, journals.count(), j.name, len(child_manifestations)))
        counter = counter + 1

def generate_publisher_relations_for_journals_without_existing_e40():
    journals = F3_Manifestation_Product_Type.objects.filter(Q(triple_set_from_subj__prop__name="p2 has type") & Q(triple_set_from_subj__obj__name__in=["journal", "newspaper"])).distinct()
    print("{} entries in total".format(journals.count()))
    counter = 1
    for j in journals:
        if not E40_Legal_Body.objects.filter(name=j.name).exists():
            insti = E40_Legal_Body.objects.create(name=j.name, institution_id="inst_from_{}".format(j.bibl_id), institution_type="journal")
            child_manifestation_triples = j.triple_set_from_obj.filter(prop__name="has host")
            for triple in child_manifestation_triples:
                RenditionTriple.objects.get_or_create(subj=insti, obj=triple.subj, prop=Property.objects.get(name="is publisher of"), rendition_hidden=True)
            print("{}/{}   {}: {}".format(counter, journals.count(), insti.name, child_manifestation_triples.count()))
        counter = counter + 1

def run(*args, **options):
    def main_run():
        generate_publisher_relations_for_journals_with_existing_e40()
        generate_publisher_relations_for_journals_without_existing_e40()
    main_run()