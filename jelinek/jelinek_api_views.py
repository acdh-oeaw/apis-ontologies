from rest_framework.response import Response
from rest_framework import viewsets
from .models import E1_Crm_Entity, F1_Work, F3_Manifestation_Product_Type, Chapter, Honour
from .jelinek_api_serializers import F1WorkSerializer, HonourSerializer, SearchSerializer, F3ManifestationProductTypeSerializer, WorkForChapterSerializer
from .jelinek_api_filters import ChapterFilter, F3ManifestationProductTypeFilter, HonourFilter, SearchFilter, F1WorkFilter
from django.db.models import Q

class F3ManifestationProductType(viewsets.ReadOnlyModelViewSet):
    serializer_class = F3ManifestationProductTypeSerializer
    filter_class = F3ManifestationProductTypeFilter
    queryset = F3_Manifestation_Product_Type.objects.all().prefetch_related('triple_set_from_obj', 'triple_set_from_subj')

class F1Work(viewsets.ReadOnlyModelViewSet):
    serializer_class = F1WorkSerializer
    filter_class = F1WorkFilter
    queryset = F1_Work.objects.all().prefetch_related('triple_set_from_subj')

class Honour(viewsets.ReadOnlyModelViewSet):
    serializer_class = HonourSerializer
    filter_class = HonourFilter
    queryset = Honour.objects.all().prefetch_related('triple_set_from_subj')

class Search(viewsets.ReadOnlyModelViewSet):
    filter_class = SearchFilter
    serializer_class = SearchSerializer

    def get_queryset(self):
        return_type = self.request.query_params.get('return_type', None)
        if return_type=="f1":
           return E1_Crm_Entity.objects.filter(Q(f1_work__isnull=False) | Q(honour__isnull=False)).select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
        elif return_type=="f3":
           return E1_Crm_Entity.objects.filter(Q(f1_work__isnull=False) | Q(honour__isnull=False) | Q(f3_manifestation_product_type__isnull=False)).select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
        elif return_type=="f31":
           return E1_Crm_Entity.objects.filter(Q(f1_work__isnull=False) | Q(honour__isnull=False) | Q(f31_performance__isnull=False)).select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
        else:
           return E1_Crm_Entity.objects.filter(Q(f1_work__isnull=False) | Q(honour__isnull=False) | Q(f3_manifestation_product_type__isnull=False) | Q(f31_performance__isnull=False) | Q(f26_recording__isnull=False)).select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            "work_instances": self.work_instances,
            "f1_only": self.f1_only
        })
        return context
    
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        work_instances = []
        f1_only = False
        # switch between desired return types
        return_type = self.request.query_params.get('return_type', None)
        if return_type == "f3":
            # retrieve all work instanes (f1 or honour)
            work_instances = queryset.filter(Q(f1_work__isnull=False) | Q(honour__isnull=False))
            if work_instances.count() == queryset.count():
                f1_only = True
            # get their related manifestations
            f3_instances = E1_Crm_Entity.objects.filter(Q(f3_manifestation_product_type__isnull=False) & Q(triple_set_from_obj__subj__in=work_instances) & Q(triple_set_from_obj__prop__name__in=["is expressed in", "is original for translation", "is reported in"])).distinct().select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
            # join the querysets and remove work instances
            queryset = queryset.filter(Q(f1_work__isnull=True) & Q(honour__isnull=True)).union(f3_instances)
        # same for f31_performances
        elif return_type == "f31":
            work_instances = queryset.filter(Q(f1_work__isnull=False) | Q(honour__isnull=False))
            if work_instances.count() == queryset.count():
                f1_only = True
            f31_instances = E1_Crm_Entity.objects.filter(Q(f31_performance__isnull=False) & Q(triple_set_from_obj__subj__in=work_instances) & Q(triple_set_from_obj__prop__name__in=["has been performed in"])).distinct().select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
            queryset = queryset.filter(Q(f1_work__isnull=True) & Q(honour__isnull=True)).union(f31_instances)
        # if no return type is specified, return f3, f31 and f26
        elif return_type is None:
            work_instances = queryset.filter(Q(f1_work__isnull=False) | Q(honour__isnull=False))
            if work_instances.count() == queryset.count():
                f1_only = True
            mixed = E1_Crm_Entity.objects.filter(
                (Q(f3_manifestation_product_type__isnull=False) | Q(f31_performance__isnull=False) | Q(f26_recording__isnull=False))
                  & Q(triple_set_from_obj__subj__in=work_instances) 
                  & Q(triple_set_from_obj__prop__name__in=["has been performed in", "is expressed in", "is original for translation", "is reported in", "R13 is realised in"])
                  ).distinct().select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
            queryset = queryset.filter(Q(f1_work__isnull=True) & Q(honour__isnull=True)).union(mixed)
        self.work_instances = work_instances
        self.f1_only = f1_only
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class WorkForChapter(viewsets.ReadOnlyModelViewSet):
    filter_class = ChapterFilter
    queryset = Chapter.objects.all().prefetch_related('triple_set_from_subj')
    serializer_class = WorkForChapterSerializer
