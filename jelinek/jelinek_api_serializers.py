from collections import OrderedDict
from datetime import datetime
from operator import itemgetter
from apis_core.apis_relations.models import TempTriple, Triple
from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from apis_ontology.models import *

serializers_cache = {}
serializers_cache_patched = {}

def remove_null_empty_from_dict(d):
    if isinstance(d, dict):
        new_d = {}
        for k, v in d.items():
            if v is not None and v != [] and v != {} and not isinstance(v, dict) and not isinstance(v, list):
                new_d[k] = v
            elif isinstance(v, dict):
                new_d[k] = remove_null_empty_from_dict(v)
            elif isinstance(v, list) and len(v) > 0:
                new_d[k] = remove_null_empty_from_dict(v)
    elif isinstance(d, list):
        new_d = []
        for v in d:
            if v is not None and v != [] and v != {} and not isinstance(v, dict) and not isinstance(v, list):
                new_d.append(v)
            elif isinstance(v, dict):
                new_d.append(remove_null_empty_from_dict(v))
            elif isinstance(v, list):
                new_d.append(remove_null_empty_from_dict(v))
    return new_d
    


def add_type(self, obj):
    return obj.__class__.__name__


def create_serializer(model):
    dict_meta = {
        "model": model,
        "exclude": [
            "source",
            "references",
            "notes",
            "review",
        ],
        "depth": 3,
    }
    if model.__name__ == "Xml_File":
        dict_meta["exclude"].append("file_content")
    metaclass = type(
        f"{model.__name__}MetaClass",
        (),
        dict_meta,
    )
    dict_class = {
        "type": serializers.SerializerMethodField(method_name="add_type"),
        "add_type": add_type,
        "Meta": metaclass,
    }
    serializer_class = type(
        f"{model.__name__}Serializer", (serializers.ModelSerializer,), dict_class
    )
    serializers_cache[model.__name__] = serializer_class

    return serializer_class


def patch_serializer(model):
    serializer = serializers_cache.get(model.__name__, create_serializer(model))

    dict_class = {
        "triple_set_from_obj": TripleSerializerFromObj(source="filtered_triples_from_obj", many=True, read_only=True),
        "triple_set_from_subj": TripleSerializerFromSubj(source="filtered_triples_from_subj", many=True, read_only=True),
        "has_children": serializers.SerializerMethodField(method_name="add_has_children"),
        
    }

    def add_has_children(self, obj):
       c = obj.triple_set_from_obj.filter(prop__name="has host").count()
       return c

    serializer_class = type(
        f"{model.__name__}SerializerPatched", (serializer,), dict_class
    )
    serializer_class.add_has_children = add_has_children
    serializers_cache_patched[model.__name__] = serializer_class
    return serializer_class


class TripleSerializer(serializers.ModelSerializer):
    property = serializers.CharField(source="prop.name")
    index_in_chapter = serializers.SerializerMethodField(method_name="get_index_in_chapter")
    rendition_hidden = serializers.SerializerMethodField(method_name="get_rendition_hidden")

    class Meta:
        model = Triple
        exclude = [
            "subj",
            "obj",
            "prop",
        ]

    def get_index_in_chapter(self, obj):
        if hasattr(obj.temptriple, "inchaptertriple"):
            if obj.temptriple.inchaptertriple.index_in_chapter is not None:
                return obj.temptriple.inchaptertriple.index_in_chapter
            else:
                if hasattr(obj.subj, "f1_work"):
                    return obj.subj.f1_work.index_in_chapter
                elif hasattr(obj.subj, "honour"):
                    return obj.subj.honour.index_in_chapter
                else:
                    return None
        else:
            return None
        
    def get_rendition_hidden(self, obj):
        if hasattr(obj.temptriple, "renditiontriple"):
            if obj.temptriple.renditiontriple.rendition_hidden is not None:
                return obj.temptriple.renditiontriple.rendition_hidden
        else:
            return False


class TripleSerializerFromObj(TripleSerializer):
    related_entity = serializers.SerializerMethodField(method_name="add_related_entity")

    def add_related_entity(self, obj):
        serializer = None
        if obj.subj.__class__ in [F1_Work, Honour, F17_Aggregation_Work, F20_Performance_Work, F21_Recording_Work]:
            serializer = F1WorkSerializer
        else:
            serializer = serializers_cache.get(
                obj.subj.__class__.__name__, create_serializer(obj.subj.__class__)
            )
        return serializer(obj.subj).data


