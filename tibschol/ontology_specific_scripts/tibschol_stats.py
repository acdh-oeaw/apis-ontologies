""" Experimental script to see high level stats on Tibschol database """

from apis_core.apis_relations.models import Triple
from django.apps import apps
from django.db.models import Count, Min


def run():
    """Counts entities in apis_ontology"""
    print("Entity\t\tCount")
    print("----------------------------")
    app_models = apps.get_app_config("apis_ontology").get_models()

    for model in app_models:
        count = model.objects.count()
        print(f"{model.__name__:15s}\t{count:>5}")

    print("----------------------------")
    print(f"Relations\t{Triple.objects.count():>5}")
    duplicate_relations = (
        Triple.objects.values("subj", "obj", "prop")
        .annotate(min_id=Min("id"))
        .annotate(count=Count("id"))
        .filter(count__gt=1)
    )
    print(f"Duplicates\t{len(duplicate_relations):>5}")
