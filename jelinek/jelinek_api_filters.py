import django_filters
from .models import Chapter, E40_Legal_Body, E55_Type, F10_Person, F1_Work, F3_Manifestation_Product_Type, F9_Place, Honour, Keyword, E1_Crm_Entity, Xml_Content_Dump
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchQuery, SearchVector

class F3ManifestationProductTypeFilter(django_filters.FilterSet):
    class Meta:
        model = F3_Manifestation_Product_Type
        fields = {'id': ['exact', 'in'],
                  'bibl_id': ['exact', 'in'],
                  'note': ['icontains'], 
                  'series': ['icontains'],
                  'short': ['icontains']
                  }
        
class F1WorkFilter(django_filters.FilterSet):
    class Meta:
        model = F1_Work
        fields = {'id': ['exact', 'in'],
                  'idno': ['exact', 'in']
                  }
class HonourFilter(django_filters.FilterSet):
    class Meta:
        model = Honour
        fields = {'id': ['exact', 'in'],
                  'honour_id': ['exact', 'in']
                  }
        
class ChapterFilter(django_filters.FilterSet):
    class Meta:
        model = Chapter
        fields = {'id': ['exact', 'in'],
                  'chapter_number': ['exact', 'in']
                  }
        
def filter_entity(expr_to_entity, class_to_check=None, role=None, lookup_expr="in", property_to_check="name", check_dump=False):
    criteria_to_join = []
    for expr in expr_to_entity:
        class_criterion_lookup = "__".join([expr, "self_contenttype__model", "iexact"])
        class_criterion = Q()
        if class_to_check is not None:
            class_criterion = Q(**{class_criterion_lookup: ContentType.objects.get_for_model(class_to_check).model})
        property_lookup = '__'.join([expr, property_to_check, lookup_expr])
        if len(expr) == 0:
            property_lookup = '__'.join([property_to_check, lookup_expr])
        role_criterion = Q()
        if role is not None:
            role_criterion_lookup = ("__").join([("__").join(expr.split("__")[:-1]), "prop__name__contains"])
            role_criterion = Q(**{role_criterion_lookup: role})
        criteria_to_join.append({
                "class_criterion": class_criterion,
                "property_lookup": property_lookup,
                "role_criterion": role_criterion
        })
    def build_filter_method(queryset, name, value):
        disjunction = Q()
        for entry in criteria_to_join:
            entry["property_criterion"] = Q(**{entry["property_lookup"]: value})
            disjunction = disjunction | (entry["property_criterion"] & entry["class_criterion"] & entry["role_criterion"])
        if check_dump:
            disjunction = disjunction | search_in_xml_content_dump(value)
        print(disjunction)
        return queryset.filter(disjunction).distinct("id")
    return build_filter_method

def filter_by_entity_id(expr_to_entity, role=None, check_dump=False, check_dump_for_name=None):
    criteria_to_join = []
    for expr in expr_to_entity:
        role_criterion = Q()
        if role is not None:
            role_criterion_lookup = ("__").join([("__").join(expr.split("__")[:-1]), "prop__name__contains"])
            role_criterion = Q(**{role_criterion_lookup: role})
        criteria_to_join.append({
                "role_criterion": role_criterion
        })
    def build_filter_method(queryset, name, value):
        # get internal id of entity with the given entity_id
        entities = [e.id for e in E1_Crm_Entity.objects.filter(entity_id__in=value)]
        id_criterion_lookup = "__".join([expr, "id__in"])
        id_criterion = Q(**{id_criterion_lookup: entities})
        disjunction = Q()
        for entry in criteria_to_join:
            disjunction = disjunction | (id_criterion & entry["role_criterion"])
        if check_dump:
            if check_dump_for_name is not None:
                disjunction = disjunction | search_in_xml_content_dump(["|".join(value), check_dump_for_name])
            else:
                disjunction = disjunction | search_in_xml_content_dump("|".join(value))
        print(disjunction)
        return queryset.filter(disjunction).distinct("id")
    return build_filter_method

