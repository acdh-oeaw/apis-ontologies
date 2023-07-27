from rest_framework import viewsets
from .models import E1_Crm_Entity, F3_Manifestation_Product_Type
from .jelinek_api_serializers import SearchSerializer, F3ManifestationProductTypeSerializer
from .jelinek_api_filters import F3ManifestationProductTypeFilter, SearchFilter
from django.db.models import Q

class F3ManifestationProductType(viewsets.ReadOnlyModelViewSet):
    """
    Custom API endpoint for F3ManifestationProductType
    """
    serializer_class = F3ManifestationProductTypeSerializer
    filter_class = F3ManifestationProductTypeFilter
    queryset = F3_Manifestation_Product_Type.objects.all().prefetch_related('triple_set_from_obj', 'triple_set_from_subj')

class Search(viewsets.ReadOnlyModelViewSet):
    filter_class = SearchFilter
    queryset = E1_Crm_Entity.objects.filter(Q(f1_work__isnull=False) | Q(honour__isnull=False) | Q(f3_manifestation_product_type__isnull=False) | Q(f31_performance__isnull=False)).select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
    serializer_class = SearchSerializer
