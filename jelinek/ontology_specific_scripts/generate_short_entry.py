from __future__ import annotations

from apis_ontology.models import *
from apis_core.apis_relations.models import Triple, TempTriple, Property
from collections import namedtuple

import re
import datetime
from lxml import etree

def format_name(entity):
    if entity.__class__ == F10_Person:
        return "{}, {}".format(entity.surname, entity.forename)
    else:
        return "{}".format(entity.name)

def generate_manifestation_short(manifestation):
    relations = [rel for rel in Triple.objects.filter(subj=manifestation)]
    relations = relations + [rel for rel in Triple.objects.filter(obj=manifestation)]
    types = [r.obj.name for r in relations if r.prop.name == "p2 has type"]
    authors = [r.subj for r in relations if r.prop.name == "is author of" and r.subj.name != "Elfriede Jelinek"]
    editors = [r.subj for r in relations if r.prop.name == "is editor of"]
    translators = [r.subj for r in relations if r.prop.name == "is translator of"]
    places = [r.obj.name for r in relations if r.prop.name == "was published in"]
    publishers = [r.subj.name for r in relations if r.prop.name == "is publisher of"]
    hosts = [r.obj for r in relations if r.prop.name == "has host" and r.subj.id == manifestation.id]
    short = ""
    if len(editors) > 0:
        short = short + " / ".join(["{}".format(format_name(author)) for author in editors]) + " (Hg.): "
    if len(authors) > 0:
        short = short + " / ".join(["{}".format(format_name(author)) for author in authors]) + ": "
    short = short + "{}. ".format(manifestation.name)

    if len(translators) > 0:
        short = short + " (Ü: " + ", ".join(["{}".format(author.name) for author in translators]) + ")"

    if len(hosts) > 0:
        short = short + "In: "
        host_relations = [rel for rel in Triple.objects.filter(subj=hosts[0])]
        host_relations = host_relations + [rel for rel in Triple.objects.filter(obj=hosts[0])]
        host_authors = [r.subj for r in host_relations if r.prop.name == "is author of" and r.subj.name != "Elfriede Jelinek"]
        host_editors = [r.subj for r in host_relations if r.prop.name == "is editor of"]
        host_translators = [r.subj for r in host_relations if r.prop.name == "is translator of"]
        host_publishers = [r.subj.name for r in host_relations if r.prop.name == "is publisher of"]
        host_places = [r.obj.name for r in host_relations if r.prop.name == "was published in"]
        if len(host_editors) > 0:
            short = short + " / ".join(["{}".format(format_name(author)) for author in host_editors]) + " (Hg.): "
        if len(host_authors) > 0:
            short = short + " / ".join(["{}".format(format_name(author)) for author in host_authors]) + ": "
        short = short + "{}. ".format(hosts[0].name)
        if hosts[0].untertitel is not None:
            short = short + "{}. ".format(hosts[0].untertitel)
        if len(host_places) > 0:
            short = short + "{}: ".format(host_places[0])
        if len(host_publishers) > 0:
            short = short + "{} ".format(host_publishers[0])
        if hosts[0].start_date_written is not None:
            short = short + "{}".format(hosts[0].start_date_written)
        if hosts[0].series is not None and hosts[0].series != manifestation.series:
            short = short + " (= {})".format(hosts[0].series)
        if hosts[0].page is not None:
            short = short + ", S. {}".format(hosts[0].page)

    if len(places) > 0:
        short = short + "{}: ".format(places[0])
    if len(publishers) > 0:
        short = short + "{} ".format(publishers[0])
    if manifestation.start_date_written is not None:
        short = short + "{}".format(manifestation.start_date_written)
    if manifestation.series is not None:
        short = short + " (= {})".format(manifestation.series)
    if manifestation.page is not None:
        short = short + ", S. {}".format(manifestation.page)

    manifestation.short = short
    return manifestation


