from apis_ontology.models import Instance, Work, Place, Person
from apis_core.apis_entities.models import Collection
from tqdm.auto import tqdm


def update_works():
    try:
        INDIAN_WORKS = Collection.objects.get(name="Indian works")
        EXTANT_WORKS = Collection.objects.get(name="Extant")
        NONEXTANT_WORKS = Collection.objects.get(name="Non-extant")
        for w in tqdm(Work.objects.all(), desc="Processing Works"):
            if INDIAN_WORKS in w.collection.all():
                w.original_language = "Sanskrit"
            else:
                w.original_language = "Tibetan"

            if EXTANT_WORKS in w.collection.all():
                w.isExtant = True

            if NONEXTANT_WORKS in w.collection.all():
                w.isExtant = False

            w.save()
    except:
        pass


def update_instances():
    EXTANT = Collection.objects.get(name="Extant")
    NONEXTANT = Collection.objects.get(name="Non-extant")
    for i in tqdm(Instance.objects.all(), desc="Processing Instances"):
        try:
            w = i.work
            if i.tibschol_ref and len(i.tibschol_ref.strip()) > 0:
                i.availability = "available"

            if NONEXTANT in i.collection.all() or NONEXTANT in w.collection.all():
                i.availability = "lost"

            i.save()
        except Exception as e:
            print("Error updating instance", i, repr(e))


def update_persons():
    try:
        INDIAN_AUTHORS = Collection.objects.get(name="Indian authors")

        for p in tqdm(Person.objects.all(), desc="Processing Persons"):
            if INDIAN_AUTHORS in p.collection.all():
                p.nationality = "Indic"
            else:
                p.nationality = "Tibetan"

            p.save()
        INDIAN_AUTHORS.delete()

    except:
        pass


def run():
    update_works()
    update_instances()
    update_persons()
    print("Done")
