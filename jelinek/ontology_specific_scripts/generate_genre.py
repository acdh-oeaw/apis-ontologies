from __future__ import annotations

from apis_ontology.models import *
from apis_core.apis_relations.models import Triple, TempTriple, Property

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

def generate_genre():

    def main():
        jelinek = F10_Person.objects.get(name="Elfriede Jelinek", pers_id="pers00000")
        for work in  F1_Work.objects.all():
        # for work in  F1_Work.objects.filter(name="Sind schreibende Frauen Fremde in dieser Welt? Die Begegnung."):
            xml_files = [t.obj for t in Triple.objects.filter(prop__name="was defined primarily in", subj=work)]
            if len(xml_files) > 0:
                for xml_file in xml_files:
                    if "001_Lyrik" in xml_file.file_path:
                        work.genre = "Lyrik"
                    elif "002_Romane" in xml_file.file_path:
                        work.genre = "Romane"
                    elif "003_Kurzprosa" in xml_file.file_path:
                        work.genre = "Kurzprosa"
                    elif "004_Theatertexte" in xml_file.file_path:
                        work.genre = "Theatertexte"
                    elif "005_TextefürHörspiele" in xml_file.file_path:
                        work.genre = "Texte für Hörspiele"
                    elif "006_DrehbücherundTextefürFilme" in xml_file.file_path:
                        work.genre = "Drehbücher und Texte für Filme"
                    elif "007_Kompositionen" in xml_file.file_path:
                        work.genre = "Kompositionen"
                    elif "008_TextefürKompositionen" in xml_file.file_path:
                        work.genre = "Texte für Kompositionen"
                    elif "009_LibrettiOper" in xml_file.file_path:
                        work.genre = "Libretti"
                    elif "010_LibrettiBallett" in xml_file.file_path:
                        work.genre = "Libretti"
                    elif "011_EssayistischeTexteRedenundStatements" in xml_file.file_path:
                        work.genre = "Essayistische Texte, Reden und Statements"
                    elif "012_Übersetzungen/001_Lyrik" in xml_file.file_path:
                        work.genre = "Übersetzungen, Lyrik"
                    elif "012_Übersetzungen/002_Prosatexte" in xml_file.file_path:
                        work.genre = "Übersetzungen, Prosatexte"
                    elif "012_Übersetzungen/003_Theaterstücke" in xml_file.file_path:
                        work.genre = "Übersetzungen, Theaterstücke"
                    elif "013_TextefürInstallationenundProjektionenFotoarbeiten" in xml_file.file_path:
                        work.genre = "Texte für Installationen und Projektionen, Fotoarbeiten"
                    elif "014_HerausgeberinundRedaktionstätigkeit" in xml_file.file_path:
                        work.genre = "Herausgeberin- und Redaktionstätigkeit"
                    elif "003_Interviews" in xml_file.file_path:
                        work.genre = "Interviews"
                        add_jelinek_as_interviewee(work, jelinek)
                    elif "0004_Bearbeitungenvo" in xml_file.file_path:
                        work.genre = "Bearbeitungen von anderen"
                    elif "0006_Sekundärliterat" in xml_file.file_path:
                        work.genre = "Sekundärliteratur"
                        work = add_names_for_seklit(work)
                    elif "0005_Würdigungen" in xml_file.file_path:
                        work.genre = "Würdigungen"
                    elif "0007_SendungenundFilmporträts" in xml_file.file_path:
                        work.genre = "Sendungen und Filmporträts"
            else:
                xml_files = [t.obj for t in Triple.objects.filter(prop__name="data read from file", subj=work)]
                for xml_file in xml_files:
                    if "0006_Sekundärliterat" in xml_file.file_path:
                        work.genre = "Sekundärliteratur"
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