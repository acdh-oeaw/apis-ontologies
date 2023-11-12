from __future__ import annotations

from apis_ontology.models import *
from apis_core.apis_relations.models import Triple, TempTriple, Property
from lxml import etree

def create_triple(entity_subj, entity_obj, prop):
    try:
        db_result = TempTriple.objects.get_or_create(
            subj=entity_subj,
            obj=entity_obj,
            prop=prop
        )
        if db_result[1] is True:
            print(f"created triple: subj: {entity_subj}, obj: {entity_obj}, prop: {prop.name}")
        else:
            print("triple already exists")
        return db_result[0]
    except:
        print(f"An error occurred with the triple creation: subj: {entity_subj}, obj: {entity_obj}, prop: {prop.name}")

    

def add_jelinek_as_interviewee(work, jelinek):
    create_triple(
        entity_subj=jelinek,
        entity_obj=work,
        prop=Property.objects.get(name="is interviewee of")
    )

def add_names_for_seklit(work):
    if work.name is None or len(work.name) == 0:
        manifestations = [t.obj for t in Triple.objects.filter(prop__name="is expressed in", subj=work)]
        if len(manifestations) == 1:
            work.name = manifestations[0].name
        elif len(set([m.name for m in manifestations if not (m.name is None or len(m.name) == 0)])) == 1:
            work.name = list(set([m.name for m in manifestations if not (m.name is None or len(m.name) == 0)]))[0]
        print("Set work {} name to {}".format(work.idno, work.name))
    return work

def identify_seklit_subsection(work, file):
    seklit_ana = ["VIDEO", "AUDIO-CD UND CD-ROM", "ONLINE", "TEXTE ZUR AUFFÜHRUNG", "SEKUNDÄRLITERATUR", "TEXTE ÜBER DIE PRODUKTION", "TEXTE ÜBER WERK", "GESPRÄCH ZUR AUFFÜHRUNG"]
    berichterstattung_ana = ["REZENSIONEN", "BERICHTE", "BUCHREZENSIONEN", "VORBERICHTE", "CHRONOLOGIE EINES SKANDALS", "WEITERE REAKTIONEN", 
                             "Zur ORF-Kultursendung K1 - KULTUR LIVE", "WERKREZENSIONEN", "KOMMENTAR", "WEITERE INTERVIEWS", "ANKÜNDIGUNGEN", 
                             "Szenische Realisierung bei überGrenzen 97, Podewil, Berlin, 3.10.1997 (zusammen mit Aufenthalt)", "Szenische Realisierung im WUK Wien, 20.2.1985",
                             "REZENSIONEN ZUR PRÄSENTATION BEI DEN FILMFESTSPIELEN IN CANNES 2001", "BERICHTE"]
    try:
        root = etree.fromstring(file.file_content)
        xpath = f"//*[@type='seklitSubsection' and .//*[@target='seklit:{work.idno}']]/@ana"
        ana = root.xpath(xpath)
        if ana and len(ana) > 0:
            if ana[0] in seklit_ana:
                work.genre = "Sekundärliteratur"
            elif ana[0] in berichterstattung_ana:
                work.genre = "Berichterstattung"
            else:
                work.genre = "Sekundärliteratur"
    except:
        print(f"Parse error in work {work.name}")
    
    
    return work

def generate_genre():
    def main():
        jelinek = F10_Person.objects.get(pers_id="pers00000")
        for work in F1_Work.objects.all():
        # for work in F1_Work.objects.filter(idno__contains="seklit"):
        # for work in  F1_Work.objects.filter(name="Sind schreibende Frauen Fremde in dieser Welt? Die Begegnung."):
            xml_files = [t.obj for t in Triple.objects.filter(prop__name="was defined primarily in", subj=work) if "index.xml" not in t.obj.name]
            if len(xml_files) > 0:
                for xml_file in xml_files:
                    if "001_Werke/012_Übersetzungen/001_Lyrik" in xml_file.file_path:
                        work.genre = "Übersetzungen, Lyrik"
                    elif "001_Werke/012_Übersetzungen/002_Prosatexte" in xml_file.file_path:
                        work.genre = "Übersetzungen, Prosatexte"
                    elif "001_Werke/012_Übersetzungen/003_Theaterstücke" in xml_file.file_path:
                        work.genre = "Übersetzungen, Theaterstücke"
                    elif "001_Werke/001_Lyrik" in xml_file.file_path:
                        work.genre = "Lyrik"
                    elif "001_Werke/002_Romane" in xml_file.file_path:
                        work.genre = "Romane"
                    elif "001_Werke/003_Kurzprosa" in xml_file.file_path:
                        work.genre = "Kurzprosa"
                    elif "001_Werke/004_Theatertexte" in xml_file.file_path:
                        work.genre = "Theatertexte"
                    elif "001_Werke/005_TextefürHörspiele" in xml_file.file_path:
                        work.genre = "Texte für Hörspiele"
                    elif "001_Werke/006_DrehbücherundTextefürFilme" in xml_file.file_path:
                        work.genre = "Drehbücher und Texte für Filme"
                    elif "001_Werke/007_Kompositionen" in xml_file.file_path:
                        work.genre = "Kompositionen"
                    elif "001_Werke/008_TextefürKompositionen" in xml_file.file_path:
                        work.genre = "Texte für Kompositionen"
                    elif "001_Werke/009_LibrettiOper" in xml_file.file_path:
                        work.genre = "Libretti"
                    elif "001_Werke/010_LibrettiBallett" in xml_file.file_path:
                        work.genre = "Libretti"
                    elif "001_Werke/011_EssayistischeTexteRedenundStatements" in xml_file.file_path:
                        work.genre = "Essayistische Texte, Reden und Statements"
                    elif "001_Werke/013_TextefürInstallationenundProjektionenFotoarbeiten" in xml_file.file_path:
                        work.genre = "Texte für Installationen und Projektionen, Fotoarbeiten"
                    elif "001_Werke/014_HerausgeberinundRedaktionstätigkeit" in xml_file.file_path:
                        work.genre = "Herausgeberin- und Redaktionstätigkeit"
                    elif "003_Interviews" in xml_file.file_path:
                        work.genre = "Interviews"
                        add_jelinek_as_interviewee(work, jelinek)
                    elif "0004_Bearbeitungenvo" in xml_file.file_path:
                        work.genre = "Bearbeitungen von anderen"
                    elif "0006_Sekundärliterat" in xml_file.file_path:
                        work = identify_seklit_subsection(work, xml_file)
                        work = add_names_for_seklit(work)
                    elif "0005_Würdigungen" in xml_file.file_path:
                        work.genre = "Würdigungen"
                    elif "0007_SendungenundFilmporträts" in xml_file.file_path:
                        work.genre = "Sendungen und Filmporträts"
            else:
                xml_files = [t.obj for t in Triple.objects.filter(prop__name="data read from file", subj=work) if "index.xml" not in t.obj.name]
                for xml_file in xml_files:
                    if "0006_Sekundärliterat" in xml_file.file_path:
                        work = identify_seklit_subsection(work, xml_file)
                        work = add_names_for_seklit(work)
                    elif "0005_Würdigungen" in xml_file.file_path:
                        work.genre = "Würdigungen"
                    elif "0004_Bearbeitungenvo" in xml_file.file_path:
                        work.genre = "Bearbeitungen von anderen"
                    elif "0007_SendungenundFilmporträts" in xml_file.file_path:
                        work.genre = "Sendungen und Filmporträts"
            work.save()
            

                

    main()


def run(*args, **options):
  
    def main_run():

        generate_genre()

    main_run()