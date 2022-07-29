from __future__ import annotations

from apis_ontology.models import *
from apis_core.apis_relations.models import Triple, TempTriple, Property



def generate_short_text():

    def short_text_Romane(work):
        relations = Triple.objects.filter(subj=work, prop__name="is expressed in")
        if len(relations) > 0:
            manifestations_and_years = []
            for rel in relations:
                publishers = Triple.objects.filter(prop__name="is publisher of", obj=rel.obj)
                if publishers.count() <= 0:
                    continue
                publishers = [p for p in publishers]
                publishers.sort(key=lambda e: e.temptriple.start_date)
                manifestations_and_years.append((rel, publishers[0], publishers[0].temptriple.start_date))
            manifestations_and_years.sort(key=lambda t: t[2])
            if len(manifestations_and_years) > 0:
                manifestation = manifestations_and_years[0][0].obj
                publisher = manifestations_and_years[0][1]
                places = Triple.objects.filter(subj__id=manifestation.id, prop__name="was published in")
                if places.count() > 0:
                    short = "Erstdruck | {}: {} {}.".format(places[0].obj.name, publisher.subj.name, publisher.temptriple.start_date_written)
                    work.short = short
        return work

    def short_text_Hoerspiele_und_Drehbuecher(work):
        relations = Triple.objects.filter(subj=work, prop__name="R13 is realised in")
        if len(relations) > 0:
            recordings = [r.obj for r in relations]
            recordings.sort(key=lambda r: r.start_date)
            places = Triple.objects.filter(subj=recordings[0], prop__name="has been performed at")
            if len(places) > 0:
                short = "Erstsendung | {} {}".format(recordings[0].start_date_written, places[0].obj.name)
                work.short = short
        return work

    def short_text_Theatertexte(work):
        relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="has been performed in") if rel.obj.performance_type == "UA"]
        if len(relations) > 0:
            perf = relations[0].obj
            institutions = [rel.obj for rel in Triple.objects.filter(prop__name="has been performed at", subj=perf)]
            short = "UA | {} {}".format(perf.start_date_written, ", ".join([inst.name for inst in institutions]))
            work.short = short
        return work

    def short_text_Uebersetzte_Werke(work):
        translations = [t.subj for t in Triple.objects.filter(obj=work, prop__name="is translation of")]
        for translation in translations:
            authors = Triple.objects.filter(prop__name="is author of", obj=translation)
            places = Triple.objects.filter(prop__name="was published in", subj=translation)
            publishers = Triple.objects.filter(prop__name="is publisher of", obj=translation)
            if authors.count() > 0 and places.count() > 0 and publishers.count() > 0:
                short = "<span rendition=\"#it\">{}</span>. Ü: {}. {}: {} {}".format(translation.name, authors[0].subj.name, places[0].obj.name, publishers[0].subj.name, publishers[0].temptriple.start_date_written)
                translation.short = short
                translation.save()
        return work
            
    def main():
        short_text_generators = [
            ("Romane", short_text_Romane), 
            ("Texte für Hörspiele", short_text_Hoerspiele_und_Drehbuecher), 
            ("Drehbücher und Texte für Filme", short_text_Hoerspiele_und_Drehbuecher), 
            ("Theatertexte", short_text_Theatertexte), 
            ("Kompositionen", short_text_Theatertexte), 
            ("Texte für Kompositionen", short_text_Theatertexte), 
            ("Libretti", short_text_Theatertexte), 
            ("Übersetzte Werke", short_text_Uebersetzte_Werke)
            ]
        for short_text_generator in short_text_generators:
            print("_____{}_____".format(short_text_generator[0]))
            works = [rel.subj for rel in Triple.objects.filter(prop__name="is in chapter", obj__name__contains=short_text_generator[0])]
            for work in works:
                print(work.name)
                work = short_text_generator[1](work)
                work.save()
                print("-> {}".format(work.short))
                

    main()


def run(*args, **options):
  
    def main_run():

        generate_short_text()

    main_run()