import django_filters
from .models import *
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
        
class F31PerformanceFilter(django_filters.FilterSet):
    class Meta:
        model = F31_Performance
        fields = {'id': ['exact', 'in'],
                  'performance_id': ['exact', 'in'],
                  'note': ['icontains'],
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
        class_criterion_lookup = "__".join([expr, "self_contenttype__model", "iexact"]).lstrip("__")
        class_criterion = Q()
        if class_to_check is not None:
            if isinstance(class_to_check, list):
                class_criterion_lookup = "__".join([expr, "self_contenttype__model", "in"]).lstrip("__")
                class_criterion = Q(**{class_criterion_lookup: [ContentType.objects.get_for_model(c).model for c in class_to_check]})
            else:
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
            disjunction = disjunction | search_in_xml_content_dump(value, classes_to_check=[class_to_check])
        print(disjunction)
        return queryset.filter(disjunction).distinct("id")
    return build_filter_method

def filter_by_entity_id(expr_to_entity, role=None, check_dump=False, check_dump_for_name=None, is_chapter=False, is_country=False, or_self=False):
    criteria_to_join = []
    for expr in expr_to_entity:
        role_criterion = Q()
        if role is not None:
            role_criterion_lookup = ("__").join([("__").join(expr.split("__")[:-1]), "prop__name__contains"])
            role_criterion = Q(**{role_criterion_lookup: role})
            if "," in role:
                role_criterion_lookup = ("__").join([("__").join(expr.split("__")[:-1]), "prop__name__in"])
                role_criterion = Q(**{role_criterion_lookup: role.split(",")})
        criteria_to_join.append({
                "role_criterion": role_criterion
        })
    def build_filter_method(queryset, name, value):
        entities = []
        # get internal id of entity with the given entity_id
        if is_chapter:
            entities = [c.id for c in Chapter.objects.filter(chapter_number__in=value)]
        elif is_country:
            entities = [c.id for c in F9_Place.objects.filter(country__in=value)]
        else:
            entities = [e.id for e in E1_Crm_Entity.objects.filter(entity_id__in=value)]
        
        disjunction = Q()
        for (idx, entry) in enumerate(criteria_to_join):
            id_criterion_lookup = "__".join([expr_to_entity[idx], "id__in"])
            id_criterion = Q(**{id_criterion_lookup: entities})
            disjunction = disjunction | (id_criterion & entry["role_criterion"])
        if check_dump:
            if check_dump_for_name is not None:
                disjunction = disjunction | search_in_xml_content_dump(["|".join(value), check_dump_for_name])
            else:
                disjunction = disjunction | search_in_xml_content_dump("|".join(value))
        if or_self:
            disjunction = disjunction | Q(entity_id__in=value)
        print(disjunction)
        return queryset.filter(disjunction).distinct("id")
    return build_filter_method

def search_in_xml_content_dump(value, classes_to_check=[]):
    search_string = ""
    if isinstance(value, list):
        search_string = " | ".join(["({})".format(entry.replace(" ", "&")) for entry in value])
    else:
        search_string = "({})".format(value.replace(" ", "&"))
    query = SearchQuery(search_string, search_type="raw")
    vector = SearchVector("file_content")
    note_vector = SearchVector("content")
    matching_dumps = [e.id for e in Xml_Content_Dump.objects.annotate(search=vector).filter(search=query)]
    matching_notes = [e.id for e in XMLNote.objects.annotate(search=note_vector).filter(search=query)]
    matching_ids = matching_dumps + matching_notes
    return Q(triple_set_from_subj__obj__in=matching_ids)


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
    work_id = TextInFilter(field_name="f1_work__entity_id", lookup_expr="in")
    # honour = django_filters.CharFilter(field_name="honour__name", lookup_expr="contains")
    honour_id = TextInFilter(field_name="honour__entity_id", lookup_expr="in")
    
    bibl_id = TextInFilter(field_name="f3_manifestation_product_type__entity_id", lookup_expr="in")
    genre = TextInFilter(field_name="f1_work__genre", lookup_expr="in")
    chapter_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], role="is in chapter", check_dump=False, is_chapter=True))
    keyword = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=Keyword, lookup_expr="in"))
    keyword_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"]))
    textLang = TextInFilter(field_name="f3_manifestation_product_type__text_language", lookup_expr="in")
    place = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=F9_Place, lookup_expr="in"))
    country = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], is_country=True))
    place_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"]))
    mediatype = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=E55_Type, lookup_expr="in"))
    startDate = django_filters.DateFilter(field_name="start_start_date", lookup_expr="gte")
    endDate = django_filters.DateFilter(field_name="start_end_date", lookup_expr="lte")
    searchTerm = django_filters.CharFilter(method=filter_entity(["", "triple_set_from_obj__subj", "triple_set_from_subj__obj"], lookup_expr="contains", check_dump=True, class_to_check=[F10_Person, E40_Legal_Body, F1_Work]))

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
        if "chapterRole" in self.data and "about" in self.data["chapterRole"]:
            self.filters['chapter_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], role="is about", is_chapter=True, check_dump=False))
        parent = super(SearchFilter, self).qs
        return parent

def search_in_vectors(cols_to_check=["dump", "note", "e1"], names_to_check=None):
        def build_filter_method(queryset, name, value):
            if isinstance(value, list):
                value = SearchQuery(" | ".join([entry.replace("_", "").replace(" ", "&") for entry in value]), search_type="raw", config="german")
                if names_to_check is not None:
                    value = value | SearchQuery(" | ".join([entry.replace("_", "").replace(" ", "&") for entry in names_to_check]), search_type="raw", config="german")
            else:
                value = SearchQuery(value, config="german")
            disjunction = Q()
            if "dump" in cols_to_check:
                disjunction = disjunction | Q(vector_related_xml_content_dump_set=value)
            if "note" in cols_to_check:
                disjunction = disjunction | Q(vector_related_xml_note_set=value)
            if "e1" in cols_to_check:
                disjunction = disjunction | Q(vector_column_e1_set=value)
            if "f10" in cols_to_check:
                disjunction = disjunction | Q(vector_related_f10_set=value)
            if "e40" in cols_to_check:
                disjunction = disjunction | Q(vector_related_E40_set=value)
            return queryset.filter(disjunction).distinct("id")
        return build_filter_method

class SearchFilter2(django_filters.FilterSet):
    class TextInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
        pass

    

    searchTerm = django_filters.CharFilter(method=search_in_vectors(cols_to_check=["f10", "dump", "note", "e1", "e40"]))
    person = django_filters.CharFilter(method=search_in_vectors(cols_to_check=["e1", "f10", "dump", "note"]))
    person_id = TextInFilter(method=search_in_vectors(cols_to_check=["f10", "dump", "note"]))
    institution = django_filters.CharFilter(method=search_in_vectors(cols_to_check=["e1", "e40", "dump", "note"]))
    institution_id = TextInFilter(method=search_in_vectors(cols_to_check=["e40", "dump", "note"]))
    title = django_filters.CharFilter(field_name="f1_work__name", lookup_expr="contains")
    # work_id = TextInFilter(field_name="f1_work__entity_id", lookup_expr="in")
    work_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_obj__subj"], or_self=True))
    bibl_id = TextInFilter(field_name="f3_manifestation_product_type__entity_id", lookup_expr="in")
    honour_id = TextInFilter(field_name="honour__entity_id", lookup_expr="in")
    genre = TextInFilter(field_name="f1_work__genre", lookup_expr="in")
    textLang = TextInFilter(field_name="f3_manifestation_product_type__text_language", lookup_expr="in")
    startDate = django_filters.DateFilter(method='start_date_filter')
    endDate = django_filters.DateFilter(method='end_date_filter')

    chapter_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], role="is in chapter", check_dump=False, is_chapter=True))
    keyword = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=Keyword, lookup_expr="in"))
    keyword_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"]))
    
    place = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=F9_Place, lookup_expr="in"))
    country = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], is_country=True))
    place_id = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"]))

    mediatype = TextInFilter(method=filter_entity(["triple_set_from_subj__obj", "triple_set_from_subj__obj__triple_set_from_subj__obj"], class_to_check=E55_Type, lookup_expr="in"))

    publisher = django_filters.CharFilter(method=search_in_vectors(cols_to_check=["e40", "dump", "note"]))
    publisher_id = TextInFilter(method=search_in_vectors(cols_to_check=["e40", "dump", "note"]))

    def start_date_filter(self, queryset, name, value):
        return queryset.filter(Q(start_end_date__gte=value) | Q(start_date__gte=value))
    def end_date_filter(self, queryset, name, value):
        return queryset.filter(Q(start_start_date__lte=value) | Q(start_date__lte=value))

    @property
    def qs(self):
        if "person_id" in self.data:
            self.filters['person'] = django_filters.CharFilter(method=empty_filter)
        if "person" in self.data:
            self.filters['person_id'] = self.TextInFilter(method=search_in_vectors(cols_to_check=["e1", "f10", "dump", "note"], names_to_check=[self.data["person"]]))
        if "personRole" in self.data:
            if "about" in self.data["personRole"]:
                self.filters['person_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], role="is about"))
            else:
                self.filters['person'] = django_filters.CharFilter(method=filter_entity(["triple_set_from_obj__subj"], class_to_check=F10_Person, lookup_expr="contains", role=self.data["personRole"]))
                self.filters['person_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_obj__subj"], role=self.data["personRole"]))
        if "institution_id" in self.data:
            self.filters['institution'] = django_filters.CharFilter(method=empty_filter)
        if "institution" in self.data:
            self.filters['institution_id'] = self.TextInFilter(method=search_in_vectors(cols_to_check=["e1", "e40", "dump", "note"], names_to_check=[self.data["institution"]]))
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
        if "chapterRole" in self.data and "about" in self.data["chapterRole"]:
            self.filters['chapter_id'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], role="is about", is_chapter=True, check_dump=False))
        parent = super(SearchFilter2, self).qs
        return parent