def search_in_xml_content_dump(value):
    search_string = ""
    if isinstance(value, list):
        search_string = " | ".join(["({})".format(entry.replace(" ", "&")) for entry in value])
    else:
        search_string = "({})".format(value.replace(" ", "&"))
    query = SearchQuery(search_string, search_type="raw")
    vector = SearchVector("file_content")
    matching_dumps = [e.id for e in Xml_Content_Dump.objects.annotate(search=vector).filter(search=query)]
    return Q(triple_set_from_subj__obj__in=matching_dumps)

def empty_filter(queryset, name, value):
    return queryset

      
class SearchFilter(django_filters.FilterSet):
    class TextInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
        pass
    person = django_filters.CharFilter(method=filter_entity(["triple_set_from_obj__subj"], class_to_check=F10_Person, lookup_expr="contains", check_dump=True))
    person_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_obj__subj"], check_dump=True))
    institution = django_filters.CharFilter(method=filter_entity(["triple_set_from_obj__subj", "triple_set_from_subj__obj"], class_to_check=E40_Legal_Body, lookup_expr="contains", check_dump=True))
    institution_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_obj__subj", "triple_set_from_subj__obj"], check_dump=True))
    title = django_filters.CharFilter(field_name="f1_work__name", lookup_expr="contains")
    work_id = django_filters.CharFilter(field_name="f1_work__entity_id", lookup_expr="contains")
    honour = django_filters.CharFilter(field_name="honour__name", lookup_expr="contains")
    honour_id = django_filters.CharFilter(field_name="honour__entity_id", lookup_expr="contains")
    genre = TextInFilter(field_name="f1_work__genre", lookup_expr="in")
    keyword = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=Keyword, lookup_expr="in"))
    keyword_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"]))
    textLang = TextInFilter(field_name="f3_manifestation_product_type__text_language", lookup_expr="in")
    place = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=F9_Place, lookup_expr="in"))
    place_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"]))
    mediatype = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=E55_Type, lookup_expr="in"))
    startDate = django_filters.DateFilter(field_name="start_start_date", lookup_expr="gte")
    endDate = django_filters.DateFilter(field_name="start_end_date", lookup_expr="lte")
    searchTerm = django_filters.CharFilter(method=filter_entity(["", "triple_set_from_obj__subj", "triple_set_from_subj__obj"], lookup_expr="contains", check_dump=True))

    @property
    def qs(self):
        if "person_id" in self.data:
            self.filters['person'] = django_filters.CharFilter(method=empty_filter)
        if "person" in self.data:
            self.filters['person_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_obj__subj"], check_dump=True, check_dump_for_name=self.data["person"]))
        if "personRole" in self.data:
            if "about" in self.data["personRole"]:
                self.filters['person_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], role="is about"))
            else:
                self.filters['person'] = django_filters.CharFilter(method=filter_entity(["triple_set_from_obj__subj"], class_to_check=F10_Person, lookup_expr="contains", role=self.data["personRole"]))
                self.filters['person_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_obj__subj"], role=self.data["personRole"]))
        if "institution_id" in self.data:
            self.filters['institution'] = django_filters.CharFilter(method=empty_filter)
        if "institution" in self.data:
            self.filters['institution_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_obj__subj", "triple_set_from_subj__obj"], check_dump=True, check_dump_for_name=self.data["institution"]))
        if "institutionRole" in self.data:
            if "about" in self.data["institutionRole"]:
                self.filters['institution_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], role="is about"))
            else:
                self.filters['institution'] = django_filters.CharFilter(method=filter_entity(["triple_set_from_obj__subj", "triple_set_from_subj__obj"], class_to_check=E40_Legal_Body, lookup_expr="contains", role=self.data["institutionRole"]))
                self.filters['institution_id'] =  self.TextInFilter(method=filter_by_entity_id(["triple_set_from_obj__subj", "triple_set_from_subj__obj"], role=self.data["institutionRole"]))
        if "workRole" in self.data and "about" in self.data["workRole"]:
            self.filters['work_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], role="is about"))
        if "honourRole" in self.data and "about" in self.data["honourRole"]:
            self.filters['honour_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], role="is about"))
        parent = super(SearchFilter, self).qs
        return parent
                