from apis.urls import urlpatterns
from rest_framework import routers
from django.urls import include, path
from .jelinek_api_views import F3ManifestationProductType, Search
from django.contrib.auth.decorators import login_required

app_name = "jelinek"


router = routers.DefaultRouter()

router.register(r'f3_manifestation', F3ManifestationProductType, basename='F3ManifestationProductType')
router.register(r'search', Search, basename='Search')

customurlpatterns = [
    path('custom-api/', include(router.urls)),
]
urlpatterns = customurlpatterns + urlpatterns
