from rest_framework.response import Response
from rest_framework import viewsets
from .models import E1_Crm_Entity, F1_Work, F3_Manifestation_Product_Type, Chapter, Honour
from .jelinek_api_serializers import F1WorkSerializer, HonourSerializer, SearchSerializer, F3ManifestationProductTypeSerializer, WorkForChapterSerializer
from .jelinek_api_filters import ChapterFilter, F3ManifestationProductTypeFilter, HonourFilter, SearchFilter, F1WorkFilter
from apis_core.apis_relations.models import Triple
from django.db.models import Q
from datetime import datetime

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
            "f1_only": self.f1_only,
            "related_work_triple_instances": self.related_work_triple_instances,
            "f3_to_host_work": self.f3_to_host_work
        })
        return context
    
    def list(self, request):
        # print("Start list function")
        currentTime = datetime.now()
        queryset = self.filter_queryset(self.get_queryset())
        # print("Finish filter queryset after {}".format((datetime.now()-currentTime).total_seconds()))
        currentTime = datetime.now()
        work_instances = []
        f3_to_host_work = {}
        related_work_triple_instances = Triple.objects.none()
        f1_only = False
        # switch between desired return types
        return_type = self.request.query_params.get('return_type', None)
        inbetween_time_start = datetime.now()
        if return_type == "f3":
            prop_names = ["is expressed in", "is original for translation", "is reported in"]

            # retrieve all work instances (f1 or honour)
            work_instance_ids = queryset.filter(Q(f1_work__isnull=False) | Q(honour__isnull=False)).values_list('id', flat=True)

            # Check if all instances are work instances
            f1_only = queryset.count() == len(work_instance_ids)

            # get their related manifestations
            related_f3_instances = E1_Crm_Entity.objects.filter(Q(f3_manifestation_product_type__isnull=False) & Q(triple_set_from_obj__subj__in=work_instances) & Q(triple_set_from_obj__prop__name__in=prop_names)).distinct().select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
            related_work_triple_instances = Triple.objects.filter(Q(subj__in=work_instances)&Q(obj__in=related_f3_instances))
            related_work_triple_ids = related_work_triple_instances.values_list("id", flat=True)
            # print("Finish related_work_triple_instances after {}".format((datetime.now()-currentTime).total_seconds()))
            currentTime = datetime.now()
            if work_instance_ids.count() == queryset.count():
                f1_only = True
            else:
                 # retrieve all manifestation instances such that we can load their related work instances
                manifestation_instances = queryset.filter(Q(f3_manifestation_product_type__isnull=False))
                
                # get their related manifestations
                #more_related_work_triple_ids = Triple.objects.filter(Q(obj__in=manifestation_instances) & Q(prop__name__in=prop_names)).distinct().values_list("id", flat=True)

                related_work_triple_instances = Triple.objects.filter((Q(obj__in=manifestation_instances) & Q(prop__name__in=prop_names)) | Q(id__in=related_work_triple_ids))
               
                # print("Finish related_work_triple_instances after {}".format((datetime.now()-currentTime).total_seconds()))
                missing_manifestation_ids = set(manifestation_instances.values_list('id', flat=True)) - set(related_work_triple_instances.values_list('obj__id', flat=True))

                # print("Finish missing_manifestation_instances after {}".format((datetime.now()-currentTime).total_seconds()))
                currentTime = datetime.now()

                if missing_manifestation_ids:
                    host_instances = Triple.objects.filter(obj__id__in=missing_manifestation_ids, prop__name="has host")
                    host_subjects = host_instances.values_list('subj', flat=True)
                    related_host_work_triple_instances = Triple.objects.filter(
                        Q(obj__in=host_subjects) & 
                        Q(prop__name__in=["is expressed in", "is original for translation", "is reported in"])
                    )
                    # print("Finish related_host_work_triple_instances after {}".format((datetime.now()-currentTime).total_seconds()))
                    currentTime = datetime.now()
                    # dictionary to map manifestations to their host triples
                    f3_to_host_work = {instance_id: [] for instance_id in missing_manifestation_ids}
                    
                    for host_instance in host_instances:
                        related_triples = related_host_work_triple_instances.filter(obj=host_instance.subj)
                        f3_to_host_work[host_instance.obj.id].extend(related_triples)
                    # print("Finish f3_to_host_work after {}".format((datetime.now()-currentTime).total_seconds()))
                    currentTime = datetime.now()
            # join the querysets and remove work instances
            queryset = queryset.filter(Q(f1_work__isnull=True) & Q(honour__isnull=True)).union(related_f3_instances)
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
        self.related_work_triple_instances = related_work_triple_instances
        self.f3_to_host_work = f3_to_host_work
        # print("Finish inbetween requests after {}".format((datetime.now()-inbetween_time_start).total_seconds()))
        # print(queryset.count())
        # print(related_work_triple_instances.count())
        currentTime = datetime.now()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            r = self.get_paginated_response(serializer.data)
            # print("Finish serialization after {}".format((datetime.now()-currentTime).total_seconds()))
            return r

        serializer = self.get_serializer(queryset, many=True)
        # print("Finish serialization after {}".format((datetime.now()-currentTime).total_seconds()))
        return Response(serializer.data)


class WorkForChapter(viewsets.ReadOnlyModelViewSet):
    filter_class = ChapterFilter
    queryset = Chapter.objects.all().prefetch_related('triple_set_from_subj')
    serializer_class = WorkForChapterSerializer
