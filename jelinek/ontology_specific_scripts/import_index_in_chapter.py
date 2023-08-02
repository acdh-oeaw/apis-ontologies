from apis_ontology.models import *
import csv

def import_order():
    with open("./apis_ontology/order.csv") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=",")
        next(csvreader, None)
        currentChapter = None
        for row in csvreader:
            if row[0] is not None and len(row[0]) > 0:
                chapters = Chapter.objects.filter(chapter_number=row[0].replace("-", "."))
                if chapters.count() == 1:
                    currentChapter = chapters[0]
                    print("Next chapter: {}".format(row[0]))
                else:
                    print("Error with chapter {}".format(row[0]))
                    currentChapter = None
            if currentChapter is not None and row[2] is not None and len(row[2]) > 0:
                matchingWorks = F1_Work.objects.filter(idno=row[2])
                if (matchingWorks.count() > 0):
                    currentWork = matchingWorks[0]
                    triples = InChapterTriple.objects.filter(subj__id=currentWork.id, obj__id=currentChapter.id)
                    if (triples.count() > 0):
                        triple = triples[0]
                        triple.index_in_chapter = row[1]
                        triple.save()

def run(*args, **options):
    def main_run():
        import_order()
    main_run()