class TripleSerializerFromSubj(TripleSerializer):
    related_entity = serializers.SerializerMethodField(method_name="add_related_entity")

    def add_related_entity(self, obj):
        if obj.prop.name == "has host": 
            serializer = serializers_cache_patched.get(
                obj.obj.__class__.__name__, patch_serializer(obj.obj.__class__)
            )
        else:
            serializer = serializers_cache.get(
                obj.obj.__class__.__name__, create_serializer(obj.obj.__class__)
            )
        return serializer(obj.obj).data
    
class SimpleTripleSerializerFromSubj(TripleSerializer):
    related_entity = serializers.SerializerMethodField(method_name="add_related_entity")

    def add_related_entity(self, obj):
        serializer = serializers_cache.get(
            obj.obj.__class__.__name__, create_serializer(obj.obj.__class__)
        )
        return serializer(obj.obj).data

class IncludeImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_for_translation = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        qs = [t.obj for t in obj.triple_set_from_subj.filter(prop__name="has image")]
        if len(qs) > 0:
            serializer = serializers_cache.get(
                qs[0].__class__.__name__, create_serializer(qs[0].__class__)
            )
            return serializer(qs[0]).data
        else:
            return None
    def get_image_for_translation(self, obj):
        qs = [t.obj for t in obj.triple_set_from_subj.filter(prop__name="has image for translation")]
        if len(qs) > 0:
            serializer = serializers_cache.get(
                qs[0].__class__.__name__, create_serializer(qs[0].__class__)
            )
            return serializer(qs[0]).data
        else:
            return None
        
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return remove_null_empty_from_dict(ret)      
        
class F1WorkSerializer(IncludeImageSerializer):
    class Meta:
        model = F1_Work
        exclude = [
            "source",
            "status",
            "references",
            "notes",
            "review",
            "text",
            "collection"
        ]
        depth = 1
class HonourSerializer(IncludeImageSerializer):
    class Meta:
        model = Honour
        exclude = [
            "source",
            "status",
            "references",
            "notes",
            "review",
            "text",
            "collection"
        ]
        depth = 1

class F3ManifestationProductTypeSerializer(serializers.ModelSerializer):
    """
    Custom serializer for F3ManifestationProductType
    """

    triple_set_from_obj = TripleSerializerFromObj(many=True, read_only=True)
    triple_set_from_subj = TripleSerializerFromSubj(source="filtered_triples_from_subj", many=True, read_only=True)
    has_children = serializers.SerializerMethodField(method_name="add_has_children")
    # triple_set_from_obj = serializers.SerializerMethodField(
    #     method_name="add_triple_set_from"
    # )

    class Meta:
        model = F3_Manifestation_Product_Type
        exclude = [
            "source",
            "status",
            "references",
            "notes",
            "review",
            "vector_column_e1_set"
        ]
        depth = 3

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return remove_null_empty_from_dict(ret)
    
    def add_has_children(self, obj):
       c = obj.triple_set_from_obj.filter(prop__name="has host").count()
       return c
    # def add_triple_set_from(self, obj):
    #     return obj.get_triple_set()

class F31PerformanceSerializer(serializers.ModelSerializer):
    """
    Custom serializer for F31Performance
    """

    triple_set_from_obj = TripleSerializerFromObj(many=True, read_only=True)
    triple_set_from_subj = TripleSerializerFromSubj(source="filtered_triples_from_subj", many=True, read_only=True)
    # triple_set_from_obj = serializers.SerializerMethodField(
    #     method_name="add_triple_set_from"
    # )

    class Meta:
        model = F31_Performance
        exclude = [
            "source",
            "status",
            "references",
            "notes",
            "review",
            "vector_column_e1_set"
        ]
        depth = 3

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return remove_null_empty_from_dict(ret)
    

class WorkForChapterSerializer(serializers.ModelSerializer):
    """
    Custom serializer to load work for chapter
    """
    triple_set_from_obj = serializers.SerializerMethodField()
    class Meta:
        model = Chapter
        fields = [
            "id", 
            "name", 
            "triple_set_from_obj"
        ]
        depth = 2

    def get_triple_set_from_obj(self, obj):
        qs = obj.triple_set_from_obj.filter(prop__name="is in chapter")
        serializer = TripleSerializerFromObj(instance=qs, many=True, read_only=True)
        return serializer.data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return remove_null_empty_from_dict(ret)

class RelatedWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = F1_Work
        fields = [
            "id",
            "name",
            "genre"
        ]   
class RelatedHonourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Honour
        fields = [
            "id",
            "name"
        ]   

class SearchSerializer(serializers.ModelSerializer):
    """
    Custom search serializer
    """
    # triple_set_from_obj = TripleSerializerFromObj(many=True, read_only=True)
    # triple_set_from_subj = SimpleTripleSerializerFromSubj(many=True, read_only=True)
    short = serializers.SerializerMethodField()
    genre = serializers.SerializerMethodField()
    related_work = serializers.SerializerMethodField()
    self_contenttype = serializers.SerializerMethodField()
    koha_id = serializers.SerializerMethodField()
    text_language = serializers.SerializerMethodField()
    
    class Meta:
        
        model = E1_Crm_Entity
        fields = (
            "name",
            "id",
            "entity_id",
            "self_contenttype",
            "start_date_written",
            "start_date",
            "short",
            "genre",
            "koha_id",
            "text_language",
            "related_work",
        )
        depth=1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.f1_mapping = {}

    def get_self_contenttype(self, obj):
        return obj.self_contenttype.id

    def get_subclass_of_obj(self, obj, model):
        if hasattr(obj, model):
            return getattr(obj, model)
        elif hasattr(obj, str.lower(model)):
            return getattr(obj, str.lower(model))
        
    def get_f1_from_mapping(self, obj):
        if obj.id in self.f1_mapping:
            return self.f1_mapping.get(obj.id)
        else:
            result = self.get_f1(obj)
            self.f1_mapping[obj.id] = result
            return result
        
    def get_f1(self, obj):
        work_instances_match = lambda subj: True
        if hasattr(obj, "related_work"):
            return [s.subj for s in obj.related_work], False
        if self.context.get("f1_only", False) and self.context.get("work_instances", None) is not None and len(self.context.get("work_instances", [])) > 0:
            work_instances_match = lambda subj: any(subj for work in self.context.get("work_instances", None) if work.id == subj.id)
        if str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F3_Manifestation_Product_Type).model):
            triples = self.context.get("related_work_triple_instances", obj.triple_set_from_obj.all())
            related_f1 = [t for t in triples if t.obj.id==obj.id and work_instances_match(t.subj)]
            if len(related_f1) >= 1:
                if any(r.prop.name in ["is expressed in", "is reported in"] for r in related_f1):
                    return [self.get_subclass_of_obj(s.subj, s.subj.self_contenttype.model) for s in related_f1], False
                elif any(r.prop.name in ["is original for translation"] for r in related_f1):
                    return [self.get_subclass_of_obj(s.subj, s.subj.self_contenttype.model) for s in related_f1], True
            else:
                f3_to_host_work = self.context.get("f3_to_host_work", {})
                related_f1 = f3_to_host_work.get(obj.id, [])
                if len(related_f1) >= 1:
                    if any(r.prop.name in ["is expressed in", "is reported in"] for r in related_f1):
                        return [self.get_subclass_of_obj(s.subj, s.subj.self_contenttype.model) for s in related_f1], False
                    elif any(r.prop.name in ["is original for translation"] for r in related_f1):
                        return [self.get_subclass_of_obj(s.subj, s.subj.self_contenttype.model) for s in related_f1], True
                else:
                    related_f3 = [t.subj for t in obj.triple_set_from_obj.filter(Q(prop__name="has host"))]
                    if len(related_f3) >= 1:
                        related_f1 = [t for f3 in related_f3 for t in f3.triple_set_from_obj.all() if t.prop.name in ["is expressed in", "is reported in"] and work_instances_match(t.subj)]
                        if len(related_f1) >= 1:
                            return [s.subj for s in related_f1], False
                        else:
                            # related_f1 = obj.triple_set_from_obj.filter(Q(prop__name="is original for translation") & work_instances_match)
                            related_f1 =[t for f3 in related_f3 for t in f3.triple_set_from_obj.all() if t.prop.name=="is original for translation" and work_instances_match(t.subj)]
                            if len(related_f1) >= 1:
                                return [s.subj for s in related_f1], True
                    
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F31_Performance).model):
            triples = self.context.get("related_work_triple_instances", obj.triple_set_from_obj.all())
            related_f1 = [t for t in triples if t.obj.id==obj.id and work_instances_match(t.subj)]
            if len(related_f1) >= 1:
                return [self.get_subclass_of_obj(s.subj, s.subj.self_contenttype.model) for s in related_f1], False
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(Honour).model):
            return [obj], False
        elif hasattr(obj, ContentType.objects.get_for_model(F1_Work).model):
            return [obj], False
        return None, False
    
    def get_related_work(self, obj):
        f1 = self.get_f1_from_mapping(obj)[0]
        if f1 is not None and f1[0].id != obj.id:
            if str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(Honour).model):
                serializer = RelatedHonourSerializer
            else:
                serializer = RelatedWorkSerializer
            return serializer(f1, many=True).data
        else:
            return None   
        
    def get_short(self, obj):
        res = ""
        if str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F3_Manifestation_Product_Type).model):
            res= self.get_subclass_of_obj(obj, obj.self_contenttype.model).short
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F31_Performance).model):
            res= self.get_subclass_of_obj(obj, obj.self_contenttype.model).short
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(Honour).model):
            res= self.get_subclass_of_obj(obj, obj.self_contenttype.model).short
        elif hasattr(obj, ContentType.objects.get_for_model(F1_Work).model):
            res= self.get_subclass_of_obj(obj, ContentType.objects.get_for_model(F1_Work).model).short
        return res
        
    def get_koha_id(self, obj):
        if str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F3_Manifestation_Product_Type).model):
            return self.get_subclass_of_obj(obj, obj.self_contenttype.model).koha_id
        else:
            return None
        
    def get_text_language(self, obj):
        if str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F3_Manifestation_Product_Type).model):
            return self.get_subclass_of_obj(obj, obj.self_contenttype.model).text_language
        else:
            return None
        
    def get_genre(self, obj):
        if hasattr(obj, "genre"):
            return obj.genre
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F3_Manifestation_Product_Type).model):
            f1_list, is_translation = self.get_f1_from_mapping(obj)
            if f1_list is not None:
                unified_genre = ", ".join(list(set([f1.genre for f1 in f1_list if hasattr(f1, "genre") and f1.genre is not None])))
            else:
                unified_genre = None
            if is_translation:
                if any(f1 for f1 in f1_list if self.get_subclass_of_obj(f1, f1.self_contenttype.model).genre in ["Lyrik", "Romane", "Kurzprosa", "Theatertexte", "Texte für Hörspiele", "Drehbücher und Texte für Filme", "Libretti"]):
                    return "Übersetzte Werke"
                else:
                    return unified_genre
            if f1_list is not None and len(f1_list) > 0:
                if str.lower(f1_list[0].self_contenttype.model) == str.lower(ContentType.objects.get_for_model(Honour).model):
                    return "Würdigungen"
                else:
                    return unified_genre
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F31_Performance).model):
            f1_list = self.get_f1_from_mapping(obj)[0]
            if f1_list is not None:
                unified_genre = ", ".join(list(set([f1.genre for f1 in f1_list if hasattr(f1, "genre") and f1.genre is not None])))
            else:
                unified_genre = None
            if f1_list is not None:
                return unified_genre
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(Honour).model):
            return "Würdigungen"
        elif hasattr(obj, ContentType.objects.get_for_model(F1_Work).model):
            return self.get_subclass_of_obj(obj, ContentType.objects.get_for_model(F1_Work).model).genre
        return None
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return remove_null_empty_from_dict(ret)
    
