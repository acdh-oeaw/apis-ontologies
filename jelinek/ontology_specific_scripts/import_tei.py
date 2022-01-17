from __future__ import annotations
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element as XmlElement
from typing import Type, List
from apis_core.apis_entities.models import *
from apis_core.apis_relations.models import TempTriple, Property
from apis_core.apis_vocabularies.models import *
from django.core.management.base import BaseCommand, CommandError
from os import listdir
from os.path import isfile, join


class ContextNode():

    xml_elem = None
    context_node_parent: ContextNode
    context_node_children_list: List[ContextNode]
    apis_object_main = None
    apis_object_attrib_list = None
    apis_object_related_list = None

    def __init__(self, xml_elem, context_node_parent):
        self.xml_elem = xml_elem
        self.context_node_parent = context_node_parent
        self.context_node_children_list = []
        self.apis_object_attrib_list = []
        self.apis_object_related_list = []

    def __str__(self):

        return self.xml_elem.tag.replace("{http://www.tei-c.org/ns/1.0}", "") + "-" + str(self.xml_elem.attrib) + "-" + self.xml_elem.text

    def __repr__(self):

        return self.__str__()




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


    @classmethod
    def check_if_e40_legal_body(cls, context_node: ContextNode):

        xml_elem = context_node.xml_elem

        return (
            xml_elem.tag.endswith("publisher")
            or xml_elem.tag.endswith("institution")
            or (
                xml_elem.tag.endswith("rs")
                and xml_elem.attrib.get("type") == "institution"
            )
            or xml_elem.tag.endswith("orgName")
        )

    @classmethod
    def check_if_f1_work(cls, context_node: ContextNode):

        xml_elem = context_node.xml_elem

        return (
            (
                xml_elem.tag.endswith("bibl")
                and xml_elem.attrib.get("ana") == "frbroo:work"
            )
            or (
                xml_elem.tag.endswith("rs")
                and xml_elem.attrib.get("type") == "work"
            )
        )

    @classmethod
    def check_if_f3_manifestation(cls, context_node: ContextNode):

        xml_elem = context_node.xml_elem

        return (
            xml_elem.tag.endswith("bibl")
            and (
                xml_elem.attrib.get("ana") == "frbroo:manifestation"
                or
                (
                    xml_elem.attrib.get("ref") is not None
                    and xml_elem.attrib.get("ref").startswith("bibls:")
                )
            )
        )

    @classmethod
    def check_if_f9_place(cls, context_node: ContextNode):

        xml_elem = context_node.xml_elem

        return xml_elem.tag.endswith("pubPlace")

    @classmethod
    def check_if_f10_person(cls, context_node: ContextNode):

        xml_elem = context_node.xml_elem

        if context_node.context_node_parent is not None:

            xml_elem_parent = context_node.context_node_parent.xml_elem

        return (
            (
                xml_elem.tag.endswith("persName")
                # and (
                #     not xml_elem_parent.tag.endswith("rs")
                #     and xml_elem_parent.attrib.get("type") != "person"
                # )
            )
            or (
                xml_elem.tag.endswith("rs")
                and xml_elem.attrib.get("type") == "person"
                and xml_elem.attrib.get("ref") is not None
                and xml_elem.attrib.get("ref").startswith("")
            )
        )

    @classmethod
    def check_if_f17_aggregation_work(cls, context_node: ContextNode):

        xml_elem = context_node.xml_elem

        return (
            xml_elem.tag.endswith("bibl")
            and xml_elem.attrib.get("ana") == "frbroo:aggregation_work"
        )

    @classmethod
    def check_if_f20_performance_work(cls, context_node: ContextNode):

        xml_elem = context_node.xml_elem

        return (
            xml_elem.tag.endswith("item")
            and xml_elem.attrib.get("ana") == "staging"
        )


    @classmethod
    def parse_entity(cls, context_node: ContextNode):

        print(f"\nParsing: tag: {context_node.xml_elem.tag}, attrib: {context_node.xml_elem.attrib}, text: {context_node.xml_elem.text.__repr__()}")

        if cls.check_if_e40_legal_body(context_node):

            cls.parse_e40_legal_body(context_node.xml_elem)

        if cls.check_if_f1_work(context_node):

            f1_work = cls.parse_f1_work(context_node.xml_elem)

            # for xml_elem_child in xml_elem:
            #
            #     if xml_elem_child

        if cls.check_if_f3_manifestation(context_node):

            cls.parse_f3_manifestation(context_node.xml_elem)

        if cls.check_if_f9_place(context_node):

            cls.parse_f9_place(context_node.xml_elem)

        if cls.check_if_f10_person(context_node):

            # TODO : Consider ruling out Project members
            cls.parse_f10_person(context_node.xml_elem)

        if cls.check_if_f17_aggregation_work(context_node):

            cls.parse_f17_aggregation_work(context_node.xml_elem)

        if cls.check_if_f20_performance_work(context_node):

            pass
            # TODO
            # cls.parse_f20_performance_work(xml_elem)

        # TODO
        if (
            context_node.xml_elem.tag.endswith("div")
            and context_node.xml_elem.attrib.get('type') == "entry"
        ):

            pass

        else:

            print(f"Nothing created")

            if context_node.xml_elem.tag not in cls.entity_xml_tag_not_parsed:

                cls.entity_xml_tag_not_parsed.add(context_node.xml_elem.tag)

            if context_node.xml_elem.text not in cls.entity_xml_text_not_parsed:

                cls.entity_xml_text_not_parsed.add(context_node.xml_elem.text)


    @classmethod
    def parse_e40_legal_body(cls, xml_elem):

        if xml_elem.text is not None:

            db_result = E40_Legal_Body.objects.get_or_create(name=xml_elem.text)

            if db_result[1] is True:

                entity = db_result[0]
                cls.counter_e40_legal_body_created += 1
                print(f"created entity: type: {entity.__class__.__name__}, name: {entity.name}, pk: {entity.pk}")

            else:

                print("entity already exists")

        else:

            # TODO : Check how often this is the case
            print("Came accross an e40 without name")

        cls.counter_e40_legal_body_parsed += 1




    @classmethod
    def parse_f1_work(cls, xml_elem):

        cls.counter_f1_work_parsed += 1
        entity = None
        title = None
        idno = None

        if (
            xml_elem.attrib.get("ref") is not None
            and xml_elem.attrib.get("ref").startswith("works:")
        ):

            idno = xml_elem.attrib.get("ref").replace("works:", "")

        if (
            xml_elem.tag.endswith("rs")
            and xml_elem.attrib.get("type") == "work"
        ):

            title = xml_elem.text

        for xml_elem_child in xml_elem:

            if xml_elem_child.tag.endswith("title"):

                if title is not None:

                    # raise Exception("Inconsistent data or mapping")
                    print("Potentially inconsistent data or mapping")

                title = xml_elem_child.text

            elif xml_elem_child.tag.endswith("idno") and xml_elem_child.attrib["type"] == "JWV":

                if idno is not None:

                    raise Exception("Inconsistent data or mapping")

                idno = xml_elem_child.text

        db_result = None

        if idno is not None:

            db_result = F1_Work.objects.get_or_create(idno=idno)

        elif title is not None:

            # TODO : Temporary Work-around until the encoding problem is solved
            # db_result = F1_Work.objects.get_or_create(name=title)
            db_hit = F1_Work.objects.filter(name=title)
            if len(db_hit) > 1:

                # TODO : Check how often this is the case
                print("Multiple occurences found, taking the first")
                db_result = [db_hit[0], False]

            elif len(db_hit) == 1:

                db_result = [db_hit[0], False]

            elif len(db_hit) == 0:

                db_result = [
                    F1_Work.objects.create(name=title),
                    True
                ]

        if db_result is not None:

            entity = db_result[0]

            if title is not None and entity.name != "" and not entity.name.startswith(
                    "unnamed") and title != entity.name:

                # TODO : Check how often this is the case
                print(
                    f"Potentially inconsistent data or mapping: title of xml node: {title}, name of entity: {entity.name}")

            elif title is not None and (entity.name == "" or entity.name.startswith("unnamed")):

                entity.name = title

            elif title is None and (entity.name == "" or entity.name.startswith("unnamed")):

                entity.name = f"unnamed f1, number {cls.counter_f1_work_parsed}"

            if idno is not None:

                entity.idno = idno

            entity.save()

            if db_result[1] is True:

                cls.counter_f1_work_created += 1
                print(f"created entity: type: {entity.__class__.__name__}, name: {entity.name}, pk: {entity.pk}")

            else:

                print("entity already exists")

        else:

            # TODO : Check how often this is the case
            print("Entity found without a uniquely identifying attribute")

        return entity


    @classmethod
    def parse_f3_manifestation(cls, xml_elem):

        cls.counter_f3_manifestation_parsed += 1

        entity_f3_manifestation = None

        title = None
        title_in_note = None
        series = None
        edition = None
        date = None
        note = None
        ref_target = None
        ref_accessed = None
        text_language = None
        bibl_id = None

        if xml_elem.attrib.get('{http://www.w3.org/XML/1998/namespace}id') is not None:

            bibl_id = xml_elem.attrib.get('{http://www.w3.org/XML/1998/namespace}id')

        if (
            xml_elem.get("ref") is not None
            and xml_elem.get("ref").startswith("bibls:")
        ):

            bibl_id = xml_elem.get("ref").replace("bibls:", "")

        for xml_elem_child in xml_elem:

            if xml_elem_child.tag.endswith("title"):

                title = xml_elem_child.text

            elif xml_elem_child.tag.endswith("hi"):

                title = xml_elem_child.text

            elif xml_elem_child.tag.endswith("series"):

                series = xml_elem_child.text

            elif xml_elem_child.tag.endswith("edition"):

                edition = xml_elem_child.text

            elif xml_elem_child.tag.endswith("date"):

                if xml_elem_child.attrib.get("type") == "lastAccessed":

                    ref_accessed = xml_elem_child.text

                else:

                    date = xml_elem_child.text

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

                print()
                pass

            else:

                print("unhandled node")
                print(xml_elem_child)

        if title is not None and title_in_note is not None:

            print(
                f"conflicting data found in frbroo:manifestation between title: '{title}' "
                f"and title_is_note: '{title_in_note}'"
            )
            return None

        elif title is None and title_in_note is not None:

            title = title_in_note

        db_result = None

        if bibl_id is not None:

            db_result = F3_Manifestation_Product_Type.objects.get_or_create(
                bibl_id=bibl_id,
            )

        elif title is not None:

            # TODO : Temporary Work-around until the encoding problem is solved
            # db_result = F3_Manifestation_Product_Type.objects.get_or_create(
            #     name=title,
            # )
            db_hit = F3_Manifestation_Product_Type.objects.filter(name=title)
            if len(db_hit) > 1:

                # TODO : Check how often this is the case
                print("Multiple occurences found, taking the first")
                db_result = [db_hit[0], False]

            elif len(db_hit) == 1:

                db_result = [db_hit[0], False]

            elif len(db_hit) == 0:

                db_result = [
                    F3_Manifestation_Product_Type.objects.create(name=title),
                    True
                ]

        else:

            # TODO : Check how often this is the case
            print("Entity found without a uniquely identifying attribute")

        if db_result is not None:

            entity = db_result[0]

            if db_result[1] is True:

                cls.counter_f3_manifestation_created += 1
                print(f"created entity: type: {entity.__class__.__name__}, name: {entity.name}, pk: {entity.pk}")

                if title is None and entity.name == "":

                    title = f"unnamed f3, number {cls.counter_f3_manifestation_parsed}"

            else:

                print("entity already exists")

            if (
                entity.name == ""
                or (
                    entity.name.startswith("unnamed")
                    and title is not None
                    and not title.startswith("unnamed")
                )
            ):

                entity.name = title

            elif title is not None and title != entity.name:

                # TODO : Check how often this is the case
                print("Inconsistent data or mapping")

            if entity.bibl_id == "":

                entity.bibl_id = bibl_id

            elif bibl_id is not None and bibl_id != entity.bibl_id:

                raise Exception("Inconsistent data or mapping")

            # TODO __sresch__ : Add consistency check for these fields
            entity.series = series
            entity.edition = edition
            entity.start_date_written = date
            entity.note = note
            entity.ref_target = ref_target
            entity.ref_accessed = ref_accessed
            entity.text_language = text_language
            entity.save()

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

    @classmethod
    def parse_f9_place(cls, xml_elem):

        cls.counter_f9_place_parsed += 1

        db_result = F9_Place.objects.get_or_create(name=xml_elem.text)

        # TODO check xml_elem.text for empty texts

        if db_result[1]:

            entity = db_result[0]
            cls.counter_f9_place_created += 1
            print(f"created entity: type: {entity.__class__.__name__}, name: {entity.name}, pk: {entity.pk}")

        else:

            print("entity already exists")


    @classmethod
    def parse_f10_person(cls, xml_elem):

        cls.counter_f10_person_parsed += 1

        forename = None

        surname = None

        for xml_elem_child in xml_elem.getchildren():

            if xml_elem_child.tag.endswith("forename"):

                forename = xml_elem_child.text

            elif xml_elem_child.tag.endswith("surname"):

                surname = xml_elem_child.text

        kwargs = {}

        if forename is None and surname is None:

            kwargs["name"] = xml_elem.text

        else:

            # TODO
            if forename is None:
                forename = ""

            if surname is None:
                surname = ""

            kwargs["forename"] = forename
            kwargs["surname"] = surname
            kwargs["name"] = forename + ", " + surname

        if kwargs["name"] is not None:

            db_result = F10_Person.objects.get_or_create(**kwargs)

            if db_result[1] is True:

                entity = db_result[0]
                cls.counter_f10_person_created += 1
                print(f"created entity: type: {entity.__class__.__name__}, name: {entity.name}, pk: {entity.pk}")

            else:

                print("entity already exists")


    @classmethod
    def parse_f17_aggregation_work(cls, xml_elem):

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


    @classmethod
    def parse_f20_performance_work(cls, xml_elem):

        cls.counter_f20_performance_work_parsed += 1

        def create_entity(xml_elem):

            note = None
            category = None
            start_date_written = None

            for context_node_child in xml_elem:

                xml_elem_child = context_node_child.xml_elem

                if xml_elem_child.tag.endswith("note"):

                    note = xml_elem_child.text

                    for context_node_child_child in context_node_child.context_node_children_list:

                        xml_elem_child_child = context_node_child_child.xml_elem

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


        def create_triples(entity_f20_performance_work, xml_elem):

            for context_node_child in xml_elem.context_node_children_list:

                xml_elem_child = context_node_child.xml_elem

                if xml_elem_child.tag.endswith("persName"):

                    entity_f10_person = context_node_child.apis_object_main

                    prop = None

                    if xml_elem_child.attrib.get("role") == "director":

                        prop = Property.objects.get(name="is director of")

                    elif xml_elem_child.attrib.get("role") == "translator":

                        prop = Property.objects.get(name="is translator of")

                    else:

                        print(
                            f"Found relation to person but without role:"
                            f" f20: {entity_f20_performance_work},"
                            f" f10: {entity_f10_person},"
                        )

                    if prop is not None:

                        triple = TempTriple.objects.get_or_create(
                            subj=entity_f10_person,
                            obj=entity_f20_performance_work,
                            prop=prop,
                        )[0]

                elif (
                    xml_elem_child.tag.endswith("rs")
                    and xml_elem_child.attrib.get("type") == "institution"
                ):

                    entity_e40_legal_body = context_node_child.apis_object_main

                    triple = TempTriple.objects.get_or_create(
                        subj=entity_f20_performance_work,
                        obj=entity_e40_legal_body,
                        prop=Property.objects.get(name="has been performed at"),
                    )[0]

        entity_f20_performance_work = create_entity(xml_elem)


    @classmethod
    def parse_triple_f3_manifestation_to_e40_legal_body(cls, context_node_of_manifestatation):

        triple = None

        entity_f3_manifestation = context_node_of_manifestatation.apis_object_main

        if entity_f3_manifestation is not None:

            for context_node_child in context_node_of_manifestatation.context_node_children_list:

                e40_legal_body_entity = context_node_child.apis_object_main

                if (
                    context_node_child.apis_object_main is not None
                    and type(e40_legal_body_entity) is E40_Legal_Body
                ):

                    prop = None

                    if context_node_child.xml_elem.tag.endswith("publisher"):

                        prop = Property.objects.get(name="is publisher of")

                    elif context_node_child.xml_elem.tag.endswith("institution"):

                        if context_node_child.xml_elem.attrib.get("role") == "editor":

                            prop = Property.objects.get(name="is editor of")

                        else:

                            print(f"Found no specifying role of institution")

                    elif (
                        context_node_child.xml_elem.tag.endswith("orgName")
                        and context_node_child.xml_elem.attrib.get("role") == "editor"
                    ):

                        prop = Property.objects.get(name="is editor of")

                    else:

                        print(
                            f"Found e40 child node of f3 without a valid relation pattern. "
                            f"f3: {context_node_of_manifestatation.apis_object_main} "
                            f"e40: {context_node_child.apis_object_main}"
                        )

                    if prop is not None:

                        triple = TempTriple.objects.get_or_create(
                            subj=e40_legal_body_entity,
                            obj=entity_f3_manifestation,
                            prop=prop
                        )[0]

        return triple


    @classmethod
    def parse_triple_f3_manifestation_host_f3_manifestation(cls, context_node_of_manifestatation):

        triple = None

        entity_f3_manifestation_hosted = context_node_of_manifestatation.apis_object_main

        if entity_f3_manifestation_hosted is not None:

            for context_node_child in context_node_of_manifestatation.context_node_children_list:

                if (
                    context_node_child.xml_elem.tag.endswith("relatedItem")
                    and context_node_child.xml_elem.attrib.get("type") == "host"
                ):

                    for context_node_child_child in context_node_child.context_node_children_list:

                        entity_f3_manifestation_host = context_node_child_child.apis_object_main

                        if (
                            context_node_child_child.xml_elem.tag.endswith("bibl")
                            and entity_f3_manifestation_host is not None
                            and type(entity_f3_manifestation_host) is F3_Manifestation_Product_Type
                        ):
                            triple = TempTriple.objects.create(
                                subj=entity_f3_manifestation_hosted,
                                obj=entity_f3_manifestation_host,
                                prop=Property.objects.get(name="host")
                            )

        return triple

    @classmethod
    def parse_triple_f3_manifestation_published_f9_place(cls, xml_elem):

        triple = None

        entity_f3_manifestation = xml_elem.apis_object_main

        if entity_f3_manifestation is not None:

            for context_node_child in xml_elem.context_node_children_list:

                f9_place = context_node_child.apis_object_main

                if (
                    context_node_child.xml_elem.tag.endswith("pubPlace")
                    and type(f9_place) is F9_Place
                ):

                    triple = TempTriple.objects.get_or_create(
                        subj=entity_f3_manifestation,
                        obj=f9_place,
                        prop=Property.objects.get(name="was published in")
                    )[0]

        return triple

    @classmethod
    def parse_triple_f3_manifestation_f10_person(cls, xml_elem):

        triple = None

        entity_f3_manifestation = xml_elem.apis_object_main

        if entity_f3_manifestation is not None:

            for context_node_child in xml_elem.context_node_children_list:

                entity_f10_person = context_node_child.apis_object_main

                if (
                    context_node_child.xml_elem.tag.endswith("persName")
                    and type(entity_f10_person) is F10_Person
                ):

                    role = context_node_child.xml_elem.attrib.get("role")

                    prop = None

                    if role == "author":

                        prop = Property.objects.get(name="is author of")

                    elif role == "translator":

                        prop = Property.objects.get(name="is translator of")

                    elif role == "editor":

                        prop = Property.objects.get(name="is editor of")

                    if prop is not None:

                        triple = TempTriple.objects.get_or_create(
                            subj=entity_f10_person,
                            obj=entity_f3_manifestation,
                            prop=prop
                        )[0]

                    else:

                        print(f"Found person with no role attached. Can not create relationship with unknown property.")

        return triple

    @classmethod
    def parse_triple_f1_to_f3(cls, xml_elem):

        triple = None

        f1_or_f17 = None

        for context_node_child in xml_elem.context_node_children_list:

            if (
                context_node_child.xml_elem.tag.endswith("bibl")
                and "ana" in context_node_child.xml_elem.attrib
            ):

                if f1_or_f17 is not None:

                    print("found multiple assignments!")

                f1_or_f17 = context_node_child.apis_object_main

            elif (
                context_node_child.xml_elem.tag.endswith("div")
                and (
                    context_node_child.xml_elem.attrib.get("type") == "frbroo:manifestations"
                    or context_node_child.xml_elem.attrib.get("type") == "frbroo:manifestation"
                )
            ):

                for c in context_node_child.context_node_children_list:

                    if c.apis_object_main.__class__ is F3_Manifestation_Product_Type:

                        f3 = c.apis_object_main

                        triple = TempTriple.objects.get_or_create(
                            subj=f1_or_f17,
                            obj=f3,
                            prop=Property.objects.get(name="is expressed in")
                        )[0]


            elif (
                context_node_child.xml_elem.tag.endswith("div")
                and context_node_child.xml_elem.attrib.get("type") == "contained"
            ):


                for bibl in context_node_child.context_node_children_list[0].context_node_children_list:

                    for c in bibl.context_node_children_list:

                        if c.apis_object_main.__class__ == F1_Work:

                            f1 = c.apis_object_main

                            triple = TempTriple.objects.get_or_create(
                                subj=f1_or_f17,
                                obj=f1,
                                prop=Property.objects.get(name="contains")
                            )[0]

        return triple


    @classmethod
    def parse_triple_f17_to_f1(cls, xml_elem):

        triple = None

        f17 = None

        for context_node_child in xml_elem.context_node_children_list:

            if context_node_child.apis_object_main.__class__ == F17_Aggregation_Work:

                f17 = context_node_child.apis_object_main

            elif (
                context_node_child.xml_elem.tag.endswith("div")
                and context_node_child.xml_elem.attrib.get("type") == "contained"
            ):

                for potential_bibl in context_node_child.context_node_children_list[0].context_node_children_list:

                    for c in potential_bibl.context_node_children_list:

                        if c.apis_object_main.__class__ == F1_Work:

                            f1 = c.apis_object_main

                            triple = TempTriple.objects.get_or_create(
                                subj=f17,
                                obj=f1,
                                prop=Property.objects.get(name="contains")
                            )[0]

        return triple


    @classmethod
    def parse_triple_f1_to_f10(cls, xml_elem):

        triple = None

        f1 = xml_elem.apis_object_main
        f10 = None

        for c in xml_elem.context_node_children_list:

            if c.apis_object_main.__class__ == F10_Person:

                f10 = c.apis_object_main

                triple = TempTriple.objects.get_or_create(
                    subj=f10,
                    obj=f1,
                    prop=Property.objects.get(name="is author of")
                )[0]

        return triple

    # @classmethod
    # def parse_context_node_OLD(cls, xml_elem: ContextNode) -> ContextNode:
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


