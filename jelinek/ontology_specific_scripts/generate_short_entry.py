from __future__ import annotations

from apis_ontology.models import *
from apis_core.apis_relations.models import Triple, TempTriple, Property
from collections import namedtuple



def generate_short_text():

    def _format_page(page):
        if page is None:
            return ""
        elif page == "unpag":
            return page
        else:
            return "S. {}".format(page)

    def _format_issue(issue, date):
        if issue is None:
            return date
        else:
            return "{}/{}".format(issue, date)

    def short_text_Lyrik(work):
        def short_text_Buchpublikationen(work):
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.edition == "first_edition"]
            if len(relations) == 0:
                relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.start_date is not None]
                relations.sort(key=lambda rel: rel.obj.start_date)
            if len(relations) > 0:
                first_manifestation = relations[0].obj
                publishers = Triple.objects.filter(prop__name="is publisher of", obj=first_manifestation)
                publishers = [p for p in publishers]
                if len(publishers) > 0:
                    publisher = publishers[0].subj
                    places = Triple.objects.filter(subj__id=first_manifestation.id, prop__name="was published in")
                    if places.count() > 0:
                        place = places[0].obj
                        short = "{}: {} {}".format(first_manifestation.name, place.name, publisher.name, first_manifestation.start_date_written)
                        if first_manifestation.series is not None:
                            short = short + " ({})".format(first_manifestation.series)
                        work.short = short
                else:
                    print("No publishers")
            else:
                print("no manifestations")
            return work
        def short_text_Einzelgedichte(work):
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.edition == "first_edition"]
            if len(relations) == 0:
                relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.start_date is not None]
                relations.sort(key=lambda rel: rel.obj.start_date)
            if len(relations) == 0:
                relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in")]
                relations.sort(key=lambda rel: rel.obj.id)
            if len(relations) > 0:
                first_manifestation = relations[0].obj
                hosts = Triple.objects.filter(subj=first_manifestation, prop__name="host")
                if hosts.count() > 0:
                    host = hosts[0].obj
                    date_written = first_manifestation.start_date_written
                    if date_written is None:
                        date_written = host.start_date_written
                    short = "Erstdruck | In: {} {}, {}.".format(host.name, date_written, _format_page(first_manifestation.page))
                    work.short = short
                else:
                    if work.idno == "work00875": #Sonderfall: Postkarte
                        editors = [e.obj for e in Triple.objects.filter(prop__name="is editor of", obj=first_manifestation)]
                        if len(editors) > 0:
                            editor = editors[0]
                            short = "{}. {}, {}".format(first_manifestation.name, editor.name, first_manifestation.start_date_written)
                            work.short = short
                    elif work.idno == "work01048": #Sonderfall: Online-Publikation
                        short = "Erstdruck | In: {} ({}) (= {}).".format(first_manifestation.ref_target, first_manifestation.ref_accessed, first_manifestation.series)
                        work.short = short
                    else:
                        print("No publishers")
            else:
                print("no manifestations")
            return work
        if Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Buchpublikationen").count() > 0:
            work = short_text_Buchpublikationen(work)
        elif Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Einzelne Werke").count() > 0:
            work = short_text_Einzelgedichte(work)
        return work

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

    def short_text_Kurzprosa(work):
        relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.edition == "first_edition"]
        if len(relations) == 0:
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.start_date is not None]
            relations.sort(key=lambda rel: rel.obj.start_date)
        if len(relations) > 0:
            first_manifestation = relations[0].obj
            hosts = Triple.objects.filter(subj=first_manifestation, prop__name="host")
            if hosts.count() > 0:
                host = hosts[0].obj
                publishers = Triple.objects.filter(prop__name="is publisher of", obj=host)
                places = Triple.objects.filter(prop__name="was published in", subj=host)
                if publishers.count() > 0 and places.count() > 0:
                    publisher = publishers[0].subj
                    place = places[0].obj
                    editors = Triple.objects.filter(prop__name="is editor of", obj=host)
                    if editors.count() > 0:
                        editor = editors[0].subj
                        if editor.__class__ == E40_Legal_Body:
                            short = "Erstdruck | In: {} (Hg.): {}. {}: {} {}, {}.".format(editor.name, host.name, place.name, publisher.name, first_manifestation.start_date_written, _format_page(first_manifestation.page))
                        elif editor.__class__ == F10_Person:
                            short = "Erstdruck | In: {}, {} (Hg.): {}. {}: {} {}, {}.".format(editor.surname, editor.forename, host.name, place.name, publisher.name, first_manifestation.start_date_written, _format_page(first_manifestation.page))
                    else:
                        short = "Erstdruck | In: {}. {}: {} {}, {}.".format(host.name, place.name, publisher.name, first_manifestation.start_date_written, _format_page(first_manifestation.page))
                    work.short = short
                else:
                    is_journal = Triple.objects.filter(prop__name="p2 has type", subj=host, obj__name="journal")
                    if is_journal.count() > 0:
                        short = "Erstdruck | In: {} {}, {}.".format(host.name, _format_issue(first_manifestation.issue, first_manifestation.start_date_written), _format_page(first_manifestation.page))
                        work.short = short
                    else:
                        print("No journal")
            else:
                is_online_publication = Triple.objects.filter(prop__name="p2 has type", subj=first_manifestation, obj__name="onlinePublication")
                if is_online_publication.count() > 0:
                    short = "Erstdruck | In: {} ({}), datiert mit {} (= {}).".format(first_manifestation.ref_target, first_manifestation.ref_accessed, first_manifestation.start_date_written, first_manifestation.series)
                    work.short = short
                else:
                    print("No hosts")
        else:
            print("No manifestations")
        return work

    def short_text_Essays(work):
        relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.edition == "first_edition"]
        if len(relations) == 0:
            relations_reversed = [rel for rel in Triple.objects.filter(obj=work, prop__name="is translation of") if rel.subj.edition == "first_edition"]
            RelInv = namedtuple("RelInv", "obj prop subj")
            relations = [RelInv(obj=rel.subj, prop=rel.prop, subj=rel.obj) for rel in relations_reversed]
        if len(relations) == 0:
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.start_date is not None]
            relations.sort(key=lambda rel: rel.obj.start_date)
        if len(relations) == 0:
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in")]
            relations.sort(key=lambda rel: rel.obj.id)
        if len(relations) == 0:
            relations_reversed = [rel for rel in Triple.objects.filter(obj=work, prop__name="is translation of") if rel.subj.start_date is not None]
            RelInv = namedtuple("RelInv", "obj prop subj")
            relations = [RelInv(obj=rel.subj, prop=rel.prop, subj=rel.obj) for rel in relations_reversed]
            relations.sort(key=lambda rel: rel.obj.start_date)

        if len(relations) > 0:
            first_manifestation = relations[0].obj
            hosts = Triple.objects.filter(subj=first_manifestation, prop__name="host")
            if hosts.count() > 0:
                host = hosts[0].obj
                publishers = Triple.objects.filter(prop__name="is publisher of", obj=host)
                places = Triple.objects.filter(prop__name="was published in", subj=host)
                if publishers.count() > 0 and places.count() > 0:
                    publisher = publishers[0].subj
                    place = places[0].obj
                    editors = Triple.objects.filter(prop__name="is editor of", obj=host)
                    if editors.count() > 0:
                        editor = editors[0].subj
                        if editor.__class__ == E40_Legal_Body:
                            short = "Erstdruck | In: {} (Hg.): {}. {}: {} {}, {}.".format(editor.name, host.name, place.name, publisher.name, first_manifestation.start_date_written, _format_page(first_manifestation.page))
                        elif editor.__class__ == F10_Person:
                            short = "Erstdruck | In: {}, {} (Hg.): {}. {}: {} {}, {}.".format(editor.surname, editor.forename, host.name, place.name, publisher.name, first_manifestation.start_date_written, _format_page(first_manifestation.page))
                    else:
                        short = "Erstdruck | In: {}. {}: {} {}, {}.".format(host.name, place.name, publisher.name, first_manifestation.start_date_written, _format_page(first_manifestation.page))
                    work.short = short
                else:
                    is_journal = Triple.objects.filter(prop__name="p2 has type", subj=host, obj__name="journal")
                    if is_journal.count() > 0:
                        short = "Erstdruck | In: {} {}, {}.".format(host.name, _format_issue(first_manifestation.issue, first_manifestation.start_date_written), _format_page(first_manifestation.page))
                        work.short = short
                    else:
                        is_playbill = Triple.objects.filter(prop__name="p2 has type", subj=host, obj__name="playbill")
                        if is_playbill.count() > 0:
                            short = "Erstdruck | In: {}, {}.".format(host.name, host.start_date_written)
                            work.short = short
                        else:
                            is_supplement = Triple.objects.filter(prop__name="p2 has type", subj=host, obj__name="supplement")
                            if is_supplement.count() > 0:
                                hosts = Triple.objects.filter(subj=host, prop__name="host")
                                if hosts.count() > 0:
                                    host_host = hosts[0].obj
                                    publishers = Triple.objects.filter(prop__name="is publisher of", obj=host_host)
                                    places = Triple.objects.filter(prop__name="was published in", subj=host_host)
                                    if publishers.count() > 0 and places.count() > 0:
                                        publisher = publishers[0].subj
                                        place = places[0].obj
                                        short = "Erstdruck | In: {} {}. {}: {} {}.".format(host.name, host_host.name, place.name, publisher.name, host_host.start_date_written)
                                        work.short = short
                                    else:
                                        print("No publishers or places")
                                else:
                                    print("No host_hosts")
                            else:
                                editors = Triple.objects.filter(prop__name="is editor of", obj=host)
                                if editors.count() > 0:
                                    editor = editors[0].subj
                                    short = "Erstdruck | In: {} (Hg.): {}, {}".format(editor.name, host.name, _format_page(first_manifestation.page))
                                    work.short = short
                                else:
                                    is_analytic_publication = Triple.objects.filter(prop__name="p2 has type", subj=host, obj__name="analyticPublication")
                                    if is_analytic_publication.count() > 0:
                                        hosts = Triple.objects.filter(subj=host, prop__name="host")
                                        if hosts.count() > 0:
                                            host_host = hosts[0].obj
                                            is_journal = Triple.objects.filter(prop__name="p2 has type", subj=host_host, obj__name="journal")
                                            if is_journal.count() > 0:
                                                short = "Erstdruck | In: {}. In: {}, {}.".format(host.name, host_host.name, host_host.start_date_written)
                                                work.short = short
                                            else:
                                                publishers = Triple.objects.filter(prop__name="is publisher of", obj=host_host)
                                                places = Triple.objects.filter(prop__name="was published in", subj=host_host)
                                                if publishers.count() > 0 and places.count() > 0:
                                                    publisher = publishers[0].subj
                                                    place = places[0].obj
                                                    short = "Erstdruck | In: {} {}. {}: {} {}.".format(host.name, host_host.name, place.name, publisher.name, host_host.start_date_written)
                                                    work.short = short
                                                else:
                                                    print("No publishers or places")
                                        else:
                                            print("No host_hosts")
            else:
                is_online_publication = Triple.objects.filter(prop__name="p2 has type", subj=first_manifestation, obj__name="onlinePublication")
                if is_online_publication.count() > 0:
                    short = "Erstdruck | In: {} ({}), datiert mit {} (= {}).".format(first_manifestation.ref_target, first_manifestation.ref_accessed, first_manifestation.start_date_written, first_manifestation.series)
                    work.short = short
                else:
                    is_book = Triple.objects.filter(prop__name="p2 has type", subj=first_manifestation, obj__name="book")
                    if is_book.count() > 0:
                        publishers = Triple.objects.filter(prop__name="is publisher of", obj=first_manifestation)
                        places = Triple.objects.filter(prop__name="was published in", subj=first_manifestation)
                        if publishers.count() > 0 and places.count() > 0:
                            publisher = publishers[0].subj
                            place = places[0].obj
                            manifestation_name = ""
                            if len(first_manifestation.name) > 0:
                                manifestation_name = "{}. ".format(first_manifestation.name)
                            short = "Erstdruck | {}{}: {} {}".format(manifestation_name, place.name, publisher.name, first_manifestation.start_date_written)
                            work.short = short
                        else:
                            print("No publishers")
                    else:
                        is_flyer = Triple.objects.filter(prop__name="p2 has type", subj=first_manifestation, obj__name="flyer")
                        if is_flyer.count() > 0:
                            short = "Flugblatt."
                            work.short = short
                        else:
                            is_unpublished = Triple.objects.filter(prop__name="p2 has type", subj=first_manifestation, obj__name="unpublished")
                            if is_unpublished.count() > 0:
                                short = "Unpubliziert."
                                work.short = short
                            print("Not unpublished")
        else:
            relations = [r for r in Triple.objects.filter(subj__name=work.name, prop__name="R13 is realised in") if r.subj.idno == work.idno]
            if len(relations) > 0:
                first_recording = min(relations, key=lambda r: r.obj.start_date).obj
                places = [p.obj for p in Triple.objects.filter(subj=first_recording, prop__name="has been performed at")]
                if len(places) > 0:
                    place = places[0]
                    short = "Erstsendung | {}, {} ({})".format(place.name, first_recording.start_date_written, first_recording.note)
                    work.short = short
                else:
                    print("No place")
            else:
                print("No recordings") #assume: unpublished
                short = "Unpubliziert."
                work.short = short
        return work

    def short_text_Hoerspiele(work):
        relations = Triple.objects.filter(subj=work, prop__name="R13 is realised in")
        if len(relations) > 0:
            recordings = [r.obj for r in relations]
            recordings.sort(key=lambda r: r.start_date)
            places = Triple.objects.filter(subj=recordings[0], prop__name="has been performed at")
            if len(places) > 0:
                short = "Erstsendung | {} {}".format(recordings[0].start_date_written, places[0].obj.name)
                work.short = short
        return work

    def short_text_Drehbuecher(work):
        # Kinostart, Erstsendung, Erstabdruck, UA, Erstpräsentation
        short = ""
        relations = Triple.objects.filter(subj=work, prop__name__in=["R13 is realised in", "is expressed in", "has been performed in"])
        if len(relations) > 0:
            recordings = [r.obj for r in relations if r.obj.start_date is not None]
            recordings.sort(key=lambda r: r.start_date)
            if len(recordings) > 0:
                first = recordings[0]
                if first.__class__ == F26_Recording:
                    places = Triple.objects.filter(subj=first, prop__name="has been performed at")
                    if len(places) > 0:
                        short = "Erstsendung | {} {}".format(first.start_date_written, places[0].obj.name)
                elif first.__class__ == F3_Manifestation_Product_Type:
                    editors = Triple.objects.filter(obj=first, prop__name="is editor of")
                    editor_string = ""
                    if len(editors) > 0:
                        editor_string = "Hg. v. {}. ".format(" und ".join([e.subj.name for e in editors]))
                    publishers = Triple.objects.filter(obj=first, prop__name="is publisher of")
                    places = Triple.objects.filter(subj=first, prop__name="was published in")
                    if len(publishers) > 0 and len(places) > 0:
                        short = "Erstdruck | {}. {}{}: {} {}.".format(first.name, editor_string, places[0].obj.name, publishers[0].subj.name, first.start_date_written)
                    elif first.ref_target is not None:
                        short = "Erstdruck | {}, datiert mit {} (= {})".format(first.ref_target, first.start_date_written, first.series)
                elif first.__class__ == F31_Performance:
                    if first.performance_type == "cinemarelease":
                        short = "Kinostart | {}".format(first.start_date_written)
                    elif first.performance_type == "UA":
                        institutions = [rel.obj for rel in Triple.objects.filter(prop__name="has been performed at", subj=first)]
                        short = "UA | {} {}".format(first.start_date_written, ", ".join([inst.name for inst in institutions]))
                    else:
                        short = ""
                else:
                    short = ""
        work.short = short
        return work

    def short_text_Theatertexte(work):
        def short_text_Einzeltext(work):
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="has been performed in") if rel.obj.performance_type == "UA"]
            if len(relations) == 0:
                relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="has been performed in") if rel.obj.start_date is not None]
                relations.sort(key=lambda rel: rel.obj.start_date)
            if len(relations) > 0:
                perf = relations[0].obj
                institutions = [rel.obj for rel in Triple.objects.filter(prop__name="has been performed at", subj=perf)]
                short = "UA | {} {}".format(perf.start_date_written, ", ".join([inst.name for inst in institutions]))
                work.short = short
            return work
        def short_text_Sammelband(work):
            relations = [r for r in Triple.objects.filter(subj=work, prop__name="is expressed in")if r.obj.start_date is not None]
            if len(relations) > 0:
                relations.sort(key=lambda rel: rel.obj.start_date)
                first_manifestation = relations[0].obj
                publishers = Triple.objects.filter(prop__name="is publisher of", obj=first_manifestation)
                publishers = [p for p in publishers]
                if len(publishers) > 0:
                    publisher = publishers[0].subj
                    places = Triple.objects.filter(subj__id=first_manifestation.id, prop__name="was published in")
                    if places.count() > 0:
                        place = places[0].obj
                        short = "{}: {} {}".format(place.name, publisher.name, first_manifestation.start_date_written)
                        if first_manifestation.series is not None:
                            short = short + " ({})".format(first_manifestation.series)
                        work.short = short
            return work
        if Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Sammelbände").count() > 0:
            work = short_text_Sammelband(work)
        elif Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Einzelne Werke").count() > 0:
            work = short_text_Einzeltext(work)
        return work

    def short_text_Uebersetzte_Werke(work):
        translations = [t.subj for t in Triple.objects.filter(obj=work, prop__name="is translation of")]
        for translation in translations:
            authors = Triple.objects.filter(prop__name="is author of", obj=translation)
            places = Triple.objects.filter(prop__name="was published in", subj=translation)
            publishers = Triple.objects.filter(prop__name="is publisher of", obj=translation)
            if authors.count() > 0 and places.count() > 0 and publishers.count() > 0:
                short = "<i>{}</i>. Ü: {}. {}: {} {}".format(translation.name, authors[0].subj.name, places[0].obj.name, publishers[0].subj.name, publishers[0].temptriple.start_date_written)
                translation.short = short
                translation.save()
        return work

    def short_text_Interviews(work):
        work = short_text_Essays(work)
        if work.short is None:
            work.short = ""
        new_short = work.short.replace("Erstdruck | ", "")
        interviewers = [t.subj for t in Triple.objects.filter(obj=work, prop__name="is interviewer of")]
        point = "."
        if work.name.endswith((".", "!", "?", ".\"")):
            point = ""
        short = ""
        if len(interviewers) > 0:
            short = "{}".format(new_short)
        else:
            short = "{}".format(point, new_short)
        work.short = short
        return work

    def short_text_Installationen(work):
        relations = Triple.objects.filter(subj=work, prop__name="R13 is realised in")
        if len(relations) > 0:
            recordings = [r.obj for r in relations]
            recordings.sort(key=lambda r: r.start_date)
            places = Triple.objects.filter(subj=recordings[0], prop__name="has been performed at")
            if len(places) > 0:
                short = "Erstpräsentation | {} {}".format(recordings[0].start_date_written, places[0].obj.name)
                work.short = short
        return work

    def short_text_Herausgeberin(work):
        relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.edition == "first_edition"]
        if len(relations) == 0:
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.start_date is not None]
            relations.sort(key=lambda rel: rel.obj.start_date)
        if len(relations) > 0:
            first_manifestation = relations[0].obj
            publishers = Triple.objects.filter(prop__name="is publisher of", obj=first_manifestation)
            publishers = [p for p in publishers]
            editors = Triple.objects.filter(prop__name="is editor of", obj=first_manifestation)
            editors = [p.subj for p in editors]
            editor_string = " / ".join(["{}, {}".format(e.surname, e.forename) for e in editors])
            if len(publishers) > 0:
                publisher = publishers[0].subj
                places = Triple.objects.filter(subj__id=first_manifestation.id, prop__name="was published in")
                if places.count() > 0:
                    place = places[0].obj
                    short = "<b>{} (Hg.): <i>{}.</i></b> {}: {} {}".format(editor_string, first_manifestation.name, place.name, publisher.name, first_manifestation.start_date_written)
                    if first_manifestation.series is not None:
                        short = short + " ({})".format(first_manifestation.series)
                    work.short = short
            else:
                print("No publishers")
        else:
            print("no manifestations")
        return work
            
    def main():
        short_text_generators = [
            # ("Lyrik", short_text_Lyrik), 
            # ("Kurzprosa", short_text_Kurzprosa), 
            # ("Essayistische Texte, Reden und Statements", short_text_Essays), 
            # ("Romane", short_text_Romane), 
            # ("Texte für Hörspiele", short_text_Hoerspiele), 
            # ("Drehbücher und Texte für Filme", short_text_Drehbuecher), 
            # ("Theatertexte", short_text_Theatertexte), 
            # ("Kompositionen", short_text_Theatertexte), 
            # ("Texte für Kompositionen", short_text_Theatertexte), 
            # ("Libretti", short_text_Theatertexte), 
            # ("Übersetzte Werke", short_text_Uebersetzte_Werke),
            # ("Übersetzungen", short_text_Essays),
            # ("Texte für Installationen und Projektionen, Fotoarbeiten", short_text_Installationen),
            ("Herausgeberin- und Redaktionstätigkeit", short_text_Herausgeberin),
            # ("Interviews", short_text_Interviews)
            ]
        for short_text_generator in short_text_generators:
            print("_____{}_____".format(short_text_generator[0]))
            works = [rel.subj for rel in Triple.objects.filter(prop__name="is in chapter", obj__name__contains=short_text_generator[0])]
            for work in works:
                print(work.name)
                work = short_text_generator[1](work)
                if work.short is not None:  
                    work.short = work.short.replace("..", ".").replace(" datiert mit None", "").replace(" None", "").replace(", .", ".").replace(" ,", ",")
                work.save()
                print("-> {}".format(work.short))
                

    main()


def run(*args, **options):
  
    def main_run():

        generate_short_text()

    main_run()