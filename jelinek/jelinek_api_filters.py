import django_filters
from .models import E40_Legal_Body, E55_Type, F10_Person, F3_Manifestation_Product_Type, F9_Place, Keyword
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

class F3ManifestationProductTypeFilter(django_filters.FilterSet):
    class Meta:
        model = F3_Manifestation_Product_Type
        fields = {'id': ['exact', 'in'],
                  'bibl_id': ['exact', 'in'],
                  'note': ['icontains'], 
                  'series': ['icontains'],
                  'short': ['icontains']
                  }
        
def filter_entity(expr_to_entity, class_to_check=None, role=None, lookup_expr="in"):
        criteria_to_join = []
        for expr in expr_to_entity:
            class_criterion_lookup = "__".join([expr, "self_contenttype__model", "iexact"])
            class_criterion = Q()
            if class_to_check is not None:
                class_criterion = Q(**{class_criterion_lookup: ContentType.objects.get_for_model(class_to_check).model})
            name_lookup = '__'.join([expr, 'name', lookup_expr])
            if len(expr) == 0:
                name_lookup = '__'.join(['name', lookup_expr])
            role_criterion = Q()
            if role is not None:
                role_criterion_lookup = ("__").join([("__").join(expr.split("__")[:-1]), "prop__name__contains"])
                role_criterion = Q(**{role_criterion_lookup: role})
            criteria_to_join.append({
                 "class_criterion": class_criterion,
                 "name_lookup": name_lookup,
                 "role_criterion": role_criterion
            })
        def build_filter_method(queryset, name, value):
            disjunction = Q()
            for entry in criteria_to_join:
                entry["name_criterion"] = Q(**{entry["name_lookup"]: value})
                disjunction = disjunction | (entry["name_criterion"] & entry["class_criterion"] & entry["role_criterion"])
            print(disjunction)
            return queryset.filter(disjunction).distinct("id")
        return build_filter_method 
      
class SearchFilter(django_filters.FilterSet):
    class TextInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
        pass
    person = django_filters.CharFilter(method=filter_entity(["triple_set_from_obj__subj"], class_to_check=F10_Person, lookup_expr="contains"))
    institution = django_filters.CharFilter(method=filter_entity(["triple_set_from_obj__subj", "triple_set_from_subj__obj"], class_to_check=E40_Legal_Body, lookup_expr="contains"))
    title = django_filters.CharFilter(field_name="f1_work__name", lookup_expr="contains")
    honour = django_filters.CharFilter(field_name="honour__name", lookup_expr="contains")
    genre = TextInFilter(field_name="f1_work__genre", lookup_expr="in")
    keyword = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=Keyword, lookup_expr="in"))
    textLang = TextInFilter(field_name="f3_manifestation_product_type__text_language", lookup_expr="in")
    place = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=F9_Place, lookup_expr="in"))
    mediatype = TextInFilter(method=filter_entity(["triple_set_from_subj__obj"], class_to_check=E55_Type, lookup_expr="in"))
    startDate = django_filters.DateFilter(field_name="start_start_date", lookup_expr="gte")
    endDate = django_filters.DateFilter(field_name="start_end_date", lookup_expr="lte")
    searchTerm = django_filters.CharFilter(method=filter_entity(["", "triple_set_from_obj__subj", "triple_set_from_subj__obj"], lookup_expr="contains"))

    @property
    def qs(self):
        if "personRole" in self.data:
            self.filters['person'] = django_filters.CharFilter(method=filter_entity(["triple_set_from_obj__subj"], class_to_check=F10_Person, lookup_expr="contains", role=self.data["personRole"]))
        if "institutionRole" in self.data:
            self.filters['institution'] = django_filters.CharFilter(method=filter_entity(["triple_set_from_obj__subj", "triple_set_from_subj__obj"], class_to_check=E40_Legal_Body, lookup_expr="contains", role=self.data["institutionRole"]))
        parent = super(SearchFilter, self).qs
        return parent
                