def reset_all():

    print("RootObject.objects.all().delete()")
    print(RootObject.objects.all().delete())

    print("construct_properties")
    construct_properties()


# TODO : Add relation entity -'read data from file'-> xml file
def crawl_xml_tree(current_xml_elem: XmlElement, parent_node: ContextNode, trees_manager: Type[TreesManager]):

    current_context_node = ContextNode(current_xml_elem, parent_node)

    trees_manager.parse_entity(current_context_node)

    for xml_elem_child in current_context_node.xml_elem:

        child_context_node = crawl_xml_tree(xml_elem_child, current_context_node, trees_manager)

        current_context_node.context_node_children_list.append(child_context_node)

    return current_context_node

    # for xml_elem_child in xml_elem.getchildren():
    #
    #     context_node_child = ContextNode(xml_elem=xml_elem_child, context_node_parent=xml_elem)
    #
    #     context_node_child = crawl_for_entity(context_node_child, trees_manager)
    #
    #     xml_elem.context_node_children_list.append(context_node_child)
    #
    # if (
    #     "{http://www.w3.org/XML/1998/namespace}id" in xml_elem.attrib
    #     and xml_elem.attrib['{http://www.w3.org/XML/1998/namespace}id'] == "bibl_000013"
    # ):
    #
    #     pass
    #
    # if (
    #     xml_elem.tag.endswith("div")
    #     and xml_elem.attrib.get('type') == "entry"
    # ):
    #
    #     pass
    #
    # xml_elem = trees_manager.enrich_context_node(xml_elem)

    # return xml_elem

# def crawl_all_csv_files():
#
#     # TODO
#     pass



# def relate_work_to_manifestations(node):
#
#     # TODO
#     pass


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
    
    trees_manager = TreesManager

    # xml_file_list = xml_file_list[657:]
    # xml_file_list = ["./manuelle-korrektur/korrigiert/bd1//001_Werke/011_EssayistischeTexteRedenundStatements/016_ZurösterreichischenPolitikundGesellschaft/001_EssaysBeiträge/014_EinVolkEinFest.xml"]

    for xml_file in xml_file_list:

        print(f"\nParsing {xml_file}")

        tree = ET.parse(xml_file)

        # TODO : Create xml file entity

        crawl_xml_tree(tree.getroot(), None, trees_manager)

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


def run(*args, **options):
    # TODO RDF : delete all model instances

    reset_all()

    xml_file_list = get_flat_file_list("./manuelle-korrektur/korrigiert/bd1/")
    xml_file_list.append("./manuelle-korrektur/korrigiert/entities/bibls.xml")
    xml_file_list.append("./manuelle-korrektur/korrigiert/entities/person_index.xml")
    xml_file_list.append("./manuelle-korrektur/korrigiert/entities/work_index.xml")

    crawl_xml_list(xml_file_list)
