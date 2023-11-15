from rest_framework.response import Response
from rest_framework import viewsets
from .models import *
from .jelinek_api_serializers import *
from .jelinek_api_filters import *
from apis_core.apis_relations.models import Triple
from django.db.models import Q, Count, Sum, Case, When, IntegerField,Exists
from datetime import datetime
from django.db.models import Q, OuterRef
from django.db.models.functions import JSONObject
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.expressions import ArraySubquery
from apis_core.apis_relations.models import Triple, Property
from django.contrib.contenttypes.models import ContentType


class F3ManifestationProductType(viewsets.ReadOnlyModelViewSet):
    serializer_class = F3ManifestationProductTypeSerializer
    filter_class = F3ManifestationProductTypeFilter
    queryset = F3_Manifestation_Product_Type.objects.all().prefetch_related('triple_set_from_obj', 'triple_set_from_subj')

class F31Performance(viewsets.ReadOnlyModelViewSet):
    serializer_class = F31PerformanceSerializer
    filter_class = F31PerformanceFilter
    queryset = F31_Performance.objects.all().prefetch_related('triple_set_from_obj', 'triple_set_from_subj')

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

        # switch between desired return types
        return_type = self.request.query_params.get('return_type', None)

        work_instances = []
        manifestation_instances = []
        f1_only = False

        prop_names = ["is expressed in", "is original for translation", "is reported in"]
        related_f3_instances = []
        related_work_triple_instances = []
        if return_type in ["f3", "f31"]:
            # create lists of work instances to fetch their manifestations and append them to the queryset
            for w in queryset:
                if hasattr(w, "f1_work") or hasattr(w, "honour"):
                    work_instances.append(w)
            # Check if all instances are work instances
            f1_only = len(queryset) == len(work_instances)
            # print("Finish work_instances after {}".format((datetime.now()-currentTime).total_seconds()))

            if return_type == "f3":
                # get their related manifestations
                # related_work_triple_instances = [triple for work in work_instances for triple in work.triple_set_from_subj.all() if triple.prop.name in prop_names]
                related_f3_instances = E1_Crm_Entity.objects.filter(triple_set_from_obj__subj__in=work_instances, triple_set_from_obj__prop__name__in=prop_names).distinct().select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
            if return_type== "f31":
                #related_work_triple_instances = [triple for work in work_instances for triple in work.triple_set_from_subj.all() if triple.prop.name == "has been performed in"]
                related_f3_instances = E1_Crm_Entity.objects.filter(triple_set_from_obj__subj__in=work_instances, triple_set_from_obj__prop__name="has been performed in").distinct().select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
           
            #related_f3_instances = E1_Crm_Entity.objects.filter(id__in=[t.obj.id for t in related_work_triple_instances]).distinct().select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
            # print("Finish related_work_triple_instances after {}".format((datetime.now()-currentTime).total_seconds()))
            currentTime = datetime.now()
            queryset = queryset.exclude(id__in=[w.id for w in work_instances]).union(related_f3_instances)

        page = self.paginate_queryset(queryset)
        f3_to_host_work = {}
        
        # switch between desired return types
        return_type = self.request.query_params.get('return_type', None)
        inbetween_time_start = datetime.now()
        if return_type == "f3":
        
            #if not f1_only:
            manifestation_instances = page
            manifestation_triples = [triple for work in manifestation_instances for triple in work.triple_set_from_obj.all() if triple.prop.name in prop_names]
            related_work_triple_instances += manifestation_triples
            
            # print("Finish related_work_triple_instances after {}".format((datetime.now()-currentTime).total_seconds()))
            missing_manifestation_ids = set(m.id for m in manifestation_instances) - set(t.obj.id for t in related_work_triple_instances)

            # print("Finish missing_manifestation_instances after {}".format((datetime.now()-currentTime).total_seconds()))
            currentTime = datetime.now()

            if missing_manifestation_ids:
                host_instances = [triple for manifestation in manifestation_instances if manifestation.id in missing_manifestation_ids for triple in manifestation.triple_set_from_obj.all() if triple.prop.name == "has host"]
                related_host_work_triple_instances = [triple for host_triple in host_instances for triple in host_triple.subj.triple_set_from_obj.all() if triple.prop.name in prop_names]
                # print("Finish related_host_work_triple_instances after {}".format((datetime.now()-currentTime).total_seconds()))
                currentTime = datetime.now()
                # dictionary to map manifestations to their host triples
                f3_to_host_work = {instance_id: [] for instance_id in missing_manifestation_ids}
                
                for host_instance in host_instances:
                    related_triples = [triple for triple in related_host_work_triple_instances if triple.obj==host_instance.subj]
                    f3_to_host_work[host_instance.obj.id].extend(related_triples)
                # print("Finish f3_to_host_work after {}".format((datetime.now()-currentTime).total_seconds()))
                currentTime = datetime.now()

        # # same for f31_performances
        elif return_type == "f31":
            #if not f1_only:
            for w in set(page) - set(related_f3_instances):
                if hasattr(w, "f31_performance"):
                    manifestation_instances.append(w)
            manifestation_triples = [triple for work in manifestation_instances for triple in work.triple_set_from_obj.all() if triple.prop.name == "has been performed in"]
            related_work_triple_instances += manifestation_triples
        #     work_instances = queryset.filter(Q(f1_work__isnull=False) | Q(honour__isnull=False))
        #     if work_instances.count() == queryset.count():
        #         f1_only = True
        #     f31_instances = E1_Crm_Entity.objects.filter(Q(f31_performance__isnull=False) & Q(triple_set_from_obj__subj__in=work_instances) & Q(triple_set_from_obj__prop__name__in=["has been performed in"])).distinct().select_related("f1_work").prefetch_related('triple_set_from_obj', 'triple_set_from_subj', "f1_work")
        #     queryset = queryset.filter(Q(f1_work__isnull=True) & Q(honour__isnull=True)).union(f31_instances)
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
        else:
            manifestation_triples = [triple for work in page for triple in work.triple_set_from_obj.filter(prop__name__in=["has been performed in", "is expressed in", "is original for translation", "is reported in", "R13 is realised in"])]
            related_work_triple_instances += manifestation_triples
        self.work_instances = work_instances
        self.f1_only = f1_only
        self.related_work_triple_instances = related_work_triple_instances
        self.f3_to_host_work = f3_to_host_work
        # print("Finish inbetween requests after {}".format((datetime.now()-inbetween_time_start).total_seconds()))
        # print(queryset.count())
        # print(len(related_work_triple_instances))
        currentTime = datetime.now()
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            r = self.get_paginated_response(serializer.data)
            # print("Finish serialization after {}".format((datetime.now()-currentTime).total_seconds()))
            return r

        serializer = self.get_serializer(queryset, many=True)
        #print("Finish serialization after {}".format((datetime.now()-currentTime).total_seconds()))
        return Response(serializer.data)


