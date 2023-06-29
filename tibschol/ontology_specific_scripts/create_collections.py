from apis_core.apis_metainfo.models import Collection


def create_collections():
    Collection.objects.get_or_create(name="Scholastics")
    Collection.objects.get_or_create(name="Scholastic works")
    Collection.objects.get_or_create(name="Indian authors")
    Collection.objects.get_or_create(name="Indian works")
    Collection.objects.get_or_create(name="Imported")
    Collection.objects.get_or_create(name="Unreviewed")
    Collection.objects.get_or_create(name="Reviewed")


def run(*args, **kwargs):
    create_collections()
