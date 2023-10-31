from apis.urls import urlpatterns
from rest_framework import routers
from django.urls import include, path
from .jelinek_api_views import *
from django.contrib.auth.decorators import login_required

app_name = "jelinek"


router = routers.DefaultRouter()

router.register(r'f3_manifestation', F3ManifestationProductType, basename='F3ManifestationProductType')
router.register(r'f31_performance', F31Performance, basename='F31Performance')
router.register(r'f1_work', F1Work, basename='F1Work')
router.register(r'honour', Honour, basename='Honour')
router.register(r'search', Search, basename='Search')
router.register(r'work_for_chapter', WorkForChapter, basename='WorkForChapter')
router.register(r'search2', SearchV2, basename="Search2")
router.register(r'entities_without_relations', EntitiesWithoutRelations, basename='EntitiesWithoutRelations')

customurlpatterns = [
    path('custom-api/', include(router.urls)),
]
urlpatterns = customurlpatterns + urlpatterns