class WorkForChapter(viewsets.ReadOnlyModelViewSet):
    filter_class = ChapterFilter
    queryset = Chapter.objects.all().prefetch_related('triple_set_from_subj')
    serializer_class = WorkForChapterSerializer


class SearchV2(viewsets.ReadOnlyModelViewSet):
    filter_class = SearchFilter2
    serializer_class = SearchSerializer2
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # apply facet filter 
        facet_filtered_queryset = FacetFilter(self.request.GET, queryset=queryset).qs

        serializer = self.get_serializer(facet_filtered_queryset, many=False)
        return Response(serializer.data)
    
    def get_queryset(self):
        f31_only = self.request.GET.get("return_type", "") == "f31"
        work_only_fields = ["title", "work_id", "honour_id", "genre", "genreFilter", "chapter_id", "keyword", "keyword_id", "workRole", 
                            "honourRole", "chapterRole", "limit", "filter_genre", "filter_keywords", "filter_startDate", 
                            "filter_endDate", "filter_persons", "filter_institutions", "filter_personRoles", "filter_institutionRoles"]
        work_only = set(i[0] for i in self.request.GET.items() if i[1] is not None and i[1] != "").issubset(work_only_fields)
        
        
        print(work_only)
        person_contenttype = ContentType.objects.get_for_model(model=F10_Person)
        institution_contenttype = ContentType.objects.get_for_model(model=E40_Legal_Body)
        person_subquery = F10_Person.objects.filter(triple_set_from_subj__obj_id=OuterRef("pk")).values(json=JSONObject(name="name", entity_id="entity_id"))
        person_property_subquery = Property.objects.filter(triple_set_from_prop__obj_id=OuterRef("pk"), triple_set_from_prop__subj__self_contenttype_id=person_contenttype).values_list('name', flat=True)
        institution_subquery = E40_Legal_Body.objects.filter(triple_set_from_subj__obj_id=OuterRef("pk")).values(json=JSONObject(name="name", entity_id="entity_id", type="institution_type"))
        institution_property_subquery = Property.objects.filter(triple_set_from_prop__obj_id=OuterRef("pk"), triple_set_from_prop__subj__self_contenttype_id=institution_contenttype).values_list('name', flat=True)
        keyword_subquery = Keyword.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk")).values_list('name', flat=True)
        place_subquery = F9_Place.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk")).values(json=JSONObject(name="name", entity_id="entity_id"))
        country_subquery = F9_Place.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk")).values_list("country", flat=True)

        # include host type if type is "analyticPublication"
        mediatype_host_subquery = Q(triple_set_from_obj__subj__triple_set_from_obj__subj_id=OuterRef("pk"), triple_set_from_obj__subj__triple_set_from_obj__subj__triple_set_from_subj__obj__name="analyticPublication")
        mediatype_subquery = E55_Type.objects.filter(triple_set_from_obj__subj_id=OuterRef("pk")).union(E55_Type.objects.filter(mediatype_host_subquery)).values_list('name', flat=True)
        work_subquery = F1_Work.objects.filter(triple_set_from_subj__obj_id=OuterRef("pk"), triple_set_from_subj__prop__name__in=["is expressed in", "is reported in", "is original for translation", "has been performed in"]).distinct().values(json=JSONObject(pk="pk", name="name", genre="genre", entity_id="entity_id"))
        work_host_subquery = F1_Work.objects.filter(triple_set_from_subj__obj__triple_set_from_subj__obj_id=OuterRef("pk"), triple_set_from_subj__prop__name__in=["is expressed in", "is reported in", "is original for translation", "has been performed in"]).distinct().values(json=JSONObject(pk="pk", name="name", genre="genre", entity_id="entity_id"))
        subclass_filter = Q(f1_work__isnull=False) | Q(honour__isnull=False) | Q(f3_manifestation_product_type__isnull=False) | Q(f31_performance__isnull=False)
        if work_only:
            subclass_filter = Q(f1_work__isnull=False) | Q(honour__isnull=False)
        elif f31_only:
            subclass_filter = Q(f31_performance__isnull=False)
        qs = E1_Crm_Entity.objects_inheritance.select_subclasses("f1_work", "f3_manifestation_product_type", "honour", "f31_performance").filter(subclass_filter).annotate(
            related_persons=ArraySubquery(person_subquery),
            related_person_roles=ArraySubquery(person_property_subquery), 
            related_institutions=ArraySubquery(institution_subquery),
            related_institution_roles=ArraySubquery(institution_property_subquery), 
            related_keywords=ArraySubquery(keyword_subquery), 
            related_places=ArraySubquery(place_subquery), 
            related_countries=ArraySubquery(country_subquery), 
            related_mediatypes=ArraySubquery(mediatype_subquery),
            related_work= Case(
                When(
                    Exists(work_subquery), then=ArraySubquery(work_subquery)
                    ),
                default=ArraySubquery(work_host_subquery)
            )
            )
        return qs
    
class EntitiesWithoutRelations(viewsets.ReadOnlyModelViewSet):
    queryset = E1_Crm_Entity.objects.annotate(relation_count=Count("triple_set_from_obj")+Count("triple_set_from_subj", filter=Q(triple_set_from_subj__obj__name__regex=r'^(?!.*_index\.xml$).*$'))).filter(relation_count=0)
    serializer_class = LonelyE1CrmEntitySerializer
    filter_class=EntitiesWithoutRelationsFilter
