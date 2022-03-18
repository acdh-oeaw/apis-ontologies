from __future__ import annotations
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element as XmlElement
from typing import Type, List
from apis_ontology.models import *
from apis_core.apis_relations.models import Triple, TempTriple, Property
from apis_core.apis_vocabularies.models import *
from django.core.management.base import BaseCommand, CommandError
from os import listdir
from os.path import isfile, join


class PathNode():

    xml_elem = None
    path_node_parent: PathNode
    path_node_children_list: List[PathNode]
    entities_list: List[RootObject]
    triples_list: List[TempTriple]

    def __init__(self, xml_elem, path_node_parent):

        self.xml_elem = xml_elem
        self.path_node_parent = path_node_parent
        self.path_node_children_list = []
        self.entities_list = []
        self.triples_list = []


    def __str__(self):

        return self.xml_elem.tag.replace("{http://www.tei-c.org/ns/1.0}", "") + "-" + str(self.xml_elem.attrib) + "-" + self.xml_elem.text

    def __repr__(self):

        return self.__str__()


def is_valid_text(var_str):

    if var_str is None:

        return False

    return not re.match(r"^$|^[ \n]*$", var_str)


# TODO : Check all object creations for redundant data creation
class TreesManager:

    # TODO output these at the end of parsing
    entity_xml_tag_not_parsed = set()
    entity_xml_text_not_parsed = set()
    helper_dict = {}

    @classmethod
    def parse_for_entities(cls, path_node: PathNode, trees_manager: Type[TreesManager]):

        def handle_after_creation(db_result, attr_dict):

            def set_attr_to_entity(entity, attr_name, attr_val):

                if attr_val is not None:

                    entity_attr_val = getattr(entity, attr_name)

                    if entity_attr_val == "" or entity_attr_val is None:

                        setattr(entity, attr_name, attr_val)

                    elif entity_attr_val != attr_val:

                        print("Potentially inconsistent data or mapping")

                return entity


            if db_result is not None:

                entity = db_result[0]

                if db_result[1] is True:

                    print(f"created entity: type: {entity.__class__.__name__}, name: {entity.name}, pk: {entity.pk}")

                else:

                    print("entity already exists")

                for attr_name, attr_val in attr_dict.items():

                    entity = set_attr_to_entity(entity, attr_name, attr_val)

                entity.save()

                return entity

            else:

                print(f"Nothing created")

                return None


        def parse_template_function(path_node: PathNode):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                foo = None

                if xml_elem: # condition

                    foo = "something"

                else:

                    return None

                return {
                    "foo": foo,
                    "bar": None
                }

            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["foo"] is not None: # foo is unique identifier

                        # db_result = EntityClass.objects.get_or_create(foo=attr_dict["foo"])
                        db_result = None

                    elif attr_dict["bar"] is not None: # bar is identifish

                        # if this entity is mostly created using these fields:
                        # db_result = EntityClass.objects.get_or_create(foo=attr_dict["bar"])

                        # if this entity is mostly created using other fields, and thus the field 'bar' could lead to multiple results
                        # db_hit = EntityClass.objects.filter(name=attr_dict["name"])
                        db_hit = None

                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            # db_result = [
                            #     EntityClass.objects.create(name=attr_dict["name"]),
                            #     True
                            # ]
                            pass

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)



        def parse_e40_legal_body(path_node: PathNode):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                name = None

                if (
                    (
                        xml_elem.tag.endswith("publisher")
                        or xml_elem.tag.endswith("institution")
                        or (
                            xml_elem.tag.endswith("rs")
                            and xml_elem.attrib.get("type") == "institution"
                        )
                        or xml_elem.tag.endswith("orgName")
                    )
                    and not (
                        xml_elem.attrib.get("ref") is not None
                        and xml_elem.attrib.get("ref").startswith("bibls:")
                    )
                    and is_valid_text(xml_elem.text)
                ):

                    name = xml_elem.text

                else:

                    return None

                return {
                    "name": name
                }

            def sub_main(path_node: PathNode):

                entities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = E40_Legal_Body.objects.get_or_create(name=attr_dict["name"])

                    entities_list.append(handle_after_creation(db_result, {}))

                return entities_list

            return sub_main(path_node)


        def parse_e55_type(path_node: PathNode):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem
                name_type = None
                name_subtype = None

                if (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("type") is not None
                    # and xml_elem.attrib.get("ana") == "frbroo:manifestation"
                ):

                    name_type = xml_elem.attrib.get("type")
                    name_subtype = xml_elem.attrib.get("subtype")

                return {
                    "name_type": name_type,
                    "name_subtype": name_subtype
                }

            def sub_main(path_node: PathNode):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict["name_type"] is not None:

                    db_result = E55_Type.objects.get_or_create(name=attr_dict["name_type"])

                    enities_list.append(handle_after_creation(db_result, {}))

                if attr_dict["name_subtype"] is not None:

                    db_result = E55_Type.objects.get_or_create(name=attr_dict["name_subtype"])

                    enities_list.append(handle_after_creation(db_result, {}))

                return enities_list

            return sub_main(path_node)


        def parse_f1_work(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem
                idno = None
                name = None
                gnd_url = None

                if (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ana") == "frbroo:work"
                    and trees_manager.helper_dict["current_type"] is F1_Work
                ):

                    for xml_elem_child in xml_elem:

                        # TODO : Check if there are titles without 'type="main"'
                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "main"
                        ):

                            name = xml_elem_child.text

                        if (
                            xml_elem_child.tag.endswith("idno")
                            and xml_elem_child.attrib["type"] == "JWV"
                        ):

                            idno = xml_elem_child.text

                elif (
                    xml_elem.tag.endswith("item")
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id").startswith("work")
                ):

                    idno = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "index"
                            and is_valid_text(xml_elem_child.text)
                        ):

                            name = xml_elem_child.text

                        elif (
                                xml_elem_child.tag.endswith("ref")
                                and xml_elem_child.attrib.get("type") == "gnd"
                                and xml_elem_child.attrib.get("target") is not None
                        ):

                            gnd_url = xml_elem_child.attrib.get("target")

                elif (
                    xml_elem.tag.endswith("rs")
                    and xml_elem.attrib.get("type") == "work"
                    and xml_elem.attrib.get("ref") is not None
                    and xml_elem.attrib.get("ref").startswith("works:")
                ):

                    idno = xml_elem.attrib.get("ref").replace("works:", "")

                    # TODO : 'ref type="category"'
                    for xml_elem_child in xml_elem:

                        if xml_elem_child.tag.endswith("title"):

                            name = xml_elem_child.text

                else:

                    return None

                return {
                    "idno": idno,
                    "name": name,
                    "gnd_url": gnd_url,
                }


            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["idno"] is not None:

                        db_result = F1_Work.objects.get_or_create(
                            idno=attr_dict["idno"],
                            self_content_type=F1_Work.get_content_type()
                        )

                    elif attr_dict["name"] is not None:

                        # db_result = F1_Work.objects.get_or_create(name=attr_dict["name"])
                        db_hit = F1_Work.objects.filter(
                            name=attr_dict["name"],
                            self_content_type=F1_Work.get_content_type()
                        )
                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            db_result = [
                                F1_Work.objects.create(name=attr_dict["name"]),
                                True
                            ]

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)


        def parse_f3_manifestation(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem
                name = ""
                title_in_note = None
                series = None
                edition = None
                start_date = None
                note = None
                ref_target = None
                ref_accessed = None
                text_language = None
                bibl_id = None

                if (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ana") == "frbroo:manifestation"
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is None
                ):

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("ptr")
                            and xml_elem_child.attrib.get("type") == "bibl"
                            and xml_elem_child.attrib.get("target") is not None
                            and xml_elem_child.attrib.get("target").startswith("bibls:")
                        ):

                            bibl_id = xml_elem_child.attrib.get("target").replace("bibls:", "")

                        elif (
                            xml_elem_child.tag is not None
                            and xml_elem_child.tag.endswith("title")
                            and is_valid_text(xml_elem_child.text)
                        ):

                            name = xml_elem_child.text

                elif (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ana") == "frbroo:manifestation"
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                ):

                    bibl_id = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag is not None
                            and xml_elem_child.tag.endswith("title")
                            and is_valid_text(xml_elem_child.text)
                        ):

                            name = xml_elem_child.text

                elif (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.get("ref") is not None
                    and xml_elem.get("ref").startswith("bibls:")
                ):
                    # TODO : When there is time check these following lines for redundancy and potential clean-ups

                    bibl_id = xml_elem.get("ref").replace("bibls:", "")

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("title")
                            and is_valid_text(xml_elem_child.text)
                        ):

                            name = xml_elem_child.text

                        elif (
                            xml_elem_child.tag.endswith("hi")
                            and is_valid_text(xml_elem_child.text)
                        ):

                            name = xml_elem_child.text

                        elif xml_elem_child.tag.endswith("series"):

                            series = xml_elem_child.text

                        elif xml_elem_child.tag.endswith("edition"):

                            edition = xml_elem_child.text

                        elif xml_elem_child.tag.endswith("date"):

                            if xml_elem_child.attrib.get("type") == "lastAccessed":

                                ref_accessed = xml_elem_child.text

                            else:

                                start_date = xml_elem_child.text

                        elif xml_elem_child.tag.endswith("note"):

                            for xml_elem_child_child in xml_elem_child.getchildren():

                                if xml_elem_child_child.tag.endswith("title"):

                                    title_in_note = xml_elem_child_child.text

                            note = xml_elem_child.text

                        elif xml_elem_child.tag.endswith("ref"):

                            ref_target = xml_elem_child.attrib.get("target")

                        elif xml_elem_child.tag.endswith("textLang"):

                            text_language = xml_elem_child.text

                        elif (
                                xml_elem_child.attrib.get("target") is not None
                                and xml_elem_child.attrib.get("target").startswith("#bibl")
                        ):

                            if bibl_id is not None:

                                raise Exception("Inconsistent data or mapping")

                            bibl_id = xml_elem_child.attrib.get("target").replace("#", "")

                        elif (
                                xml_elem_child.tag.endswith("ptr")
                                and xml_elem_child.attrib.get("type") is not None
                                and xml_elem_child.attrib.get("type") == "bibl"
                                and xml_elem_child.attrib.get("target") is not None
                                and xml_elem_child.attrib.get("target").startswith("bibls:")
                        ):

                            if bibl_id is not None:

                                raise Exception("Inconsistent data or mapping")

                            bibl_id = xml_elem_child.attrib.get("target").replace("bibls:", "")

                        elif (
                                xml_elem_child.tag.endswith("persName")
                                or xml_elem_child.tag.endswith("pubPlace")
                                or xml_elem_child.tag.endswith("publisher")
                                or xml_elem_child.tag.endswith("orgName")
                        ):

                            # TODO
                            pass

                        else:

                            print("unhandled node")
                            print(xml_elem_child)

                elif (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ana") != "frbroo:work"
                    and xml_elem.attrib.get("ana") != "frbroo:manifestation"
                ):

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("title")
                            and is_valid_text(xml_elem_child.text)
                        ):

                            name = xml_elem_child.text

                else:

                    return None

                return {
                    "bibl_id": bibl_id,
                    "name": name,
                    "title_in_note": title_in_note,
                    "series": series,
                    "edition": edition,
                    "start_date": start_date,
                    "note": note,
                    "ref_target": ref_target,
                    "ref_accessed": ref_accessed,
                    "text_language": text_language,
                }

            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["bibl_id"] is not None:

                        db_result = F3_Manifestation_Product_Type.objects.get_or_create(
                            bibl_id=attr_dict["bibl_id"],
                        )

                    elif attr_dict["name"] is not None:

                        # TODO : Temporary Work-around until the encoding problem is solved
                        # db_result = F3_Manifestation_Product_Type.objects.get_or_create(
                        #     name=attr_dict["name"],
                        # )
                        db_hit = F3_Manifestation_Product_Type.objects.filter(name=attr_dict["name"])

                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            db_result = [
                                F3_Manifestation_Product_Type.objects.create(name=attr_dict["name"]),
                                True
                            ]

                    else:

                        # TODO : Check how often this is the case
                        print("Entity found without a uniquely identifying attribute")

                    if db_result is not None:

                            # TODO : Maybe reactivate a default naming scheme for empty entries, or maybe not
                            # if attr_dict["name"] is None and entity.name == "":
                            #
                            #     attr_dict["name"] = f"unnamed f3, number {cls.counter_f3_manifestation_parsed}"

                        # TODO : Check this if condition if it is used
                        if (
                            db_result[0].name == ""
                            or (
                                db_result[0].name.startswith("unnamed")
                                and attr_dict["name"] is not None
                                and not attr_dict["name"].startswith("unnamed")
                            )
                        ):

                            db_result[0].name = attr_dict["name"]

                        elif attr_dict["name"] is not None and attr_dict["name"] != db_result[0].name:

                            # TODO : Check how often this is the case
                            print("Inconsistent data or mapping")

                        if db_result[0].bibl_id == "":

                            db_result[0].bibl_id = attr_dict["bibl_id"]

                        elif attr_dict["bibl_id"] is not None and attr_dict["bibl_id"] != db_result[0].bibl_id:

                            raise Exception("Inconsistent data or mapping")

                        enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)


        def parse_f9_place(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                name = None

                if (
                    xml_elem.tag.endswith("pubPlace")
                    and is_valid_text(xml_elem.text)
                ):

                    name = xml_elem.text.replace("pubPlace", "")

                else:

                    return None

                return {
                    "name": name
                }

            def sub_main(path_node: PathNode):

                entities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = F9_Place.objects.get_or_create(name=attr_dict["name"])

                    entities_list.append(handle_after_creation(db_result, {}))

                return entities_list

            return sub_main(path_node)


        def parse_f10_person(path_node):

            def parse_persName(xml_elem: XmlElement):

                name = None
                forename = None
                surname = None

                if (
                    xml_elem.text is not None
                    and is_valid_text(xml_elem.text)
                ):

                    name = xml_elem.text

                for xml_elem_child in xml_elem:

                    if xml_elem_child.tag.endswith("forename") and is_valid_text(xml_elem_child.text):

                        forename = xml_elem_child.text

                    if xml_elem_child.tag.endswith("surname") and is_valid_text(xml_elem_child.text):

                        surname = xml_elem_child.text

                if name is None:

                    if forename is None and surname is None:

                        name = ""

                    else:

                        if forename is None:

                            forename = ""

                        if surname is None:

                            surname = ""

                        name = forename + " " + surname

                return name, forename, surname


            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem
                pers_id = None
                name = None
                forename = None
                surname = None
                gnd_url = None

                if (
                    xml_elem.tag.endswith("rs")
                    and xml_elem.attrib.get("type") == "person"
                    and xml_elem.attrib.get("ref") is not None
                    and xml_elem.attrib.get("ref").startswith("persons:")
                ):

                    for xml_elem_child in xml_elem:

                        if xml_elem_child.tag.endswith("persName"):

                            name, forename, surname = parse_persName(xml_elem_child)

                    pers_id = xml_elem.attrib.get("ref").replace("persons:", "")

                elif (
                    xml_elem.tag.endswith("persName")
                    and (
                        path_node.path_node_parent is not None
                        and not path_node.path_node_parent.xml_elem.tag.endswith("rs")
                        and path_node.path_node_parent.xml_elem.attrib.get("type") != "person"
                        and (
                            not path_node.path_node_parent.xml_elem.tag.endswith("item") # as in person_index.xml
                            or (
                                path_node.path_node_parent.xml_elem.tag.endswith("item")
                                and  path_node.path_node_parent.xml_elem.attrib.get("ana") == "staging" # as in xmls in 001_Werke/004_Theatertexte/FRBR-Works/
                            )
                        )
                    )
                ):

                    name, forename, surname = parse_persName(xml_elem)

                elif (
                    xml_elem.tag.endswith("item")
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                ):

                    pers_id = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")

                    for xml_elem_child in xml_elem:

                        if xml_elem_child.tag.endswith("persName"):

                            name, forename, surname = parse_persName(xml_elem_child)

                        elif (
                            xml_elem_child.tag.endswith("ref")
                            and xml_elem_child.attrib.get("type") == "gnd"
                            and xml_elem_child.attrib.get("target") is not None
                        ):

                            gnd_url = xml_elem_child.attrib.get("target")

                else:

                    return None

                return {
                    "pers_id": pers_id,
                    "name": name,
                    "forename": forename,
                    "surname": surname,
                    "gnd_url": gnd_url,
                }

            def sub_main(path_node):

                entities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None
                    db_hit = None

                    if attr_dict["pers_id"] is not None:

                        db_result = F10_Person.objects.get_or_create(pers_id=attr_dict["pers_id"])

                    elif attr_dict["forename"] is not None and attr_dict["surname"] is not None:

                        db_hit = F10_Person.objects.filter(forename=attr_dict["forename"], surname=attr_dict["surname"])

                    elif attr_dict["name"] is not None:

                        # There can be multiple persons with the same name, hence until disambiguation can be finished,
                        # db_result = F10_Person.objects.get_or_create(name=attr_dict["name"])
                        db_hit = F10_Person.objects.filter(name=attr_dict["name"])

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    if db_hit is not None:

                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            db_result = [
                                F10_Person.objects.create(name=attr_dict["name"]),
                                True
                            ]

                    entities_list.append(handle_after_creation(db_result, attr_dict))

                return entities_list

            return sub_main(path_node)

        def parse_f17_aggregation_work(path_node):

            # cls.counter_f17_aggregation_work_parsed += 1
            #
            # title = None
            #
            # for c in xml_elem.getchildren():
            #
            #     if c.tag.endswith("title"):
            #
            #         if title is None:
            #
            #             title = c.text
            #
            #         else:
            #
            #             print("Found multiple titles!")
            #
            # db_result = F17_Aggregation_Work.objects.get_or_create(name=title)
            #
            # if db_result[1] is True:
            #
            #     entity = db_result[0]
            #     cls.counter_f17_aggregation_work_created += 1
            #     print(f"created entity: type: {entity.__class__.__name__}, name: {entity.name}, pk: {entity.pk}")
            #
            # else:
            #
            #     print("entity already exists")

            pass

        def parse_f21_recording_work(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem
                name = None
                idno = None

                if (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ana") == "frbroo:work"
                ):

                    for xml_elem_child in xml_elem:

                        # TODO : Check if there are titles without 'type="main"'
                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "main"
                            and trees_manager.helper_dict["current_type"] is F21_Recording_Work
                        ):

                            name = xml_elem_child.text

                        if (
                            xml_elem_child.tag.endswith("idno")
                            and xml_elem_child.attrib["type"] == "JWV"
                        ):

                            idno = xml_elem_child.text

                else:

                    return None

                return {
                    "name": name,
                    "idno": idno,
                }


            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["name"] is not None:

                        # db_result = F21_Recording_Work.objects.get_or_create(name=attr_dict["name"])
                        db_hit = F21_Recording_Work.objects.filter(name=attr_dict["name"])
                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            db_result = [
                                F21_Recording_Work.objects.create(name=attr_dict["name"]),
                                True
                            ]

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)


        def parse_f26_recording(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem
                name = None
                airing_date = None
                helper_org = None

                if (
                    xml_elem.tag.endswith("item")
                    and xml_elem.attrib.get("type") == "broadcast"
                ):

                    for xml_elem_child in xml_elem:

                        # TODO : Check if there are titles without 'type="main"'
                        if (
                            xml_elem_child.tag.endswith("date")
                        ):

                            airing_date = xml_elem_child.text

                        elif (
                            xml_elem_child.tag.endswith("orgName")
                            and xml_elem_child.attrib["role"] == "broadcaster"
                        ):

                            helper_org = xml_elem_child.text

                    if airing_date is not None and helper_org is not None:

                        name = "aired on " + airing_date + " at " + helper_org

                    elif airing_date is not None:

                        name = "aired on " + airing_date

                    elif helper_org is not None:

                        name = "aired at " + helper_org

                    else:

                        name = "Unknown recording date"

                else:

                    return None

                return {
                    "name": name,
                    "airing_date": airing_date,
                }


            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["name"] is not None:

                        # db_result = F26_Recording.objects.get_or_create(name=attr_dict["name"])
                        db_hit = F26_Recording.objects.filter(name=attr_dict["name"])
                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            db_result = [
                                F26_Recording.objects.create(name=attr_dict["name"]),
                                True
                            ]

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)


        def parse_f31_performance(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                name = ""
                note = None
                category = None
                start_date_written = None
                institution = None

                if (
                    xml_elem.tag.endswith("item")
                    and xml_elem.attrib.get("ana") == "staging"
                ):

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("date")
                            and is_valid_text(xml_elem_child.text)
                        ):

                            start_date_written = xml_elem_child.text

                        elif (
                            xml_elem_child.tag.endswith("rs")
                            and xml_elem_child.attrib.get("type") == "institution"
                            and is_valid_text(xml_elem_child.text)
                        ):

                            institution = xml_elem_child.text

                        elif (
                            xml_elem_child.tag.endswith("note")
                            and is_valid_text(xml_elem_child.text)
                        ):

                            note = xml_elem_child.text

                            for xml_elem_child_child in xml_elem_child:

                                if (
                                    xml_elem_child_child.tag.endswith("ref")
                                    and xml_elem_child_child.attrib.get("type") == "category"
                                    and is_valid_text(xml_elem_child_child.text)
                                ):

                                    category = xml_elem_child_child.text

                else:

                    return None

                if (
                    start_date_written is not None
                    and institution is not None
                ):

                    name = f"Aufführung, Am {start_date_written}, Bei {institution}"

                elif start_date_written is not None:

                    name = f"Aufführung, Am {start_date_written}"

                elif institution is not None:

                    name = f"Bei {institution}"

                return {
                    "name": name,
                    "note": note,
                    "category": category,
                    "start_date_written": start_date_written,
                }

            def sub_main(path_node: PathNode):

                entities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["name"] != "":

                        db_result = F31_Performance.objects.get_or_create(name=attr_dict["name"])

                        entities_list.append(handle_after_creation(db_result, attr_dict))

                    else:

                        print("Entity found without a uniquely identifying attribute")

                return entities_list

            return sub_main(path_node)


        def parse_chapter(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                chapter_number = None

                if (
                    path_node.path_node_parent is not None
                    and path_node.path_node_parent.xml_elem.tag.endswith("keywords")
                    and path_node.path_node_parent.xml_elem.attrib.get("ana") == "chapters"
                    and xml_elem.tag.endswith("term")
                    and xml_elem.attrib.get("n") is not None
                    and is_valid_text(xml_elem.text)
                ):

                    chapter_number = xml_elem.attrib.get("n")
                    name = xml_elem.text

                else:

                    return None

                return {
                    "chapter_number": chapter_number,
                    "name": name
                }


            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["chapter_number"] is not None:

                        db_result = Chapter.objects.get_or_create(chapter_number=attr_dict["chapter_number"])

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)


        def sub_main(path_node):

            print(f"\nParsing: tag: {path_node.xml_elem.tag}, attrib: {path_node.xml_elem.attrib}, text: {path_node.xml_elem.text.__repr__()}")

            path_node.entities_list.extend(parse_e40_legal_body(path_node))

            path_node.entities_list.extend(parse_e55_type(path_node))

            path_node.entities_list.extend(parse_f1_work(path_node))

            path_node.entities_list.extend(parse_f3_manifestation(path_node))

            path_node.entities_list.extend(parse_f9_place(path_node))

            # TODO : Consider ruling out Project members
            path_node.entities_list.extend(parse_f10_person(path_node))

            path_node.entities_list.extend(parse_f21_recording_work(path_node))

            path_node.entities_list.extend(parse_f26_recording(path_node))

            path_node.entities_list.extend(parse_f31_performance(path_node))

            path_node.entities_list.extend(parse_chapter(path_node))


            # cls.parse_f17_aggregation_work(path_node.xml_elem)

            # TODO
            # cls.parse_f20_performance_work(xml_elem)

            # # TODO
            # if (
            #     path_node.xml_elem.tag.endswith("div")
            #     and path_node.xml_elem.attrib.get('type') == "entry"
            # ):
            #
            #     pass
            #
            # else:
            #
            #     print(f"Nothing created")
            #
            #     if path_node.xml_elem.tag not in cls.entity_xml_tag_not_parsed:
            #
            #         cls.entity_xml_tag_not_parsed.add(path_node.xml_elem.tag)
            #
            #     if path_node.xml_elem.text not in cls.entity_xml_text_not_parsed:
            #
            #         cls.entity_xml_text_not_parsed.add(path_node.xml_elem.text)

            return path_node

        return sub_main(path_node)


    @classmethod
    def parse_for_triples(cls, path_node: PathNode):

        def climb_up(path_node, level):

            if level > 0:

                level -= 1

                path_node_next_up = path_node.path_node_parent

                if path_node_next_up is not None:

                    return climb_up(path_node_next_up, level)

                else:

                    raise Exception("No more parents")

            else:

                return path_node


        def create_triple(entity_subj, entity_obj, prop):

            db_result = TempTriple.objects.get_or_create(
                subj=entity_subj,
                obj=entity_obj,
                prop=prop
            )

            if db_result[1] is True:

                print(f"created triple: subj: {entity_subj}, obj: {entity_obj}, prop: {prop.name}")

            else:

                print("triple already exists")

            return db_result[0]

        def parse_triples_from_f1_work(entity_work, path_node):

            def triple_from_f1_to_f3(entity_work, path_node):

                def check_and_create_triple_to_f3(entity_work, path_node_other):

                    for entity_other in path_node_other.entities_list:

                        if entity_other.__class__ is F3_Manifestation_Product_Type:

                            create_triple(
                                entity_subj=entity_work,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="is expressed in")
                            )

                for neighbour_path_node in path_node.path_node_parent.path_node_children_list:

                    # direct manifestations
                    if (
                        neighbour_path_node.xml_elem.tag.endswith("div")
                        and neighbour_path_node.xml_elem.attrib.get("type") == "frbroo:manifestations"
                    ):

                        for neighbour_child_path_node in neighbour_path_node.path_node_children_list:

                            if neighbour_child_path_node.xml_elem.tag.endswith("listBibl"):

                                for neighbour_child_child_path_node in neighbour_child_path_node.path_node_children_list:

                                    check_and_create_triple_to_f3(entity_work, neighbour_child_child_path_node)

                            else:

                                check_and_create_triple_to_f3(entity_work, neighbour_child_path_node)

                    # translated manifestations
                    elif (
                        neighbour_path_node.xml_elem.tag.endswith("div")
                        and neighbour_path_node.xml_elem.attrib.get("type") == "translations"
                    ):

                        for list_bibl_path_node in neighbour_path_node.path_node_children_list:

                            for list_bibl_child_path_node in list_bibl_path_node.path_node_children_list:

                                if (
                                    list_bibl_child_path_node.xml_elem.tag is not None
                                    and list_bibl_child_path_node.xml_elem.tag.endswith("bibl")
                                ):

                                    for entity_manifestation in list_bibl_child_path_node.entities_list:

                                        if entity_manifestation.__class__ is F3_Manifestation_Product_Type:

                                            create_triple(
                                                entity_subj=entity_manifestation,
                                                entity_obj=entity_work,
                                                prop=Property.objects.get(name="is translation of")
                                            )


            def triple_from_f1_to_f10(entity_work, path_node):

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if entity_other.__class__ == F10_Person:

                            for child_child_path_node in child_path_node.path_node_children_list:

                                if (
                                        child_child_path_node.xml_elem.tag.endswith("persName")
                                        and child_child_path_node.xml_elem.attrib.get("role") == "author"
                                ):

                                    create_triple(
                                        entity_subj=entity_other,
                                        entity_obj=entity_work,
                                        prop=Property.objects.get(name="is author of")
                                    )

            def triple_from_f1_to_f31(entity_work, path_node):

                for neighbour_path_node in path_node.path_node_parent.path_node_children_list:

                    if (
                        neighbour_path_node.xml_elem.tag.endswith("div")
                        and neighbour_path_node.xml_elem.attrib.get("type") == "stagings"
                    ):

                        for neighbour_path_node_child in neighbour_path_node.path_node_children_list:

                            if (
                                neighbour_path_node_child.xml_elem.tag.endswith("list")
                                and neighbour_path_node_child.xml_elem.attrib.get("type") == "stagings"
                            ):

                                for item_path_node in neighbour_path_node_child.path_node_children_list:

                                    for entity_other in item_path_node.entities_list:

                                        if entity_other.__class__ is F31_Performance:

                                            create_triple(
                                                entity_subj=entity_work,
                                                entity_obj=entity_other,
                                                prop=Property.objects.get(name="has been performed in"),
                                            )


            triple_from_f1_to_f3(entity_work, path_node)
            triple_from_f1_to_f10(entity_work, path_node)
            triple_from_f1_to_f31(entity_work, path_node)

        def parse_triples_from_f3_manifestation(entity_manifestation, path_node):

            def triples_from_f3_to_e55(entity_manifestation, path_node):

                name_subtype = path_node.xml_elem.attrib.get("subtype")
                name_type = path_node.xml_elem.attrib.get("type")

                subtype_found = False
                type_found = False
                entity_found = None

                for entity_other in path_node.entities_list:

                    if entity_other.__class__ is E55_Type and entity_other.name is not None:

                        # TODO : After db fix with regards to upper-lower-case colloations, remove this 'lower()' here
                        if (
                            name_subtype is not None
                            and entity_other.name.lower() == name_subtype.lower()
                        ):

                            subtype_found = True
                            entity_found = entity_other

                        elif (
                            name_type is not None
                            and entity_other.name.lower() == name_type.lower()
                            and not subtype_found
                        ):

                            entity_found = entity_other

                if entity_found is None and (name_subtype is not None or name_type is not None):

                    raise Exception("Found a type, but no correspondingly created entity for it")

                if entity_found is not None:

                    create_triple(
                        entity_subj=entity_manifestation,
                        entity_obj=entity_found,
                        prop=Property.objects.get(name="p2 has type")
                    )

            def triples_from_f3_to_f3(entity_manifestation, path_node: PathNode):

                for path_node_child in path_node.path_node_children_list:

                    if (
                        path_node_child.xml_elem.tag.endswith("relatedItem")
                        and path_node_child.xml_elem.attrib.get("type") == "host"
                    ):

                        for path_node_child_child in path_node_child.path_node_children_list:

                            for entity_other in path_node_child_child.entities_list:

                                if (
                                    path_node_child_child.xml_elem.tag.endswith("bibl")
                                    and entity_other.__class__ is F3_Manifestation_Product_Type
                                ):

                                    create_triple(
                                        entity_subj=entity_manifestation,
                                        entity_obj=entity_other,
                                        prop=Property.objects.get(name="host")
                                    )

            def triples_from_f3_to_f9(entity_manifestation, path_node: PathNode):

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if (
                            entity_other.__class__ is F9_Place
                            and child_path_node.xml_elem.tag.endswith("pubPlace")
                        ):

                            create_triple(
                                entity_subj=entity_manifestation,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="was published in")
                            )

            def triples_from_f3_to_e40(entity_manifestation, path_node: PathNode):

                date = None
                triple = None

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if (
                            entity_other.__class__ is E40_Legal_Body
                            and child_path_node.xml_elem.tag.endswith("publisher")
                        ):

                            triple = create_triple(
                                entity_subj=entity_other,
                                entity_obj=entity_manifestation,
                                prop=Property.objects.get(name="is publisher of")
                            )

                    if (
                        child_path_node.xml_elem.tag.endswith("date")
                        and is_valid_text(child_path_node.xml_elem.text)
                    ):

                        date = child_path_node.xml_elem.text

                if triple is not None and date is not None:

                    triple.start_date_written = date
                    triple.save()

            triples_from_f3_to_e55(entity_manifestation, path_node)
            triples_from_f3_to_f3(entity_manifestation, path_node)
            triples_from_f3_to_f9(entity_manifestation, path_node)
            triples_from_f3_to_e40(entity_manifestation, path_node)

        def parse_triples_from_e55_manifestation(entity_e55, path_node):

            name_type = path_node.xml_elem.attrib.get("type")
            name_subtype = path_node.xml_elem.attrib.get("subtype")

            if name_type is not None and name_subtype is not None:

                entity_type = None
                entity_subtype = None

                for entity in path_node.entities_list:

                    if entity.name == name_type:

                        entity_type = entity

                    if entity.name == name_subtype:

                        entity_subtype = entity

                if entity_type is None or entity_subtype is None:

                    raise Exception("At least one of the entities is None, but not supposed to be.")

                create_triple(
                    entity_subj=entity_subtype,
                    entity_obj=entity_type,
                    prop=Property.objects.get(name="p127 has broader term")
                )

        def parse_triples_from_f10_person(entity_person, path_node: PathNode):

            def triple_from_f10_to_f3(entity_person, path_node: PathNode):

                if path_node.path_node_parent.xml_elem.tag.endswith("bibl"):

                    for entity_other in path_node.path_node_parent.entities_list:

                        if entity_other.__class__ is F3_Manifestation_Product_Type:

                            create_triple(
                                entity_subj=entity_person,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="is author of")
                            )

            def triple_from_f10_to_f21(entity_person, path_node: PathNode):

                if path_node.path_node_parent.xml_elem.tag.endswith("bibl"):

                    for entity_other in path_node.path_node_parent.entities_list:

                        if entity_other.__class__ is F21_Recording_Work:

                            create_triple(
                                entity_subj=entity_person,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="is author of")
                            )

            triple_from_f10_to_f3(entity_person, path_node)
            triple_from_f10_to_f21(entity_person, path_node)


        def parse_triples_from_f21_recording_work(entity_recording_work, path_node: PathNode):

            def triple_from_f21_to_f26(entity_recording_work, path_node: PathNode):

                for path_node_neighbour in path_node.path_node_parent.path_node_children_list:

                    if path_node_neighbour.xml_elem.attrib.get("type") == "broadcasts":

                        for path_node_neighbour_child in path_node_neighbour.path_node_children_list:

                            for path_node_neighbour_child_child in path_node_neighbour_child.path_node_children_list:

                                for entity_other in path_node_neighbour_child_child.entities_list:

                                    if entity_other.__class__ is F26_Recording:

                                        create_triple(
                                            entity_subj=entity_recording_work,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="R13 is realised in"),
                                        )

            triple_from_f21_to_f26(entity_recording_work, path_node)

            parse_triples_from_f1_work(entity_recording_work, path_node)

        def parse_triples_from_f31_performance(entity_performance, path_node: PathNode):

            def triple_from_f31_to_e40(entity_performance, path_node: PathNode):

                for path_node_child in path_node.path_node_children_list:

                    for entity_other in path_node_child.entities_list:

                        if entity_other.__class__ is E40_Legal_Body:

                            create_triple(
                                entity_subj=entity_performance,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="has been performed at"),
                            )


            def triple_from_f31_to_f10(entity_performance, path_node: PathNode):

                for path_node_child in path_node.path_node_children_list:

                    entity_person = None
                    role = None

                    for entity_other in path_node_child.entities_list:

                        if entity_other.__class__ is F10_Person:

                            entity_person = entity_other

                    if path_node_child.xml_elem.attrib.get("role") is not None:

                        role = path_node_child.xml_elem.attrib.get("role")

                    if role is None:

                        for path_node_child_child in path_node_child.path_node_children_list:

                            if path_node_child_child.xml_elem.attrib.get("role") is not None:

                                role = path_node_child_child.xml_elem.attrib.get("role")

                    if entity_person is not None:

                        if role is not None:

                            if role == "director":

                                create_triple(
                                    entity_subj=entity_person,
                                    entity_obj=entity_performance,
                                    prop=Property.objects.get(name="is director of"),
                                )

                            elif role == "translator":

                                pass # to be ignored, because a translated theatre play needs to have its own work

                            else:

                                # TODO : Check how often this is the case
                                print(f"Found unspecified role {role}")

                        else:

                            # TODO : Check how often this is the case
                            print("Found a relation to a person without a role")

            triple_from_f31_to_e40(entity_performance, path_node)
            triple_from_f31_to_f10(entity_performance, path_node)


        def parse_triples_from_chapter(entity_chapter, path_node: PathNode):

            path_node_tei = climb_up(path_node, 5)

            def triple_from_chapter_to_f1(entity_chapter, path_node: PathNode):

                for path_node_text in path_node_tei.path_node_children_list:

                    if path_node_text.xml_elem.tag.endswith("text"):

                        for path_node_body in path_node_text.path_node_children_list:

                            if path_node_body.xml_elem.tag.endswith("body"):

                                for path_node_div in path_node_body.path_node_children_list:

                                    if path_node_div.xml_elem.tag.endswith("div"):

                                        for path_node_bibl in path_node_div.path_node_children_list:

                                            for entity_work in path_node_bibl.entities_list:

                                                if entity_work.__class__ == F1_Work:

                                                    create_triple(
                                                        entity_subj=entity_work,
                                                        entity_obj=entity_chapter,
                                                        prop=Property.objects.get(name="is in chapter"),
                                                    )

                                                break

                                        break

                                break

                        break

            def triple_from_chapter_to_chapter(entity_chapter: Chapter, path_node: PathNode):

                chapter_number_parent = ".".join(entity_chapter.chapter_number.split(".")[:-1])

                if chapter_number_parent != "":

                    entity_chapter_parent = Chapter.objects.get(chapter_number=chapter_number_parent)

                    create_triple(
                        entity_subj=entity_chapter,
                        entity_obj=entity_chapter_parent,
                        prop=Property.objects.get(name="is sub chapter of")
                    )


            triple_from_chapter_to_f1(entity_chapter, path_node)
            triple_from_chapter_to_chapter(entity_chapter, path_node)


        def parse_triples_from_xml_file(entity_xml_file, path_node: PathNode):

            def triple_to_all(entity_xml_file, path_node_current: PathNode):

                for entity_other in path_node_current.entities_list:

                    if not entity_other.__class__ is entity_xml_file.__class__:

                        create_triple(
                            entity_subj=entity_other,
                            entity_obj=entity_xml_file,
                            prop=Property.objects.get(name="data read from file"),
                        )

                    if (
                            path_node_current.path_node_parent is not None
                            and path_node_current.path_node_parent.xml_elem.tag.endswith("div")
                            and path_node_current.path_node_parent.xml_elem.attrib.get("type") == "entry"
                            and path_node_current.path_node_parent.path_node_parent.xml_elem.tag.endswith("body")
                            and path_node_current.path_node_parent.path_node_parent.path_node_parent.xml_elem.tag.endswith("text")
                    ):

                        create_triple(
                            entity_subj=entity_other,
                            entity_obj=entity_xml_file,
                            prop=Property.objects.get(name="was defined primarily in"),
                        )

                for path_node_child in path_node_current.path_node_children_list:

                    triple_to_all(entity_xml_file, path_node_child)


            triple_to_all(entity_xml_file, path_node)


        def sub_main(path_node):

            for entity in path_node.entities_list:

                if entity.__class__ is E55_Type:

                    parse_triples_from_e55_manifestation(entity, path_node)

                elif entity.__class__ is F1_Work:

                    parse_triples_from_f1_work(entity, path_node)

                elif entity.__class__ is F3_Manifestation_Product_Type:

                    parse_triples_from_f3_manifestation(entity, path_node)

                elif entity.__class__ is F10_Person:

                    parse_triples_from_f10_person(entity, path_node)

                elif entity.__class__ is F21_Recording_Work:

                    parse_triples_from_f21_recording_work(entity, path_node)

                elif entity.__class__ is F31_Performance:

                    parse_triples_from_f31_performance(entity, path_node)

                elif entity.__class__ is Chapter:

                    parse_triples_from_chapter(entity, path_node)

                elif entity.__class__ is Xml_File:

                    parse_triples_from_xml_file(entity, path_node)

        sub_main(path_node)