def exclude_null_values(queryset, name, value):
    filter_name = "{}__isnull".format(name)
    return queryset.exclude(Q(**{filter_name: True}))

def filter_on_related_work(queryset, name, value):
    matches = [q.id for q in queryset if next((item for item in q.related_work if item["genre"] in value), None)]
    res = queryset.filter(Q(id__in=matches) | Q(f1_work__genre__in=value))
    return res

class FacetFilter(django_filters.FilterSet):
    class TextInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
        pass

    filter_persons = TextInFilter(method=search_in_vectors(cols_to_check=["f10", "dump", "note"]))
    filter_institutions = TextInFilter(method=search_in_vectors(cols_to_check=["e40", "dump", "note"]))
    # filter_genre = TextInFilter(field_name="f1_work__genre", lookup_expr="in")
    filter_genre = TextInFilter(method=filter_on_related_work)
    filter_keywords = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=Keyword, lookup_expr="in"))
    filter_countries = TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"], is_country=True))
    filter_places= TextInFilter(method=filter_by_entity_id(["triple_set_from_subj__obj"]))
    filter_mediatypes = TextInFilter(method=filter_entity(["triple_set_from_subj__obj", "triple_set_from_subj__obj__triple_set_from_subj__obj"], class_to_check=E55_Type, lookup_expr="in"))
    filter_mediagroups = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=E55_Type, lookup_expr="in"))
    filter_languages = TextInFilter(field_name="f3_manifestation_product_type__text_language", lookup_expr="in")
    filter_startDate = django_filters.DateFilter(method="start_date_filter")
    filter_endDate = django_filters.DateFilter(method="end_date_filter")
    filter_koha = django_filters.CharFilter(field_name="f3_manifestation_product_type__koha_id", method=exclude_null_values)

    def start_date_filter(self, queryset, name, value):
        return queryset.filter(Q(start_end_date__gte=value) | Q(start_date__gte=value))
    def end_date_filter(self, queryset, name, value):
        return queryset.filter(Q(start_start_date__lte=value) | Q(start_date__lte=value))

    @property
    def qs(self):
        if "filter_personRoles" in self.data:
            self.filters['filter_persons'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_obj__subj"], role=self.data["filter_personRoles"]))
        if "filter_institutionRoles" in self.data:
            self.filters['filter_institutions'] = self.TextInFilter(method=filter_by_entity_id(["triple_set_from_obj__subj", "triple_set_from_subj__obj"], role=self.data["filter_institutionRoles"]))
        
        parent = super(FacetFilter, self).qs
        return parent


class EntitiesWithoutRelationsFilter(django_filters.FilterSet):
    class Meta:
        model = E1_Crm_Entity
        fields = {'id': ['exact', 'in'],
                  'self_contenttype': ['exact', 'in']
                  }   
