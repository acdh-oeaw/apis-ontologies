import django_filters
from .models import F3_Manifestation_Product_Type

class F3ManifestationProductTypeFilter(django_filters.FilterSet):
    class Meta:
        model = F3_Manifestation_Product_Type
        fields = {'id': ['exact', 'in'],
                  'bibl_id': ['exact', 'in'],
                  'note': ['icontains'], 
                  'series': ['icontains'],
                  'short': ['icontains']
                  }
                