class SearchSerializerWork(serializers.Serializer):
    id = serializers.IntegerField(source="pk")
    name = serializers.CharField()
    genre = serializers.CharField()
    entity_id = serializers.CharField()

class SearchSerializerResult(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.IntegerField()
    entity_id = serializers.CharField(required=False)
    self_contenttype_id = serializers.IntegerField(required=False)
    start_date_written = serializers.CharField(required=False)
    start_date = serializers.DateField(required=False)
    short = serializers.CharField(required=False)
    koha_id = serializers.CharField(required=False)
    genre = serializers.CharField(required=False)
    text_language = serializers.CharField(required=False)
    related_work = SearchSerializerWork(many=True, required=False)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return remove_null_empty_from_dict(ret)

class SearchSerializerFacetsDetail(serializers.Serializer):   
    name = serializers.CharField()
    search_by = serializers.CharField()
    count = serializers.IntegerField()

class SearchSerializerFacets(serializers.Serializer):
    person = SearchSerializerFacetsDetail(many=True)
    personRoles = SearchSerializerFacetsDetail(many=True)
    institution = SearchSerializerFacetsDetail(many=True)
    institutionRoles = SearchSerializerFacetsDetail(many=True)
    genre = SearchSerializerFacetsDetail(many=True)
    keywords = SearchSerializerFacetsDetail(many=True)
    place = SearchSerializerFacetsDetail(many=True)
    country = SearchSerializerFacetsDetail(many=True)
    mediatype = SearchSerializerFacetsDetail(many=True)
    date = SearchSerializerFacetsDetail(many=True)
    language = SearchSerializerFacetsDetail(many=True)
    publishers = SearchSerializerFacetsDetail(many=True)
        
    
class SearchSerializer2(serializers.Serializer):
    count = serializers.IntegerField()
    facets = SearchSerializerFacets()
    results = SearchSerializerResult(many=True)

    def __init__(self, instance=None, data=..., **kwargs):
        res = {
            "count": instance.count(), 
            "facets": {
                "person": {}, 
                "personRoles": {}, 
                "institution": {}, 
                "institutionRoles": {}, 
                "genre": {}, 
                "keywords": {}, 
                "place": {}, 
                "country": {},
                "mediatype": {},
                "date": {},
                "language": {},
                "publishers": {},
            }, 
            "results": instance}
        subqueries_to_facet_mapping = {
            "related_persons": "person",
            "related_person_roles": "personRoles",
            "related_institutions": "institution",
            "related_institution_roles": "institutionRoles",
            "related_keywords": "keywords",
            "related_places": "place",
            "related_countries": "country",
            "related_mediatypes": "mediatype"
        }
        props_to_facet_mapping = {
            "genre": "genre",
            "start_date": "date",
            "text_language": "language"
        }
        id_to_name_mapping = {}
        for inst in instance:
            for field in subqueries_to_facet_mapping:
                if hasattr(inst, field):
                    for val in getattr(inst, field):
                        if isinstance(val, dict):
                            id_to_name_mapping[val["entity_id"]] = val["name"]
                            type = val.get("type", "")
                            val = val["entity_id"]
                         
                        if val not in res["facets"][subqueries_to_facet_mapping[field]]:
                            res["facets"][subqueries_to_facet_mapping[field]][val] = 0
                        res["facets"][subqueries_to_facet_mapping[field]][val] += 1

                        if field == "related_institutions" and type == "publisher":
                            if val not in res["facets"]["publishers"]:
                                res["facets"]["publishers"][val] = 0
                            res["facets"]["publishers"][val] += 1

            for field in props_to_facet_mapping:
                if hasattr(inst, field) and getattr(inst, field) is not None:
                    val = getattr(inst, field)
                    if isinstance(val, dict):
                        id_to_name_mapping[val["entity_id"]] = val["name"]
                        val = val["entity_id"]
                    if val not in res["facets"][props_to_facet_mapping[field]]:
                        res["facets"][props_to_facet_mapping[field]][val] = 0
                    res["facets"][props_to_facet_mapping[field]][val] += 1

        for field in subqueries_to_facet_mapping:   
            final = []
            for k, v in res["facets"][subqueries_to_facet_mapping[field]].items():
                final.append({"search_by": k, "name": id_to_name_mapping.get(k, k), "count": v})
            res["facets"][subqueries_to_facet_mapping[field]] = sorted(final, key=lambda k: k["count"], reverse=True)

        for field in ["publishers"]:   
            final = []
            for k, v in res["facets"][field].items():
                final.append({"search_by": k, "name": id_to_name_mapping.get(k, k), "count": v})
            res["facets"][field] = sorted(final, key=lambda k: k["count"], reverse=True)

        for field in props_to_facet_mapping:   
            final = []
            for k, v in res["facets"][props_to_facet_mapping[field]].items():
                final.append({"search_by": k, "name": id_to_name_mapping.get(k, k), "count": v})
            res["facets"][props_to_facet_mapping[field]] = sorted(final, key=lambda k: k["count"], reverse=True)
        
        super().__init__(instance=res, **kwargs)
        

class LonelyE1CrmEntitySerializer(serializers.ModelSerializer):
    details_url = serializers.SerializerMethodField()
    class Meta:
        model = E1_Crm_Entity
        fields = [
            "id",
            "name",
            "self_contenttype",
            "entity_id",
            "details_url",
        ]
        depth=1
    def get_details_url(self, obj):
        return "https://apis-jelinek.acdh-dev.oeaw.ac.at/apis/entities/entity/e1_crm_entity/{}/detail/".format(obj.id)
