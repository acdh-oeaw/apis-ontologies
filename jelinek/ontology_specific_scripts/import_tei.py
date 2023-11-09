from __future__ import annotations

import xml.etree.ElementTree
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element as XmlElement
from typing import Type, List

from apis_ontology.models import *
from apis_core.apis_relations.models import Triple, TempTriple, Property
from apis_core.utils import caching
from apis_core.apis_vocabularies.models import *
from django.core.management.base import BaseCommand, CommandError
from os import listdir
from os.path import isfile, isdir, join
from .generate_short_entry import run as generate_short
from .generate_genre import run as generate_genre
from .generate_xml_dumps import run as generate_xml_dumps
from .generate_publisher_relations_for_journals import run as generate_publisher_relations_for_journals
from .import_index_in_chapter import run as import_index_in_chapter
from .populate_indexes import run as populate_indexes
from .assign_default_manifestation import run as assign_default_manifestation
import os


# The main logic of parsing xml nodes and correlating them with apis models probably would have
# been better with xpath expressions instead of python if-else checks. I thought too late of this.

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

def remove_whitespace(var_str):
    if var_str is None:
        return ""
    white_space_beginning_regex = re.compile(r"^\s+", re.MULTILINE)
    multiple_white_spaces_in_middle_regex = re.compile(r"(\s\s+|\n)", re.MULTILINE)
    return multiple_white_spaces_in_middle_regex.sub(" ", white_space_beginning_regex.sub("", var_str)).strip()

def remove_xml_tags(var_str):
    regex = re.compile(r"<.*?>", re.MULTILINE)
    return regex.sub("", var_str).strip()

def remove_outer_xml_tags(var_str):
    regex = re.compile(r"^<.*?>", re.MULTILINE)
    first = regex.sub("", var_str).strip()
    regex = re.compile(r"</ns0:title>$")
    last = regex.sub("", first).strip()
    regex = re.compile(r"</ns0:edition>$")
    last = regex.sub("", last).strip()
    regex = re.compile(r"</ns0:head>$")
    last = regex.sub("", last).strip()
    regex = re.compile(r"</ns0:orgName>$")
    last = regex.sub("", last).strip()
    regex = re.compile(r"</ns0:ref>$")
    last = regex.sub("", last).strip()
    regex = re.compile(r"</ns0:figDesc>$")
    last = regex.sub("", last).strip()
    return last

