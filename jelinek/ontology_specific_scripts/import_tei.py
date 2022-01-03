import xml.etree.ElementTree as ET
from apis_core.apis_entities.models import *
from apis_core.apis_relations.models import TempTriple, Property
from apis_core.apis_vocabularies.models import *
from django.core.management.base import BaseCommand, CommandError



class ContextNode():

    xml_node = None
    context_node_parent = None
    context_node_children_list = None
    apis_object_main = None
    apis_object_attrib_list = None
    apis_object_related_list = None

    def __init__(self, xml_node, context_node_parent):
        self.xml_node = xml_node
        self.context_node_parent = context_node_parent
        self.context_node_children_list = []
        self.apis_object_attrib_list = []
        self.apis_object_related_list = []

    def __str__(self):

        return self.xml_node.tag.replace("{http://www.tei-c.org/ns/1.0}", "") + "-" + str(self.xml_node.attrib) + "-" + self.xml_node.text

    def __repr__(self):

        return self.__str__()




class AbstractObjectCreator():

    @classmethod
    def enrich_context_node(cls, context_node_current):

        return None


# TODO : Check all object creations for redundant data creation
class ObjectCreator(AbstractObjectCreator):

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


    @classmethod
    def parse_e40_legal_body(cls, context_node_current):

        cls.counter_e40_legal_body_parsed += 1

        db_result = E40_Legal_Body.objects.get_or_create(name=context_node_current.xml_node.text)

        # TODO check context_node_current.xml_node.text for empty texts
        context_node_current.apis_object_main = db_result[0]

        if db_result[1] is True:

            cls.counter_e40_legal_body_created += 1

        return context_node_current



    @classmethod
    def parse_f1_work(cls, context_node_current):

        cls.counter_f1_work_parsed += 1

        title = None

        if (
            context_node_current.xml_node.tag.endswith("rs")
            and context_node_current.xml_node.attrib.get("type") == "work"
        ):

            title = context_node_current.xml_node.text

        else:

            for c in context_node_current.xml_node.getchildren():

                if c.tag.endswith("title"):

                    title = c.text

        if title is not None:

            db_result = F1_Work.objects.get_or_create(name=title)

            context_node_current.apis_object_main = db_result[0]

            if db_result[1] is True:

                cls.counter_f1_work_created += 1

        else:

            print("title is None")


        return context_node_current


    @classmethod
    def parse_f3_manifestation(cls, context_node_current):

        cls.counter_f3_manifestation_parsed += 1

        def create_entity(context_node_current):

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

            bibl_id = context_node_current.xml_node.attrib.get('{http://www.w3.org/XML/1998/namespace}id')

            for context_node_child in context_node_current.context_node_children_list:

                xml_node_child = context_node_child.xml_node

                if xml_node_child.tag.endswith("title"):

                    title = xml_node_child.text

                elif xml_node_child.tag.endswith("series"):

                    series = xml_node_child.text

                elif xml_node_child.tag.endswith("edition"):

                    edition = xml_node_child.text

                elif xml_node_child.tag.endswith("date"):

                    if xml_node_child.attrib.get("type") == "lastAccessed":

                        ref_accessed = xml_node_child.text

                    else:

                        date = xml_node_child.text

                elif xml_node_child.tag.endswith("note"):

                    for xml_node_child_child in xml_node_child.getchildren():

                        if xml_node_child_child.tag.endswith("title"):

                            title_in_note = xml_node_child_child.text

                    note = xml_node_child.text

                elif xml_node_child.tag.endswith("ref"):

                    ref_target = xml_node_child.attrib.get("target")

                elif xml_node_child.tag.endswith("textLang"):

                    text_language = xml_node_child.text

                # elif xml_node_child.attrib.get("target").startswith("#bibl"):
                elif xml_node_child.attrib.get("target") is not None:

                    if xml_node_child.attrib.get("target").startswith("#bibl"):

                        bibl_id = xml_node_child.attrib.get("target").replace("#", "")

                elif (
                    xml_node_child.tag.endswith("persName")
                    or xml_node_child.tag.endswith("pubPlace")
                    or xml_node_child.tag.endswith("publisher")
                    or xml_node_child.tag.endswith("orgName")
                ):

                    pass

                else:

                    print("unhandled node")
                    print(xml_node_child)

            if title is not None and title_in_note is not None:

                print(
                    f"conflicting data found in frbroo:manifestation between title: '{title}' "
                    f"and title_is_note: '{title_in_note}'"
                )
                return None

            elif title is None and title_in_note is not None:

                title = title_in_note

            if title is None and bibl_id is not None:

                db_result = F3_Manifestation_Product_Type.objects.get_or_create(
                    bibl_id=bibl_id,
                )

                entity_f3_manifestation = db_result[0]

                if title is None and entity_f3_manifestation.name.startswith("unnamed"):

                    title = f"unnamed f3, number {cls.counter_f3_manifestation_parsed}"

                else:

                    title = entity_f3_manifestation.name

                entity_f3_manifestation.name = title
                entity_f3_manifestation.series = series
                entity_f3_manifestation.edition = edition
                entity_f3_manifestation.start_date_written = date
                entity_f3_manifestation.note = note
                entity_f3_manifestation.ref_target = ref_target
                entity_f3_manifestation.ref_accessed = ref_accessed
                entity_f3_manifestation.text_language = text_language
                entity_f3_manifestation.bibl_id = bibl_id
                entity_f3_manifestation.save()

                if db_result[1] is True:

                    cls.counter_f3_manifestation_created += 1

                return entity_f3_manifestation


            else:

                if title is None:

                    title = f"unnamed f3, number {cls.counter_f3_manifestation_parsed}"

                db_result = F3_Manifestation_Product_Type.objects.get_or_create(
                    name=title,
                )

                entity_f3_manifestation = db_result[0]

                entity_f3_manifestation.bibl_id = bibl_id
                entity_f3_manifestation.series = series
                entity_f3_manifestation.edition = edition
                entity_f3_manifestation.start_date_written = date
                entity_f3_manifestation.note = note
                entity_f3_manifestation.ref_target = ref_target
                entity_f3_manifestation.ref_accessed = ref_accessed
                entity_f3_manifestation.text_language = text_language
                entity_f3_manifestation.save()

                if db_result[1] is True:

                    cls.counter_f3_manifestation_created += 1

                return entity_f3_manifestation


        def create_triples(entity_f3_manifestation, context_node_current):

            str_e55_type = None
            str_e55_subtype = None
            entity_e55_type = None
            entity_e55_subtype = None

            for attrib_key, attrib_value in context_node_current.xml_node.attrib.items():

                if attrib_key == "type":

                    cls.counter_e55type_parsed += 1

                    if str_e55_type is None:

                        str_e55_type = attrib_value

                        db_result = E55_Type.objects.get_or_create(name=str_e55_type)

                        entity_e55_type = db_result[0]

                        if db_result[1] is True:

                            cls.counter_e55type_created += 1

                    else:

                        print(f"Conflict: found a type before")

                elif attrib_key == "subtype":

                    cls.counter_e55type_parsed += 1

                    if str_e55_subtype is None:

                        str_e55_subtype = attrib_value

                        db_result = E55_Type.objects.get_or_create(name=str_e55_subtype)

                        entity_e55_subtype = db_result[0]

                        if db_result[1] is True:

                            cls.counter_e55type_created += 1

                    else:

                        print(f"Conflict: found a subtype before")

            if entity_e55_type is not None and entity_e55_subtype is not None:

                triple = TempTriple.objects.get_or_create(
                    subj=entity_e55_subtype,
                    obj=entity_e55_type,
                    prop=Property.objects.get(name="p127 has broader term")
                )[0]

            elif entity_e55_type is None and entity_e55_subtype is not None:

                print(f"found subtype but no type: node:{entity_e55_subtype}")

            if entity_e55_type is not None:

                context_node_current.apis_object_attrib_list.append(entity_e55_type)

            if entity_e55_subtype is not None:

                context_node_current.apis_object_attrib_list.append(entity_e55_subtype)

            if entity_f3_manifestation is not None and entity_e55_type is not None:

                triple = TempTriple.objects.get_or_create(
                    subj=entity_f3_manifestation,
                    obj=entity_e55_type,
                    prop=Property.objects.get(name="p2 has type")
                )[0]

        entity_f3_manifestation = create_entity(context_node_current)

        context_node_current.apis_object_main = entity_f3_manifestation

        create_triples(entity_f3_manifestation, context_node_current)

        # print(f"done with {context_node_current.apis_object_main.bibl_id}")

        return context_node_current


    @classmethod
    def parse_f9_place(cls, context_node_current):

        cls.counter_f9_place_parsed += 1

        db_result = F9_Place.objects.get_or_create(name=context_node_current.xml_node.text)

        # TODO check context_node_current.xml_node.text for empty texts
        context_node_current.apis_object_main = db_result[0]

        if db_result[1]:

            cls.counter_f9_place_created += 1

        return context_node_current


    @classmethod
    def parse_f10_person(cls, context_node_current):

        cls.counter_f10_person_parsed += 1

        forename = None

        surname = None

        for xml_node_child in context_node_current.xml_node.getchildren():

            if xml_node_child.tag.endswith("forename"):

                forename = xml_node_child.text

            elif xml_node_child.tag.endswith("surname"):

                surname = xml_node_child.text

        kwargs = {}

        if forename is None and surname is None:

            kwargs["name"] = context_node_current.xml_node.text

        else:

            # TODO
            if forename is None:
                forename = ""

            if surname is None:
                surname = ""

            kwargs["forename"] = forename
            kwargs["surname"] = surname
            kwargs["name"] = forename + ", " + surname

        db_result = F10_Person.objects.get_or_create(**kwargs)

        context_node_current.apis_object_main = db_result[0]

        if db_result[1] is True:

            cls.counter_f10_person_created += 1

        return context_node_current


    @classmethod
    def parse_f17_aggregation_work(cls, context_node_current):

        cls.counter_f17_aggregation_work_parsed += 1

        title = None

        for c in context_node_current.xml_node.getchildren():

            if c.tag.endswith("title"):

                if title is None:

                    title = c.text

                else:

                    print("Found multiple titles!")

        db_result = F17_Aggregation_Work.objects.get_or_create(name=title)

        context_node_current.apis_object_main = db_result[0]

        if db_result[1] is True:

            cls.counter_f17_aggregation_work_created += 1

        return context_node_current


    @classmethod
    def parse_f20_performance_work(cls, context_node_current):

        cls.counter_f20_performance_work_parsed += 1

        def create_entity(context_node_current):

            note = None
            category = None
            start_date_written = None

            for context_node_child in context_node_current.context_node_children_list:

                xml_node_child = context_node_child.xml_node

                if xml_node_child.tag.endswith("note"):

                    note = xml_node_child.text

                    for context_node_child_child in context_node_child.context_node_children_list:

                        xml_node_child_child = context_node_child_child.xml_node

                        if (
                            xml_node_child_child.tag.endswith("ref")
                            and xml_node_child_child.attrib.get("type") == "category"
                        ):

                            category = xml_node_child_child.text

                elif xml_node_child.tag.endswith("date"):

                    start_date_written = xml_node_child.text

            name = f"unnamed f20, number {cls.counter_f20_performance_work_parsed}"

            db_result = F20_Performance_Work.objects.get_or_create(name=name)

            entity_f20_performance_work = db_result[0]

            entity_f20_performance_work.note = note

            entity_f20_performance_work.category = category

            entity_f20_performance_work.start_date_written = start_date_written

            entity_f20_performance_work.save()

            if db_result[1] is True:

                cls.counter_f20_performance_work_created += 1

            return entity_f20_performance_work


        def create_triples(entity_f20_performance_work, context_node_current):

            for context_node_child in context_node_current.context_node_children_list:

                xml_node_child = context_node_child.xml_node

                if xml_node_child.tag.endswith("persName"):

                    entity_f10_person = context_node_child.apis_object_main

                    prop = None

                    if xml_node_child.attrib.get("role") == "director":

                        prop = Property.objects.get(name="is director of")

                    elif xml_node_child.attrib.get("role") == "translator":

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
                    xml_node_child.tag.endswith("rs")
                    and xml_node_child.attrib.get("type") == "institution"
                ):

                    entity_e40_legal_body = context_node_child.apis_object_main

                    triple = TempTriple.objects.get_or_create(
                        subj=entity_f20_performance_work,
                        obj=entity_e40_legal_body,
                        prop=Property.objects.get(name="has been performed at"),
                    )[0]

        entity_f20_performance_work = create_entity(context_node_current)

        context_node_current.apis_object_main = entity_f20_performance_work

        create_triples(entity_f20_performance_work, context_node_current)

        return context_node_current


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

                    if context_node_child.xml_node.tag.endswith("publisher"):

                        prop = Property.objects.get(name="is publisher of")

                    elif context_node_child.xml_node.tag.endswith("institution"):

                        if context_node_child.xml_node.attrib.get("role") == "editor":

                            prop = Property.objects.get(name="is editor of")

                        else:

                            print(f"Found no specifying role of institution")

                    elif (
                        context_node_child.xml_node.tag.endswith("orgName")
                        and context_node_child.xml_node.attrib.get("role") == "editor"
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
                    context_node_child.xml_node.tag.endswith("relatedItem")
                    and context_node_child.xml_node.attrib.get("type") == "host"
                ):

                    for context_node_child_child in context_node_child.context_node_children_list:

                        entity_f3_manifestation_host = context_node_child_child.apis_object_main

                        if (
                            context_node_child_child.xml_node.tag.endswith("bibl")
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
    def parse_triple_f3_manifestation_published_f9_place(cls, context_node_current):

        triple = None

        entity_f3_manifestation = context_node_current.apis_object_main

        if entity_f3_manifestation is not None:

            for context_node_child in context_node_current.context_node_children_list:

                f9_place = context_node_child.apis_object_main

                if (
                    context_node_child.xml_node.tag.endswith("pubPlace")
                    and type(f9_place) is F9_Place
                ):

                    triple = TempTriple.objects.get_or_create(
                        subj=entity_f3_manifestation,
                        obj=f9_place,
                        prop=Property.objects.get(name="was published in")
                    )[0]

        return triple

    @classmethod
    def parse_triple_f3_manifestation_f10_person(cls, context_node_current):

        triple = None

        entity_f3_manifestation = context_node_current.apis_object_main

        if entity_f3_manifestation is not None:

            for context_node_child in context_node_current.context_node_children_list:

                entity_f10_person = context_node_child.apis_object_main

                if (
                    context_node_child.xml_node.tag.endswith("persName")
                    and type(entity_f10_person) is F10_Person
                ):

                    role = context_node_child.xml_node.attrib.get("role")

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
    def parse_triple_f1_to_f3(cls, context_node_current):

        triple = None

        f1_or_f17 = None

        for context_node_child in context_node_current.context_node_children_list:

            if (
                context_node_child.xml_node.tag.endswith("bibl")
                and "ana" in context_node_child.xml_node.attrib
            ):

                if f1_or_f17 is not None:

                    print("found multiple assignments!")

                f1_or_f17 = context_node_child.apis_object_main

            elif (
                context_node_child.xml_node.tag.endswith("div")
                and (
                    context_node_child.xml_node.attrib.get("type") == "frbroo:manifestations"
                    or context_node_child.xml_node.attrib.get("type") == "frbroo:manifestation"
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
                context_node_child.xml_node.tag.endswith("div")
                and context_node_child.xml_node.attrib.get("type") == "contained"
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
    def parse_triple_f17_to_f1(cls, context_node_current):

        triple = None

        f17 = None

        for context_node_child in context_node_current.context_node_children_list:

            if context_node_child.apis_object_main.__class__ == F17_Aggregation_Work:

                f17 = context_node_child.apis_object_main

            elif (
                context_node_child.xml_node.tag.endswith("div")
                and context_node_child.xml_node.attrib.get("type") == "contained"
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
    def parse_triple_f1_to_f10(cls, context_node_current):

        triple = None

        f1 = context_node_current.apis_object_main
        f10 = None

        for c in context_node_current.context_node_children_list:

            if c.apis_object_main.__class__ == F10_Person:

                f10 = c.apis_object_main

                triple = TempTriple.objects.get_or_create(
                    subj=f10,
                    obj=f1,
                    prop=Property.objects.get(name="is author of")
                )[0]

        return triple

    @classmethod
    def enrich_context_node(cls, context_node_current: ContextNode) -> ContextNode:

        if (
            context_node_current.xml_node.tag.endswith("bibl")
            and context_node_current.xml_node.attrib.get("ana") == "frbroo:work"
        ):

            context_node_current = cls.parse_f1_work(context_node_current)

            cls.parse_triple_f1_to_f10(context_node_current)

        elif (
            context_node_current.xml_node.tag.endswith("bibl")
            and context_node_current.xml_node.attrib.get("ana") == "frbroo:aggregation_work"
        ):

            context_node_current = cls.parse_f17_aggregation_work(context_node_current)

        elif (
            context_node_current.xml_node.tag.endswith("rs")
            and context_node_current.xml_node.attrib.get("type") == "work"
        ):

            context_node_current = cls.parse_f1_work(context_node_current)

        elif (
            context_node_current.xml_node.tag.endswith("bibl")
            and context_node_current.xml_node.attrib.get("ana") == "frbroo:manifestation"
        ):

            context_node_current = cls.parse_f3_manifestation(context_node_current)

            triple_f3_manifestation_to_e40_legal_body = cls.parse_triple_f3_manifestation_to_e40_legal_body(context_node_current)

            triple_f3_manifestation_host_f3_manifestation = cls.parse_triple_f3_manifestation_host_f3_manifestation(context_node_current)

            triple_f3_manifestation_published_f9_place = cls.parse_triple_f3_manifestation_published_f9_place(context_node_current)

            triple_f3_manifestation_f10_person = cls.parse_triple_f3_manifestation_f10_person(context_node_current)

        elif (
            context_node_current.xml_node.tag.endswith("publisher")
            or context_node_current.xml_node.tag.endswith("institution")
            or (
                context_node_current.xml_node.tag.endswith("rs")
                and context_node_current.xml_node.attrib.get("type") == "institution"
            )
            or context_node_current.xml_node.tag.endswith("orgName")
        ):

            context_node_current = cls.parse_e40_legal_body(context_node_current)

        elif context_node_current.xml_node.tag.endswith("pubPlace"):

            context_node_current = cls.parse_f9_place(context_node_current)

        elif context_node_current.xml_node.tag.endswith("persName"):

            context_node_current = cls.parse_f10_person(context_node_current)

        elif (
            context_node_current.xml_node.tag.endswith("item")
            and context_node_current.xml_node.attrib.get("ana") == "staging"
        ):

            pass
            # TODO
            # context_node_current = cls.parse_f20_performance_work(context_node_current)

        elif (
            context_node_current.xml_node.tag.endswith("div")
            and context_node_current.xml_node.attrib.get('type') == "entry"
        ):

            cls.parse_triple_f1_to_f3(context_node_current)

            cls.parse_triple_f17_to_f1(context_node_current)


        return context_node_current


def crawl(context_node_current: ContextNode, object_creator: AbstractObjectCreator) -> ContextNode:

    for xml_node_child in context_node_current.xml_node.getchildren():

        context_node_child = ContextNode(xml_node=xml_node_child, context_node_parent=context_node_current)

        context_node_child = crawl(context_node_child, object_creator)

        context_node_current.context_node_children_list.append(context_node_child)


    if (
        "{http://www.w3.org/XML/1998/namespace}id" in context_node_current.xml_node.attrib
        and context_node_current.xml_node.attrib['{http://www.w3.org/XML/1998/namespace}id'] == "bibl_000013"
    ):

        pass

    if (
        context_node_current.xml_node.tag.endswith("div")
        and context_node_current.xml_node.attrib.get('type') == "entry"
    ):

        pass

    context_node_current = object_creator.enrich_context_node(context_node_current)

    return context_node_current


def crawl_all_csv_files():

    # TODO
    pass



def relate_work_to_manifestations(node):

    # TODO
    pass



def crawl_all_xml_folders():



    def get_files(folder):

        from os import listdir
        from os.path import isfile, join
        return [
            folder + "/" + f
            for f in listdir(folder) if isfile(join(folder, f)) if not f.endswith(".swp")
        ]

    # files_001_lyrik_001_buchpublikationen = get_files("../manuelle-korrektur/korrigiert/bd1/001_Werke/001_Lyrik/001_Buchpublikationen")
    # files_001_lyrik_frbr_works = get_files("../manuelle-korrektur/korrigiert/bd1/001_Werke/001_Lyrik/FRBR-Works")
    # files_002_romane = get_files("../manuelle-korrektur/korrigiert/bd1/001_Werke/002_Romane")
    # files_003_kurzprosa = get_files("../manuelle-korrektur/korrigiert/bd1/001_Werke/003_Kurzprosa")
    # files_004_theatertexte = get_files("../manuelle-korrektur/korrigiert/bd1/001_Werke/004_Theatertexte/FRBR-Works")


    all_files = \
        ["../manuelle-korrektur/korrigiert/bibls.xml"] \
        + get_files("../manuelle-korrektur/korrigiert/bd1/001_Werke/001_Lyrik/001_Buchpublikationen") \
        + get_files("../manuelle-korrektur/korrigiert/bd1/001_Werke/001_Lyrik/FRBR-Works") \
        + get_files("../manuelle-korrektur/korrigiert/bd1/001_Werke/002_Romane") \
        + get_files("../manuelle-korrektur/korrigiert/bd1/001_Werke/003_Kurzprosa") \
        + get_files("../manuelle-korrektur/korrigiert/bd1/001_Werke/004_Theatertexte/FRBR-Works")

    i = 1

    for i2, x in enumerate(all_files):
        i = i2
        if "003_ohne Titel" in x:
            print("i", i)
            break


    # RootObject.objects.all().delete()
    # from apis_ontology.models import construct_properties
    # construct_properties()


    # for i3, tei_xml_file in enumerate(all_files):
    for i3, tei_xml_file in enumerate(all_files[1:]):
    # for i3, tei_xml_file in enumerate([all_files[0]] + [all_files[i]]):
    # for i3, tei_xml_file in enumerate([all_files[0]]):
    # for i3, tei_xml_file in enumerate([all_files[i]]):

        tree = ET.parse(tei_xml_file)

        xml_node_root = tree.getroot()

        crawl(ContextNode(xml_node_root, None), ObjectCreator)

        print(f"ObjectCreator.counter_e40_legal_body_parsed{ObjectCreator.counter_e40_legal_body_parsed}")
        print(f"ObjectCreator.counter_e40_legal_body_created: {ObjectCreator.counter_e40_legal_body_created}")

        print(f"ObjectCreator.counter_e55type_parsed: {ObjectCreator.counter_e55type_parsed}")
        print(f"ObjectCreator.counter_e55type_created: {ObjectCreator.counter_e55type_created}")

        print(f"ObjectCreator.counter_f1_work_parsed: {ObjectCreator.counter_f1_work_parsed}")
        print(f"ObjectCreator.counter_f1_work_created: {ObjectCreator.counter_f1_work_created}")

        print(f"ObjectCreator.counter_f3_manifestation_parsed: {ObjectCreator.counter_f3_manifestation_parsed}")
        print(f"ObjectCreator.counter_f3_manifestation_created: {ObjectCreator.counter_f3_manifestation_created}")

        print(f"ObjectCreator.counter_f9_place_parsed: {ObjectCreator.counter_f9_place_parsed}")
        print(f"ObjectCreator.counter_f9_place_created: {ObjectCreator.counter_f9_place_created}")

        print(f"ObjectCreator.counter_f10_person_parsed: {ObjectCreator.counter_f10_person_parsed}")
        print(f"ObjectCreator.counter_f10_person_created: {ObjectCreator.counter_f10_person_created}")

        print(f"ObjectCreator.counter_f17_aggregation_work_parsed: {ObjectCreator.counter_f17_aggregation_work_parsed}")
        print(f"ObjectCreator.counter_f17_aggregation_work_created: {ObjectCreator.counter_f17_aggregation_work_created}")

        print(f"ObjectCreator.counter_f20_performance_work_parsed: {ObjectCreator.counter_f20_performance_work_parsed}")
        print(f"ObjectCreator.counter_f20_performance_work_created: {ObjectCreator.counter_f20_performance_work_created}")



def run(*args, **options):
    # TODO RDF : delete all model instances

    crawl_all_csv_files()

    crawl_all_xml_folders()
