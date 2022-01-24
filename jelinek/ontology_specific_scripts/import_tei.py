from __future__ import annotations
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element as XmlElement
from typing import Type, List
from apis_core.apis_entities.models import *
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

    counter_e40_legal_body_parsed = 0
    counter_e40_legal_body_created = 0
    counter_e55type_parsed = 0
    counter_e55type_created = 0
    counter_f1_work_parsed = 0
    counter_f1_work_created = 0
    counter_f3_manifestation_parsed = 0
    counter_f3_manifestation_created = 0
    counter_f9_place_parsed = 0
    counter_f9_place_created = 0
    counter_f10_person_parsed = 0
    counter_f10_person_created = 0
    counter_f17_aggregation_work_parsed = 0
    counter_f17_aggregation_work_created = 0
    counter_f20_performance_work_parsed = 0
    counter_f20_performance_work_created = 0

    # TODO output these at the end of parsing
    entity_xml_tag_not_parsed = set()
    entity_xml_text_not_parsed = set()


    # @classmethod
    # def check_if_e40_legal_body(cls, path_node: PathNode):
    #
    #     xml_elem = path_node.xml_elem
    #
    #     return (
    #         xml_elem.tag.endswith("publisher")
    #         or xml_elem.tag.endswith("institution")
    #         or (
    #             xml_elem.tag.endswith("rs")
    #             and xml_elem.attrib.get("type") == "institution"
    #         )
    #         or xml_elem.tag.endswith("orgName")
    #     )
    #
    # @classmethod
    # def check_if_f1_work(cls, path_node: PathNode):
    #
    #     xml_elem = path_node.xml_elem
    #
    #     return (
    #         (
    #             xml_elem.tag.endswith("bibl")
    #             and xml_elem.attrib.get("ana") == "frbroo:work"
    #         )
    #         or (
    #             xml_elem.tag.endswith("rs")
    #             and xml_elem.attrib.get("type") == "work"
    #         )
    #     )
    #
    # @classmethod
    # def check_if_f3_manifestation(cls, path_node: PathNode):
    #
    #     xml_elem = path_node.xml_elem
    #
    #     return (
    #         xml_elem.tag.endswith("bibl")
    #         and (
    #             xml_elem.attrib.get("ana") == "frbroo:manifestation"
    #             or
    #             (
    #                 xml_elem.attrib.get("ref") is not None
    #                 and xml_elem.attrib.get("ref").startswith("bibls:")
    #             )
    #         )
    #     )
    #
    # @classmethod
    # def check_if_f9_place(cls, path_node: PathNode):
    #
    #     xml_elem = path_node.xml_elem
    #
    #     return xml_elem.tag.endswith("pubPlace")
    #
    # @classmethod
    # def check_if_f10_person(cls, path_node: PathNode):
    #
    #     xml_elem = path_node.xml_elem
    #
    #     if path_node.path_node_parent is not None:
    #
    #         xml_elem_parent = path_node.path_node_parent.xml_elem
    #
    #     return (
    #         (
    #             xml_elem.tag.endswith("persName")
    #             # and (
    #             #     not xml_elem_parent.tag.endswith("rs")
    #             #     and xml_elem_parent.attrib.get("type") != "person"
    #             # )
    #         )
    #         or (
    #             xml_elem.tag.endswith("rs")
    #             and xml_elem.attrib.get("type") == "person"
    #             and xml_elem.attrib.get("ref") is not None
    #             and xml_elem.attrib.get("ref").startswith("")
    #         )
    #     )
    #
    # @classmethod
    # def check_if_f17_aggregation_work(cls, path_node: PathNode):
    #
    #     xml_elem = path_node.xml_elem
    #
    #     return (
    #         xml_elem.tag.endswith("bibl")
    #         and xml_elem.attrib.get("ana") == "frbroo:aggregation_work"
    #     )
    #
    # @classmethod
    # def check_if_f20_performance_work(cls, path_node: PathNode):
    #
    #     xml_elem = path_node.xml_elem
    #
    #     return (
    #         xml_elem.tag.endswith("item")
    #         and xml_elem.attrib.get("ana") == "staging"
    #     )


    @classmethod
    def parse_for_entities(cls, path_node: PathNode):

        def handle_after_creation(db_result, attr_dict):

            def set_attr_to_entity(entity, attr_name, attr_val):

                if attr_val is not None:

                    entity_attr_val = getattr(entity, attr_name)

                    if entity_attr_val == "":

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

                if (
                        xml_elem.tag.endswith("bibl")
                        and xml_elem.attrib.get("ana") == "frbroo:work"
                ):

                    for xml_elem_child in xml_elem:

                        # TODO : Check if there are titles without 'type="main"'
                        if xml_elem_child.tag.endswith("title"):

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
                    "name": name
                }


            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["idno"] is not None:

                        db_result = F1_Work.objects.get_or_create(idno=attr_dict["idno"])

                    elif attr_dict["name"] is not None:

                        # db_result = F1_Work.objects.get_or_create(name=attr_dict["name"])
                        db_hit = F1_Work.objects.filter(name=attr_dict["name"])
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

                        if xml_elem_child.tag.endswith("title"):

                            name = xml_elem_child.text

                        elif xml_elem_child.tag.endswith("hi"):

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


            # def create_triples(entity_f3_manifestation, xml_elem):
            #
            #     str_e55_type = None
            #     str_e55_subtype = None
            #     entity_e55_type = None
            #     entity_e55_subtype = None
            #
            #     for attrib_key, attrib_value in xml_elem.attrib.items():
            #
            #         if attrib_key == "type":
            #
            #             cls.counter_e55type_parsed += 1
            #
            #             if str_e55_type is None:
            #
            #                 str_e55_type = attrib_value
            #
            #                 db_result = E55_Type.objects.get_or_create(name=str_e55_type)
            #
            #                 entity_e55_type = db_result[0]
            #
            #                 if db_result[1] is True:
            #
            #                     cls.counter_e55type_created += 1
            #                     print(f"created entity: type:  e55", db_result[0].name, db_result[0].pk)
            #
            #                 else:
            #
            #                     print("entity already exists")
            #
            #             else:
            #
            #                 print(f"Conflict: found a type before")
            #
            #         elif attrib_key == "subtype":
            #
            #             cls.counter_e55type_parsed += 1
            #
            #             if str_e55_subtype is None:
            #
            #                 str_e55_subtype = attrib_value
            #
            #                 db_result = E55_Type.objects.get_or_create(name=str_e55_subtype)
            #
            #                 entity_e55_subtype = db_result[0]
            #
            #                 if db_result[1] is True:
            #
            #                     cls.counter_e55type_created += 1
            #                     print(f"created entity: type:  e55", db_result[0].name, db_result[0].pk)
            #
            #                 else:
            #
            #                     print("entity already exists")
            #
            #             else:
            #
            #                 print(f"Conflict: found a subtype before")
            #
            #     if entity_e55_type is not None and entity_e55_subtype is not None:
            #
            #         triple = TempTriple.objects.get_or_create(
            #             subj=entity_e55_subtype,
            #             obj=entity_e55_type,
            #             prop=Property.objects.get(name="p127 has broader term")
            #         )[0]
            #
            #     elif entity_e55_type is None and entity_e55_subtype is not None:
            #
            #         print(f"found subtype but no type: node:{entity_e55_subtype}")
            #
            #     if entity_e55_type is not None:
            #
            #         xml_elem.apis_object_attrib_list.append(entity_e55_type)
            #
            #     if entity_e55_subtype is not None:
            #
            #         xml_elem.apis_object_attrib_list.append(entity_e55_subtype)
            #
            #     if entity_f3_manifestation is not None and entity_e55_type is not None:
            #
            #         triple = TempTriple.objects.get_or_create(
            #             subj=entity_f3_manifestation,
            #             obj=entity_e55_type,
            #             prop=Property.objects.get(name="p2 has type")
            #         )[0]

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

                    if xml_elem_child.tag.endswith("forename"):

                        forename = xml_elem_child.text

                    if xml_elem_child.tag.endswith("surname"):

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
                    )
                ):

                    name, forename, surname = parse_persName(xml_elem)

                else:

                    return None

                return {
                    "pers_id": pers_id,
                    "name": name,
                    "forename": forename,
                    "surname": surname,
                }

            def sub_main(path_node):

                entities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["pers_id"] is not None:

                        db_result = F10_Person.objects.get_or_create(pers_id=attr_dict["pers_id"])

                    elif attr_dict["forename"] is not None and attr_dict["surname"] is not None:

                        db_result = F10_Person.objects.get_or_create(forename=attr_dict["forename"], surname=attr_dict["surname"])

                    elif attr_dict["name"] is not None:

                        # There can be multiple persons with the same name, hence until disambiguation can be finished,
                        # db_result = F10_Person.objects.get_or_create(name=attr_dict["name"])
                        db_hit = F10_Person.objects.filter(name=attr_dict["name"])
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

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    entities_list.append(handle_after_creation(db_result, attr_dict))

                    # TODO : Triple creation here

                return entities_list

            return sub_main(path_node)

            #
            # cls.counter_f10_person_parsed += 1
            #
            # forename = None
            #
            # surname = None
            #
            # for xml_elem_child in xml_elem.getchildren():
            #
            #     if xml_elem_child.tag.endswith("forename"):
            #
            #         forename = xml_elem_child.text
            #
            #     elif xml_elem_child.tag.endswith("surname"):
            #
            #         surname = xml_elem_child.text
            #
            # kwargs = {}
            #
            # if forename is None and surname is None:
            #
            #     kwargs["name"] = xml_elem.text
            #
            # else:
            #
            #     # TODO
            #     if forename is None:
            #         forename = ""
            #
            #     if surname is None:
            #         surname = ""
            #
            #     kwargs["forename"] = forename
            #     kwargs["surname"] = surname
            #     kwargs["name"] = forename + ", " + surname
            #
            # if kwargs["name"] is not None:
            #
            #     db_result = F10_Person.objects.get_or_create(**kwargs)
            #
            #     if db_result[1] is True:
            #
            #         entity = db_result[0]
            #         cls.counter_f10_person_created += 1
            #         print(f"created entity: type: {entity.__class__.__name__}, name: {entity.name}, pk: {entity.pk}")
            #
            #     else:
            #
            #         print("entity already exists")

        def parse_f17_aggregation_work(path_node):

            cls.counter_f17_aggregation_work_parsed += 1

            title = None

            for c in xml_elem.getchildren():

                if c.tag.endswith("title"):

                    if title is None:

                        title = c.text

                    else:

                        print("Found multiple titles!")

            db_result = F17_Aggregation_Work.objects.get_or_create(name=title)

            if db_result[1] is True:

                entity = db_result[0]
                cls.counter_f17_aggregation_work_created += 1
                print(f"created entity: type: {entity.__class__.__name__}, name: {entity.name}, pk: {entity.pk}")

            else:

                print("entity already exists")


        def parse_f20_performance_work(path_node):

            cls.counter_f20_performance_work_parsed += 1

            def create_entity(xml_elem):

                note = None
                category = None
                start_date_written = None

                for path_node_child in xml_elem:

                    xml_elem_child = path_node_child.xml_elem

                    if xml_elem_child.tag.endswith("note"):

                        note = xml_elem_child.text

                        for path_node_child_child in path_node_child.path_node_children_list:

                            xml_elem_child_child = path_node_child_child.xml_elem

                            if (
                                    xml_elem_child_child.tag.endswith("ref")
                                    and xml_elem_child_child.attrib.get("type") == "category"
                            ):

                                category = xml_elem_child_child.text

                    elif xml_elem_child.tag.endswith("date"):

                        start_date_written = xml_elem_child.text

                name = f"unnamed f20, number {cls.counter_f20_performance_work_parsed}"

                db_result = F20_Performance_Work.objects.get_or_create(name=name)

                entity_f20_performance_work = db_result[0]

                entity_f20_performance_work.note = note

                entity_f20_performance_work.category = category

                entity_f20_performance_work.start_date_written = start_date_written

                entity_f20_performance_work.save()

                if db_result[1] is True:

                    entity = db_result[0]
                    cls.counter_f20_performance_work_created += 1
                    print(f"created entity: type: {entity.__class__.__name__}, name: {entity.name}, pk: {entity.pk}")

                else:

                    print("entity already exists")

                return entity_f20_performance_work


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

        # def create_triples(entity_f20_performance_work, xml_elem):
        #
        #     for path_node_child in xml_elem.path_node_children_list:
        #
        #         xml_elem_child = path_node_child.xml_elem
        #
        #         if xml_elem_child.tag.endswith("persName"):
        #
        #             entity_f10_person = path_node_child.apis_object_main
        #
        #             prop = None
        #
        #             if xml_elem_child.attrib.get("role") == "director":
        #
        #                 prop = Property.objects.get(name="is director of")
        #
        #             elif xml_elem_child.attrib.get("role") == "translator":
        #
        #                 prop = Property.objects.get(name="is translator of")
        #
        #             else:
        #
        #                 print(
        #                     f"Found relation to person but without role:"
        #                     f" f20: {entity_f20_performance_work},"
        #                     f" f10: {entity_f10_person},"
        #                 )
        #
        #             if prop is not None:
        #
        #                 triple = TempTriple.objects.get_or_create(
        #                     subj=entity_f10_person,
        #                     obj=entity_f20_performance_work,
        #                     prop=prop,
        #                 )[0]
        #
        #         elif (
        #             xml_elem_child.tag.endswith("rs")
        #             and xml_elem_child.attrib.get("type") == "institution"
        #         ):
        #
        #             entity_e40_legal_body = path_node_child.apis_object_main
        #
        #             triple = TempTriple.objects.get_or_create(
        #                 subj=entity_f20_performance_work,
        #                 obj=entity_e40_legal_body,
        #                 prop=Property.objects.get(name="has been performed at"),
        #             )[0]

    # @classmethod
    # def parse_triple_f3_manifestation_to_e40_legal_body(cls, path_node_of_manifestatation):
    #
    #     triple = None
    #
    #     entity_f3_manifestation = path_node_of_manifestatation.apis_object_main
    #
    #     if entity_f3_manifestation is not None:
    #
    #         for path_node_child in path_node_of_manifestatation.path_node_children_list:
    #
    #             e40_legal_body_entity = path_node_child.apis_object_main
    #
    #             if (
    #                 path_node_child.apis_object_main is not None
    #                 and type(e40_legal_body_entity) is E40_Legal_Body
    #             ):
    #
    #                 prop = None
    #
    #                 if path_node_child.xml_elem.tag.endswith("publisher"):
    #
    #                     prop = Property.objects.get(name="is publisher of")
    #
    #                 elif path_node_child.xml_elem.tag.endswith("institution"):
    #
    #                     if path_node_child.xml_elem.attrib.get("role") == "editor":
    #
    #                         prop = Property.objects.get(name="is editor of")
    #
    #                     else:
    #
    #                         print(f"Found no specifying role of institution")
    #
    #                 elif (
    #                     path_node_child.xml_elem.tag.endswith("orgName")
    #                     and path_node_child.xml_elem.attrib.get("role") == "editor"
    #                 ):
    #
    #                     prop = Property.objects.get(name="is editor of")
    #
    #                 else:
    #
    #                     print(
    #                         f"Found e40 child node of f3 without a valid relation pattern. "
    #                         f"f3: {path_node_of_manifestatation.apis_object_main} "
    #                         f"e40: {path_node_child.apis_object_main}"
    #                     )
    #
    #                 if prop is not None:
    #
    #                     triple = TempTriple.objects.get_or_create(
    #                         subj=e40_legal_body_entity,
    #                         obj=entity_f3_manifestation,
    #                         prop=prop
    #                     )[0]
    #
    #     return triple
    #
    #
    # @classmethod
    # def parse_triple_f3_manifestation_host_f3_manifestation(cls, path_node_of_manifestatation):
    #
    #     triple = None
    #
    #     entity_f3_manifestation_hosted = path_node_of_manifestatation.apis_object_main
    #
    #     if entity_f3_manifestation_hosted is not None:
    #
    #         for path_node_child in path_node_of_manifestatation.path_node_children_list:
    #
    #             if (
    #                 path_node_child.xml_elem.tag.endswith("relatedItem")
    #                 and path_node_child.xml_elem.attrib.get("type") == "host"
    #             ):
    #
    #                 for path_node_child_child in path_node_child.path_node_children_list:
    #
    #                     entity_f3_manifestation_host = path_node_child_child.apis_object_main
    #
    #                     if (
    #                         path_node_child_child.xml_elem.tag.endswith("bibl")
    #                         and entity_f3_manifestation_host is not None
    #                         and type(entity_f3_manifestation_host) is F3_Manifestation_Product_Type
    #                     ):
    #                         triple = TempTriple.objects.create(
    #                             subj=entity_f3_manifestation_hosted,
    #                             obj=entity_f3_manifestation_host,
    #                             prop=Property.objects.get(name="host")
    #                         )
    #
    #     return triple
    #
    # @classmethod
    # def parse_triple_f3_manifestation_published_f9_place(cls, xml_elem):
    #
    #     triple = None
    #
    #     entity_f3_manifestation = xml_elem.apis_object_main
    #
    #     if entity_f3_manifestation is not None:
    #
    #         for path_node_child in xml_elem.path_node_children_list:
    #
    #             f9_place = path_node_child.apis_object_main
    #
    #             if (
    #                 path_node_child.xml_elem.tag.endswith("pubPlace")
    #                 and type(f9_place) is F9_Place
    #             ):
    #
    #                 triple = TempTriple.objects.get_or_create(
    #                     subj=entity_f3_manifestation,
    #                     obj=f9_place,
    #                     prop=Property.objects.get(name="was published in")
    #                 )[0]
    #
    #     return triple
    #
    # @classmethod
    # def parse_triple_f3_manifestation_f10_person(cls, xml_elem):
    #
    #     triple = None
    #
    #     entity_f3_manifestation = xml_elem.apis_object_main
    #
    #     if entity_f3_manifestation is not None:
    #
    #         for path_node_child in xml_elem.path_node_children_list:
    #
    #             entity_f10_person = path_node_child.apis_object_main
    #
    #             if (
    #                 path_node_child.xml_elem.tag.endswith("persName")
    #                 and type(entity_f10_person) is F10_Person
    #             ):
    #
    #                 role = path_node_child.xml_elem.attrib.get("role")
    #
    #                 prop = None
    #
    #                 if role == "author":
    #
    #                     prop = Property.objects.get(name="is author of")
    #
    #                 elif role == "translator":
    #
    #                     prop = Property.objects.get(name="is translator of")
    #
    #                 elif role == "editor":
    #
    #                     prop = Property.objects.get(name="is editor of")
    #
    #                 if prop is not None:
    #
    #                     triple = TempTriple.objects.get_or_create(
    #                         subj=entity_f10_person,
    #                         obj=entity_f3_manifestation,
    #                         prop=prop
    #                     )[0]
    #
    #                 else:
    #
    #                     print(f"Found person with no role attached. Can not create relationship with unknown property.")
    #
    #     return triple
    #
    # @classmethod
    # def parse_triple_f1_to_f3(cls, xml_elem):
    #
    #     triple = None
    #
    #     f1_or_f17 = None
    #
    #     for path_node_child in xml_elem.path_node_children_list:
    #
    #         if (
    #             path_node_child.xml_elem.tag.endswith("bibl")
    #             and "ana" in path_node_child.xml_elem.attrib
    #         ):
    #
    #             if f1_or_f17 is not None:
    #
    #                 print("found multiple assignments!")
    #
    #             f1_or_f17 = path_node_child.apis_object_main
    #
    #         elif (
    #             path_node_child.xml_elem.tag.endswith("div")
    #             and (
    #                 path_node_child.xml_elem.attrib.get("type") == "frbroo:manifestations"
    #                 or path_node_child.xml_elem.attrib.get("type") == "frbroo:manifestation"
    #             )
    #         ):
    #
    #             for c in path_node_child.path_node_children_list:
    #
    #                 if c.apis_object_main.__class__ is F3_Manifestation_Product_Type:
    #
    #                     f3 = c.apis_object_main
    #
    #                     triple = TempTriple.objects.get_or_create(
    #                         subj=f1_or_f17,
    #                         obj=f3,
    #                         prop=Property.objects.get(name="is expressed in")
    #                     )[0]
    #
    #
    #         elif (
    #             path_node_child.xml_elem.tag.endswith("div")
    #             and path_node_child.xml_elem.attrib.get("type") == "contained"
    #         ):
    #
    #
    #             for bibl in path_node_child.path_node_children_list[0].path_node_children_list:
    #
    #                 for c in bibl.path_node_children_list:
    #
    #                     if c.apis_object_main.__class__ == F1_Work:
    #
    #                         f1 = c.apis_object_main
    #
    #                         triple = TempTriple.objects.get_or_create(
    #                             subj=f1_or_f17,
    #                             obj=f1,
    #                             prop=Property.objects.get(name="contains")
    #                         )[0]
    #
    #     return triple
    #
    #
    # @classmethod
    # def parse_triple_f17_to_f1(cls, xml_elem):
    #
    #     triple = None
    #
    #     f17 = None
    #
    #     for path_node_child in xml_elem.path_node_children_list:
    #
    #         if path_node_child.apis_object_main.__class__ == F17_Aggregation_Work:
    #
    #             f17 = path_node_child.apis_object_main
    #
    #         elif (
    #             path_node_child.xml_elem.tag.endswith("div")
    #             and path_node_child.xml_elem.attrib.get("type") == "contained"
    #         ):
    #
    #             for potential_bibl in path_node_child.path_node_children_list[0].path_node_children_list:
    #
    #                 for c in potential_bibl.path_node_children_list:
    #
    #                     if c.apis_object_main.__class__ == F1_Work:
    #
    #                         f1 = c.apis_object_main
    #
    #                         triple = TempTriple.objects.get_or_create(
    #                             subj=f17,
    #                             obj=f1,
    #                             prop=Property.objects.get(name="contains")
    #                         )[0]
    #
    #     return triple
    #
    #
    # @classmethod
    # def parse_triple_f1_to_f10(cls, xml_elem):
    #
    #     triple = None
    #
    #     f1 = xml_elem.apis_object_main
    #     f10 = None
    #
    #     for c in xml_elem.path_node_children_list:
    #
    #         if c.apis_object_main.__class__ == F10_Person:
    #
    #             f10 = c.apis_object_main
    #
    #             triple = TempTriple.objects.get_or_create(
    #                 subj=f10,
    #                 obj=f1,
    #                 prop=Property.objects.get(name="is author of")
    #             )[0]
    #
    #     return triple
    #
    # @classmethod
    # def parse_path_node_OLD(cls, xml_elem: ContextNode) -> ContextNode:
    # 
    #     if (
    #         xml_elem.tag.endswith("bibl")
    #         and xml_elem.attrib.get("ana") == "frbroo:work"
    #     ):
    # 
    #         xml_elem = cls.parse_f1_work(xml_elem)
    # 
    #         cls.parse_triple_f1_to_f10(xml_elem)
    # 
    #     elif (
    #         xml_elem.tag.endswith("bibl")
    #         and xml_elem.attrib.get("ana") == "frbroo:aggregation_work"
    #     ):
    # 
    #         xml_elem = cls.parse_f17_aggregation_work(xml_elem)
    # 
    #     elif (
    #         xml_elem.tag.endswith("rs")
    #         and xml_elem.attrib.get("type") == "work"
    #     ):
    # 
    #         xml_elem = cls.parse_f1_work(xml_elem)
    # 
    #     elif (
    #         xml_elem.tag.endswith("bibl")
    #         and xml_elem.attrib.get("ana") == "frbroo:manifestation"
    #     ):
    # 
    #         xml_elem = cls.parse_f3_manifestation(xml_elem)
    # 
    #         triple_f3_manifestation_to_e40_legal_body = cls.parse_triple_f3_manifestation_to_e40_legal_body(xml_elem)
    # 
    #         triple_f3_manifestation_host_f3_manifestation = cls.parse_triple_f3_manifestation_host_f3_manifestation(xml_elem)
    # 
    #         triple_f3_manifestation_published_f9_place = cls.parse_triple_f3_manifestation_published_f9_place(xml_elem)
    # 
    #         triple_f3_manifestation_f10_person = cls.parse_triple_f3_manifestation_f10_person(xml_elem)
    # 
    #     elif (
    #         xml_elem.tag.endswith("publisher")
    #         or xml_elem.tag.endswith("institution")
    #         or (
    #             xml_elem.tag.endswith("rs")
    #             and xml_elem.attrib.get("type") == "institution"
    #         )
    #         or xml_elem.tag.endswith("orgName")
    #     ):
    # 
    #         xml_elem = cls.parse_e40_legal_body(xml_elem)
    # 
    #     elif xml_elem.tag.endswith("pubPlace"):
    # 
    #         xml_elem = cls.parse_f9_place(xml_elem)
    # 
    #     elif xml_elem.tag.endswith("persName"):
    # 
    #         xml_elem = cls.parse_f10_person(xml_elem)
    # 
    #     elif (
    #         xml_elem.tag.endswith("item")
    #         and xml_elem.attrib.get("ana") == "staging"
    #     ):
    # 
    #         pass
    #         # TODO
    #         # xml_elem = cls.parse_f20_performance_work(xml_elem)
    # 
    #     elif (
    #         xml_elem.tag.endswith("div")
    #         and xml_elem.attrib.get('type') == "entry"
    #     ):
    # 
    #         cls.parse_triple_f1_to_f3(xml_elem)
    # 
    #         cls.parse_triple_f17_to_f1(xml_elem)
    # 
    # 
    #     return xml_elem

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

            def triple_from_f1_to_f3(entity_work, path_node):

                for neighbour_path_node in path_node.path_node_parent.path_node_children_list:

                    # direct manifestations
                    if (
                        neighbour_path_node.xml_elem.tag.endswith("div")
                        and neighbour_path_node.xml_elem.attrib.get("type") == "frbroo:manifestations"
                    ):

                        for neighbour_child_path_node in neighbour_path_node.path_node_children_list:

                            if neighbour_child_path_node.xml_elem.tag.endswith("listBibl"):

                                for neighbour_child_child_path_node in neighbour_child_path_node.path_node_children_list:

                                    for entity_other in neighbour_child_child_path_node.entities_list:

                                        if entity_other.__class__ is F3_Manifestation_Product_Type:

                                            create_triple(
                                                entity_subj=entity_work,
                                                entity_obj=entity_other,
                                                prop=Property.objects.get(name="is expressed in")
                                            )

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

            triple_from_f1_to_f10(entity_work, path_node)
            triple_from_f1_to_f3(entity_work, path_node)

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

            triple_from_f10_to_f3(entity_person, path_node)


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



        def sub_main(path_node):

            for entity in path_node.entities_list:

                if entity.__class__ == F1_Work:

                    parse_triples_from_f1_work(entity, path_node)

                elif entity.__class__ == F3_Manifestation_Product_Type:

                    parse_triples_from_f3_manifestation(entity, path_node)

                elif entity.__class__ == E55_Type:

                    parse_triples_from_e55_manifestation(entity, path_node)

                elif entity.__class__ == F10_Person:

                    parse_triples_from_f10_person(entity, path_node)

                elif entity.__class__ == Chapter:

                    parse_triples_from_chapter(entity, path_node)

        sub_main(path_node)




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


        # TODO : Add relation entity -'read data from file'-> xml file
        def crawl_xml_tree_for_entities(path_node: PathNode, trees_manager: Type[TreesManager]):

            path_node = trees_manager.parse_for_entities(path_node)

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

            # xml_file_list = ["./manuelle-korrektur/korrigiert/bd1/001_Werke/011_EssayistischeTexteRedenundStatements/016_ZurösterreichischenPolitikundGesellschaft/001_EssaysBeiträge/014_EinVolkEinFest.xml"]

            for xml_file in xml_file_list:

                print(f"\nParsing {xml_file}")

                tree = ET.parse(xml_file)

                # TODO : Create xml file entity

                root_path_node = crawl_xml_tree_for_entities(PathNode(tree.getroot(), None), trees_manager)
                crawl_xml_tree_for_triples(root_path_node, trees_manager)

            print(f"ObjectCreator.counter_e40_legal_body_parsed: {trees_manager.counter_e40_legal_body_parsed}")
            print(f"ObjectCreator.counter_e40_legal_body_created: {trees_manager.counter_e40_legal_body_created}")

            print(f"ObjectCreator.counter_e55type_parsed: {trees_manager.counter_e55type_parsed}")
            print(f"ObjectCreator.counter_e55type_created: {trees_manager.counter_e55type_created}")

            print(f"ObjectCreator.counter_f1_work_parsed: {trees_manager.counter_f1_work_parsed}")
            print(f"ObjectCreator.counter_f1_work_created: {trees_manager.counter_f1_work_created}")

            print(f"ObjectCreator.counter_f3_manifestation_parsed: {trees_manager.counter_f3_manifestation_parsed}")
            print(f"ObjectCreator.counter_f3_manifestation_created: {trees_manager.counter_f3_manifestation_created}")

            print(f"ObjectCreator.counter_f9_place_parsed: {trees_manager.counter_f9_place_parsed}")
            print(f"ObjectCreator.counter_f9_place_created: {trees_manager.counter_f9_place_created}")

            print(f"ObjectCreator.counter_f10_person_parsed: {trees_manager.counter_f10_person_parsed}")
            print(f"ObjectCreator.counter_f10_person_created: {trees_manager.counter_f10_person_created}")

            print(f"ObjectCreator.counter_f17_aggregation_work_parsed: {trees_manager.counter_f17_aggregation_work_parsed}")
            print(f"ObjectCreator.counter_f17_aggregation_work_created: {trees_manager.counter_f17_aggregation_work_created}")

            print(f"ObjectCreator.counter_f20_performance_work_parsed: {trees_manager.counter_f20_performance_work_parsed}")
            print(f"ObjectCreator.counter_f20_performance_work_created: {trees_manager.counter_f20_performance_work_created}")

        sub_main(xml_file_list)


    def sub_main():

        reset_all()

        xml_file_list = []
        xml_file_list.extend(get_flat_file_list("./manuelle-korrektur/korrigiert/bd1/"))
        xml_file_list.append("./manuelle-korrektur/korrigiert/entities/bibls.xml")
        # xml_file_list.append("./manuelle-korrektur/korrigiert/entities/bibls_test.xml")
        xml_file_list.append("./manuelle-korrektur/korrigiert/entities/work_index.xml")
        xml_file_list.append("./manuelle-korrektur/korrigiert/entities/person_index.xml")

        crawl_xml_list(xml_file_list)

    sub_main()