def get_uppermost_parent(path_node):
    parent = path_node.path_node_parent
    while parent.path_node_parent is not None:
        parent = parent.path_node_parent
    return parent



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

                attr_dict = {
                    "some_key": None
                }

                if xml_elem.tag.endswith("some_key"): # some condition

                    attr_dict["some_key"] = "some value"

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["some_key"] is not None: # foo is unique identifier

                        db_result = F1_Work.objects.get_or_create(some_key=attr_dict["some_key"])
                        db_result = None

                    elif attr_dict["some_key_2"] is not None: # bar is identifish

                        # if this entity is mostly created using these fields:
                        db_result = F1_Work.objects.get_or_create(some_key_2=attr_dict["some_key_2"])

                        # if this entity is mostly created using other fields, and thus the field 'bar' could lead to multiple results
                        db_hit = F1_Work.objects.filter(some_key_2=attr_dict["some_key_2"])

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
                            pass

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)


        def parse_e40_legal_body(path_node: PathNode):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                attr_dict = {
                    "name": None,
                    "institution_id": None,
                    "institution_type": None,
                    "date": None
                }

                if (
                    (
                        xml_elem.tag.endswith("publisher")
                        or xml_elem.tag.endswith("institution")
                        or (
                            xml_elem.tag.endswith("rs")
                            and (xml_elem.attrib.get("type") in ["institution","theater","festival","place","broadcaster","ensemble","publisher"])
                        )
                        #or xml_elem.tag.endswith("orgName")
                    )
                    and not (
                        xml_elem.attrib.get("ref") is not None
                        and xml_elem.attrib.get("ref").startswith("bibls:")
                    )
                    #and is_valid_text(xml_elem.text)
                ):
                    for child in xml_elem:
                        if (child.tag.endswith("orgName") or child.tag.endswith("title")) and not child.attrib.get("type") == "alternative":
                            attr_dict["name"] = remove_whitespace(remove_xml_tags(ET.tostring(child, encoding="unicode").strip(child.tail)))
                        elif child.tag.endswith("place") and child.attrib.get("type") == "venue":
                            attr_dict["name"] = child.text
                        elif child.tag.endswith("date"):
                            attr_dict["start_date_written"] = child.text.replace("gegr.", "")

                    if attr_dict["name"] is None and is_valid_text(xml_elem.text):
                        attr_dict["name"] = remove_whitespace(xml_elem.text)

                    if xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None:
                        attr_dict["institution_id"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
                    elif xml_elem.attrib.get("ref") is not None and not "place:place_" in xml_elem.attrib.get("ref"):
                        attr_dict["institution_id"] = xml_elem.attrib.get("ref").replace("insti:", "").replace("venues:","")

                    if  xml_elem.tag.endswith("publisher") or xml_elem.attrib.get("type") in ["publisher"]:
                        attr_dict["institution_type"] = "publisher"

                elif (
                    xml_elem.tag.endswith("orgName")
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                ):
                    attr_dict["name"] = remove_whitespace(xml_elem.text)

                if len([v for v in attr_dict.values() if v is not None]) > 0:
                    if attr_dict["name"] is not None:
                        attr_dict["name"] = attr_dict["name"].replace("&amp;", "&")

                    return attr_dict

                else:

                    return None

            def sub_main(path_node: PathNode):

                entities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    if attr_dict["institution_id"] is not None:

                        db_result = E40_Legal_Body.objects.get_or_create(institution_id=attr_dict["institution_id"])

                    elif attr_dict["name"] is not None:

                        # db_result = F21_Recording_Work.objects.get_or_create(name=attr_dict["name"])
                        db_hit = E40_Legal_Body.objects.filter(name=attr_dict["name"])
                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            db_result = [
                                E40_Legal_Body.objects.create(name=attr_dict["name"]),
                                True
                            ]

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    entities_list.append(handle_after_creation(db_result, attr_dict))

                
                return entities_list

            return sub_main(path_node)


        def parse_e55_type(path_node: PathNode):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                attr_dict = {
                    "name_type": None,
                    "name_subtype": None,
                    "name_mediatype": None,
                }

                if (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("type") is not None
                    and xml_elem.attrib.get("type") != "content"
                ):
                    attr_dict["name_type"] = xml_elem.attrib.get("type")
                    attr_dict["name_subtype"] = xml_elem.attrib.get("subtype")
                    attr_dict["name_mediatype"] = xml_elem.attrib.get("mediatype")

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

            def sub_main(path_node: PathNode):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    if attr_dict["name_type"] is not None:

                        db_result = E55_Type.objects.get_or_create(name=attr_dict["name_type"])

                        enities_list.append(handle_after_creation(db_result, {}))

                    if attr_dict["name_subtype"] is not None:

                        db_result = E55_Type.objects.get_or_create(name=attr_dict["name_subtype"])

                        enities_list.append(handle_after_creation(db_result, {}))

                    if attr_dict["name_mediatype"] is not None:

                        db_result = E55_Type.objects.get_or_create(name=attr_dict["name_mediatype"])

                        enities_list.append(handle_after_creation(db_result, {}))

                return enities_list

            return sub_main(path_node)


        def parse_f1_work(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem
                
                attr_dict = {
                    "idno": None,
                    "name": None,
                    "gnd_url": None,
                    "index_in_chapter": None,
                    "index_desc": None,
                    "untertitel": None,
                    "note": None,
                }

                if (
                    xml_elem.tag.endswith("bibl")
                    and (xml_elem.attrib.get("ana") == "frbroo:work" or xml_elem.attrib.get("ana") == "frbroo:aggregation_work")
                    and (trees_manager.helper_dict["current_type"] == "work" or trees_manager.helper_dict["current_type"] == "seklit")
                    and not xml_elem.attrib.get("type") in ["audio_vis_work", "tv_work", "audio_work", "movie"]
                ):

                    if (xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None and xml_elem.attrib.get("type") == "seklit"):
                        attr_dict["idno"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
                    if path_node.path_node_parent != None:
                        parent = path_node.path_node_parent
                        while parent.path_node_parent != None:
                            parent = parent.path_node_parent
                        if len(parent.entities_list) > 0:
                            xml = [f for f in parent.entities_list if "xml" in f.name]
                            if len(xml) > 0:
                                xml_file_name = xml[0].name.replace(".xml", "")
                                if len(xml_file_name) > 0:
                                    if xml_file_name.split("_")[0] == "interview":
                                        attr_dict["index_in_chapter"] = int(xml_file_name.split("_")[1])
                                    elif xml_file_name.split("_")[0].isnumeric():
                                        attr_dict["index_in_chapter"] = int(xml_file_name.split("_")[0])

                    for xml_elem_child in xml_elem:

                        # TODO : Check if there are titles without 'type="main"'
                        if (
                            xml_elem_child.tag.endswith("title")
                            and (xml_elem_child.attrib.get("type") == "main" or (xml_elem_child.attrib.get("type") == None and attr_dict["name"] == ""))
                        ):

                            attr_dict["name"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "sub"
                        ):

                            if attr_dict["untertitel"] is not None:
                                attr_dict["untertitel"] = attr_dict["untertitel"] + "<br>" + remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))
                            else:
                                attr_dict["untertitel"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "index_desc"
                        ):

                            attr_dict["index_desc"] = remove_whitespace(xml_elem_child.text)

                        if (
                            xml_elem_child.tag.endswith("idno")
                            and xml_elem_child.attrib["type"] == "JWV"
                        ):

                            attr_dict["idno"] = xml_elem_child.text

                elif (
                    xml_elem.tag.endswith("item")
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id").startswith("work")
                ):

                    attr_dict["idno"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "index"
                            and is_valid_text(xml_elem_child.text)
                        ):

                            attr_dict["name"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif (
                            xml_elem_child.tag.endswith("ref")
                            and xml_elem_child.attrib.get("type") == "gnd"
                            and xml_elem_child.attrib.get("target") is not None
                        ):

                            attr_dict["gnd_url"] = xml_elem_child.attrib.get("target")

                        elif (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "index_desc"
                        ):

                            attr_dict["index_desc"] = remove_whitespace(xml_elem_child.text)
                elif (
                    (xml_elem.tag.endswith("item")
                    and xml_elem.attrib.get("ana") is not None
                    and xml_elem.attrib.get("ana").startswith("seklit"))
                    or (xml_elem.tag.endswith("div") and xml_elem.attrib.get("type") == "head_section")
                ):

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("ptr")
                            and xml_elem_child.attrib.get("type") == "seklit"
                        ):

                            attr_dict["idno"] = xml_elem_child.attrib.get("target").replace("seklit:", "")
                        
                        elif (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "index"
                            and is_valid_text(xml_elem_child.text)
                        ):

                            attr_dict["name"] = remove_whitespace(xml_elem_child.text)

                        elif (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "index_desc"
                        ):

                            attr_dict["index_desc"] = remove_whitespace(xml_elem_child.text)

                        elif (
                            xml_elem_child.tag.endswith("ref")
                            and xml_elem_child.attrib.get("type") == "gnd"
                            and xml_elem_child.attrib.get("target") is not None
                        ):

                            attr_dict["gnd_url"] = xml_elem_child.attrib.get("target")

                elif (
                    xml_elem.tag.endswith("rs")
                    and xml_elem.attrib.get("type") == "work"
                    and xml_elem.attrib.get("ref") is not None
                    and xml_elem.attrib.get("ref").startswith("works:")
                    and trees_manager.helper_dict["current_type"] != "broadcast_index"
                    
                ):

                    attr_dict["idno"] = xml_elem.attrib.get("ref").replace("works:", "")

                elif (
                    xml_elem.tag.endswith("rs")
                    and xml_elem.attrib.get("type") == "seklit"
                    and xml_elem.attrib.get("ref") is not None
                    and xml_elem.attrib.get("ref").startswith("seklit:")
                    and trees_manager.helper_dict["current_type"] != "broadcast_index"
                    
                ):

                    attr_dict["idno"] = xml_elem.attrib.get("ref").replace("seklit:", "")

                    # TODO : 'ref type="category"'
                    # for xml_elem_child in xml_elem:

                    #     if xml_elem_child.tag.endswith("title"):

                    #         attr_dict["name"] = remove_whitespace(xml_elem_child.text)

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None


            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None
                    if attr_dict["name"] is not None:
                        attr_dict["name"] = attr_dict["name"][:255]

                    if attr_dict["idno"] is not None:
                        db_hit = F1_Work.objects.filter(idno=attr_dict["idno"])

                        if len(db_hit) <= 1:
                            
                            db_result = F1_Work.objects.get_or_create(
                                idno=attr_dict["idno"]
                            )
                        else:
                            print("Multiple entries using the same idno found - that shouldn't happen")
                            db_result = [db_hit[0], False]

                    elif attr_dict["name"] is not None:

                        if (trees_manager.helper_dict["current_type"] == "seklit"):
                            db_result = [
                                F1_Work.objects.create(name=attr_dict["name"]),
                                True
                            ]
                            
                        else:

                            # db_result = F1_Work.objects.get_or_create(name=attr_dict["name"])
                            db_hit = F1_Work.objects.filter(
                                name=attr_dict["name"],
                                self_contenttype=caching.get_contenttype_of_class(F1_Work)
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

        def parse_honour(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem
                
                attr_dict = {
                    "honour_id": None,
                    "name": None,
                    "index_in_chapter": None,
                    "start_date_written": None,
                    "date_hidden": None
                }

                if (
                    xml_elem.tag.endswith("event")
                    and (xml_elem.attrib.get("type") == "honour" or xml_elem.attrib.get("type") == "awards_ceremony")
                ):

                    if (xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None):
                        attr_dict["honour_id"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
                        if len(attr_dict["honour_id"].split("_")) > 1 and attr_dict["honour_id"].split("_")[1].isnumeric():
                            attr_dict["index_in_chapter"] = int(attr_dict["honour_id"].split("_")[1])

                    for xml_elem_child in xml_elem:

                        # TODO : Check if there are titles without 'type="main"'
                        if (
                            xml_elem_child.tag.endswith("head")
                        ):

                            attr_dict["name"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        if (
                            xml_elem_child.tag.endswith("date")
                        ):

                            attr_dict["start_date_written"] = xml_elem_child.text
                            if (xml_elem_child.attrib.get("rendition", "") in ["hidden", "#hidden"]):
                                attr_dict["date_hidden"] = True

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None


            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None
                    if attr_dict["name"] is not None:
                        attr_dict["name"] = attr_dict["name"][:255]

                    if attr_dict["honour_id"] is not None:
                        db_hit = Honour.objects.filter(honour_id=attr_dict["honour_id"])

                        if len(db_hit) <= 1:
                            
                            db_result = Honour.objects.get_or_create(
                                honour_id=attr_dict["honour_id"],
                                self_contenttype=caching.get_contenttype_of_class(Honour)
                            )
                        else:
                            print("Multiple entries using the same honour_id found - that shouldn't happen")
                            db_result = [db_hit[0], False]

                    elif attr_dict["name"] is not None:

                        # db_result = Honour.objects.get_or_create(name=attr_dict["name"])
                        db_hit = Honour.objects.filter(
                            name=attr_dict["name"],
                            self_contenttype=caching.get_contenttype_of_class(Honour)
                            
                        )
                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            db_result = [
                                Honour.objects.create(name=attr_dict["name"]),
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

                attr_dict = {
                    "bibl_id": None,
                    "koha_id": None,
                    "name": None,
                    "title_in_note": None,
                    "title_hidden": None,
                    "date_hidden": None,
                    "series": None,
                    "edition": None,
                    "page": None,
                    "issue": None,
                    "volume": None,
                    "start_date_written": None,
                    "note": None,
                    "ref_target": None,
                    "ref_accessed": None,
                    "text_language": None,
                    "untertitel": None,
                    "scope_style": None,
                }

                if (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ana") == "frbroo:manifestation"
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is None
                ):

                    if xml_elem.attrib.get("n") is not None:
                        attr_dict["edition"] = xml_elem.attrib.get("n")

                    for xml_elem_child in xml_elem:

                        if xml_elem_child.tag is None:
                            continue
                        
                        if (
                            xml_elem_child.tag.endswith("ptr")
                            and xml_elem_child.attrib.get("type") == "bibl"
                            and xml_elem_child.attrib.get("target") is not None
                            and xml_elem_child.attrib.get("target").startswith("bibls:")
                        ):

                            attr_dict["bibl_id"] = xml_elem_child.attrib.get("target").replace("bibls:", "")

                        elif (
                             xml_elem_child.tag.endswith("title")
                            and is_valid_text(xml_elem_child.text)
                        ):
                            if (xml_elem_child.attrib.get("type") == "sub"):
                                attr_dict["untertitel"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))
                            else:
                                attr_dict["name"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))
                                if (xml_elem_child.attrib.get("rendition", "") in ["hidden", "#hidden"]):
                                    attr_dict["title_hidden"] = True

                        elif (
                             xml_elem_child.tag.endswith("rs")
                            and (xml_elem_child.attrib.get("type") == "work"
                            or xml_elem_child.attrib.get("type") == "seklit")
                        ):
                            for xml_elem_child_child in xml_elem_child:
                                if (
                                    xml_elem_child_child.tag is not None
                                    and xml_elem_child_child.tag.endswith("title")
                                    and is_valid_text(xml_elem_child_child.text)
                                ):
                                    if (xml_elem_child_child.attrib.get("type") == "sub"):
                                        attr_dict["untertitel"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child_child, encoding="unicode").strip(xml_elem_child_child.tail)))
                                    else:
                                        attr_dict["name"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))
                                        attr_dict["name"] = attr_dict["name"].replace("</ns0:title> </ns0:rs>", "")
                                    if (xml_elem_child.attrib.get("rendition", "") in ["hidden", "#hidden"]):
                                        attr_dict["title_hidden"] = True

                        elif (
                             xml_elem_child.tag.endswith("note")
                        ):
                            attr_dict["note"] = ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)
                        elif xml_elem_child.tag.endswith("edition"):

                            attr_dict["edition"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif (
                            xml_elem_child.tag.endswith("biblScope")
                            and xml_elem_child.attrib.get("unit") is not None
                        ):

                            attr_dict[xml_elem_child.attrib.get("unit")] = xml_elem_child.text

                            if (xml_elem_child.attrib.get("style") is not None):

                                attr_dict["scope_style"] = xml_elem_child.attrib.get("style")

                        elif xml_elem_child.tag.endswith("date"):

                            if xml_elem_child.attrib.get("type") == "lastAccessed":

                                attr_dict["ref_accessed"] = xml_elem_child.text

                            elif xml_elem_child.attrib.get("to") is not None:

                                attr_dict["start_date_written"] = attr_dict["start_date_written"] + " - " + xml_elem_child.text
                            
                            else:

                                attr_dict["start_date_written"] = xml_elem_child.text
                                if (xml_elem_child.attrib.get("rendition", "") in ["hidden", "#hidden"]):
                                        attr_dict["date_hidden"] = True

                        elif xml_elem_child.tag.endswith("ref"):

                            attr_dict["ref_target"] = xml_elem_child.attrib.get("target")
                            attr_dict["series"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif xml_elem_child.tag.endswith("textLang"):

                            attr_dict["text_language"] = xml_elem_child.text

                        elif xml_elem_child.tag.endswith("series"):

                            attr_dict["series"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif xml_elem_child.tag.endswith("edition"):

                            attr_dict["edition"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif (
                            xml_elem_child.tag is not None
                            and xml_elem_child.tag.endswith("note")
                        ):
                            attr_dict["note"] = ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)

                    if attr_dict["name"] is None:
                        for path_node_sibling in path_node.path_node_parent.path_node_parent.path_node_children_list:
                            if (
                            path_node_sibling.xml_elem.tag is not None
                            and path_node_sibling.xml_elem.tag.endswith("title")
                            and is_valid_text(path_node_sibling.xml_elem.text)
                            ):
                                if (path_node_sibling.xml_elem.attrib.get("type") == "sub"):
                                    attr_dict["untertitel"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(path_node_sibling, encoding="unicode").strip(path_node_sibling.tail)))
                                else:
                                    attr_dict["name"] = remove_whitespace(remove_xml_tags(ET.tostring(path_node_sibling.xml_elem, encoding="unicode").strip(path_node_sibling.xml_elem.tail)))


                elif (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ana") == "frbroo:manifestation"
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                ):

                    attr_dict["bibl_id"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
                    if xml_elem.attrib.get("n") is not None:
                        attr_dict["edition"] = xml_elem.attrib.get("n")

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag is not None
                            and xml_elem_child.tag.endswith("title")
                        ):
                            if (xml_elem_child.attrib.get("type") == "sub"):
                                attr_dict["untertitel"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))
                            else:
                                attr_dict["name"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))
                                if (xml_elem_child.attrib.get("rendition", "") in ["hidden", "#hidden"]):
                                        attr_dict["title_hidden"] = True

                        elif xml_elem_child.tag.endswith("edition"):

                            attr_dict["edition"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif (
                            xml_elem_child.tag.endswith("biblScope")
                            and xml_elem_child.attrib.get("unit") is not None
                        ):

                            attr_dict[xml_elem_child.attrib.get("unit")] = xml_elem_child.text

                            if (xml_elem_child.attrib.get("style") is not None):

                                attr_dict["scope_style"] = xml_elem_child.attrib.get("style")

                        elif xml_elem_child.tag.endswith("date"):

                            if xml_elem_child.attrib.get("type") == "lastAccessed":

                                attr_dict["ref_accessed"] = xml_elem_child.text

                            elif xml_elem_child.attrib.get("to") is not None:

                                attr_dict["start_date_written"] = attr_dict["start_date_written"] + " - " + xml_elem_child.text
                            
                            else:

                                attr_dict["start_date_written"] = xml_elem_child.text
                                if (xml_elem_child.attrib.get("rendition", "") in ["hidden", "#hidden"]):
                                        attr_dict["date_hidden"] = True

                        elif xml_elem_child.tag.endswith("ref"):

                            attr_dict["ref_target"] = xml_elem_child.attrib.get("target")
                            attr_dict["series"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif xml_elem_child.tag.endswith("textLang"):

                            attr_dict["text_language"] = xml_elem_child.text

                        elif xml_elem_child.tag.endswith("series"):

                            attr_dict["series"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif xml_elem_child.tag.endswith("edition"):

                            attr_dict["edition"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif (
                            xml_elem_child.tag is not None
                            and xml_elem_child.tag.endswith("note")
                        ):
                            attr_dict["note"] = ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)

                        elif (
                            xml_elem_child.tag.endswith("relatedItem")
                            and xml_elem_child.attrib.get("ana") == "has_expression"
                            ):
                            for ref in xml_elem_child:
                                if (ref.attrib.get("type") == "koha" and ref.attrib.get("target") is not None):
                                    attr_dict["koha_id"] = ref.attrib.get("target").replace("koha:", "")

                elif (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ref") is not None
                    and xml_elem.attrib.get("ref").startswith("bibls:")
                ):
                    # TODO : When there is time check these following lines for redundancy and potential clean-ups

                    bibl_id = xml_elem.get("ref").replace("bibls:", "")

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag is not None
                            and xml_elem_child.tag.endswith("title")
                            and is_valid_text(xml_elem_child.text)
                        ):
                            if (xml_elem_child.attrib.get("type") == "sub"):
                                attr_dict["untertitel"] = attr_dict["untertitel"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))
                            else:
                                attr_dict["name"] = remove_whitespace(remove_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))
                                if (xml_elem_child.attrib.get("rendition", "") in ["hidden", "#hidden"]):
                                    attr_dict["title_hidden"] = True
                        elif (
                            xml_elem_child.tag.endswith("hi")
                            and is_valid_text(xml_elem_child.text)
                        ):

                            attr_dict["name"] = attr_dict["untertitel"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif xml_elem_child.tag.endswith("series"):

                            attr_dict["series"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        elif xml_elem_child.tag.endswith("edition"):

                            attr_dict["edition"] = xml_elem_child.text

                        elif xml_elem_child.tag.endswith("date"):

                            if xml_elem_child.attrib.get("type") == "lastAccessed":

                                attr_dict["ref_accessed"] = xml_elem_child.text

                            elif xml_elem_child.attrib.get("to") is not None:

                                attr_dict["start_date_written"] = attr_dict["start_date_written"] + " - " + xml_elem_child.text
                            
                            else:

                                attr_dict["start_date_written"] = xml_elem_child.text
                                if (xml_elem_child.attrib.get("rendition", "") in ["hidden", "#hidden"]):
                                        attr_dict["date_hidden"] = True

                        elif xml_elem_child.tag.endswith("note"):

                            for xml_elem_child_child in xml_elem_child.getchildren():

                                if xml_elem_child_child.tag.endswith("title"):

                                    attr_dict["title_in_note"] = xml_elem_child_child.text

                            attr_dict["note"] = ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)

                        elif xml_elem_child.tag.endswith("ref"):

                            attr_dict["ref_target"] = xml_elem_child.attrib.get("target")

                        elif xml_elem_child.tag.endswith("textLang"):

                            attr_dict["text_language"] = xml_elem_child.text

                        elif (
                            xml_elem_child.attrib.get("target") is not None
                            and xml_elem_child.attrib.get("target").startswith("#bibl")
                        ):

                            if bibl_id is not None:

                                raise Exception("Inconsistent data or mapping")

                            attr_dict["bibl_id"] = xml_elem_child.attrib.get("target").replace("#", "")

                        elif (
                            xml_elem_child.tag.endswith("ptr")
                            and xml_elem_child.attrib.get("type") is not None
                            and xml_elem_child.attrib.get("type") == "bibl"
                            and xml_elem_child.attrib.get("target") is not None
                            and xml_elem_child.attrib.get("target").startswith("bibls:")
                        ):

                            if bibl_id is not None:

                                raise Exception("Inconsistent data or mapping")

                            attr_dict["bibl_id"] = xml_elem_child.attrib.get("target").replace("bibls:", "")

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
                    and xml_elem.attrib.get("ana") != "frbroo:aggregation_work"
                    and xml_elem.attrib.get("ana") != "frbroo:manifestation"
                ):

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("title")
                            and is_valid_text(xml_elem_child.text)
                        ):

                            attr_dict["name"] = remove_whitespace(xml_elem_child.text)

                elif (
                    xml_elem.tag.endswith("relatedItem")
                    and xml_elem.attrib.get("type") == "host"
                ):
                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("ptr")
                            and xml_elem_child.attrib.get("type") == "bibl"
                            and xml_elem_child.attrib.get("target") is not None
                        ):
                            attr_dict["bibl_id"] = xml_elem_child.attrib.get("target").replace("bibls:", "")
                        elif (
                            xml_elem_child.tag.endswith("bibl")
                            and xml_elem_child.attrib.get("ana") == "frbroo:manifestation"
                        ):
                            for xml_elem_child_child in xml_elem_child:
                                if (
                                    xml_elem_child_child.tag.endswith("ptr")
                                    and xml_elem_child_child.attrib.get("type") == "bibl"
                                    and xml_elem_child_child.attrib.get("target") is not None
                                ):
                                    attr_dict["bibl_id"] = xml_elem_child_child.attrib.get("target").replace("bibls:", "")

                if attr_dict["name"] is not None:
                    attr_dict["name"] = attr_dict["name"][:255]
                
                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    if attr_dict["name"] is not None:
                        attr_dict["name"] = attr_dict["name"][:255]

                    db_result = None

                    if attr_dict["bibl_id"] is not None:

                        db_result = F3_Manifestation_Product_Type.objects.get_or_create(
                            bibl_id=attr_dict["bibl_id"],
                        )

                    elif attr_dict["name"] is not None:

                        filter_dict = dict(filter(lambda entry: entry[1] is not None, attr_dict.items()))
                        db_hit = F3_Manifestation_Product_Type.objects.filter(**filter_dict)

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

                        enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)


        def parse_f9_place(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                attr_dict = {
                    "name": None,
                    "place_id": None,
                    "country": None
                }

                if (
                    xml_elem.tag.endswith("rs") and xml_elem.attrib.get("type") == "place"
                ):
                    
                    if xml_elem.attrib.get("ref") is not None:
                        attr_dict["place_id"] = xml_elem.attrib.get("ref").replace("place:", "")

                    for child in xml_elem:

                        if (
                            (child.tag.endswith("pubPlace") or child.tag.endswith("places"))
                            and is_valid_text(child.text)
                        ):

                            attr_dict["name"] = remove_whitespace(child.text).replace("pubPlace", "")

                elif (xml_elem.tag.endswith("place")):
                    if xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None:
                        attr_dict["place_id"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
                    for child in xml_elem:
                        if (
                            child.tag.endswith("placeName")
                            and is_valid_text(child.text)
                        ):
                            attr_dict["name"] = remove_whitespace(child.text)
                        elif (
                            child.tag.endswith("country")
                            and is_valid_text(child.text)
                        ):
                            attr_dict["country"] = remove_whitespace(child.text)
                elif (
                    xml_elem.tag.endswith("pubPlace")
                    and not path_node.path_node_parent.xml_elem.tag.endswith("rs")):

                                attr_dict["name"] = remove_whitespace(xml_elem.text).replace("pubPlace", "")
              
                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

            def sub_main(path_node: PathNode):

                entities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["place_id"] is not None:

                        db_result = F9_Place.objects.get_or_create(place_id=attr_dict["place_id"])

                    elif attr_dict["name"] is not None:

                        db_result = F9_Place.objects.get_or_create(name=attr_dict["name"])                    

                    entities_list.append(handle_after_creation(db_result, attr_dict))

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

                    name = remove_whitespace(xml_elem.text)

                for xml_elem_child in xml_elem:

                    if xml_elem_child.tag.endswith("forename") and is_valid_text(xml_elem_child.text):

                        forename = remove_whitespace(xml_elem_child.text)

                    if xml_elem_child.tag.endswith("surname") and is_valid_text(xml_elem_child.text):

                        surname = remove_whitespace(xml_elem_child.text)

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

                attr_dict = {
                    "pers_id": None,
                    "name": None,
                    "forename": None,
                    "surname": None,
                    "gnd_url": None,
                    "start_date_written": None,
                    "end_date_written": None,
                }

                if (
                    xml_elem.tag.endswith("rs")
                    and xml_elem.attrib.get("type") == "person"
                ):

                    for xml_elem_child in xml_elem:

                        if xml_elem_child.tag.endswith("persName"):

                            attr_dict["name"], attr_dict["forename"], attr_dict["surname"] = parse_persName(xml_elem_child)

                    if (
                        xml_elem.attrib.get("ref") is not None
                        and xml_elem.attrib.get("ref").startswith("persons:")
                    ):
                        attr_dict["pers_id"] = xml_elem.attrib.get("ref").replace("persons:", "")

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
                                and path_node.path_node_parent.xml_elem.attrib.get("ana") == "staging" # as in xmls in 001_Werke/004_Theatertexte/FRBR-Works/
                            )
                        )
                    )
                ):

                    attr_dict["name"], attr_dict["forename"], attr_dict["surname"] = parse_persName(xml_elem)

                elif (
                    xml_elem.tag.endswith("personGrp")
                ):

                    attr_dict["name"] = remove_whitespace(xml_elem.text)

                elif (
                    xml_elem.tag.endswith("item")
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id").startswith("pers")
                ):

                    attr_dict["pers_id"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")

                    for xml_elem_child in xml_elem:

                        if (xml_elem_child.tag.endswith("persName") 
                        and xml_elem_child.attrib.get("type") is not None
                        and xml_elem_child.attrib.get("type") == "register"):

                            attr_dict["name"], attr_dict["forename"], attr_dict["surname"] = parse_persName(xml_elem_child)

                        elif (
                            xml_elem_child.tag.endswith("ref")
                            and xml_elem_child.attrib.get("type") == "gnd"
                            and xml_elem_child.attrib.get("target") is not None
                        ):

                            attr_dict["gnd_url"] = xml_elem_child.attrib.get("target")

                        elif (
                            xml_elem_child.tag.endswith("date")
                        ):
                            if xml_elem_child.text.startswith("geb."):
                                attr_dict["start_date_written"] = xml_elem_child.text.replace("geb. ", "")
                            elif "-" in xml_elem_child.text:
                                attr_dict["start_date_written"] = xml_elem_child.text.split("-")[0]
                                attr_dict["end_date_written"] = xml_elem_child.text.split("-")[1]
                            else:
                                print("Strange date: ", xml_elem_child.text)

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

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

        def parse_f20_performance_work(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                attr_dict = {
                    "name": None,
                    "untertitel": None,
                    "idno": None,
                }

                if (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ana") == "frbroo:work"
                    and (
                        trees_manager.helper_dict["current_type"] == "009_LibrettiOper"
                        or trees_manager.helper_dict["current_type"] == "013_TextefürInstallationenundProjektionenFotoarbeiten"
                    )
                ):
                    if path_node.path_node_parent != None:
                        parent = path_node.path_node_parent
                        while parent.path_node_parent != None:
                            parent = parent.path_node_parent
                        if len(parent.entities_list) > 0:
                            xml = [f for f in parent.entities_list if "xml" in f.name]
                            if len(xml) > 0:
                                xml_file_name = xml[0].name.replace(".xml", "")
                                if len(xml_file_name) > 0:
                                    if xml_file_name.split("_")[0] == "interview":
                                        attr_dict["index_in_chapter"] = int(xml_file_name.split("_")[1])
                                    else:
                                        attr_dict["index_in_chapter"] = int(xml_file_name.split("_")[0])

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("title")
                            and (xml_elem_child.attrib.get("type") == "main" or xml_elem_child.attrib.get("type") == None)
                        ):

                            attr_dict["name"] = remove_whitespace(xml_elem_child.text)

                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "sub"
                        ):

                            if attr_dict["untertitel"] is not None:
                                attr_dict["untertitel"] = attr_dict["untertitel"] + "<br>" + remove_whitespace(xml_elem_child.text)
                            else:
                                attr_dict["untertitel"] = remove_whitespace(xml_elem_child.text)

                        if (
                            xml_elem_child.tag.endswith("idno")
                            and xml_elem_child.attrib["type"] == "JWV"
                        ):

                            attr_dict["idno"] = xml_elem_child.text

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

            def sub_main(path_node: PathNode):

                entities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    if attr_dict["idno"] is not None:

                        db_result = F20_Performance_Work.objects.get_or_create(
                            idno=attr_dict["idno"]
                        )

                    elif attr_dict["name"] is not None:

                        # db_result = F20_Performance_Work.objects.get_or_create(name=attr_dict["name"])
                        db_hit = F20_Performance_Work.objects.filter(
                            name=attr_dict["name"],
                            # self_contenttype=F20_Performance_Work.get_content_type()
                        )
                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            db_result = [
                                F20_Performance_Work.objects.create(name=attr_dict["name"]),
                                True
                            ]

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    entities_list.append(handle_after_creation(db_result, attr_dict))

                return entities_list

            return sub_main(path_node)


        def parse_f17_aggregation_work(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem
                
                attr_dict = {
                    "idno": None,
                    "name": None,
                    "gnd_url": None,
                    "index_in_chapter": None,
                    "untertitel": None
                }

                if (
                    xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ana") == "frbroo:aggregation_work"
                    and trees_manager.helper_dict["current_type"] == "work"
                ):

                    if path_node.path_node_parent != None:
                        parent = path_node.path_node_parent
                        while parent.path_node_parent != None:
                            parent = parent.path_node_parent
                        if len(parent.entities_list) > 0:
                            xml = [f for f in parent.entities_list if "xml" in f.name]
                            if len(xml) > 0:
                                xml_file_name = xml[0].name.replace(".xml", "")
                                if len(xml_file_name) > 0:
                                    if xml_file_name.split("_")[0] == "interview":
                                        attr_dict["index_in_chapter"] = int(xml_file_name.split("_")[1])
                                    else:
                                        attr_dict["index_in_chapter"] = int(xml_file_name.split("_")[0])

                    for xml_elem_child in xml_elem:

                        # TODO : Check if there are titles without 'type="main"'
                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "main"
                        ):

                            attr_dict["name"] = remove_whitespace(xml_elem_child.text)

                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "sub"
                        ):

                            if attr_dict["untertitel"] is not None:
                                attr_dict["untertitel"] = attr_dict["untertitel"] + "<br>" + remove_whitespace(xml_elem_child.text)
                            else:
                                attr_dict["untertitel"] = remove_whitespace(xml_elem_child.text)

                        if (
                            xml_elem_child.tag.endswith("idno")
                            and xml_elem_child.attrib["type"] == "JWV"
                        ):

                            attr_dict["idno"] = xml_elem_child.text

                elif (
                    xml_elem.tag.endswith("item")
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id").startswith("work")
                ):

                    attr_dict["idno"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "index"
                            and is_valid_text(xml_elem_child.text)
                        ):

                            attr_dict["name"] = remove_whitespace(xml_elem_child.text)

                        elif (
                            xml_elem_child.tag.endswith("ref")
                            and xml_elem_child.attrib.get("type") == "gnd"
                            and xml_elem_child.attrib.get("target") is not None
                        ):

                            attr_dict["gnd_url"] = xml_elem_child.attrib.get("target")

                elif (
                    xml_elem.tag.endswith("rs")
                    and xml_elem.attrib.get("type") == "work"
                    and xml_elem.attrib.get("ref") is not None
                    and xml_elem.attrib.get("ref").startswith("works:")
                ):

                    attr_dict["idno"] = xml_elem.attrib.get("ref").replace("works:", "")

                    # TODO : 'ref type="category"'
                    # for xml_elem_child in xml_elem:

                    #     if xml_elem_child.tag.endswith("title"):

                    #         attr_dict["name"] = remove_whitespace(xml_elem_child.text)

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None


            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["idno"] is not None:

                        db_result = F1_Work.objects.get_or_create(
                            idno=attr_dict["idno"]
                        )

                    elif attr_dict["name"] is not None:

                        # db_result = F1_Work.objects.get_or_create(name=attr_dict["name"])
                        db_hit = F1_Work.objects.filter(
                            name=attr_dict["name"],
                            # self_contenttype=F1_Work.get_content_type()
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


        def parse_f21_recording_work(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                attr_dict = {
                    "name": None,
                    "untertitel": None,
                    "idno": None,
                }

                if (
                    (
                        trees_manager.helper_dict["current_type"] == "005_TextefürHörspiele"
                        or trees_manager.helper_dict["current_type"] == "006_DrehbücherundTextefürFilme"
                        or trees_manager.helper_dict["current_type"] == "007_Kompositionen"
                        or xml_elem.attrib.get("type") == "audio_work"
                        or xml_elem.attrib.get("type") == "tv_work"
                        or xml_elem.attrib.get("type") == "audio_vis_work"
                        or xml_elem.attrib.get("type") == "movie"
                    )
                    and xml_elem.tag.endswith("bibl")
                    and xml_elem.attrib.get("ana") == "frbroo:work"
                ):
                    if (
                        xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                    ):
                        attr_dict["idno"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")

                    if path_node.path_node_parent != None:
                        parent = path_node.path_node_parent
                        while parent.path_node_parent != None:
                            parent = parent.path_node_parent
                        if len(parent.entities_list) > 0:
                            xml = [f for f in parent.entities_list if "xml" in f.name]
                            if len(xml) > 0:
                                xml_file_name = xml[0].name.replace(".xml", "")
                                if len(xml_file_name) > 0:
                                    if xml_file_name.split("_")[0] == "interview":
                                        attr_dict["index_in_chapter"] = int(xml_file_name.split("_")[1])
                                    else:
                                        attr_dict["index_in_chapter"] = int(xml_file_name.split("_")[0])
                                        
                    for xml_elem_child in xml_elem:

                        # TODO : Check if there are titles without 'type="main"'
                        if (
                            xml_elem_child.tag.endswith("title")
                            and (xml_elem_child.attrib.get("type") == "main" or (xml_elem_child.attrib.get("type") == None and attr_dict["name"] is None))
                        ):

                            attr_dict["name"] = remove_whitespace(xml_elem_child.text)

                        if (
                            xml_elem_child.tag.endswith("title")
                            and xml_elem_child.attrib.get("type") == "sub"
                        ):

                            if attr_dict["untertitel"] is None:
                                attr_dict["untertitel"] = ""
                            attr_dict["untertitel"] = attr_dict["untertitel"] + remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))

                        if (
                            xml_elem_child.tag.endswith("idno")
                            and xml_elem_child.attrib["type"] == "JWV"
                        ):

                            attr_dict["idno"] = xml_elem_child.text
                        
                        if (
                            xml_elem_child.tag.endswith("date")
                            and attr_dict["untertitel"] is None
                        ):
                            attr_dict["untertitel"] = xml_elem_child.text


                if (
                    (
                        trees_manager.helper_dict["current_type"] == "broadcast_index"
                    )
                    and xml_elem.tag.endswith("rs")
                    and xml_elem.attrib.get("ref") is not None
                    and xml_elem.attrib.get("ref").startswith("works:")
                ):
                    attr_dict["idno"] = xml_elem.attrib.get("ref").replace("works:","")
                            
                    for xml_elem_child in xml_elem:

                        # TODO : Check if there are titles without 'type="main"'
                        if (
                            xml_elem_child.tag.endswith("title")
                        ):

                            attr_dict["name"] = remove_whitespace(xml_elem_child.text)

                elif (
                    xml_elem.tag.endswith("rs")
                    and (xml_elem.attrib.get("type") in ["audio_vis_work", "audio_work", "tv_work", "movie"])
                    and xml_elem.attrib.get("ref") is not None
                    and xml_elem.attrib.get("ref").startswith("audio_vis_work:")
                ):

                    attr_dict["idno"] = xml_elem.attrib.get("ref").replace("audio_vis_work:", "")

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None


            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["idno"] is not None:

                        db_result = F1_Work.objects.get_or_create(
                            idno=attr_dict["idno"]
                        )


                    elif attr_dict["name"] is not None:

                        # db_result = F21_Recording_Work.objects.get_or_create(name=attr_dict["name"])
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


        def parse_f26_recording(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                attr_dict = {
                    "name": None,
                    "airing_date": None,
                    "broadcast_id": None,
                    "start_date_written": None,
                    "date_hidden": None,
                    "recording_type": None,
                    "note": None
                }
                helper_org = None

                if (
                    (xml_elem.tag.endswith("item") or xml_elem.tag.endswith("event"))
                    and xml_elem.attrib.get("type") == "broadcast"
                ):

                    if (
                        xml_elem.attrib.get("ana") is not None
                    ):
                        attr_dict["recording_type"] = xml_elem.attrib.get("ana")
                    if (
                        xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                    ):
                        attr_dict["broadcast_id"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
                    elif (
                        xml_elem.attrib.get("id") is not None
                        and len(xml_elem.attrib.get("id")) > 0
                    ):
                        attr_dict["broadcast_id"] = xml_elem.attrib.get("id")
                    elif (
                        xml_elem.attrib.get("target") is not None
                    ):
                        attr_dict["broadcast_id"] = xml_elem.attrib.get("target").replace("broadcast:", "")
        
                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("date")
                        ):

                            airing_date = xml_elem_child.text
                            attr_dict["airing_date"] = xml_elem_child.text
                            attr_dict["start_date_written"] = xml_elem_child.text
                            if xml_elem_child.attrib.get("rendition", "") in ["hidden", "#hidden"]:
                                attr_dict["date_hidden"] = True

                        elif (
                            (xml_elem_child.tag.endswith("orgName")
                            and xml_elem_child.attrib["role"] == "broadcaster") or
                            (xml_elem_child.tag.endswith("rs")
                            and xml_elem_child.attrib["type"] == "broadcaster")
                        ):

                            helper_org = xml_elem_child.text

                        elif xml_elem_child.tag.endswith("title"):
                            attr_dict["name"] = remove_whitespace(remove_outer_xml_tags((ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail))))
                        elif xml_elem_child.tag.endswith("note"):
                            attr_dict["note"] = ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)

                    # if attr_dict["name"] is None:

                    #     if attr_dict["airing_date"] is not None and helper_org is not None:

                    #         attr_dict["name"] = "aired on " + airing_date + " at " + helper_org

                    #     elif attr_dict["airing_date"] is not None:

                    #         attr_dict["name"] = "aired on " + airing_date

                    #     elif helper_org is not None:

                    #         attr_dict["name"] = "aired at " + helper_org

                    #     else:

                    #         attr_dict["name"] = "Unknown recording date"

                    if (
                        attr_dict["broadcast_id"] is None or attr_dict["broadcast_id"] == ""
                    ):
                        if path_node.path_node_parent != None:
                            parent = path_node.path_node_parent
                            while parent.path_node_parent != None:
                                parent = parent.path_node_parent
                            if len(parent.entities_list) > 0:
                                xml = [f for f in parent.entities_list if "xml" in f.name]
                                if len(xml) > 0:
                                    xml_file_name = xml[0].name.replace(".xml", "")
                                    attr_dict["broadcast_id"] = "broadcast_{}_{}".format(xml_file_name, attr_dict["start_date_written"])
 
                elif (xml_elem.tag.endswith("item") and xml_elem.attrib.get("type") is None):
                    for xml_elem_child in xml_elem:

                        if (xml_elem_child.tag.endswith("ptr") and xml_elem_child.attrib.get("type") == "broadcast"):
                            if (
                                xml_elem_child.attrib.get("target") is not None
                            ):
                                attr_dict["broadcast_id"] = xml_elem_child.attrib.get("target").replace("broadcast:", "")

                
                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None


            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["broadcast_id"] is not None:

                        # db_result = F26_Recording.objects.get_or_create(name=attr_dict["name"])
                        db_hit = F26_Recording.objects.filter(broadcast_id=attr_dict["broadcast_id"])
                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            db_result = [
                                F26_Recording.objects.create(broadcast_id=attr_dict["broadcast_id"]),
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

                attr_dict = {
                    "name": None,
                    "note": None,
                    "category": None,
                    "date_hidden": None,
                    "start_date_written": None,
                    "start_date": None,
                    "performance_id": None,
                    "performance_type": None
                }
                institution = None

                if (
                    (xml_elem.tag.endswith("event") or xml_elem.tag.endswith("item"))
                    and (
                        xml_elem.attrib.get("ana") == "staging" 
                        or xml_elem.attrib.get("ana") == "UA" 
                        or xml_elem.attrib.get("ana") == "UL" 
                        or xml_elem.attrib.get("ana") == "UA_Film" 
                        or xml_elem.attrib.get("ana") == "UA_film" 
                        or xml_elem.attrib.get("ana") == "EA" 
                        or xml_elem.attrib.get("ana") == "cinemarelease" 
                        or xml_elem.attrib.get("ana") == "EP"
                        or xml_elem.attrib.get("ana") == "presentation"
                        )
                ):

                    if (xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None):
                            attr_dict["performance_id"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")

                    if xml_elem.attrib.get("ana") == "UA":
                            attr_dict["performance_type"] = "UA"
                    if xml_elem.attrib.get("ana") == "UL":
                            attr_dict["performance_type"] = "UL"
                    elif xml_elem.attrib.get("ana") == "UA_Film":
                            attr_dict["performance_type"] = "UA_Film"
                    elif xml_elem.attrib.get("ana") == "UA_film":
                            attr_dict["performance_type"] = "UA_Film"
                    elif xml_elem.attrib.get("ana") == "cinemarelease":
                            attr_dict["performance_type"] = "cinemarelease"
                    elif xml_elem.attrib.get("ana") == "EA":
                            attr_dict["performance_type"] = "EA"
                    elif xml_elem.attrib.get("ana") == "EP":
                            attr_dict["performance_type"] = "EP"
                    elif xml_elem.attrib.get("ana") == "presentation":
                            attr_dict["performance_type"] = "presentation"

                    for xml_elem_child in xml_elem:

                        if (
                            xml_elem_child.tag.endswith("date")
                            and is_valid_text(xml_elem_child.text)
                        ):

                            attr_dict["start_date_written"] = xml_elem_child.text
                            if (xml_elem_child.attrib.get("rendition", "") in ["hidden", "#hidden"]):
                                attr_dict["date_hidden"] = True
                            if xml_elem_child.attrib.get("when") is not None:
                                attr_dict["start_date"] = xml_elem_child.attrib.get("when")

                        elif (
                            (xml_elem_child.tag.endswith("rs")
                            and xml_elem_child.attrib.get("type") == "institution")
                            or ((xml_elem_child.tag.endswith("note")
                            and xml_elem_child.attrib.get("type") == "institutions"))
                            and is_valid_text(xml_elem_child.text)
                        ):

                            institution = xml_elem_child.text

                        elif (
                            xml_elem_child.tag.endswith("note")
                            # and is_valid_text(xml_elem_child.text)
                        ):

                            attr_dict["note"] = ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)
                            categories = ""

                            for xml_elem_child_child in xml_elem_child:

                                if (
                                    xml_elem_child_child.tag.endswith("ref")
                                    and xml_elem_child_child.attrib.get("type") == "category"
                                    and is_valid_text(xml_elem_child_child.text)
                                ):

                                    categories += xml_elem_child_child.text + "; "

                            if len(categories) > 0:

                                attr_dict["category"] = categories
                elif (
                    xml_elem.tag.endswith("ptr")
                    and (xml_elem.attrib.get("type") == "staging" or xml_elem.attrib.get("type") == "UA" or xml_elem.attrib.get("type") == "cinemarelease")
                    and xml_elem.attrib.get("target").startswith("insz")
                ):
                    attr_dict["performance_id"] = xml_elem.attrib.get("target").replace("insz:", "")
                    # attr_dict["performance_type"] = xml_elem.attrib.get("type")


                if (
                    attr_dict["start_date_written"] is not None
                    and institution is not None
                ):

                    attr_dict["name"] = f"Aufführung, Am {attr_dict['start_date_written']}, Bei {institution}"

                elif attr_dict["start_date_written"] is not None:

                    attr_dict["name"] = f"Aufführung, Am {attr_dict['start_date_written']}"

                elif institution is not None:

                    attr_dict["name"] = f"Bei {institution}"

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

            def sub_main(path_node: PathNode):

                entities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["performance_id"] is not None:

                        db_result = F31_Performance.objects.get_or_create(performance_id=attr_dict["performance_id"])

                        entities_list.append(handle_after_creation(db_result, attr_dict))

                    elif attr_dict["name"] is not None:

                        # db_result = F21_Recording_Work.objects.get_or_create(name=attr_dict["name"])
                        db_hit = F31_Performance.objects.filter(name=attr_dict["name"])
                        if len(db_hit) > 1:

                            # TODO : Check how often this is the case
                            print("Multiple occurences found, taking the first")
                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 1:

                            db_result = [db_hit[0], False]

                        elif len(db_hit) == 0:

                            db_result = [
                                F31_Performance.objects.create(name=attr_dict["name"]),
                                True
                            ]

                    else:

                        print("Entity found without a uniquely identifying attribute")

                return entities_list

            return sub_main(path_node)


        def parse_chapter(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                attr_dict = {
                    "chapter_number": None,
                    "chapter_type": None,
                    "name": None
                }

                if (
                    path_node.path_node_parent is not None
                    and path_node.path_node_parent.xml_elem.tag.endswith("keywords")
                    and path_node.path_node_parent.xml_elem.attrib.get("ana") == "chapters"
                    and xml_elem.tag.endswith("term")
                    and xml_elem.attrib.get("n") is not None
                    and is_valid_text(xml_elem.text)
                ):

                    if xml_elem.attrib.get("n").startswith("7-"):
                        attr_dict["chapter_number"] = xml_elem.attrib.get("n").replace("7-", "7.x").replace("-",".")
                    else:
                        attr_dict["chapter_number"] = xml_elem.attrib.get("n").replace("-",".")
                    attr_dict["chapter_type"] = xml_elem.attrib.get("type")
                    attr_dict["name"] = remove_whitespace(xml_elem.text)
                
                elif (
                    path_node.path_node_parent is not None
                    and path_node.path_node_parent.path_node_parent is not None
                    and path_node.path_node_parent.path_node_parent.xml_elem.tag.endswith("keywords")
                    and path_node.path_node_parent.path_node_parent.xml_elem.attrib.get("ana") == "about"
                    and xml_elem.tag.endswith("rs")
                    and xml_elem.attrib.get("type", "") == "chapter"
                ):
                    attr_dict["chapter_number"] = xml_elem.attrib.get("ref").replace("-",".")
                    attr_dict["name"] = remove_whitespace(xml_elem.text)

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

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

        def parse_keyword(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                attr_dict = {
                    "name": None,
                    "keyword_id": None
                }

                if (
                    path_node.path_node_parent is not None
                    and (not path_node.path_node_parent.xml_elem.attrib.get("ana") == "textlang")
                    and xml_elem.tag.endswith("term")
                    and xml_elem.attrib.get("n") is None
                    and is_valid_text(xml_elem.text)
                ):
                    attr_dict["name"] = remove_whitespace(xml_elem.text)
                    if (xml_elem.attrib.get("ref") is not None):
                        attr_dict["keyword_id"] = xml_elem.attrib.get("ref").replace("term:", "")
                        
                if (xml_elem.tag.endswith("gloss")
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                    and is_valid_text(xml_elem.text)
                ):
                    attr_dict["name"] = remove_whitespace(xml_elem.text)
                    attr_dict["keyword_id"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["keyword_id"] is not None:

                        db_result = Keyword.objects.get_or_create(keyword_id=attr_dict["keyword_id"])

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)

        def parse_note(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                attr_dict = {
                    "name": None,
                    "content": None,
                    "context": None,
                    "type": None,
                    "rendition": None,
                }

                if (
                    path_node.path_node_parent is not None
                    and xml_elem.tag.endswith("note")
                ):

                    top_level_node = get_uppermost_parent(path_node)
                    # navigate to chapters
                    def find_all_entities_of_class(subtree, class_name, found_elements=[], stop_after_tag=None, stop_after_attr=None):
                        queue = []     #Initialize a queue
                        found_elements += [e for e in subtree.entities_list if e.__class__ == class_name]
                        queue.append(subtree)

                        while queue:          # Creating loop to visit each node
                            node = queue.pop(0) 
                            for child in node.path_node_children_list:
                                if stop_after_attr is not None and child.xml_elem.attrib.get(stop_after_attr[0], "") == stop_after_attr[1]:
                                    break
                                found_elements += [e for e in child.entities_list if e.__class__ == class_name]
                                queue.append(child)
                                if stop_after_tag is not None and child.xml_elem.tag.endswith(stop_after_tag):
                                    break
                                
                        return found_elements
                    chapters = find_all_entities_of_class(top_level_node, Chapter, [], stop_after_attr=["ana", "about"])
                    if len(chapters) > 0:
                        leaf_chapters = []
                        for (idx, c) in enumerate(chapters):
                            if idx > 0 and len(c.chapter_number.split("-")[0]) == 1:
                                leaf_chapters.append(chapters[idx-1])
                        if chapters[-1] not in leaf_chapters:
                            leaf_chapters.append(chapters[-1])
                        if len(leaf_chapters) > 0:
                            attr_dict["context"] = ", ".join(c.chapter_number for c in leaf_chapters)
                        
                    attr_dict["content"] = ET.tostring(xml_elem, encoding="unicode").strip(xml_elem.tail)

                    if(xml_elem.attrib.get("rendition") is not None):
                        attr_dict["rendition"] = xml_elem.attrib.get("rendition")
                    if(xml_elem.attrib.get("type") is not None):
                        attr_dict["type"] = xml_elem.attrib.get("type")

                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    # if attr_dict["name"] is not None:

                    #db_result = XMLNote.objects.get_or_create(attr_dict)
                    db_result = [XMLNote.objects.create(), True]

                    # else:

                        # print("Entity found without a uniquely identifying attribute")

                    enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)

        def parse_e38_image(path_node):

            def parse_attr(path_node: PathNode):

                xml_elem = path_node.xml_elem

                attr_dict = {
                    "name": None,
                    "image_id": None,
                    "description": None,
                    "alt_text": None,
                    "filename": None,
                }

                if (
                    xml_elem.tag.endswith("figure")
                    and xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id") is not None
                    and xml_elem.attrib.get("type") is not None
                    and xml_elem.attrib.get("type") == "illustration"
                ):
                    attr_dict["name"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
                    attr_dict["image_id"] = xml_elem.attrib.get("{http://www.w3.org/XML/1998/namespace}id")
                    
                    for xml_elem_child in xml_elem:
                        if (xml_elem_child.tag.endswith("figDesc") and xml_elem_child.attrib.get("type") is not None):
                            if xml_elem_child.attrib.get("type") == "alt":
                                attr_dict["alt_text"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))
                            elif xml_elem_child.attrib.get("type") == "main":
                                attr_dict["description"] = remove_whitespace(remove_outer_xml_tags(ET.tostring(xml_elem_child, encoding="unicode").strip(xml_elem_child.tail)))
                        if xml_elem_child.tag.endswith("graphic") and xml_elem_child.attrib.get("url") is not None:
                            attr_dict["filename"] = xml_elem_child.attrib.get("url")
                
                elif (
                    xml_elem.tag.endswith("ptr")
                    and xml_elem.attrib.get("type", "") == "image"
                    and xml_elem.attrib.get("target") is not None
                ):
                    attr_dict["name"] = xml_elem.attrib.get("target").replace("images:", "")
                    attr_dict["image_id"] = xml_elem.attrib.get("target").replace("images:", "")
                    
                       
                if len([v for v in attr_dict.values() if v is not None]) > 0:

                    return attr_dict

                else:

                    return None

            def sub_main(path_node):

                enities_list = []

                attr_dict = parse_attr(path_node)

                if attr_dict is not None:

                    db_result = None

                    if attr_dict["image_id"] is not None:

                        db_result = E38_Image.objects.get_or_create(image_id=attr_dict["image_id"])

                    else:

                        print("Entity found without a uniquely identifying attribute")

                    enities_list.append(handle_after_creation(db_result, attr_dict))

                return enities_list

            return sub_main(path_node)

        def main_parse_for_entities(path_node):

            print(f"\nParsing: tag: {path_node.xml_elem.tag}, attrib: {path_node.xml_elem.attrib}, text: {path_node.xml_elem.text.__repr__()}")

            path_node.entities_list.extend(parse_e40_legal_body(path_node))

            path_node.entities_list.extend(parse_e55_type(path_node))

            path_node.entities_list.extend(parse_f1_work(path_node))

            path_node.entities_list.extend(parse_honour(path_node))

            path_node.entities_list.extend(parse_f3_manifestation(path_node))

            path_node.entities_list.extend(parse_f9_place(path_node))

            # TODO : Consider ruling out Project members
            path_node.entities_list.extend(parse_f10_person(path_node))

            # path_node.entities_list.extend(parse_f20_performance_work(path_node))

            path_node.entities_list.extend(parse_f21_recording_work(path_node))

            path_node.entities_list.extend(parse_f26_recording(path_node))

            path_node.entities_list.extend(parse_f31_performance(path_node))

            path_node.entities_list.extend(parse_chapter(path_node))

            path_node.entities_list.extend(parse_keyword(path_node))

            path_node.entities_list.extend(parse_note(path_node))

            path_node.entities_list.extend(parse_e38_image(path_node))


            # cls.parse_f17_aggregation_work(path_node.xml_elem)

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

        return main_parse_for_entities(path_node)


    @classmethod
    def parse_for_triples(cls, path_node: PathNode):

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

        def create_triple(entity_subj, entity_obj, prop, path_node=None):

            db_result = None
            if prop.name == "is in chapter":
                db_result = InChapterTriple.objects.get_or_create(
                    subj=entity_subj,
                    obj=entity_obj,
                    prop=prop
                )
            else:
                hidden = None
                if path_node is not None:
                    current_path_node = path_node
                    while hidden is None and current_path_node.path_node_parent is not None:
                        if current_path_node.xml_elem.attrib.get("rendition", "") in ["#hidden", "hidden"]:
                            hidden = True
                        current_path_node = current_path_node.path_node_parent

                db_result = RenditionTriple.objects.get_or_create(
                    subj=entity_subj,
                    obj=entity_obj,
                    prop=prop,
                    rendition_hidden=hidden
                )

            if db_result[1] is True:

                print(f"created triple: subj: {entity_subj}, obj: {entity_obj}, prop: {prop.name}")

            else:

                print("triple already exists")

            return db_result[0]

        def parse_triples_from_f1_work(entity_work, path_node):

            def triple_from_f1_to_f1(entity_work, path_node):
                if (
                            path_node.path_node_parent is not None
                            and path_node.path_node_parent.xml_elem.tag.endswith("div")
                            and path_node.path_node_parent.xml_elem.attrib.get("type") == "entry"
                            and path_node.path_node_parent.path_node_parent.xml_elem.tag.endswith("body")
                            and path_node.path_node_parent.path_node_parent.path_node_parent.xml_elem.tag.endswith("text")
                    ):
                        parent = get_uppermost_parent(path_node)
                        teiHeader = parent.path_node_children_list[0]
                        textClass = teiHeader.path_node_children_list[1].path_node_children_list[0]
                        for keywords in textClass.path_node_children_list:
                            if keywords.xml_elem.attrib.get("ana") == "about":
                                for term in keywords.path_node_children_list:
                                    for rs in term.path_node_children_list:
                                        for entity_other in rs.entities_list:
                                            if entity_other != entity_work and entity_other.__class__ in [F1_Work, F10_Person, E40_Legal_Body, Honour, Chapter]:
                                                if entity_other is None or entity_work is None:
                                                    print("One of the two entities is none, this shouldn't happen")
                                                else:
                                                    create_triple(entity_obj=entity_other, entity_subj=entity_work,prop=Property.objects.get(name="is about"), path_node=rs)
                        
                        for sibling in path_node.path_node_parent.path_node_children_list:
                            if (
                                sibling.xml_elem.attrib.get("type") is not None 
                                and (sibling.xml_elem.attrib.get("type").endswith("frbroo:manifestations"))
                            ):
                                for sibling_child in sibling.path_node_children_list:
                                    if (
                                        sibling_child.xml_elem.tag.endswith("listBibl") 
                                        and sibling_child.xml_elem.attrib.get("type") == "content"
                                        ):
                                        for sibling_grandchild in sibling_child.path_node_children_list:
                                            for entity_other in sibling_grandchild.entities_list:
                                                if (
                                                    entity_other.__class__ is F3_Manifestation_Product_Type
                                                    or entity_other.__class__ is F1_Work
                                                ):
                                                    create_triple(
                                                        entity_subj=entity_work,
                                                        entity_obj=entity_other,
                                                        prop=Property.objects.get(name="contains"),
                                                        path_node=sibling_grandchild                                              
                                                    )
                            elif (
                                sibling.xml_elem.attrib.get("type") is not None 
                                and (sibling.xml_elem.attrib.get("type").endswith("basedOn") or sibling.xml_elem.attrib.get("type").endswith("commentary"))
                            ):
                                for sibling_child in sibling.path_node_children_list:
                                    for p in sibling_child.path_node_children_list:
                                        for rs in p.path_node_children_list:
                                            for entity_other in rs.entities_list:
                                                if entity_other != entity_work and entity_other.__class__ in [F1_Work, F10_Person, E40_Legal_Body, Honour, Chapter]:
                                                    if entity_other is None or entity_work is None:
                                                        print("One of the two entities is none, this shouldn't happen")
                                                    else:
                                                        create_triple(entity_obj=entity_other, entity_subj=entity_work,prop=Property.objects.get(name="is about"),path_node=rs)
                        
                elif (
                        path_node.path_node_parent is not None
                        and "0006_Sekundärliterat" in TreesManager.helper_dict["file_path"]
                        and entity_work.idno.startswith("seklit")
                    ):
                        parent = get_uppermost_parent(path_node)
                        teiHeader = parent.path_node_children_list[0]
                        textClass = teiHeader.path_node_children_list[1].path_node_children_list[0]
                        for keywords in textClass.path_node_children_list:
                            if keywords.xml_elem.attrib.get("ana") == "about":
                                for term in keywords.path_node_children_list:
                                    for rs in term.path_node_children_list:
                                        for entity_other in rs.entities_list:
                                            if entity_other != entity_work and entity_other.__class__ in [F1_Work, F10_Person, E40_Legal_Body, Honour, Chapter]:
                                                if entity_other is None or entity_work is None:
                                                    print("One of the two entities is none, this shouldn't happen")
                                                else:
                                                    create_triple(entity_obj=entity_other, entity_subj=entity_work,prop=Property.objects.get(name="is about"),path_node=rs)
                elif (
                            "0007_SendungenundFilmporträts" in TreesManager.helper_dict["file_path"]
                            and path_node.path_node_parent is not None
                            and path_node.path_node_parent.path_node_parent is not None
                            and path_node.path_node_parent.path_node_parent.xml_elem.tag.endswith("div")
                            and path_node.path_node_parent.path_node_parent.xml_elem.attrib.get("type") == "head_section"
                    ):
                        parent = get_uppermost_parent(path_node)
                        teiHeader = parent.path_node_children_list[0]
                        textClass = teiHeader.path_node_children_list[1].path_node_children_list[0]
                        for keywords in textClass.path_node_children_list:
                            if keywords.xml_elem.attrib.get("ana") == "about":
                                for term in keywords.path_node_children_list:
                                    for rs in term.path_node_children_list:
                                        for entity_other in rs.entities_list:
                                            if entity_other != entity_work and entity_other.__class__ in [F1_Work, F10_Person, E40_Legal_Body, Honour, Chapter]:
                                                if entity_other is None or entity_work is None:
                                                    print("One of the two entities is none, this shouldn't happen")
                                                else:
                                                    create_triple(entity_obj=entity_other, entity_subj=entity_work,prop=Property.objects.get(name="is about"), path_node=rs)
                        

                elif (  path_node.path_node_parent is not None
                        and path_node.path_node_parent.xml_elem.tag.endswith("div")
                        and path_node.path_node_parent.xml_elem.attrib.get("type") == "section"
                        and path_node.path_node_parent.path_node_parent.xml_elem.tag.endswith("body")
                        and path_node.path_node_parent.path_node_parent.path_node_parent.xml_elem.tag.endswith("text")
                    ):
                        for sibling in path_node.path_node_parent.path_node_children_list:
                            if (
                                sibling.xml_elem.attrib.get("ana") is not None 
                                and (sibling.xml_elem.attrib.get("ana") == "contained" or sibling.xml_elem.attrib.get("ana") == "content")
                            ):
                                for sibling_child in sibling.path_node_children_list:
                                    for entity_other in sibling_child.entities_list:
                                        if (
                                            entity_other.__class__ is F3_Manifestation_Product_Type
                                            or entity_other.__class__ is F1_Work
                                        ):
                                            create_triple(
                                                entity_subj=entity_work,
                                                entity_obj=entity_other,
                                                prop=Property.objects.get(name="contains"),
                                                path_node=sibling_child
                                            )
                
            def triple_from_f1_to_f3(entity_work, path_node):

                def check_and_create_triple_to_f3(entity_work, path_node_other):

                    for entity_other in path_node_other.entities_list:

                        if entity_other.__class__ is F3_Manifestation_Product_Type:

                            create_triple(
                                entity_subj=entity_work,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="is expressed in"),
                                path_node=path_node_other
                            )

                for neighbour_path_node in path_node.path_node_parent.path_node_children_list:

                    # translated manifestations
                    if (
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
                                                entity_obj=entity_manifestation,
                                                entity_subj=entity_work,
                                                prop=Property.objects.get(name="is original for translation"),
                                                path_node=list_bibl_child_path_node
                                            )

                    # contained manifestations (aggregation_work)
                    elif (
                        neighbour_path_node.xml_elem.tag.endswith("div")
                        and neighbour_path_node.xml_elem.attrib.get("type") == "content"
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
                                                entity_subj=entity_work,
                                                entity_obj=entity_manifestation,
                                                prop=Property.objects.get(name="contains"),
                                                path_node=list_bibl_child_path_node
                                            )
                    elif (
                        neighbour_path_node.xml_elem.tag.endswith("listBibl")
                        and neighbour_path_node.xml_elem.attrib.get("type") == "content"
                    ):

                        for list_bibl_child_path_node in neighbour_path_node.path_node_children_list:

                            if (
                                list_bibl_child_path_node.xml_elem.tag is not None
                                and list_bibl_child_path_node.xml_elem.tag.endswith("bibl")
                            ):

                                for entity_manifestation in list_bibl_child_path_node.entities_list:

                                    if entity_manifestation.__class__ is F3_Manifestation_Product_Type:

                                        create_triple(
                                            entity_subj=entity_work,
                                            entity_obj=entity_manifestation,
                                            prop=Property.objects.get(name="contains"),
                                            path_node=list_bibl_child_path_node
                                        )
                    
                    # direct manifestations
                    elif (
                        neighbour_path_node.xml_elem.tag.endswith("div")
                    ):

                        for neighbour_child_path_node in neighbour_path_node.path_node_children_list:

                            if neighbour_child_path_node.xml_elem.tag.endswith(("listBibl", "p")):

                                for neighbour_child_child_path_node in neighbour_child_path_node.path_node_children_list:

                                    check_and_create_triple_to_f3(entity_work, neighbour_child_child_path_node)

                            else:

                                check_and_create_triple_to_f3(entity_work, neighbour_child_path_node)

                # for seklit works + manifestations
                for path_node_child in path_node.path_node_children_list:
                    if path_node_child.xml_elem.tag.endswith("listBibl"):
                        for path_node_child_child in path_node_child.path_node_children_list:
                            if path_node_child_child.xml_elem.tag.endswith("bibl"):
                                check_and_create_triple_to_f3(entity_work, path_node_child_child)

            def triple_from_f1_to_f10(entity_work, path_node):

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if entity_other.__class__ == F10_Person:

                            if child_path_node.xml_elem.tag.endswith("personGrp"):

                                if (child_path_node.xml_elem.attrib.get("role") == "editor"):

                                    create_triple(
                                            entity_subj=entity_other,
                                            entity_obj=entity_work,
                                            prop=Property.objects.get(name="is editor of"),
                                            path_node=child_path_node
                                        )
                                elif (child_path_node.xml_elem.attrib.get("role") == "author"):

                                    create_triple(
                                            entity_subj=entity_other,
                                            entity_obj=entity_work,
                                            prop=Property.objects.get(name="is author of"),
                                            path_node=child_path_node
                                        )


                            for child_child_path_node in child_path_node.path_node_children_list:

                                if (
                                        child_child_path_node.xml_elem.tag.endswith("persName")
                                ):

                                    if child_child_path_node.xml_elem.attrib.get("role") == "author":

                                        create_triple(
                                            entity_subj=entity_other,
                                            entity_obj=entity_work,
                                            prop=Property.objects.get(name="is author of"),
                                            path_node = child_child_path_node
                                        )

                                    elif (child_child_path_node.xml_elem.attrib.get("role") == "editor"):

                                        create_triple(
                                            entity_subj=entity_other,
                                            entity_obj=entity_work,
                                            prop=Property.objects.get(name="is editor of"),
                                            path_node = child_child_path_node
                                        )

                                    elif (child_child_path_node.xml_elem.attrib.get("role") == "interviewer"):

                                        create_triple(
                                            entity_subj=entity_other,
                                            entity_obj=entity_work,
                                            prop=Property.objects.get(name="is interviewer of"),
                                            path_node = child_child_path_node
                                        )

                                    elif (child_child_path_node.xml_elem.attrib.get("role") == "interviewee"):

                                        create_triple(
                                            entity_subj=entity_other,
                                            entity_obj=entity_work,
                                            prop=Property.objects.get(name="is interviewee of"),
                                            path_node = child_child_path_node
                                        )

                                    elif (child_child_path_node.xml_elem.attrib.get("role") == "adaptioner"):

                                        create_triple(
                                            entity_subj=entity_other,
                                            entity_obj=entity_work,
                                            prop=Property.objects.get(name="is adaptioner of"),
                                            path_node = child_child_path_node
                                        )

                                    # elif (child_child_path_node.xml_elem.attrib.get("role") == "contributor"):

                                    #     create_triple(
                                    #         entity_subj=entity_other,
                                    #         entity_obj=entity_work,
                                    #         prop=Property.objects.get(name="is contributor of")
                                    #     )

                                    # elif (child_child_path_node.xml_elem.attrib.get("role") == "actor"):

                                    #     create_triple(
                                    #         entity_subj=entity_other,
                                    #         entity_obj=entity_work,
                                    #         prop=Property.objects.get(name="is actor of")
                                    #     )

                                    # elif (child_child_path_node.xml_elem.attrib.get("role") == "director"):

                                    #     create_triple(
                                    #         entity_subj=entity_other,
                                    #         entity_obj=entity_work,
                                    #         prop=Property.objects.get(name="is director of")
                                    #     )

                for neighbor_path_node in path_node.path_node_parent.path_node_children_list:
                    for child_path_node in neighbor_path_node.path_node_children_list:
                        for child_child_path_node in child_path_node.path_node_children_list:
                            for entity_other in child_child_path_node.entities_list:
                                if entity_other.__class__ == F10_Person:
                                    for child_child_child_path_node in child_child_path_node.path_node_children_list:
                                        if (
                                                child_child_child_path_node.xml_elem.tag.endswith("persName")
                                        ):

                                            if (child_child_child_path_node.xml_elem.attrib.get("role") == "contributor"):

                                                create_triple(
                                                    entity_subj=entity_other,
                                                    entity_obj=entity_work,
                                                    prop=Property.objects.get(name="is contributor of"),
                                                    path_node=child_child_child_path_node
                                                )

                                            elif (child_child_child_path_node.xml_elem.attrib.get("role") == "actor"):

                                                create_triple(
                                                    entity_subj=entity_other,
                                                    entity_obj=entity_work,
                                                    prop=Property.objects.get(name="is actor of"),
                                                    path_node=child_child_child_path_node
                                                )

                                            elif (child_child_child_path_node.xml_elem.attrib.get("role") == "director"):

                                                create_triple(
                                                    entity_subj=entity_other,
                                                    entity_obj=entity_work,
                                                    prop=Property.objects.get(name="is director of"),
                                                    path_node=child_child_child_path_node
                                                )                   
                                
            def triple_from_f1_to_f31(entity_work, path_node):
                parent = path_node.path_node_parent
                if parent.xml_elem.tag.endswith("head"):
                    parent = parent.path_node_parent.path_node_parent
                    for neighbour_path_node in parent.path_node_children_list:
                        for child_path_node in neighbour_path_node.path_node_children_list:
                            if child_path_node.xml_elem.tag.endswith("item"):
                                for entity_other in child_path_node.entities_list:
                                        if entity_other.__class__ == F31_Performance:
                                            create_triple(
                                                        entity_obj=entity_other,
                                                        entity_subj=entity_work,
                                                        prop=Property.objects.get(name="has been performed in"),
                                                        path_node=child_path_node
                                                    )
                                for child_child_path_node in child_path_node.path_node_children_list:
                                    for entity_other in child_child_path_node.entities_list:
                                        if entity_other.__class__ == F31_Performance:
                                            create_triple(
                                                        entity_obj=entity_other,
                                                        entity_subj=entity_work,
                                                        prop=Property.objects.get(name="has been performed in"),
                                                        path_node=child_child_path_node
                                                    )
                for neighbour_path_node in parent.path_node_children_list:
                    for child_path_node in neighbour_path_node.path_node_children_list:
                        for child_child_path_node in child_path_node.path_node_children_list:
                            if child_child_path_node.xml_elem.tag.endswith("item"):
                                for entity_other in child_child_path_node.entities_list:
                                        if entity_other.__class__ == F31_Performance:
                                            create_triple(
                                                        entity_obj=entity_other,
                                                        entity_subj=entity_work,
                                                        prop=Property.objects.get(name="has been performed in"),
                                                        path_node=child_child_path_node
                                                    )
                                for child_child_child_path_node in child_child_path_node.path_node_children_list:
                                    for entity_other in child_child_child_path_node.entities_list:
                                        if entity_other.__class__ == F31_Performance:
                                            create_triple(
                                                        entity_obj=entity_other,
                                                        entity_subj=entity_work,
                                                        prop=Property.objects.get(name="has been performed in"),
                                                        path_node=child_child_child_path_node
                                                    )
                                    if child_child_child_path_node.xml_elem.tag.endswith("p"):
                                        for item_path_node in child_child_child_path_node.path_node_children_list:
                                            for ptr_path_node in item_path_node.path_node_children_list:
                                                for entity_other in ptr_path_node.entities_list:
                                                    if entity_other.__class__ == F31_Performance:
                                                        create_triple(
                                                                    entity_obj=entity_other,
                                                                    entity_subj=entity_work,
                                                                    prop=Property.objects.get(name="has been performed in"),
                                                                    path_node=ptr_path_node
                                                                )
                
            def triples_from_f1_to_note(entity_work, path_node: PathNode):

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if (
                            entity_other.__class__ is XMLNote
                            and child_path_node.xml_elem.tag.endswith("note")
                        ):

                            create_triple(
                                entity_subj=entity_work,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="has note"),
                                path_node=child_path_node
                            )

            def triple_from_f1_to_f26(entity_recording_work, path_node: PathNode):

                for path_node_neighbour in path_node.path_node_parent.path_node_children_list:

                    if path_node_neighbour.xml_elem.attrib.get("type") in ["broadcasts", "broadcast", "radio", "cinemarelease"]:

                        for path_node_neighbour_child in path_node_neighbour.path_node_children_list:

                            for path_node_neighbour_child_child in path_node_neighbour_child.path_node_children_list:

                                if (path_node_neighbour_child_child.xml_elem.tag.endswith("item")):

                                    for path_node_neighbour_child_child_child in path_node_neighbour_child_child.path_node_children_list:
                                        for entity_other in path_node_neighbour_child_child_child.entities_list:
                                            if entity_other.__class__ is F26_Recording:
                                                create_triple(
                                                    entity_subj=entity_recording_work,
                                                    entity_obj=entity_other,
                                                    prop=Property.objects.get(name="R13 is realised in"),
                                                    path_node=path_node_neighbour_child_child_child
                                                )

                                        if path_node_neighbour_child_child_child.xml_elem.tag.endswith("p"):
                                            for item_path_node in path_node_neighbour_child_child_child.path_node_children_list:
                                                for entity_other in item_path_node.entities_list:
                                                    if entity_other.__class__ is F26_Recording:
                                                        create_triple(
                                                            entity_subj=entity_recording_work,
                                                            entity_obj=entity_other,
                                                            prop=Property.objects.get(name="R13 is realised in"),
                                                            path_node=item_path_node
                                                        )

                                for entity_other in path_node_neighbour_child_child.entities_list:

                                    if entity_other.__class__ is F26_Recording:

                                        create_triple(
                                            entity_subj=entity_recording_work,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="R13 is realised in"),
                                            path_node=path_node_neighbour_child_child
                                        )
                

            triple_from_f1_to_f1(entity_work, path_node)
            triple_from_f1_to_f3(entity_work, path_node)
            triple_from_f1_to_f10(entity_work, path_node)
            triple_from_f1_to_f31(entity_work, path_node)
            triples_from_f1_to_note(entity_work, path_node)
            triple_from_f1_to_f26(entity_work, path_node)

        def parse_triples_from_honour(entity_honour, path_node):

            def triples_from_honour_to_e55(entity_honour, path_node):

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

                if entity_found is None and (name_subtype is not None or name_type is not None) and name_type != "host":

                    # TODO : Check how often this is the case
                    print("Found a type, but no correspondingly created entity for it")

                if entity_found is not None:

                    create_triple(
                        entity_subj=entity_honour,
                        entity_obj=entity_found,
                        prop=Property.objects.get(name="p2 has type")
                    )

            def triples_from_honour_to_f9(entity_honour, path_node: PathNode):

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if (
                            entity_other.__class__ is F9_Place
                        ):

                            create_triple(
                                entity_subj=entity_honour,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="took place in"),
                                path_node=child_path_node
                            )

            def triples_from_honour_to_e40(entity_honour, path_node: PathNode):

                date = None
                triple = None

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if (
                            entity_other.__class__ is E40_Legal_Body
                        ):

                            triple = create_triple(
                                entity_subj=entity_other,
                                entity_obj=entity_honour,
                                prop=Property.objects.get(name="is organizer of"),
                                path_node=child_path_node
                            )

                if triple is not None:
                    triple.save()

            def triples_from_honour_to_note(entity_honour, path_node: PathNode):

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if (
                            entity_other.__class__ is XMLNote
                            and child_path_node.xml_elem.tag.endswith("note")
                        ):

                            create_triple(
                                entity_subj=entity_honour,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="has note"),
                                path_node=child_path_node
                            )

            def triples_from_honour_to_f3(entity_honour, path_node):

                def check_and_create_triple_to_f3(entity_honour, path_node_other):

                    for entity_other in path_node_other.entities_list:

                        if entity_other.__class__ is F3_Manifestation_Product_Type:

                            create_triple(
                                entity_subj=entity_honour,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="is reported in"),
                                path_node=path_node_other
                            )

                for neighbour_path_node in path_node.path_node_parent.path_node_parent.path_node_children_list:

                    # direct manifestations
                    if (
                        neighbour_path_node.xml_elem.tag.endswith("div")
                        and neighbour_path_node.xml_elem.attrib.get("type") == "berichte"
                    ):

                        for neighbour_child_path_node in neighbour_path_node.path_node_children_list:

                            if neighbour_child_path_node.xml_elem.tag.endswith("listBibl"):

                                for neighbour_child_child_path_node in neighbour_child_path_node.path_node_children_list:

                                    check_and_create_triple_to_f3(entity_honour, neighbour_child_child_path_node)

                            else:

                                check_and_create_triple_to_f3(entity_honour, neighbour_child_path_node)

            triples_from_honour_to_e55(entity_honour, path_node)
            triples_from_honour_to_f9(entity_honour, path_node)
            triples_from_honour_to_e40(entity_honour, path_node)
            triples_from_honour_to_note(entity_honour, path_node)
            triples_from_honour_to_f3(entity_honour, path_node)

        def parse_triples_from_f3_manifestation(entity_manifestation, path_node):

            def triples_from_f3_to_e55(entity_manifestation, path_node):

                name_mediatype = path_node.xml_elem.attrib.get("mediatype")
                name_subtype = path_node.xml_elem.attrib.get("subtype")
                name_type = path_node.xml_elem.attrib.get("type")

                mediatype_found = None
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

                        if (
                            name_mediatype is not None
                            and entity_other.name.lower() == name_mediatype.lower()
                        ):
                            mediatype_found = entity_other

                if entity_found is None and (name_subtype is not None or name_type is not None) and name_type != "host":

                    # TODO : Check how often this is the case
                    print("Found a type, but no correspondingly created entity for it")

                if entity_found is not None:

                    create_triple(
                        entity_subj=entity_manifestation,
                        entity_obj=entity_found,
                        prop=Property.objects.get(name="p2 has type")
                    )

                if mediatype_found is not None:

                    create_triple(
                        entity_subj=entity_manifestation,
                        entity_obj=mediatype_found,
                        prop=Property.objects.get(name="p2 has type")
                    )

            def triples_from_f3_to_f3(entity_manifestation, path_node: PathNode):

                for path_node_child in path_node.path_node_children_list:

                    if (
                        path_node_child.xml_elem.tag.endswith("relatedItem")
                        and path_node_child.xml_elem.attrib.get("type") == "host"
                    ):

                        #for path_node_child_child in path_node_child.path_node_children_list:

                        for entity_other in path_node_child.entities_list:

                            if (
                                entity_other.__class__ is F3_Manifestation_Product_Type
                            ):

                                create_triple(
                                    entity_subj=entity_manifestation,
                                    entity_obj=entity_other,
                                    prop=Property.objects.get(name="has host"),
                                    path_node=path_node_child
                                )

            def triples_from_f3_to_f9(entity_manifestation, path_node: PathNode):

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if (
                            entity_other.__class__ is F9_Place
                        ):

                            create_triple(
                                entity_subj=entity_manifestation,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="was published in"),
                                path_node=child_path_node
                            )

            def triples_from_f3_to_e40(entity_manifestation, path_node: PathNode):

                date = None
                triple = None

                for child_path_node in path_node.path_node_children_list:

                    role = child_path_node.xml_elem.attrib.get("role")
                    if role is None:
                        for child_child_path_node in child_path_node.path_node_children_list:
                            if child_child_path_node.xml_elem.attrib.get("role") is not None:
                                role = child_child_path_node.xml_elem.attrib.get("role")

                    for entity_other in child_path_node.entities_list:

                        if (
                            entity_other.__class__ is E40_Legal_Body
                            and child_path_node.xml_elem.tag.endswith("publisher")
                        ):

                            triple = create_triple(
                                entity_subj=entity_other,
                                entity_obj=entity_manifestation,
                                prop=Property.objects.get(name="is publisher of"),
                                path_node=child_path_node
                            )

                        if (
                            entity_other.__class__ is E40_Legal_Body
                            and (role == "editor"
                            or role == "possessor")
                        ):

                            triple = create_triple(
                                entity_subj=entity_other,
                                entity_obj=entity_manifestation,
                                prop=Property.objects.get(name="is editor of"),
                                path_node=child_path_node
                            )

                        if (
                            entity_other.__class__ is E40_Legal_Body
                            and (role == "author")
                        ):

                            triple = create_triple(
                                entity_subj=entity_other,
                                entity_obj=entity_manifestation,
                                prop=Property.objects.get(name="is author of"),
                                path_node=child_path_node
                            )
                        if (
                            entity_other.__class__ is E40_Legal_Body
                            and (role == "interviewer")
                        ):

                            triple = create_triple(
                                entity_subj=entity_other,
                                entity_obj=entity_manifestation,
                                prop=Property.objects.get(name="is interviewer of"),
                                path_node=child_path_node
                            )

                        if (
                            entity_other.__class__ is E40_Legal_Body
                            and (role == "broadcaster")
                        ):

                            triple = create_triple(
                                entity_subj=entity_other,
                                entity_obj=entity_manifestation,
                                prop=Property.objects.get(name="is broadcaster of"),
                                path_node=child_path_node
                            )

                    for child_child_path_node in child_path_node.path_node_children_list:

                        for entity_other in child_child_path_node.entities_list:

                            if (
                                entity_other.__class__ is E40_Legal_Body
                                and child_child_path_node.xml_elem.tag.endswith("publisher")
                            ):

                                triple = create_triple(
                                    entity_subj=entity_other,
                                    entity_obj=entity_manifestation,
                                    prop=Property.objects.get(name="is publisher of"),
                                    path_node=child_child_path_node
                                )

                            if (
                                entity_other.__class__ is E40_Legal_Body
                                and (child_child_path_node.xml_elem.attrib.get("role") == "editor"
                                or child_child_path_node.xml_elem.attrib.get("role") == "possessor")
                            ):

                                triple = create_triple(
                                    entity_subj=entity_other,
                                    entity_obj=entity_manifestation,
                                    prop=Property.objects.get(name="is editor of"),
                                    path_node=child_child_path_node
                                )
                            if (
                                entity_other.__class__ is E40_Legal_Body
                                and (child_child_path_node.xml_elem.attrib.get("role") == "author")
                            ):

                                triple = create_triple(
                                    entity_subj=entity_other,
                                    entity_obj=entity_manifestation,
                                    prop=Property.objects.get(name="is author of"),
                                    path_node=child_child_path_node
                                )
                            if (
                                entity_other.__class__ is E40_Legal_Body
                                and (child_child_path_node.xml_elem.attrib.get("role") == "interviewer")
                            ):

                                triple = create_triple(
                                    entity_subj=entity_other,
                                    entity_obj=entity_manifestation,
                                    prop=Property.objects.get(name="is interviewer of"),
                                    path_node=child_child_path_node
                                )
                            if (
                            entity_other.__class__ is E40_Legal_Body
                            and (child_child_path_node.xml_elem.attrib.get("role") == "broadcaster")
                            ):

                                triple = create_triple(
                                    entity_subj=entity_other,
                                    entity_obj=entity_manifestation,
                                    prop=Property.objects.get(name="is broadcaster of"),
                                    path_node=child_child_path_node
                                )

                    if (
                        child_path_node.xml_elem.tag.endswith("date")
                        and is_valid_text(child_path_node.xml_elem.text)
                    ):

                        date = child_path_node.xml_elem.text

                    if (
                        child_path_node.xml_elem.tag.endswith("date")
                        and is_valid_text(child_path_node.xml_elem.text)
                    ):

                        date = child_path_node.xml_elem.text

                

                if triple is not None:
                    if date is not None:
                        triple.start_date_written = date
                    triple.save()

            def triples_from_f3_to_note(entity_manifestation, path_node: PathNode):

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if (
                            entity_other.__class__ is XMLNote
                            and child_path_node.xml_elem.tag.endswith("note")
                        ):

                            create_triple(
                                entity_subj=entity_manifestation,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="has note"),
                                path_node=child_path_node
                            )
                if path_node.xml_elem.tag.endswith("ptr"):
                    for path_node_sibling in path_node.path_node_parent.path_node_children_list:
                        for entity_other in path_node_sibling.entities_list:
                            if (
                                entity_other.__class__ is XMLNote
                            ):
                                create_triple(
                                    entity_subj=entity_manifestation,
                                    entity_obj=entity_other,
                                    prop=Property.objects.get(name="has note"),
                                    path_node=path_node_sibling
                                )

            def triples_from_f3_to_f31(entity_manifestation, path_node: PathNode):
                for child_path_node in path_node.path_node_children_list:
                    if (child_path_node.xml_elem.tag.endswith("relatedItem")
                        and child_path_node.xml_elem.attrib.get("type", "") == "recording-event"):
                        for ptr in child_path_node.path_node_children_list:
                            for entity_other in ptr.entities_list:
                                if entity_other.__class__ == F31_Performance:
                                    create_triple(
                                        entity_subj=entity_other,
                                        entity_obj=entity_manifestation,
                                        prop=Property.objects.get(name="has recording artefact")
                                    )



            triples_from_f3_to_e55(entity_manifestation, path_node)
            triples_from_f3_to_f3(entity_manifestation, path_node)
            triples_from_f3_to_f9(entity_manifestation, path_node)
            triples_from_f3_to_e40(entity_manifestation, path_node)
            triples_from_f3_to_note(entity_manifestation, path_node)
            triples_from_f3_to_f31(entity_manifestation, path_node)

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
        
        def parse_triples_from_e40_legal_body(entity_e40, path_node):

            for child in path_node.path_node_children_list:
                if child.xml_elem.tag.endswith("places"):
                    for place in child.entities_list:
                        create_triple(
                            entity_subj=entity_e40,
                            entity_obj=place,
                            prop=Property.objects.get(name="is located in"),
                            path_node=child
                        )

        def parse_triples_from_f10_person(entity_person, path_node: PathNode):

            def triple_from_f10_to_f3(entity_person, path_node: PathNode):

                if path_node.path_node_parent.xml_elem.tag.endswith("bibl"):

                    for entity_other in path_node.path_node_parent.entities_list:

                        if entity_other.__class__ is F3_Manifestation_Product_Type:

                            if path_node.xml_elem.tag.endswith("personGrp"):

                                if (path_node.xml_elem.attrib.get("role") == "editor"):

                                    create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is editor of"),
                                            path_node=path_node
                                        )
                                elif (path_node.xml_elem.attrib.get("role") == "author"):

                                    create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is author of"),
                                            path_node=path_node
                                    )

                                elif (path_node.xml_elem.attrib.get("role") == "redaktion"):

                                    create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is redactor of"),
                                            path_node=path_node
                                    )

                            for child_path_node in path_node.path_node_children_list:

                                if (child_path_node.xml_elem.tag.endswith("persName")):

                                    if (child_path_node.xml_elem.attrib.get("role") == "author"):
                                        
                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is author of"),
                                            path_node = child_path_node
                                        )
                                    elif (child_path_node.xml_elem.attrib.get("role") == "composer"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is composer of"),
                                            path_node = child_path_node
                                        )
                                    elif (child_path_node.xml_elem.attrib.get("role") == "editor"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is editor of"),
                                            path_node = child_path_node
                                        )

                                    elif (child_path_node.xml_elem.attrib.get("role") == "interviewer"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is interviewer of"),
                                            path_node = child_path_node
                                        )

                                    elif (child_path_node.xml_elem.attrib.get("role") == "interviewee"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is interviewee of"),
                                            path_node = child_path_node
                                        )

                                    elif (child_path_node.xml_elem.attrib.get("role") == "translator"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is translator of"),
                                            path_node = child_path_node
                                        )

                                    elif (child_path_node.xml_elem.attrib.get("role") == "voice_actor"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is voice actor of"),
                                            path_node = child_path_node
                                        )

                                    elif (child_path_node.xml_elem.attrib.get("role") == "director"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is director of"),
                                            path_node = child_path_node
                                        )

                                    elif (child_path_node.xml_elem.attrib.get("role") == "redaktion"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is redactor of"),
                                            path_node = child_path_node
                                        )

            def triple_from_f10_to_f21(entity_person, path_node: PathNode):

                if path_node.path_node_parent.xml_elem.tag.endswith("bibl"):

                    for entity_other in path_node.path_node_parent.entities_list:

                        if entity_other.__class__ is F1_Work:
                            for child_path_node in path_node.path_node_children_list:
                                if (
                                    child_path_node.xml_elem.tag.endswith("persName")
                                ):
                                    if (child_path_node.xml_elem.attrib.get("role") == "contributor"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is contributor of"),
                                            path_node=child_path_node
                                        )
                                    elif (child_path_node.xml_elem.attrib.get("role") == "actor"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is actor of"),
                                            path_node=child_path_node
                                        )
                                    elif (child_path_node.xml_elem.attrib.get("role") == "voice_actor"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is voice actor of"),
                                            path_node=child_path_node
                                        )
                                    elif (child_path_node.xml_elem.attrib.get("role") == "director"):

                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is director of"),
                                            path_node=child_path_node
                                        )
                                    else:
                                        create_triple(
                                            entity_subj=entity_person,
                                            entity_obj=entity_other,
                                            prop=Property.objects.get(name="is author of"),
                                            path_node=child_path_node
                                        )


            triple_from_f10_to_f3(entity_person, path_node)
            triple_from_f10_to_f21(entity_person, path_node)


        def parse_triples_from_f21_recording_work(entity_recording_work, path_node: PathNode):

            def triple_from_f21_to_f10(entity_work, path_node):

                for neighbor_path_node in path_node.path_node_parent.path_node_children_list:
                    for child_path_node in neighbor_path_node.path_node_children_list:
                        for child_child_path_node in child_path_node.path_node_children_list:
                            for entity_other in child_child_path_node.entities_list:
                                if entity_other.__class__ == F10_Person:
                                    for child_child_child_path_node in child_child_path_node.path_node_children_list:
                                        if (
                                                child_child_child_path_node.xml_elem.tag.endswith("persName")
                                        ):

                                            if (child_child_child_path_node.xml_elem.attrib.get("role") == "contributor"):

                                                create_triple(
                                                    entity_subj=entity_other,
                                                    entity_obj=entity_work,
                                                    prop=Property.objects.get(name="is contributor of"),
                                                    path_node=child_child_child_path_node
                                                )

                                            elif (child_child_child_path_node.xml_elem.attrib.get("role") == "actor"):

                                                create_triple(
                                                    entity_subj=entity_other,
                                                    entity_obj=entity_work,
                                                    prop=Property.objects.get(name="is actor of"),
                                                    path_node=child_child_child_path_node
                                                )

                                            elif (child_child_child_path_node.xml_elem.attrib.get("role") == "director"):

                                                create_triple(
                                                    entity_subj=entity_other,
                                                    entity_obj=entity_work,
                                                    prop=Property.objects.get(name="is director of"),
                                                    path_node=child_child_child_path_node
                                                )
                    

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
                                            path_node=path_node_neighbour_child_child
                                        )

            def triple_from_f21_to_chapter(entity_recording_work, path_node: PathNode):

                # TODO Barbara und Katharina: relate to chapter
                pass

            triple_from_f21_to_f26(entity_recording_work, path_node)
            triple_from_f21_to_chapter(entity_recording_work, path_node)
            triple_from_f21_to_f10(entity_recording_work, path_node)

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
                                path_node=path_node_child
                            )

                    if (len(path_node_child.entities_list) <= 1 and path_node_child.xml_elem.attrib.get("type") == "institutions") or (path_node_child.xml_elem.tag.endswith("note")):

                        for path_node_child in path_node_child.path_node_children_list:

                            for entity_other in path_node_child.entities_list:

                                if entity_other.__class__ is E40_Legal_Body:

                                    for path_node_child_child in path_node_child.path_node_children_list:

                                        if (path_node_child_child.xml_elem.attrib.get("role") == "organizer"):

                                            create_triple(
                                                entity_obj=entity_performance,
                                                entity_subj=entity_other,
                                                prop=Property.objects.get(name="is organizer of"),
                                                path_node=path_node_child_child
                                            )

                                        if (path_node_child_child.xml_elem.attrib.get("role") == "broadcaster"):

                                            create_triple(
                                                entity_obj=entity_performance,
                                                entity_subj=entity_other,
                                                prop=Property.objects.get(name="is broadcaster of"),
                                                path_node=path_node_child_child
                                            )

                                    create_triple(
                                                entity_subj=entity_performance,
                                                entity_obj=entity_other,
                                                prop=Property.objects.get(name="has been performed at"),
                                                path_node=path_node_child
                                            )

            def triple_from_f31_to_f1(entity_performance, path_node: PathNode):

                for path_node_child in path_node.path_node_children_list:

                    for entity_other in path_node_child.entities_list:

                        if has_class_as_parent(entity_other.__class__, F1_Work):

                            create_triple(
                                entity_obj=entity_performance,
                                entity_subj=entity_other,
                                prop=Property.objects.get(name="has been performed in"),
                                path_node=path_node_child
                            )

                    if len(path_node_child.entities_list) == 0 and path_node_child.xml_elem.attrib.get("type") == "basedOn":
                        
                        for path_node_child in path_node_child.path_node_children_list:

                            for entity_other in path_node_child.entities_list:

                                if has_class_as_parent(entity_other.__class__, F1_Work):

                                    create_triple(
                                        entity_obj=entity_performance,
                                        entity_subj=entity_other,
                                        prop=Property.objects.get(name="has been performed in"),
                                        path_node=path_node_child
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
                                    path_node=path_node_child
                                )

                            elif role == "translator":

                                create_triple(
                                    entity_subj=entity_person,
                                    entity_obj=entity_performance,
                                    prop=Property.objects.get(name="is translator of"),
                                    path_node=path_node_child
                                )

                                #pass # to be ignored, because a translated theatre play needs to have its own work

                            elif role == "composer":

                                create_triple(
                                    entity_subj=entity_person,
                                    entity_obj=entity_performance,
                                    prop=Property.objects.get(name="is composer of"),
                                    path_node=path_node_child
                                )

                            elif role == "singer":

                                create_triple(
                                    entity_subj=entity_person,
                                    entity_obj=entity_performance,
                                    prop=Property.objects.get(name="is singer of"),
                                    path_node=path_node_child
                                )

                            elif role == "musician":

                                create_triple(
                                    entity_subj=entity_person,
                                    entity_obj=entity_performance,
                                    prop=Property.objects.get(name="is musician of"),
                                    path_node=path_node_child
                                )

                            elif role == "musical_direction":

                                create_triple(
                                    entity_subj=entity_person,
                                    entity_obj=entity_performance,
                                    prop=Property.objects.get(name="is musical director of"),
                                    path_node=path_node_child
                                )

                            elif role == "choreographer":

                                create_triple(
                                    entity_subj=entity_person,
                                    entity_obj=entity_performance,
                                    prop=Property.objects.get(name="is choreographer of"),
                                    path_node=path_node_child
                                )

                            else:

                                # TODO : Check how often this is the case
                                print(f"Found unspecified role {role}")

                        else:

                            # TODO : Check how often this is the case
                            print("Found a relation to a person without a role")

            def triples_from_f31_to_note(entity_manifestation, path_node: PathNode):

                for child_path_node in path_node.path_node_children_list:

                    for entity_other in child_path_node.entities_list:

                        if (
                            entity_other.__class__ is XMLNote
                            and child_path_node.xml_elem.tag.endswith("note")
                        ):

                            create_triple(
                                entity_subj=entity_manifestation,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="has note"),
                                path_node=child_path_node
                            )
                if path_node.xml_elem.tag.endswith("ptr"):
                    for path_node_sibling in path_node.path_node_parent.path_node_children_list:
                        for entity_other in path_node_sibling.entities_list:
                            if (
                                entity_other.__class__ is XMLNote
                            ):
                                create_triple(
                                    entity_subj=entity_manifestation,
                                    entity_obj=entity_other,
                                    prop=Property.objects.get(name="has note"),
                                    path_node=path_node_sibling
                                )

            triple_from_f31_to_e40(entity_performance, path_node)
            triple_from_f31_to_f10(entity_performance, path_node)
            triple_from_f31_to_f1(entity_performance, path_node)
            triples_from_f31_to_note(entity_performance, path_node)

        def parse_triples_from_f26_recording(entity_broadcast, path_node: PathNode):

            def triple_from_f26_to_f21(entity_broadcast, path_node: PathNode):

                for path_node_child in path_node.path_node_children_list:

                    for entity_other in path_node_child.entities_list:

                        if (entity_other.__class__ is F21_Recording_Work) or (entity_other.__class__ is F1_Work):

                            create_triple(
                                entity_obj=entity_broadcast,
                                entity_subj=entity_other,
                                prop=Property.objects.get(name="R13 is realised in"),
                                path_node=path_node_child
                            )

                    if len(path_node_child.entities_list) == 0 and path_node_child.xml_elem.attrib.get("type") == "basedOn":
                        
                        for path_node_child in path_node_child.path_node_children_list:

                            for entity_other in path_node_child.entities_list:

                                if entity_other.__class__ is F1_Work:

                                    create_triple(
                                        entity_obj=entity_broadcast,
                                        entity_subj=entity_other,
                                        prop=Property.objects.get(name="R13 is realised in"),
                                        path_node=path_node_child
                                    )
            def triple_from_f26_to_e40(entity_broadcast, path_node: PathNode):

                for path_node_child in path_node.path_node_children_list:

                    for entity_other in path_node_child.entities_list:

                        if entity_other.__class__ is E40_Legal_Body:

                            if path_node_child.xml_elem.attrib.get("type") == "broadcaster":
                                create_triple(
                                    entity_obj=entity_broadcast,
                                    entity_subj=entity_other,
                                    prop=Property.objects.get(name="is broadcaster of"),
                                )
                            elif path_node_child.xml_elem.attrib.get("type") == "institution":
                                for org_name in path_node_child.path_node_children_list:
                                    if org_name.xml_elem.attrib.get("role") == "broadcaster":
                                        create_triple(
                                            entity_obj=entity_broadcast,
                                            entity_subj=entity_other,
                                            prop=Property.objects.get(name="is broadcaster of"),
                                            path_node=org_name
                                        ) 
                                
                            create_triple(
                                entity_subj=entity_broadcast,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="has been performed at"),
                                path_node=path_node_child
                            )                
            def triples_from_f26_to_note(entity_manifestation, path_node: PathNode):

                for child_path_node in path_node.path_node_children_list:
                    for entity_other in child_path_node.entities_list:
                        if (
                            entity_other.__class__ is XMLNote
                            and child_path_node.xml_elem.tag.endswith("note")
                        ):
                            create_triple(
                                entity_subj=entity_manifestation,
                                entity_obj=entity_other,
                                prop=Property.objects.get(name="has note"),
                                path_node=child_path_node
                            )

                if path_node.xml_elem.tag.endswith("ptr"):
                    for path_node_sibling in path_node.path_node_parent.path_node_children_list:
                        for entity_other in path_node_sibling.entities_list:
                            if (
                                entity_other.__class__ is XMLNote
                            ):
                                create_triple(
                                    entity_subj=entity_manifestation,
                                    entity_obj=entity_other,
                                    prop=Property.objects.get(name="has note"),
                                    path_node=path_node_sibling
                                )

                    
            triple_from_f26_to_f21(entity_broadcast, path_node)
            triple_from_f26_to_e40(entity_broadcast, path_node)
            triples_from_f26_to_note(entity_broadcast, path_node)

        def parse_triples_from_e38_image(entity_image, path_node: PathNode):

            path_node_tei = get_uppermost_parent(path_node)
            property_name = "has image"
            if "002_ÜbersetzteWerke" in TreesManager.helper_dict["file_path"]:
                property_name = "has image for translation"

            def triple_from_e38_image_to_f1(entity_image, path_node: PathNode):

                for path_node_text in path_node_tei.path_node_children_list:

                    if path_node_text.xml_elem.tag.endswith("text"):

                        for path_node_body in path_node_text.path_node_children_list:

                            if path_node_body.xml_elem.tag.endswith("body"):

                                for path_node_div in path_node_body.path_node_children_list:

                                    if path_node_div.xml_elem.tag.endswith("div"):

                                        for path_node_bibl in path_node_div.path_node_children_list:

                                            for entity_work in path_node_bibl.entities_list:

                                                if has_class_as_parent(entity_work.__class__, F1_Work) or has_class_as_parent(entity_work.__class__, Honour):

                                                    create_triple(
                                                        entity_subj=entity_work,
                                                        entity_obj=entity_image,
                                                        prop=Property.objects.get(name=property_name),
                                                        path_node=path_node_bibl
                                                    )

                                                break

                                        if path_node_div.xml_elem.attrib.get("type") == "honour":    
                                            for path_node_div_div in path_node_div.path_node_children_list: 
                                                for path_node_bibl in path_node_div_div.path_node_children_list:

                                                    for entity_work in path_node_bibl.entities_list:

                                                        if has_class_as_parent(entity_work.__class__, F1_Work) or has_class_as_parent(entity_work.__class__, Honour):

                                                            create_triple(
                                                                entity_subj=entity_work,
                                                                entity_obj=entity_image,
                                                                prop=Property.objects.get(name=property_name),
                                                                path_node=path_node_bibl
                                                            )

                                                        break

                                        for path_node_div_div in path_node_div.path_node_children_list:

                                            if path_node_div_div.xml_elem.tag.endswith("div") and path_node_div_div.xml_elem.attrib.get("type") == "head_section":

                                                for path_node_bibl in path_node_div_div.path_node_children_list:

                                                    for entity_work in path_node_bibl.entities_list:

                                                        if has_class_as_parent(entity_work.__class__, F1_Work) or has_class_as_parent(entity_work.__class__, Honour):

                                                            create_triple(
                                                                entity_subj=entity_work,
                                                                entity_obj=entity_image,
                                                                prop=Property.objects.get(name=property_name),
                                                                path_node=path_node_bibl
                                                            )

                                                    if path_node_bibl.xml_elem.tag.endswith("head"):
                                                        for path_node_bibl in path_node_bibl.path_node_children_list:

                                                            for entity_work in path_node_bibl.entities_list:

                                                                if has_class_as_parent(entity_work.__class__, F1_Work) or has_class_as_parent(entity_work.__class__, Honour):

                                                                    create_triple(
                                                                        entity_subj=entity_work,
                                                                        entity_obj=entity_image,
                                                                        prop=Property.objects.get(name=property_name),
                                                                        path_node=path_node_bibl
                                                                    )

                                                break

                                        break

                                break

                                break

                        break


            triple_from_e38_image_to_f1(entity_image, path_node)


        def parse_triples_from_chapter(entity_chapter, path_node: PathNode):

            def find_all_inner_f1_entities(path_node):
                path_node_entities = []
                if path_node.xml_elem.tag.endswith("rs"):
                    return path_node_entities
                for entity in path_node.entities_list:
                    if has_class_as_parent(entity.__class__, F1_Work):
                        path_node_entities.append(entity)
                for child in path_node.path_node_children_list:
                    path_node_entities += find_all_inner_f1_entities(child)
                return path_node_entities

            path_node_tei = climb_up(path_node, 5)

            def triple_from_chapter_to_f1(entity_chapter, path_node: PathNode):

                for path_node_text in path_node_tei.path_node_children_list:

                    if path_node_text.xml_elem.tag.endswith("text"):

                        for path_node_body in path_node_text.path_node_children_list:

                            if path_node_body.xml_elem.tag.endswith("body"):

                                for path_node_div in path_node_body.path_node_children_list:

                                    if path_node_div.xml_elem.tag.endswith("div"):

                                        for path_node_div_child in path_node_div.path_node_children_list:

                                            for entity_work in path_node_div_child.entities_list:

                                                if has_class_as_parent(entity_work.__class__, F1_Work):

                                                    create_triple(
                                                        entity_subj=entity_work,
                                                        entity_obj=entity_chapter,
                                                        prop=Property.objects.get(name="is in chapter"),
                                                        path_node=path_node_div_child
                                                    )

                                                if not entity_chapter.chapter_number.startswith("6"):
                                                    break

                                        if entity_chapter.chapter_number.startswith("6"):
                                            for path_node_div_child in path_node_div.path_node_children_list:

                                                if (path_node_div_child.xml_elem.attrib.get("type", "") in ["seklitSubsection", "stagingSeklit"]
                                                    or path_node_div_child.xml_elem.tag.endswith("list")):

                                                    for f1 in find_all_inner_f1_entities(path_node_div_child):
                                                        create_triple(
                                                                        entity_subj=f1,
                                                                        entity_obj=entity_chapter,
                                                                        prop=Property.objects.get(name="is in chapter")
                                                                    )
                                        if entity_chapter.chapter_number.startswith("7"):
                                            for path_node_div_child in path_node_div.path_node_children_list:

                                                if path_node_div_child.xml_elem.attrib.get("type", "") in ["head_section"]:

                                                    for f1 in find_all_inner_f1_entities(path_node_div_child):
                                                        create_triple(
                                                                        entity_subj=f1,
                                                                        entity_obj=entity_chapter,
                                                                        prop=Property.objects.get(name="is in chapter"),
                                                                    )

                                        break

                                break

                        break
                
                teiHeader = path_node_tei.path_node_children_list[0]
                textClass = teiHeader.path_node_children_list[1].path_node_children_list[0]
                for keywords in textClass.path_node_children_list:
                    if keywords.xml_elem.attrib.get("ana") == "about":
                        for term in keywords.path_node_children_list:
                            for rs in term.path_node_children_list:
                                for entity_other in rs.entities_list:
                                    if entity_other != entity_chapter and has_class_as_parent(entity_other.__class__, F1_Work):
                                        if entity_other is None or entity_chapter is None:
                                            print("One of the two entities is none, this shouldn't happen")
                                        else:
                                            create_triple(entity_obj=entity_other, entity_subj=entity_chapter,prop=Property.objects.get(name="is about"))
                        
            def triple_from_chapter_to_honour(entity_chapter, path_node: PathNode):

                for path_node_text in path_node_tei.path_node_children_list:

                    if path_node_text.xml_elem.tag.endswith("text"):

                        for path_node_body in path_node_text.path_node_children_list:

                            if path_node_body.xml_elem.tag.endswith("body"):

                                for path_node_div in path_node_body.path_node_children_list:

                                    if path_node_div.xml_elem.tag.endswith("div"):

                                        for path_node_div_child in path_node_div.path_node_children_list:

                                            for path_node_event in path_node_div_child.path_node_children_list:

                                                for entity_work in path_node_event.entities_list:

                                                    if has_class_as_parent(entity_work.__class__, Honour):

                                                        create_triple(
                                                            entity_subj=entity_work,
                                                            entity_obj=entity_chapter,
                                                            prop=Property.objects.get(name="is in chapter"),
                                                            path_node=path_node_event
                                                        )

                                                    if not entity_chapter.chapter_number.startswith("6"):
                                                        break

                                           
                                        break

                                break

                        break


            def triple_from_chapter_to_chapter(entity_chapter: Chapter, path_node: PathNode):

                chapter_number_parent = ".".join(entity_chapter.chapter_number.split(".")[:-1])

                if chapter_number_parent != "":

                    
                    try:
                        entity_chapter_parent = Chapter.objects.get(chapter_number=chapter_number_parent)
                        create_triple(
                            entity_subj=entity_chapter,
                            entity_obj=entity_chapter_parent,
                            prop=Property.objects.get(name="is sub chapter of")
                        )
                    except Chapter.DoesNotExist:
                        pass

            triple_from_chapter_to_f1(entity_chapter, path_node)
            triple_from_chapter_to_honour(entity_chapter, path_node)
            triple_from_chapter_to_chapter(entity_chapter, path_node)
            
        def parse_triples_from_keyword(entity_keyword, path_node: PathNode):

            path_node_tei = get_uppermost_parent(path_node)

            def triple_from_keyword_to_f1(entity_keyword, path_node: PathNode):

                for path_node_text in path_node_tei.path_node_children_list:

                    if path_node_text.xml_elem.tag.endswith("text"):

                        for path_node_body in path_node_text.path_node_children_list:

                            if path_node_body.xml_elem.tag.endswith("body"):

                                for path_node_div in path_node_body.path_node_children_list:

                                    if path_node_div.xml_elem.tag.endswith("div"):

                                        for path_node_bibl in path_node_div.path_node_children_list:

                                            for entity_work in path_node_bibl.entities_list:

                                                if has_class_as_parent(entity_work.__class__, F1_Work) or has_class_as_parent(entity_work.__class__, Honour):

                                                    create_triple(
                                                        entity_subj=entity_work,
                                                        entity_obj=entity_keyword,
                                                        prop=Property.objects.get(name="has keyword")
                                                    )

                                                break

                                        if path_node_div.xml_elem.attrib.get("type") == "honour":    
                                            for path_node_div_div in path_node_div.path_node_children_list: 
                                                for path_node_bibl in path_node_div_div.path_node_children_list:

                                                    for entity_work in path_node_bibl.entities_list:

                                                        if has_class_as_parent(entity_work.__class__, F1_Work) or has_class_as_parent(entity_work.__class__, Honour):

                                                            create_triple(
                                                                entity_subj=entity_work,
                                                                entity_obj=entity_keyword,
                                                                prop=Property.objects.get(name="has keyword"),
                                                            )

                                                        break

                                        for path_node_div_div in path_node_div.path_node_children_list:

                                            if path_node_div_div.xml_elem.tag.endswith("div") and path_node_div_div.xml_elem.attrib.get("type") == "head_section":

                                                for path_node_bibl in path_node_div_div.path_node_children_list:

                                                    for entity_work in path_node_bibl.entities_list:

                                                        if has_class_as_parent(entity_work.__class__, F1_Work) or has_class_as_parent(entity_work.__class__, Honour):

                                                            create_triple(
                                                                entity_subj=entity_work,
                                                                entity_obj=entity_keyword,
                                                                prop=Property.objects.get(name="has keyword"),
                                                            )

                                                    if path_node_bibl.xml_elem.tag.endswith("head"):
                                                        for path_node_bibl in path_node_bibl.path_node_children_list:

                                                            for entity_work in path_node_bibl.entities_list:

                                                                if has_class_as_parent(entity_work.__class__, F1_Work) or has_class_as_parent(entity_work.__class__, Honour):

                                                                    create_triple(
                                                                        entity_subj=entity_work,
                                                                        entity_obj=entity_keyword,
                                                                        prop=Property.objects.get(name="has keyword"),
                                                                    )

                                                break

                                        break

                                break

                                break

                        break


            triple_from_keyword_to_f1(entity_keyword, path_node)


        def parse_triples_from_xml_file(entity_xml_file, path_node: PathNode):

            def triple_to_all(entity_xml_file, path_node_current: PathNode):

                for entity_other in path_node_current.entities_list:

                    if entity_other is None:
                        continue

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
                    elif (
                            path_node_current.path_node_parent is not None
                            and path_node_current.path_node_parent.xml_elem.tag.endswith("div")
                            and path_node_current.path_node_parent.xml_elem.attrib.get("type") == "head_section"
                            and path_node_current.path_node_parent.path_node_parent.xml_elem.tag.endswith("div")
                            and path_node_current.path_node_parent.path_node_parent.xml_elem.attrib.get("type") in ["honour", "prize"]
                            and path_node_current.path_node_parent.path_node_parent.path_node_parent.xml_elem.tag.endswith("body")
                            and path_node_current.path_node_parent.path_node_parent.path_node_parent.path_node_parent.xml_elem.tag.endswith("text")
                    ):

                        create_triple(
                            entity_subj=entity_other,
                            entity_obj=entity_xml_file,
                            prop=Property.objects.get(name="was defined primarily in"),
                        )
                    elif (
                            path_node_current.path_node_parent is not None
                            and path_node_current.path_node_parent.xml_elem.tag.endswith("head")
                            and path_node_current.path_node_parent.path_node_parent.xml_elem.tag.endswith("div")
                            and path_node_current.path_node_parent.path_node_parent.xml_elem.attrib.get("type") == "head_section"
                            and path_node_current.path_node_parent.path_node_parent.path_node_parent.xml_elem.tag.endswith("div")
                            and path_node_current.path_node_parent.path_node_parent.path_node_parent.xml_elem.attrib.get("type") == "entry"
                            and path_node_current.path_node_parent.path_node_parent.path_node_parent.path_node_parent.xml_elem.tag.endswith("body")
                            and path_node_current.path_node_parent.path_node_parent.path_node_parent.path_node_parent.path_node_parent.xml_elem.tag.endswith("text")
                            and (entity_other.__class__ == F1_Work or entity_other.__class__ == F21_Recording_Work)
                    ):

                        create_triple(
                            entity_subj=entity_other,
                            entity_obj=entity_xml_file,
                            prop=Property.objects.get(name="was defined primarily in"),
                        )

                for path_node_child in path_node_current.path_node_children_list:

                    triple_to_all(entity_xml_file, path_node_child)


            triple_to_all(entity_xml_file, path_node)


        def main_parse_for_triples(path_node):

            for entity in path_node.entities_list:

                if entity.__class__ is E55_Type:

                    parse_triples_from_e55_manifestation(entity, path_node)

                elif entity.__class__ is E40_Legal_Body:

                    parse_triples_from_e40_legal_body(entity, path_node)

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

                elif entity.__class__ is F26_Recording:

                    parse_triples_from_f26_recording(entity, path_node)

                elif entity.__class__ is Chapter:

                    parse_triples_from_chapter(entity, path_node)

                elif entity.__class__ is Xml_File:

                    parse_triples_from_xml_file(entity, path_node)

                elif entity.__class__ is Keyword:

                    parse_triples_from_keyword(entity, path_node)

                elif entity.__class__ is Honour:

                    parse_triples_from_honour(entity, path_node)

                elif entity.__class__ is E38_Image:

                    parse_triples_from_e38_image(entity, path_node)

        main_parse_for_triples(path_node)


