from apis.urls import urlpatterns
from django.urls import path
from .views import CustomReferenceDetailView, TempTripleAutocomplete, TempEntityClassAutocomplete, CustomReferenceDeleteView

customurlpatterns = [
    path("bibsonomy/references/<int:pk>", CustomReferenceDetailView.as_view(), name='referencedetail'),
    path('bibsonomy/tempentityclass-autocomplete/', TempEntityClassAutocomplete.as_view(), name="tempentityclass-autocomplete",),
    path('bibsonomy/temptriple-autocomplete/', TempTripleAutocomplete.as_view(), name="temptriple-autocomplete",),
    path('bibsonomy/references/<int:pk>/delete', CustomReferenceDeleteView.as_view(), name='referencedelete'),
]
urlpatterns = customurlpatterns + urlpatterns
