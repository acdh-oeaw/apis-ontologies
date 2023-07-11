"""QA script to weed out duplicate imports."""
from apis_core.apis_relations.models import Triple
from django.db.models import Count, Min


def run():
    """
    Analyse mistakes in initial import.

    Count triples that have the same subj, obj and prop.
    Keep first record and delete others.
    """
    duplicate_relations = (
        Triple.objects.values("subj", "obj", "prop")
        .annotate(min_id=Min("id"))
        .annotate(count=Count("id"))
        .filter(count__gt=1)
    )
    print(f"Found {len(duplicate_relations)} duplicates. ")
    for record in duplicate_relations:
        subj, obj, prop, min_id = (
            record["subj"],
            record["obj"],
            record["prop"],
            record["min_id"],
        )
        duplicate_instances = Triple.objects.filter(
            subj=subj, obj=obj, prop=prop
        ).exclude(id=min_id)
        print(f"{len(duplicate_instances)} to be deleted. Keeping {min_id}.")
        print(", ".join(f"{d.subj} - {d.obj}" for d in duplicate_instances))
        duplicate_instances.delete()