def generate_short_text():

    def _format_page(page):
        if page is None:
            return ""
        elif page == "unpag":
            return page
        else:
            return "S. {}".format(page)

    def _format_issue(issue, date, scopeStyle=None):
        if issue is None:
            return date
        else:
            if scopeStyle is not None and scopeStyle == "annual":
                return "{}/{}".format(issue, date)
            else:
                return "{} ({})".format(issue, date)

    def get_sorted_manifestations_for_work(work, include_translations=False):
        relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.edition == "first_edition"]
        if len(relations) == 0 and include_translations:
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is original for translation") if rel.obj.edition == "first_edition"]
            
        if len(relations) == 0:
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in") if rel.obj.start_date is not None]
            relations.sort(key=lambda rel: rel.obj.start_date)
        if len(relations) == 0:
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is expressed in")]
            relations.sort(key=lambda rel: rel.obj.id)
        if len(relations) == 0 and include_translations:
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is original for translation") if rel.obj.start_date is not None]
            
            relations.sort(key=lambda rel: rel.obj.start_date)
        return relations

    def get_erstdruck_string(manifestation):
        triples = [triple for triple in manifestation.triple_set_from_subj.all()]
        types = [triple.obj.name for triple in manifestation.triple_set_from_subj.all() if triple.prop.name == "p2 has type"]
        if len(types) > 0:
            if types[0] == "onlinePublication":
                return "Erstveröffentlichung"
        return "Erstdruck"

    def short_text_Lyrik(work):
        def short_text_Buchpublikationen(work):
            relations = get_sorted_manifestations_for_work(work)
            has_translator = False
            if work.index_in_chapter >= 7: ## koniec/ende and Gesammelte Gedichte/Poésies Complètes have translations
                        relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="is original for translation") if rel.obj.start_date is not None]
                        # RelInv = namedtuple("RelInv", "obj prop subj")
                        # relations = [RelInv(obj=rel.subj, prop=rel.prop, subj=rel.obj) for rel in relations_reversed]
                        relations.sort(key=lambda rel: rel.obj.start_date)
                        has_translator = True
            if len(relations) > 0:
                first_manifestation = relations[0].obj
                publishers = Triple.objects.filter(prop__name="is publisher of", obj=first_manifestation)
                publishers = [p for p in publishers]
                translator_string = ""
                if has_translator:
                    translators = Triple.objects.filter(prop__name__in=["is translator of", "is editor of"], obj=first_manifestation)
                    translators = [t.subj for t in translators]
                    translator_string = "Ü: {}. ".format(", ".join([t.name for t in translators]))
                if len(publishers) > 0:
                    publisher = publishers[0].subj
                    places = Triple.objects.filter(subj__id=first_manifestation.id, prop__name="was published in")
                    if places.count() > 0:
                        place = places[0].obj
                        short = "<b><i>{}.</i></b> {}{}: {} {}".format(first_manifestation.name, translator_string, place.name, publisher.name, first_manifestation.start_date_written)
                        if first_manifestation.name == "o. T.":
                           short = "<b>{} <i>{}.</i></b> {}{}: {} {}".format(first_manifestation.name, work.untertitel, translator_string, place.name, publisher.name, first_manifestation.start_date_written)
                        if first_manifestation.series is not None:
                            short = short + " (= {})".format(first_manifestation.series)
                        short = short + "."
                        work.short = short
                else:
                    print("No publishers")                        
            else:
                print("no manifestations")
            return work
        def short_text_Einzelgedichte(work):
            relations = get_sorted_manifestations_for_work(work)
            if len(relations) > 0:
                if len(relations) > 1:
                    print("Multiple first editions")
                    filtered_relations = [r for r in relations if len([t for t in Triple.objects.filter(subj=r.obj, prop__name="has host") if t.obj.bibl_id == "bibl_000657"]) > 0]
                    if len(filtered_relations) > 0:
                        relations = filtered_relations
                first_manifestation = relations[0].obj
                hosts = Triple.objects.filter(subj=first_manifestation, prop__name="has host")
                if hosts.count() > 0:
                    host = hosts[0].obj
                    date_written = first_manifestation.start_date_written
                    if date_written is None:
                        date_written = host.start_date_written
                    is_book = Triple.objects.filter(prop__name="p2 has type", subj=host, obj__name="book")
                    if is_book.count() > 0:
                        publishers = Triple.objects.filter(prop__name="is publisher of", obj=host)
                        publishers = [p for p in publishers]
                        if len(publishers) > 0:
                            publisher = publishers[0].subj
                            places = Triple.objects.filter(subj__id=host.id, prop__name="was published in")
                            if places.count() > 0:
                                place = places[0].obj
                                short = "{} | In: {}. {}: {} {}, {}.".format(get_erstdruck_string(first_manifestation), host.name, place.name, publisher.name, date_written, _format_page(first_manifestation.page))
                                if host.name == "o. T.":
                                    short = "{} | In: {} {}. {}: {} {}, {}.".format(get_erstdruck_string(first_manifestation), host.name, host.untertitel,place.name, publisher.name, date_written, _format_page(first_manifestation.page))
                                work.short = short
                    else:
                        short = "{} | In: {} {}, {}.".format(get_erstdruck_string(first_manifestation), host.name, date_written, _format_page(first_manifestation.page))
                        work.short = short
                    short = "{} | In: {} {}, {}".format(get_erstdruck_string(first_manifestation), host.name, date_written, _format_page(first_manifestation.page))
                    if host.series is not None:
                            short = short + " (= {})".format(host.series)
                    short = short + "."
                    work.short = short
                else:
                    if work.idno == "work00875": #Sonderfall: Postkarte
                        short = "{}, {}".format(first_manifestation.name, first_manifestation.start_date_written)
                        work.short = short
                    elif work.idno == "work01048": #Sonderfall: Online-Publikation
                        short = "{} | In: {} ({}) (= {}).".format(get_erstdruck_string(first_manifestation), first_manifestation.ref_target, first_manifestation.ref_accessed, first_manifestation.series)
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
                publishers.sort(key=lambda e: e.temptriple.start_date if e.temptriple.start_date is not None else datetime.datetime.now().date())
                manifestations_and_years.append((rel, publishers[0], publishers[0].temptriple.start_date))
            manifestations_and_years.sort(key=lambda t: t[2] if t[2] is not None else datetime.datetime.now().date())
            if len(manifestations_and_years) > 0:
                manifestation = manifestations_and_years[0][0].obj
                publisher = manifestations_and_years[0][1]
                places = Triple.objects.filter(subj__id=manifestation.id, prop__name="was published in")
                if places.count() > 0:
                    short = "{} | {}: {} {}.".format(get_erstdruck_string(manifestation), places[0].obj.name, publisher.subj.name, publisher.temptriple.start_date_written)
                    work.short = short
            else:
                all_manifestations = [r.obj for r in relations]
                all_manifestations.sort(key=lambda m: m.start_date if m.start_date is not None else datetime.datetime.now().date())
                first_manifestation = all_manifestations[0]
                short = "{} | In: {} ({}), datiert mit {} (= {}).".format(get_erstdruck_string(first_manifestation), first_manifestation.ref_target, first_manifestation.ref_accessed, first_manifestation.start_date_written, first_manifestation.series)
                work.short = short
        return work

    def short_text_Kurzprosa(work):
        relations = get_sorted_manifestations_for_work(work)
        if len(relations) > 0:
            first_manifestation = relations[0].obj
            hosts = Triple.objects.filter(subj=first_manifestation, prop__name="has host")
            if hosts.count() > 0:
                host = hosts[0].obj
                publishers = Triple.objects.filter(prop__name="is publisher of", obj=host)
                places = Triple.objects.filter(prop__name="was published in", subj=host)
                if publishers.count() > 0 and places.count() > 0:
                    publisher = publishers[0].subj
                    place = places[0].obj
                    editors = Triple.objects.filter(prop__name="is editor of", obj=host)
                    start_date = first_manifestation.start_date_written
                    if start_date is None:
                        start_date = host.start_date_written
                    if editors.count() > 0:
                        editor = editors[0].subj
                        if editor.__class__ == E40_Legal_Body:
                            short = "{} | In: {} (Hg.): {}. {}: {} {}, {}.".format(get_erstdruck_string(first_manifestation), editor.name, host.name, place.name, publisher.name, start_date, _format_page(first_manifestation.page))
                        elif editor.__class__ == F10_Person:
                            short = "{} | In: {}, {} (Hg.): {}. {}: {} {}, {}.".format(get_erstdruck_string(first_manifestation), editor.surname, editor.forename, host.name, place.name, publisher.name, start_date, _format_page(first_manifestation.page))
                    else:
                        short = "{} | In: {}. {}: {} {}, {}.".format(get_erstdruck_string(first_manifestation), host.name, place.name, publisher.name, start_date, _format_page(first_manifestation.page))
                    work.short = short
                else:
                    is_journal = Triple.objects.filter(prop__name="p2 has type", subj=host, obj__name__in=["journal", "newspaper"])
                    if is_journal.count() > 0:
                        short = "{} | In: {} {}, {}.".format(get_erstdruck_string(first_manifestation), host.name, _format_issue(first_manifestation.issue, first_manifestation.start_date_written, host.scope_style), _format_page(first_manifestation.page))
                        work.short = short
                    else:
                        print("No journal")
            else:
                is_online_publication = Triple.objects.filter(prop__name="p2 has type", subj=first_manifestation, obj__name="onlinePublication")
                if is_online_publication.count() > 0:
                    short = "{} | In: {} ({}), datiert mit {} (= {}).".format(get_erstdruck_string(first_manifestation), first_manifestation.ref_target, first_manifestation.ref_accessed, first_manifestation.start_date_written, first_manifestation.series)
                    work.short = short
                else:
                    print("No hosts")
        else:
            print("No manifestations")
        return work

    def short_text_Essays(work, is_translation=False):
        def short_text_Einzeln(work):
            relations = get_sorted_manifestations_for_work(work, include_translations=True)
            if len(relations) > 0:
                first_manifestation = relations[0].obj
                hosts = Triple.objects.filter(subj=first_manifestation, prop__name="has host")
                if hosts.count() > 0:
                    host = hosts[0].obj
                    publishers = Triple.objects.filter(prop__name="is publisher of", obj=host)
                    places = Triple.objects.filter(prop__name="was published in", subj=host)
                    if publishers.count() > 0 and places.count() > 0:
                        publisher = publishers[0].subj
                        place = places[0].obj
                        editors = Triple.objects.filter(prop__name="is editor of", obj=host)
                        first_date = first_manifestation.start_date_written
                        if first_date is None:
                            first_date = host.start_date_written
                        if editors.count() > 0:
                            editor = editors[0].subj
                            if editor.__class__ == E40_Legal_Body:
                                short = "{} | In: {} (Hg.): {}. {}: {} {}, {}.".format(get_erstdruck_string(first_manifestation), editor.name, host.name, place.name, publisher.name, first_date, _format_page(first_manifestation.page))
                            elif editor.__class__ == F10_Person:
                                short = "{} | In: {}, {} (Hg.): {}. {}: {} {}, {}.".format(get_erstdruck_string(first_manifestation), editor.surname, editor.forename, host.name, place.name, publisher.name, first_date, _format_page(first_manifestation.page))
                        else:
                            short = "{} | In: {}. {}: {} {}, {}.".format(get_erstdruck_string(first_manifestation), host.name, place.name, publisher.name, first_date, _format_page(first_manifestation.page))
                        work.short = short
                    else:
                        is_journal = Triple.objects.filter(prop__name="p2 has type", subj=host, obj__name__in=["journal", "newspaper"])
                        if is_journal.count() > 0:
                            short = "Erstdruck | In: {} {}, {}.".format(host.name, _format_issue(first_manifestation.issue, first_manifestation.start_date_written, host.scope_style), _format_page(first_manifestation.page))
                            work.short = short
                        else:
                            is_playbill = Triple.objects.filter(prop__name="p2 has type", subj=host, obj__name="playbill")
                            if is_playbill.count() > 0:
                                short = "Erstdruck | In: {}, {}.".format(host.name, host.start_date_written)
                                work.short = short
                            else:
                                is_supplement = Triple.objects.filter(prop__name="p2 has type", subj=host, obj__name__in=["supplement", "booklet"])
                                if is_supplement.count() > 0:
                                    hosts = Triple.objects.filter(subj=host, prop__name="has host")
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
                                            hosts = Triple.objects.filter(subj=host, prop__name="has host")
                                            if hosts.count() > 0:
                                                host_host = hosts[0].obj
                                                is_journal = Triple.objects.filter(prop__name="p2 has type", subj=host_host, obj__name__in=["journal", "newspaper"])
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
                        short = "Erstveröffentlichung | In: {} ({}), datiert mit {} (= {}).".format(first_manifestation.ref_target, first_manifestation.ref_accessed, first_manifestation.start_date_written, first_manifestation.series)
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
                                short = "<b><i>{}</i></b>{}: {} {}.".format(manifestation_name, place.name, publisher.name, first_manifestation.start_date_written)
                                if is_translation:
                                    short = "Erstdruck | {}: {} {}.".format(place.name, publisher.name, first_manifestation.start_date_written)
                                
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
                    first_recording = min(relations, key=lambda r: r.obj.start_date if r.obj.start_date is not None else datetime.datetime.now().date()).obj
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

        def short_text_Sammelbaende(work):
            relations = get_sorted_manifestations_for_work(work, include_translations=True)
            if len(relations) > 0:
                first_manifestation = relations[0].obj
                publishers = Triple.objects.filter(prop__name="is publisher of", obj=first_manifestation)
                places = Triple.objects.filter(prop__name="was published in", subj=first_manifestation)
                if publishers.count() > 0 and places.count() > 0:
                    publisher = publishers[0].subj
                    place = places[0].obj
                    manifestation_name = ""
                    subtitle = ""
                    if len(first_manifestation.name) > 0:
                        manifestation_name = "{}. ".format(first_manifestation.name)
                    else:
                        manifestation_name = "{}. ".format(work.name)
                    if first_manifestation.untertitel is not None and len (first_manifestation.untertitel) > 0:
                        subtitle = "{}. ".format(first_manifestation.untertitel)
                    short = "<b><i>{}</i></b>{}{}: {} {}.".format(manifestation_name, subtitle, place.name, publisher.name, first_manifestation.start_date_written)
                    work.short = short
            return work

        if Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Sammelbände").count() > 0:
            work = short_text_Sammelbaende(work)
        else:
            work = short_text_Einzeln(work)
        return work

    def short_text_Hoerspiele(work):
        relations = Triple.objects.filter(subj=work, prop__name="R13 is realised in")
        if len(relations) > 0:
            recordings = [r.obj for r in relations if r.obj.start_date is not None]
            recordings.sort(key=lambda r: r.start_date)
            recording = recordings[0]
            institutions = [re.sub(r"\<.*?\>", "", rel.obj.content) for rel in Triple.objects.filter(prop__name="has note", subj=recording) if "type=\"broadcaster\"" in rel.obj.content]
            if len(institutions) == 0:
                institutions = [rel.obj.name for rel in Triple.objects.filter(prop__name="has been performed at", subj=recording)]
            if len(institutions) > 0:
                short = "Erstsendung | {} {}".format(recordings[0].start_date_written, ", ".join(institutions))
                short = re.sub(r"\(.*?\)", "", short)
                work.short = short
                
        return work

    def short_text_Drehbuecher(work):
        # Kinostart, Erstsendung, Erstabdruck, UA, Erstpräsentation
        short = ""
        relations = Triple.objects.filter(subj=work, prop__name__in=["R13 is realised in", "is expressed in", "has been performed in"])
        if len(relations) > 0:
            recordings = [r.obj for r in relations if r.obj.start_date is not None]
            recordings.sort(key=lambda r: r.start_date)
            if work.idno == "work00104":
                recordings = [r.obj for r in relations if r.obj.__class__ == F31_Performance and r.obj.performance_type == "EP" ]
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
                        short = "{} | {}. {}{}: {} {}.".format(get_erstdruck_string(first), first.name, editor_string, places[0].obj.name, publishers[0].subj.name, first.start_date_written)
                    elif first.ref_target is not None:
                        short = "{} | {}, datiert mit {} (= {})".format(get_erstdruck_string(first), first.ref_target, first.start_date_written, first.series)
                elif first.__class__ == F31_Performance:
                    if first.performance_type == "cinemarelease":
                        short = "Kinostart | {}".format(first.start_date_written)
                    elif first.performance_type == "UA":
                        institutions = [rel.obj for rel in Triple.objects.filter(prop__name="has been performed at", subj=first)]
                        short = "UA | {} {}".format(first.start_date_written, ", ".join([inst.name for inst in institutions]))
                    elif first.performance_type == "UA_Film":
                        institutions = [rel.obj for rel in Triple.objects.filter(prop__name="has been performed at", subj=first)]
                        short = "UA | {} {}".format(", ".join([inst.name for inst in institutions]), first.start_date_written)
                    elif first.performance_type == "EP":
                        institutions = [rel.obj for rel in Triple.objects.filter(prop__name="has been performed at", subj=first)]
                        notes = [rel.obj for rel in Triple.objects.filter(prop__name="has note", subj=first) if "rendition=\"#inline\"" in rel.obj.content]
                        relevant_notes = " ".join([n.content for n in notes])
                        short = "Erstpräsentation | {} {} {}".format(first.start_date_written, ", ".join([inst.name for inst in institutions]), relevant_notes)
                    else:
                        short = ""
                else:
                    short = ""
        work.short = short
        return work

    def short_text_Bearbeitungen(work):
        # Kinostart, Erstsendung, Erstabdruck, UA, Erstpräsentation
        short = ""
        relations = Triple.objects.filter(subj=work, prop__name__in=["R13 is realised in", "is expressed in", "has been performed in"])
        if len(relations) > 0:
            recordings = [r.obj for r in relations]
            recordings.sort(key=lambda r: r.start_date if (r.start_date is not None) else datetime.datetime.now().date())
            if len(recordings) > 0:
                first = recordings[0]
                if first.__class__ == F26_Recording:
                    places = Triple.objects.filter(subj=first, prop__name="has been performed at")
                    if len(places) > 0:
                        short = "Erstsendung | {} {}".format(first.start_date_written, places[0].obj.name)
                elif first.__class__ == F3_Manifestation_Product_Type:
                    hosts = Triple.objects.filter(subj=first, prop__name="host")
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
                                    short = "{} | In: {} (Hg.): {}. {}: {} {}, {}.".format(get_erstdruck_string(first), editor.name, host.name, place.name, publisher.name, first.start_date_written, _format_page(first.page))
                                elif editor.__class__ == F10_Person:
                                    short = "{} | In: {}, {} (Hg.): {}. {}: {} {}, {}.".format(get_erstdruck_string(first), editor.surname, editor.forename, host.name, place.name, publisher.name, first.start_date_written, _format_page(first.page))
                            else:
                                short = "{} | In: {}. {}: {} {}, {}.".format(get_erstdruck_string(first), host.name, place.name, publisher.name, first.start_date_written, _format_page(first.page))
                    else:
                        editors = Triple.objects.filter(obj=first, prop__name="is editor of")
                        editor_string = ""
                        if len(editors) > 0:
                            editor_string = "Hg. v. {}. ".format(" und ".join([e.subj.name for e in editors]))
                        publishers = Triple.objects.filter(obj=first, prop__name="is publisher of")
                        places = Triple.objects.filter(subj=first, prop__name="was published in")
                        if len(publishers) > 0 and len(places) > 0:
                            short = "{} | {}. {}{}: {} {}.".format(get_erstdruck_string(first), first.name, editor_string, places[0].obj.name, publishers[0].subj.name, first.start_date_written)
                        elif first.ref_target is not None:
                            short = "{} | {}, datiert mit {} (= {})".format(get_erstdruck_string(first), first.ref_target, first.start_date_written, first.series)
                elif first.__class__ == F31_Performance:
                    if first.performance_type == "cinemarelease":
                        short = "Kinostart | {}".format(first.start_date_written)
                    elif first.performance_type == "UA":
                        institutions = [rel.obj for rel in Triple.objects.filter(prop__name="has been performed at", subj=first)]
                        short = "UA | {} {}".format(first.start_date_written, ", ".join([inst.name for inst in institutions]))
                    elif first.performance_type == "EP":
                        institutions = [rel.obj for rel in Triple.objects.filter(prop__name="has been performed at", subj=first)]
                        short = "Erstpräsentation | {} {}".format(first.start_date_written, ", ".join([inst.name for inst in institutions]))
                    else:
                        short = ""
                else:
                    short = ""
        else:
            xml_doc = [t.obj for t in Triple.objects.filter(subj=work, prop__name="was defined primarily in")]
            if len(xml_doc) > 0:
                xml_doc = xml_doc[0]
                root = etree.fromstring(xml_doc.file_content)
                
                production = root.xpath("//*[@type='production']")
                if len(production) > 0:
                    short = "".join([t for t in production[0].itertext()])
                    short = " ".join(short.split())
        work.short = short
        return work

    def short_text_Theatertexte(work):
        def short_text_Einzeltext(work):
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="has been performed in") if rel.obj.performance_type == "UA"]
            # if len(relations) == 0:
            #     relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="has been performed in") if rel.obj.start_date is not None]
            #     relations.sort(key=lambda rel: rel.obj.start_date)
            if len(relations) > 0:
                perf = relations[0].obj
                institutions = [re.sub(r"\<.*?\>", "", rel.obj.content) for rel in Triple.objects.filter(prop__name="has note", subj=perf) if "type=\"institutions\"" in rel.obj.content]
                if len(institutions) == 0:
                    institutions = [rel.obj.name for rel in Triple.objects.filter(prop__name="has been performed at", subj=perf)]
                short = "UA | {} {}".format(perf.start_date_written, ", ".join([inst for inst in institutions]))
                short = re.sub(r"\n", " ", short,0,re.MULTILINE)
                short = re.sub(r" *\(.*?\)", "", short,0,re.MULTILINE)
                short = re.sub(r", *$", "", short)
                
                work.short = short
            else:
                work = short_text_Essays(work)
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
                        subtitle = ""
                        if first_manifestation.note is not None and "type=\"subtitle\"" in first_manifestation.note:
                            subtitle = " " + re.sub(r"<.*?>", "", first_manifestation.note)
                        short = "<b><i>{}.</i></b>{} {}: {} {}.".format(first_manifestation.name, subtitle, place.name, publisher.name, first_manifestation.start_date_written)
                        if first_manifestation.series is not None:
                            short = short + " (= {})".format(first_manifestation.series)
                        work.short = short
            return work
        if Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Sammelbände").count() > 0:
            work = short_text_Sammelband(work)
        elif Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Einzelne Werke").count() > 0:
            work = short_text_Einzeltext(work)
        else:
            work = short_text_Einzeltext(work)
        return work
    
    def short_text_Uebersetzungen(work):
        def short_test_Uebersetzte_Theaterstuecke(work):
            relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="has been performed in") if rel.obj.performance_type == "UA"]
            if len(relations) == 0:
                relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="has been performed in") if rel.obj.start_date is not None]
                relations.sort(key=lambda rel: rel.obj.start_date)
            if len(relations) > 0:
                perf = relations[0].obj
                institutions = [re.sub(r"\<.*?\>", "", rel.obj.content) for rel in Triple.objects.filter(prop__name="has note", subj=perf) if "type=\"institutions\"" in rel.obj.content]
                if len(institutions) == 0:
                    institutions = [rel.obj.name for rel in Triple.objects.filter(prop__name="has been performed at", subj=perf)]
                directors = [rel.subj for rel in Triple.objects.filter(obj=perf, prop__name="is director of")]
                short = "EA | {} {}".format(perf.start_date_written, ", ".join([inst for inst in institutions]))
                if (len(directors) > 0):
                    short = short + ", I: {}".format(directors[0].name)
               
                short = re.sub(r"\n", " ", short,0,re.MULTILINE)
                short = re.sub(r" *\(.*?\)", "", short,0,re.MULTILINE)
                short = re.sub(r", *$", "", short)
                
                work.short = short
            return work
        if Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Theaterstücke").count() > 0:
            work = short_test_Uebersetzte_Theaterstuecke(work)
        else:
            work = short_text_Essays(work, is_translation=True)
        return work

    def short_text_Uebersetzte_Werke(work):
        def short_text_Sammelbaende(work):
            relations = [t.obj for t in Triple.objects.filter(subj=work, prop__name="is original for translation") if t.obj.start_date is not None]
            if len(relations) > 0:
                first_manifestation = relations[0]
                publishers = Triple.objects.filter(prop__name="is publisher of", obj=first_manifestation)
                publishers = [p for p in publishers]
                authors = Triple.objects.filter(prop__name="is author of", obj=first_manifestation)
                authors = [p.subj for p in authors]
                if len(publishers) > 0 and len(authors) > 0:
                    publisher = publishers[0].subj
                    author = authors[0]
                    places = Triple.objects.filter(subj__id=first_manifestation.id, prop__name="was published in")
                    if places.count() > 0:
                        place = places[0].obj
                        short = "<b>{}: <i>{}.</i></b> {}: {} {}".format(author.name, first_manifestation.name, place.name, publisher.name, first_manifestation.start_date_written)
                        if first_manifestation.series is not None:
                            short = short + " (= {})".format(first_manifestation.series)
                        short = short + "."
                        work.short = short
            return work
        def short_text_single(work):
            translations = [t.obj for t in Triple.objects.filter(subj=work, prop__name="is original for translation")]
            for translation in translations:
                authors = Triple.objects.filter(prop__name="is author of", obj=translation)
                places = Triple.objects.filter(prop__name="was published in", subj=translation)
                publishers = Triple.objects.filter(prop__name="is publisher of", obj=translation)
                if authors.count() > 0 and places.count() > 0 and publishers.count() > 0:
                    short = "<i>{}</i>. Ü: {}. {}: {} {}".format(translation.name, authors[0].subj.name, places[0].obj.name, publishers[0].subj.name, publishers[0].temptriple.start_date_written)
                    translation.short = short
                    translation.save()
            return work
        if Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Sammelbaende").count() > 0:
            work = short_text_Sammelbaende(work)
        else:
            work = short_text_single(work)
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
            interviewer_string = (" / ").join(["{}, {}".format(i.surname, i.forename) for i in interviewers])
            short = "<b>{}: <i>{}{}</i></b> {}".format(interviewer_string, work.name, point, new_short)
        else:
            short = "{}{} {}".format(work.name, point, new_short)
        short = short.replace("N., N.", "N. N.")
        work.short = short
        return work

    def short_text_Seklit(work):
        work = short_text_Essays(work)
        if work.short is None:
            work.short = ""
        new_short = work.short.replace("Erstdruck | ", "")
        interviewers = [t.subj for t in Triple.objects.filter(obj=work, prop__name="is editor of")]
        point = "."
        if work.name.endswith((".", "!", "?", ".\"")):
            point = ""
        short = ""
        if len(interviewers) > 0:
            interviewer_string = (" / ").join(["{}, {}".format(i.surname, i.forename) for i in interviewers])
            short = "{}: <i>{}{}</i> {}".format(interviewer_string, work.name, point, new_short)
        else:
            short = "{}{} {}".format(work.name, point, new_short)
        work.short = short
        return work

    def short_text_Installationen(work):
        relations = [rel for rel in Triple.objects.filter(subj=work, prop__name="has been performed in") if rel.obj.performance_type == "EP"]
        if len(relations) > 0:
            recordings = [r.obj for r in relations]
            recordings.sort(key=lambda r: r.start_date if r.start_date is not None else datetime.datetime.now().date())
            first = recordings[0]
            institutions = [re.sub(r"\<.*?\>", "", rel.obj.content) for rel in Triple.objects.filter(prop__name="has note", subj=first) if "type=\"institutions\"" in rel.obj.content]
            if len(institutions) == 0:
                institutions = [rel.obj.name for rel in Triple.objects.filter(prop__name="has been performed at", subj=first)]
            institutions = list(set(institutions))
            short = "Erstpräsentation | {} {}".format(first.start_date_written, ", ".join([inst for inst in institutions]))
            short = re.sub(r"\n", " ", short,0,re.MULTILINE)
            short = re.sub(r" *\(.*?\)", "", short,0,re.MULTILINE)
            short = re.sub(r", *$", "", short)
            short = re.sub(r"  +", " ", short)
            work.short = short
        return work

    def short_text_Herausgeberin(work):
        relations = get_sorted_manifestations_for_work(work)
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
                        short = short + " (= {})".format(first_manifestation.series)
                    short = short + "."
                    work.short = short
            else:
                print("No publishers")
        else:
            print("no manifestations")
        return work

    def short_text_Performance(performance):
        places = [t.obj for t in Triple.objects.filter(subj=performance, prop__name="has been performed at")]
        directors = [t.subj for t in Triple.objects.filter(obj=performance, prop__name="is director of")]
        if len(places) > 0 and len(directors) > 0:
            short = "{} {}, I: {}".format(performance.start_date_written, places[0].name, directors[0].name)
            performance.short = short
        return performance

    def short_text_Honour(work):
        def short_text_Preise(work):
            xml_doc = [t.obj for t in Triple.objects.filter(subj=work, prop__name="was defined primarily in")]
            if len(xml_doc) > 0:
                xml_doc = xml_doc[0]
                root = etree.fromstring(xml_doc.file_content)
                production = root.xpath("//*[@ana='shortinfo']")
                if len(production) > 0:
                    short = "".join([t for t in production[0].itertext()])
                    short = " ".join(short.split())
                    work.short = short
            return work
        def short_text_Symposien(work):
            xml_doc = [t.obj for t in Triple.objects.filter(subj=work, prop__name="was defined primarily in")]
            if len(xml_doc) > 0:
                xml_doc = xml_doc[0]
                root = etree.fromstring(xml_doc.file_content)
                organizers = root.xpath("//*[@type='head_section']//*[@role='organizer']")
                if len(organizers) > 0:
                    if len(organizers) > 1:
                        organizerstring = ", ".join([o.text for o in organizers[:-1]]) + " & " + organizers[-1].text
                        short = "VeranstalterInnen | {}".format(organizerstring)
                    elif len(organizers) == 1:
                        organizerstring = organizers[0].text
                        short = "VeranstalterIn | {}".format(organizerstring)
                    work.short = short
            return work
        work.short = ""
        if Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Preise und Preisverleihungen").count() > 0:
            work = short_text_Preise(work)
        elif Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Symposien und Schwerpunkte").count() > 0:
            work = short_text_Symposien(work)
        return work

    def short_text_Sendungen(work):
        def short_text_RadioFernsehen(work):
            xml_doc = [t.obj for t in Triple.objects.filter(subj=work, prop__name="was defined primarily in")]
            if len(xml_doc) > 0:
                xml_doc = xml_doc[0]
                root = etree.fromstring(xml_doc.file_content)
                head_section = root.xpath("//*[@type='head_section']/*[name()='head']")
                if len(head_section) > 0:
                    xmlString = "".join([t for t in head_section[0].itertext() if t != work.name])
                    short = "<i>{}</i> {}".format(work.name, xmlString.lstrip())
                    short = " ".join(short.split())
                    short = re.sub(r" \(.*?\)", "", short)
                    work.short = short
            return work
        def short_text_Filme(work):
            xml_doc = [t.obj for t in Triple.objects.filter(subj=work, prop__name="was defined primarily in")]
            if len(xml_doc) > 0:
                xml_doc = xml_doc[0]
                root = etree.fromstring(xml_doc.file_content)
                head_section = root.xpath("//*[@type='head_section']")
                if len(head_section) > 0:
                    head_section = head_section[0]
                    directors = head_section.xpath(".//*[@role='director']")
                    if len(directors) == 0:
                        directors = head_section.xpath(".//*[@role='production']")
                    director = ", ".join([d.text for d in directors])
                    date = [d.text for d in head_section.xpath(".//*") if d.tag.endswith("date")][0]
                    first_row = "{}: {} ({})".format(director, work.name, date)
                    if len(director) == 0:
                        first_row = "{} ({})".format(work.name, date)
                    short = first_row
                    performances = [t.obj for t in Triple.objects.filter(subj=work, prop__name="has been performed in")]
                    performances.sort(key=lambda e: e.start_date if e.start_date is not None else datetime.datetime.now().date())
                    if len(performances) > 0:
                        second_row = "Film-Premiere | {}".format(performances[0].start_date_written)
                        short = short + "$" + second_row
                    short = " ".join(short.split())
                    work.short = short
            return work
        work.short = ""
        if Triple.objects.filter(subj=work, prop__name="is in chapter", obj__name="Filme").count() > 0:
            work = short_text_Filme(work)
        else:
            work = short_text_RadioFernsehen(work)
        return work


    def main():
        short_text_generators = [
            ("Lyrik", short_text_Lyrik, "1.1"), 
            ("Kurzprosa", short_text_Kurzprosa, "1.3"), 
            ("Essayistische Texte, Reden und Statements", short_text_Essays, "1.10"), 
            ("Romane", short_text_Romane, "1.2"), 
            ("Texte für Hörspiele", short_text_Hoerspiele, "1.5"), 
            ("Drehbücher und Texte für Filme", short_text_Drehbuecher, "1.6"), 
            ("Theatertexte", short_text_Theatertexte, "1.4"), 
            ("Kompositionen", short_text_Theatertexte, "1.7"), 
            ("Texte für Kompositionen", short_text_Theatertexte, "1.8"), 
            ("Libretti", short_text_Theatertexte, "1.9"), 
            ("Übersetzte Werke", short_text_Uebersetzte_Werke, "2"),
            ("Übersetzungen", short_text_Uebersetzungen, "1.11"),
            ("Texte für Installationen und Projektionen, Fotoarbeiten", short_text_Installationen, "1.12"),
            ("Herausgeberin- und Redaktionstätigkeit", short_text_Herausgeberin, "1.13"),
            ("Interviews", short_text_Interviews, "3"),
            ("Bearbeitungen von anderen", short_text_Bearbeitungen, "4"),
            ("Sekundärliteratur", short_text_Seklit, "6"),
            ("Würdigungen", short_text_Honour, "5"),
            ("Sendungen und Filmporträts", short_text_Sendungen, "7"),
            
            ]
        for short_text_generator in short_text_generators:
            print("_____{}_____".format(short_text_generator[0]))
            works = [rel.subj for rel in Triple.objects.filter(prop__name="is in chapter", obj__name__contains=short_text_generator[0]) if rel.obj.chapter_number == short_text_generator[2]]
            for work in works:
                if len(work.name) > 0:
                    print(work.name)
                    try:
                        work = short_text_generator[1](work)
                    except Exception as e:
                        print("An error occurred during short entry generation")
                    if work.short is not None:  
                        work.short = work.short.replace("..", ".").replace(" datiert mit None", "").replace(" None", "").replace(", .", ".").replace(" ,", ",")
                    else:
                        print("-...-")
                    work.save()
                    print("-> {}".format(work.short))

        # Generate short entries for performances
        print("_____Performances_____")
        performances = F31_Performance.objects.all()
        for p in performances:
            print(p.name)
            p = short_text_Performance(p)
            if p.short is not None:  
                p.short = p.short.replace("..", ".").replace(" datiert mit None", "").replace(" None", "").replace(", .", ".").replace(" ,", ",")
            p.save()
            print("-> {}".format(p.short))

        # Generate short entries for manifestations
        print("_____Manifestations_____")
        manifestations = F3_Manifestation_Product_Type.objects.all()
        for p in manifestations:
            print(p.name)
            p = generate_manifestation_short(p)
            if p.short is not None:  
                p.short = p.short.replace("..", ".").replace(" datiert mit None", "").replace(" None", "").replace(", .", ".").replace(" ,", ",")
            p.save()
            print("-> {}".format(p.short))
                

    main()


def run(*args, **options):
  
    def main_run():

        generate_short_text()

    main_run()