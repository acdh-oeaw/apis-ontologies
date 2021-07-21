import xml.etree.ElementTree as ET
from apis_core.apis_entities.models import *
from apis_core.apis_relations.models import TempTriple, Property
from apis_core.apis_vocabularies.models import *
from django.core.management.base import BaseCommand, CommandError

def crawl(node_list):

    node_pair = node_list[-1]
    node = node_pair[0]
    node_entity = node_pair[1]

    if node.tag.endswith("bibl") and node.attrib.get("ana") == "frbroo:work":

        title = None

        for c in node.getchildren():

            if c.tag.endswith("title"):

                title = c.text

        f1_work = F1_Work.objects.get_or_create(name=title)[0]

        node_entity = f1_work

    elif node.tag.endswith("bibl") and node.attrib.get("ana") == "frbroo:manifestation":

        e55_type = None
        type = node.attrib.get("type")
        if type is not None:

            e55_type = E55_Type.objects.get_or_create(name=type)[0]

        e55_type_sub = None
        subtype = node.attrib.get("subtype")
        if subtype is not None:

            if type is None:

                print(f"found subtype but no type: node:{node}, attrib: {node.attrib}")

            else:

                e55_type_sub = E55_Type.objects.get_or_create(name=subtype)[0]
                TempTriple.objects.get_or_create(
                    subj=e55_type_sub,
                    obj=e55_type,
                    prop=Property.objects.get(name="p127 has broader term")
                )

        title = None
        date = None
        note = None

        for c in node.getchildren():

            if c.tag.endswith("title"):

                title = c.text

            elif c.tag.endswith("date"):

                date = c.text

            elif c.tag.endswith("note"):

                note = c.text

        f4_manifestation_singleton = None
        if title is not None:

            f4_manifestation_singleton = F4_Manifestation_Singleton.objects.get_or_create(
                name=title,
                start_date_written=date,
                note=note
            )[0]

            if e55_type is not None:

                TempTriple.objects.get_or_create(
                    subj=f4_manifestation_singleton,
                    obj=e55_type,
                    prop=Property.objects.get(name="p2 has type")
                )

            node_entity = f4_manifestation_singleton

            node_pair_above = node_list[-2]
            node_pair_above_2 = node_list[-3]
            if node_pair_above[0].tag.endswith("relatedItem"):

                if node_pair_above[0].attrib.get("type") == "host" and node_pair_above_2[1] is not None:

                    TempTriple.objects.create(
                        subj=node_pair_above_2[1],
                        obj=node_entity,
                        prop=Property.objects.get(name="host")
                    )

        else:

            print(f"Found manifestation without title: node:{node}, attrib: {node.attrib}")

    elif node.tag.endswith("persName"):

        f10_person = None

        if not node_list[-2][0].tag.endswith("respStmt"):

            forename = None
            surname = None

            for c in node.getchildren():

                if c.tag.endswith("forename"):

                    forename = c.text

                elif c.tag.endswith("surname"):

                    surname = c.text

            if forename is None and surname is None:

                f10_person = F10_Person.objects.get_or_create(
                    name=node.text,
                )[0]

            else:

                f10_person = F10_Person.objects.get_or_create(
                    forename=forename,
                    surname=surname,
                    name=forename + " " + surname,
                )[0]

            node_pair_above = node_list[-2]
            if node_pair_above[0].tag.endswith("bibl") and node_pair_above[1] is not None:

                role = node.attrib.get("role")

                prop = None

                if role == "author":

                    prop = Property.objects.get(name="is author of")

                elif role == "translator":

                    prop = Property.objects.get(name="is translator of")

                elif role == "editor":

                    prop = Property.objects.get(name="is editor of")

                if prop is not None:

                    triple = TempTriple.objects.get_or_create(
                        subj=f10_person,
                        obj=node_pair_above[1],
                        prop=prop
                    )[0]

    elif node.tag.endswith("publisher"):

        try:

            publisher = Publisher.objects.get_or_create(
                name=node.text
            )[0]

            node_pair_above = node_list[-2]
            if node_pair_above[0].tag.endswith("bibl") and node_pair_above[1] is not None:

                triple = TempTriple.objects.get_or_create(
                    subj=publisher,
                    obj=node_pair_above[1],
                    prop=Property.objects.get(name="is publisher of")
                )[0]

        except Exception as ex:

            print(ex)

    node_list[-1] = (node, node_entity)

    for c in node.getchildren():

        node_list.append((c, None))

        crawl(node_list)

        del node_list[-1]


def node_is_work(node):

    ana = node.attrib.get("ana")

    return ana is not None and ana == "frbroo:work"


def run(*args, **options):
    # TODO RDF : delete all model instances
    RootObject.objects.all().delete()
    from apis_ontology.models import construct_properties
    construct_properties()

    tei_xml_file = "../manuelle-korrektur/korrigiert/bd1/001_Werke/004_Theatertexte/FRBR-Works/001_WasgeschahnachdemNoraihrenMannverlassenhatteoderStützenderGesellschaften.xml"

    tree = ET.parse(tei_xml_file)

    root = tree.getroot()

    crawl([(root, None)])

    print()

