from apis_core.apis_metainfo.models import Collection


def create_collections():
    Collection.objects.get_or_create(name="Scholastics")
    Collection.objects.get_or_create(name="Scholastic works")
    Collection.objects.get_or_create(name="Indian authors")
    Collection.objects.get_or_create(name="Indian works")
    Collection.objects.get_or_create(name="Imported")
    Collection.objects.get_or_create(name="Unreviewed")
    Collection.objects.get_or_create(name="Reviewed")
    Collection.objects.get_or_create(name="Comment review")
    Collection.objects.get_or_create(name="Error import")
    Collection.objects.get_or_create(name="Extant")
    Collection.objects.get_or_create(name="Non-extant")


def run(*args, **kwargs):
    create_collections()
