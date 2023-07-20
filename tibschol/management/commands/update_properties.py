import logging

import pandas as pd
from apis_core.apis_relations.models import Property, TempTriple
from django.core.management.base import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--fake", action="store_true", help="Whether to fake or really update"
        )

    def handle(self, *args, **kwargs):
        def delete_property_by_name(prop_name, fake=False):
            try:
                p = Property.objects.get(name=prop_name)
                relations = TempTriple.objects.filter(prop=p)
                print(f"Found {len(relations)} triples for '{prop_name}'.")

                if not fake:
                    p.delete()
            except Property.DoesNotExist:
                print(f"Could not find property {prop_name}.")

        def merge_property_by_name(old_prop_name, new_prop_name, fake=False):
            try:
                old_p = Property.objects.get(name=old_prop_name)
                relations = TempTriple.objects.filter(prop=old_p)
                print(f"Found {len(relations)} triples for '{old_prop_name}'.")

                if not fake:
                    new_p, _ = Property.objects.get_or_create(
                        name=new_prop_name,
                    )
                    for subj_class in old_p.subj_class.all():
                        new_p.subj_class.add(subj_class)

                    for obj_class in old_p.obj_class.all():
                        new_p.obj_class.add(obj_class)

                    for rel in relations:
                        # migrate to the new property
                        TempTriple.objects.create(
                            subj=rel.subj, obj=rel.obj, prop=new_p
                        )

                    # delete old props
                    relations.delete()

            except Property.DoesNotExist:
                print(f"Could not find property {prop_name}.")

        def add_property(prop_name, reverse, subj_class, obj_class, fake=False):
            if fake:
                print("Faking add property.")
                return
            subj_class = ContentType.objects.get(model=subj_class)
            obj_class = ContentType.objects.get(model=obj_class)

            p, _ = Property.objects.get_or_create(
                name=prop_name,
                name_reverse=reverse,
            )
            p.subj_class.add(subj_class)
            p.obj_class.add(obj_class)

        delete_property_by_name("clan relation of", fake=kwargs["fake"])
        delete_property_by_name("cousin of", fake=kwargs["fake"])
        merge_property_by_name("father of", "parent of", fake=kwargs["fake"])
        merge_property_by_name("mother of", "parent of", fake=kwargs["fake"])
        add_property(
            "sibling of", "sibling of", "Person", "Person", fake=kwargs["fake"]
        )
        add_property(
            "contains citations of", "is cited in", "Work", "Work", fake=kwargs["fake"]
        )
        add_property(
            "is copied from", "is source for", "Instance", "Instance", fake=kwargs["fake"]
        )
        add_property(
            "is located within", "contains", "Place", "Place", fake=kwargs["fake"]
        )
