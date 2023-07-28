from collections import OrderedDict
from operator import itemgetter
from apis_core.apis_relations.models import TempTriple, Triple
from rest_framework import serializers
from rest_framework.fields import empty
from django.contrib.contenttypes.models import ContentType
from apis_ontology.models import Chapter, E1_Crm_Entity, F31_Performance, F3_Manifestation_Product_Type, F1_Work, Honour

serializers_cache = {}
serializers_cache_patched = {}

def remove_null_empty_from_dict(d):
    if isinstance(d, dict):
        new_d = {}
        for k, v in d.items():
            if v is not None and v != [] and v != {} and v != "" and not isinstance(v, dict) and not isinstance(v, list):
                new_d[k] = v
            elif isinstance(v, dict):
                new_d[k] = remove_null_empty_from_dict(v)
            elif isinstance(v, list):
                new_d[k] = remove_null_empty_from_dict(v)
    elif isinstance(d, list):
        new_d = []
        for v in d:
            if v is not None and v != [] and v != {} and v != "" and not isinstance(v, dict) and not isinstance(v, list):
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

        "triple_set_from_obj": TripleSerializerFromObj(many=True, read_only=True),
        "triple_set_from_subj": TripleSerializerFromSubj(many=True, read_only=True),
    }

    serializer_class = type(
        f"{model.__name__}SerializerPatched", (serializer,), dict_class
    )
    serializers_cache_patched[model.__name__] = serializer_class
    return serializer_class


class TripleSerializer(serializers.ModelSerializer):
    property = serializers.CharField(source="prop.name")

    class Meta:
        model = Triple
        exclude = [
            "subj",
            "obj",
            "prop",
        ]


class TripleSerializerFromObj(TripleSerializer):
    related_entity = serializers.SerializerMethodField(method_name="add_related_entity")

    def add_related_entity(self, obj):
        serializer = None
        if obj.subj.__class__ in [F1_Work, Honour]:
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
        
        
class F1WorkSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_for_translation = serializers.SerializerMethodField()
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

class F3ManifestationProductTypeSerializer(serializers.ModelSerializer):
    """
    Custom serializer for F3ManifestationProductType
    """

    triple_set_from_obj = TripleSerializerFromObj(many=True, read_only=True)
    triple_set_from_subj = TripleSerializerFromSubj(many=True, read_only=True)
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
        ]
        depth = 3

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return remove_null_empty_from_dict(ret)
    

    # def add_triple_set_from(self, obj):
    #     return obj.get_triple_set()

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
    

class SearchSerializer(serializers.ModelSerializer):
    """
    Custom search endpoint
    """
    # triple_set_from_obj = TripleSerializerFromObj(many=True, read_only=True)
    # triple_set_from_subj = SimpleTripleSerializerFromSubj(many=True, read_only=True)
    short = serializers.SerializerMethodField()
    genre = serializers.SerializerMethodField()
    related_work = serializers.SerializerMethodField()
    self_contenttype = serializers.SerializerMethodField()
    
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
            "related_work",
        )
        depth=1

    def get_self_contenttype(self, obj):
        return obj.self_contenttype.id

    def get_subclass_of_obj(self, obj, model):
        if hasattr(obj, model):
            return getattr(obj, model)
        elif hasattr(obj, str.lower(model)):
            return getattr(obj, str.lower(model))
        
    def get_f1(self, obj):
        if str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F3_Manifestation_Product_Type).model):
            related_f1 = obj.triple_set_from_obj.filter(prop__name="is expressed in")
            if len(related_f1) == 1:
                return related_f1[0].subj
            else:
                related_f1 = obj.triple_set_from_obj.filter(prop__name="is original for translation")
                if len(related_f1) == 1:
                    return related_f1[0].subj
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F31_Performance).model):
            related_f1 = obj.triple_set_from_obj.filter(prop__name="has been performed in")
            if len(related_f1) == 1:
                return related_f1[0].subj
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(Honour).model):
            return obj
        elif hasattr(obj, ContentType.objects.get_for_model(F1_Work).model):
            return obj
        return None
    
    def get_related_work(self, obj):
        f1 = self.get_f1(obj)
        if f1 is not None and f1.id != obj.id:
            serializer = serializers_cache.get(
                f1.__class__.__name__, create_serializer(f1.__class__)
            )
            return serializer(f1).data
        else:
            return None   
        
    def get_short(self, obj):
        if str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F3_Manifestation_Product_Type).model):
            return self.get_subclass_of_obj(obj, obj.self_contenttype.model).short
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F31_Performance).model):
            return self.get_subclass_of_obj(obj, obj.self_contenttype.model).short
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(Honour).model):
            return self.get_subclass_of_obj(obj, obj.self_contenttype.model).short
        elif hasattr(obj, ContentType.objects.get_for_model(F1_Work).model):
            return self.get_subclass_of_obj(obj, ContentType.objects.get_for_model(F1_Work).model).short
        else:
            return ""
        
    def get_genre(self, obj):
        if hasattr(obj, "genre"):
            return obj.genre
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F3_Manifestation_Product_Type).model):
            f1 = self.get_f1(obj)
            if f1 is not None:
                return f1.genre
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(F31_Performance).model):
            f1 = self.get_f1(obj)
            if f1 is not None:
                return f1.genre
        elif str.lower(obj.self_contenttype.model) == str.lower(ContentType.objects.get_for_model(Honour).model):
            return "Würdigungen"
        elif hasattr(obj, ContentType.objects.get_for_model(F1_Work).model):
            return self.get_subclass_of_obj(obj, ContentType.objects.get_for_model(F1_Work).model).genre
        return None
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return remove_null_empty_from_dict(ret)
        