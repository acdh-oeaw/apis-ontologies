from rest_framework import viewsets
from .models import F3_Manifestation_Product_Type
from .jelinek_api_serializers import F3ManifestationProductTypeSerializer
from .jelinek_api_filters import F3ManifestationProductTypeFilter


class F3ManifestationProductType(viewsets.ReadOnlyModelViewSet):
    """
    Custom API endpoint for F3ManifestationProductType
    """
    serializer_class = F3ManifestationProductTypeSerializer
    filter_class = F3ManifestationProductTypeFilter
    queryset = F3_Manifestation_Product_Type.objects.all().prefetch_related('triple_set_from_obj', 'triple_set_from_subj')

 