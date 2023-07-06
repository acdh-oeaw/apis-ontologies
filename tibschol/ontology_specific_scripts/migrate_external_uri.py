from apis_core.apis_metainfo.models import Uri
from apis_ontology.models import Instance, Person, Place, Work


def migrate_external_uri_for_entity(entity):
    uris = Uri.objects.filter(root_object_id=entity.id)
    for uri in uris:
        if (uri.domain != "apis default"):
            entity.external_link = uri.uri
            uri.delete()
    entity.save()


def run(*args, **kwargs):
    for work in Work.objects.all():
        migrate_external_uri_for_entity(work)
    for instance in Instance.objects.all():
        migrate_external_uri_for_entity(instance)
    for person in Person.objects.all():
        migrate_external_uri_for_entity(person)
    for place in Place.objects.all():
        migrate_external_uri_for_entity(place)
