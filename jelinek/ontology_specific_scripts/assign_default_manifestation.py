from __future__ import annotations

from apis_ontology.models import *
from apis_core.apis_relations.models import Triple, TempTriple, Property
from collections import namedtuple

import re
import datetime
from lxml import etree

def assign_default_manifestations():

    def get_sorted_manifestations_for_work(work, include_translations=False):
        relations = [rel.obj for rel in Triple.objects.filter(subj=work, prop__name__in=["is expressed in", "is reported in"]) if rel.obj.edition == "first_edition"]
        if len(relations) == 0 and include_translations:
            relations = [rel.subj for rel in Triple.objects.filter(obj=work, prop__name="is translation of") if rel.subj.edition == "first_edition"]
        if len(relations) == 0:
            relations = [rel.obj for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.start_date is not None]
            relations.sort(key=lambda rel: rel.start_date)
        if len(relations) == 0:
            relations = [rel.obj for rel in Triple.objects.filter(subj=work, prop__name="is expressed in")]
            relations.sort(key=lambda rel: rel.id)
        if len(relations) == 0 and include_translations:
            relations = [rel.subj for rel in Triple.objects.filter(obj=work, prop__name="is translation of") if rel.subj.start_date is not None]
            relations.sort(key=lambda rel: rel.start_date)
        return relations
    def get_sorted_performances_for_work(work, included_types=None):
        relations = [rel.obj for rel in Triple.objects.filter(subj=work, obj__self_contenttype=ContentType.objects.get_for_model(F31_Performance))]
        if included_types is not None:
            relations = filter(lambda r: r.performance_type in included_types, relations)
        elif len(relations) >= 1:
            relations = filter(lambda r: r.start_date is not None, relations)
            relations.sort(key=lambda rel: rel.start_date)
        return relations
    def get_sorted_recordings_for_work(work, included_types=None):
        relations = [rel.obj for rel in Triple.objects.filter(subj=work, obj__self_contenttype=ContentType.objects.get_for_model(F26_Recording))]
        if included_types is not None:
            relations = filter(lambda r: r.recording_type in included_types, relations)
        elif len(relations) >= 1:
            relations = filter(lambda r: r.start_date is not None, relations)
            relations.sort(key=lambda rel: rel.start_date)
        return relations

    

    def main():
        default_manifestation_generator = [
            ("Lyrik", get_sorted_manifestations_for_work, "1.1"), 
            ("Kurzprosa", get_sorted_manifestations_for_work, "1.3"), 
            ("Essayistische Texte, Reden und Statements", get_sorted_manifestations_for_work, "1.10"), 
            ("Romane", get_sorted_manifestations_for_work, "1.2"), 
            ("Texte für Hörspiele", get_sorted_manifestations_for_work, "1.5"), 
            ("Drehbücher und Texte für Filme", get_sorted_manifestations_for_work, "1.6"), 
            ("Theatertexte", get_sorted_manifestations_for_work, "1.4"), 
            ("Kompositionen", get_sorted_manifestations_for_work, "1.7"), 
            ("Texte für Kompositionen", get_sorted_manifestations_for_work, "1.8"), 
            ("Libretti", get_sorted_manifestations_for_work, "1.9"), 
            ("Übersetzte Werke", get_sorted_manifestations_for_work, "2"),
            ("Übersetzungen", get_sorted_manifestations_for_work, "1.11"),
            ("Texte für Installationen und Projektionen, Fotoarbeiten", get_sorted_manifestations_for_work, "1.12"),
            ("Herausgeberin- und Redaktionstätigkeit", get_sorted_manifestations_for_work, "1.13"),
            ("Interviews", get_sorted_manifestations_for_work, "3"),
            ("Bearbeitungen von anderen", get_sorted_manifestations_for_work, "4"),
            ("Sekundärliteratur", get_sorted_manifestations_for_work, "6"),
            ("Würdigungen", get_sorted_manifestations_for_work, "5"),
            ("Sendungen und Filmporträts", get_sorted_manifestations_for_work, "7"),
            
            ]
        for default_generator in default_manifestation_generator:
            print("_____{}_____".format(default_generator[0]))
            works = [rel.subj for rel in Triple.objects.filter(prop__name="is in chapter", obj__name__contains=default_generator[0]) if rel.obj.chapter_number == default_generator[2] and rel.subj.start_date_written is None]
            for work in works:
                if len(work.name) > 0:
                    manifestations = default_generator[1](work)
                    if manifestations is None or len(manifestations) == 0:
                        print(work.name)
                    else:
                        first_manifestation = manifestations[0]
                        if first_manifestation.start_date_written is None:
                            hosts = [t.obj for t in first_manifestation.triple_set_from_subj.filter(prop__name="has host") if t.obj.start_date is not None]
                            if len(hosts) > 0:
                                hosts.sort(key=lambda h: h.start_date )
                                first_manifestation = hosts[0]
                        work.start_date_written = first_manifestation.start_date_written
                        work.save()
                

    main()


def run(*args, **options):
  
    def main_run():

        assign_default_manifestations()

    main_run()