from collections import OrderedDict
from operator import itemgetter
from apis_core.apis_relations.models import TempTriple, Triple
from rest_framework import serializers
from rest_framework.fields import empty
from .models import F3_Manifestation_Product_Type

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
            "self_contenttype",
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
            "self_contenttype",
            "ref_target",
            "ref_accessed",
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