def parse_xml_as_entity(xml_file_path):
    # Temporary helper method to parse the xml_file path to create an entity representing the xml file
    # for help in curation

    db_result = Xml_File.objects.get_or_create(file_path=xml_file_path)

    if db_result[1] is False and False: #remove and False!!!

        raise Exception("XML file already parsed.")

    else:

        xml_ent = db_result[0]

        name = xml_file_path.split("/")[-1]

        with open(xml_file_path, "r", encoding="UTF-8") as f:

            file_content = f.read()

        xml_ent.name = name
        if len(file_content) < 4000000:
            xml_ent.file_content = file_content
        xml_ent.save()

    return db_result[0]


def run(*args, **options):
    # TODO RDF: delete all model instances

    def reset_all():

        print("RootObject.objects.all().delete()")
        print(RootObject.objects.all().delete())

        print("construct_properties")
        construct_properties()


    def get_flat_file_list(folder):

        list_current = []

        for f in listdir(folder):

            path = folder + "/" + f

            if isfile(path) and f.endswith(".xml"):

                list_current.append(path)

            elif isdir(path):

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


        def main_crawl_xml_list(xml_file_list):

            trees_manager = TreesManager

            for xml_file_path in xml_file_list:

                print(f"\nParsing {xml_file_path}")

                try:

                    tree = ET.parse(xml_file_path)

                except xml.etree.ElementTree.ParseError as e:
                    print(e)

                    print(f"Parse error in file {xml_file_path}")

                else:

                    xml_entity = parse_xml_as_entity(xml_file_path)

                    path_node_root = PathNode(tree.getroot(), None)
                    path_node_root.entities_list.append(xml_entity)

                    current_type = None

                    if "005_TextefürHörspiele" in xml_file_path:

                        current_type = "005_TextefürHörspiele"

                    elif "006_DrehbücherundTextefürFilme" in xml_file_path:

                        current_type = "006_DrehbücherundTextefürFilme"

                    elif "007_Kompositionen" in xml_file_path:

                        current_type = "007_Kompositionen"

                    # elif "009_LibrettiOper" in xml_file_path:

                    #     current_type = "009_LibrettiOper"


                    # elif "013_TextefürInstallationenundProjektionenFotoarbeiten" in xml_file_path:

                    #     current_type = "013_TextefürInstallationenundProjektionenFotoarbeiten"

                    elif "broadcast_index" in xml_file_path:

                        current_type = "broadcast_index"
                    
                    elif "0006_Sekundärliterat" in xml_file_path:

                        current_type = "seklit"

                    elif "0004_Bearbeitungenvo/0003_Hörspiele" in xml_file_path:

                        current_type = "005_TextefürHörspiele"

                    else:

                        current_type = "work"

                    trees_manager.helper_dict["current_type"] = current_type
                    trees_manager.helper_dict["file_path"] = xml_file_path

                    path_node_root = crawl_xml_tree_for_entities(path_node_root, trees_manager)
                    crawl_xml_tree_for_triples(path_node_root, trees_manager)

        main_crawl_xml_list(xml_file_list)


    def main_run():

        if "RESET" in os.environ and os.environ.get("RESET") == "true":
            reset_all()
            print("Reset all")

        xml_file_list = []

        if "FILES" in os.environ:
            for file_string in os.environ.get("FILES").split(" "):
                xml_file_list.append(file_string)
            print("Full file list: ", xml_file_list)

        if "DIRECTORIES" in os.environ:
            for directory_string in os.environ.get("DIRECTORIES").split(" "):
                xml_file_list.extend(get_flat_file_list(directory_string))
            print("Full file list: ", xml_file_list)

        if len(xml_file_list) == 0:
            print("No files nor directories in env found")
            xml_file_list.extend(get_flat_file_list("./manuelle-korrektur/korrigiert/entities"))
            work_xml_idx = next(i for i,file in enumerate(xml_file_list) if '/work_index.xml' in file)
            xml_file_list.append(xml_file_list.pop(work_xml_idx))
            first_files = ["/institution_index.xml", "/places_index.xml", "/venues_index.xml", "/person_index.xml"]
            for filename in first_files:
                xml_idx = next(i for i,file in enumerate(xml_file_list) if filename in file)
                xml_file_list.insert(0, xml_file_list.pop(xml_idx))
            xml_file_list.extend(get_flat_file_list("./manuelle-korrektur/korrigiert/bd1/001_Werke"))
            xml_file_list.extend(get_flat_file_list("./manuelle-korrektur/korrigiert/bd1/002_ÜbersetzteWerke"))
            xml_file_list.extend(get_flat_file_list("./manuelle-korrektur/korrigiert/bd1/003_Interviews"))
            xml_file_list.extend(get_flat_file_list("./manuelle-korrektur/korrigiert/bd2"))
            


        crawl_xml_list(xml_file_list)

        generate_genre()
        generate_xml_dumps()
        generate_short()
        import_index_in_chapter()
        assign_default_manifestation()
        generate_publisher_relations_for_journals()
        populate_indexes()
        

    main_run()