def parse_xml_entity_tmp(xml_file_path):
    # Temporary helper method to parse the xml_file path to create an entity representing the xml file
    # for help in curation

    db_result = Xml_File.objects.get_or_create(file_path=xml_file_path)

    if db_result[1] is False:

        raise Exception("XML file already parsed.")

    else:

        xml_ent = db_result[0]

        name = xml_file_path.split("/")[-1]

        with open(xml_file_path, "r") as f:

            file_content = f.read()

        xml_ent.name = name
        xml_ent.file_content = file_content
        xml_ent.save()

    return db_result[0]


def run(*args, **options):
    # TODO RDF : delete all model instances

    def reset_all():

        print("RootObject.objects.all().delete()")
        print(RootObject.objects.all().delete())

        print("construct_properties")
        construct_properties()


    def get_flat_file_list(folder):

        list_current = []

        for f in listdir(folder):

            path = folder + "/" + f

            if isfile(path) and f.endswith(".xml") and not f.endswith(".swp"):

                list_current.append(path)

            else:

                list_current.extend(get_flat_file_list(path))

        return list_current


    def crawl_xml_list(xml_file_list):

        def crawl_xml_tree_for_entities(path_node: PathNode, trees_manager: Type[TreesManager]):

            path_node = trees_manager.parse_for_entities(path_node, trees_manager)

            for xml_elem_child in path_node.xml_elem:

                child_path_node = PathNode(xml_elem_child, path_node)

                child_path_node = crawl_xml_tree_for_entities(child_path_node, trees_manager)

                path_node.path_node_children_list.append(child_path_node)

            return path_node


        def crawl_xml_tree_for_triples(path_node: PathNode, trees_manager: Type[TreesManager]):

            path_node.triples_list = trees_manager.parse_for_triples(path_node)

            for child_path_node in path_node.path_node_children_list:

                crawl_xml_tree_for_triples(child_path_node, trees_manager)


        def sub_main(xml_file_list):

            # Probably this algorithm could be done better with xpaths.
            # I did not think of them early enough until development had been already mostly done.
            # Should this be refactored, then implementing the several path-finding steps with xpaths might be more elegant.

            trees_manager = TreesManager

            for xml_file_path in xml_file_list:

                print(f"\nParsing {xml_file_path}")

                tree = ET.parse(xml_file_path)

                xml_entity = parse_xml_entity_tmp(xml_file_path)

                path_node_root = PathNode(tree.getroot(), None)
                path_node_root.entities_list.append(xml_entity)

                current_type = None

                if (
                    "005_TextefürHörspiele" in xml_file_path
                    or "006_DrehbücherundTextefürFilme" in xml_file_path
                ):

                    current_type = F21_Recording_Work

                # TODO : add more elsif to differentiate other types coming from other folders

                else:

                    current_type = F1_Work

                trees_manager.helper_dict["current_type"] = current_type

                path_node_root = crawl_xml_tree_for_entities(path_node_root, trees_manager)
                crawl_xml_tree_for_triples(path_node_root, trees_manager)

        sub_main(xml_file_list)


    def sub_main():

        reset_all()

        xml_file_list = []
        # xml_file_list.extend(get_flat_file_list("./manuelle-korrektur/korrigiert/bd1/"))
        # xml_file_list.append("./manuelle-korrektur/korrigiert/entities/bibls.xml")
        # xml_file_list.append("./manuelle-korrektur/korrigiert/entities/work_index.xml")
        # xml_file_list.append("./manuelle-korrektur/korrigiert/entities/person_index.xml")

        xml_file_list.append("./manuelle-korrektur/korrigiert/bd1/003_Interviews/FRBR-Works/interview_0015.xml")

        crawl_xml_list(xml_file_list)

    sub_main()