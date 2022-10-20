from __future__ import annotations

from apis_ontology.models import *
from apis_core.apis_relations.models import Triple, TempTriple, Property



def generate_genre():

    def main():
        for work in  F1_Work.objects.all():
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
                    elif "0006_Sekundärliterat" in xml_file.file_path:
                        work.genre = "Sekundärliteratur"
                    elif "0005_Würdigungen" in xml_file.file_path:
                        work.genre = "Würdigungen"
            else:
                xml_files = [t.obj for t in Triple.objects.filter(prop__name="data read from file", subj=work)]
                for xml_file in xml_files:
                    if "0006_Sekundärliterat" in xml_file.file_path:
                        work.genre = "Sekundärliteratur"
                    elif "0005_Würdigungen" in xml_file.file_path:
                        work.genre = "Würdigungen"
            work.save()
            

                

    main()


def run(*args, **options):
  
    def main_run():

        generate_genre()

    main_run()