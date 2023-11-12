from apis_ontology.models import Xml_Content_Dump, Xml_File, F1_Work
from apis_core.apis_relations.models import Triple, Property
from lxml import etree
import re

def has_class_as_parent(class_to_check, class_parent):
            if class_to_check is type:
                return False
            elif class_to_check is class_parent:
                return True
            else:
                for parent in class_to_check.__bases__:
                    if has_class_as_parent(parent, class_parent):
                        return True
                return False


def generate_xml_dumps():
    for xml in Xml_File.objects.all():
        primary_f1 = [t.subj for t in Triple.objects.filter(obj=xml, prop__name="was defined primarily in") if has_class_as_parent(t.subj.__class__, F1_Work)]
        if (len(primary_f1) > 0):
            try:
                root = etree.fromstring(xml.file_content)
                for list in root.xpath("//*[name()='listBibl']"):
                    list.getparent().remove(list)
                body = root.xpath("//*[name()='body']")
                if len(body) > 0:
                    extracted_xml_content = "".join([t for t in body[0].itertext()])
                    extracted_xml_content += " ".join(ref for ref in body[0].xpath("//@ref"))
                    extracted_xml_content = re.sub(r"\n", " ", extracted_xml_content,0,re.MULTILINE)
                    extracted_xml_content = re.sub(r"  +", " ", extracted_xml_content,0,re.MULTILINE)
                    print(extracted_xml_content)
                    dump = Xml_Content_Dump.objects.get_or_create(name=xml.name, file_content=extracted_xml_content)[0]
                    for f1 in primary_f1:
                        Triple.objects.get_or_create(
                            subj=f1,
                            obj=dump,
                            prop=Property.objects.get(name="data read from dump")
                        )
                        print("Created triple from dump {} to f1 {}".format(dump.name, f1.name))
            except Exception as e:
                 print("An error occurred during xml dump generation")



def run(*args, **options):
    def main_run():
        generate_xml_dumps()
    main_run()