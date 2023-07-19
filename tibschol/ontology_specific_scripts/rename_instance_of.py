"""
Clean up of properties and triples
    Removes the incorrect Instance-instance of-Work relationship
    Creates Work-has as an instance-Instance relationships
"""

import logging

from apis_core.apis_relations.models import Property, TempTriple, Triple

logger = logging.getLogger(__name__)


def run():
    """see docstring"""
    try:
        wrong_instance_of = Property.objects.get(name="Instance of")
        logger.info("Found wrong instance of property - %s.", wrong_instance_of)
        correct_instance_of, _ = Property.objects.get_or_create(
            name_reverse="instance of", name="has as an instance"
        )
        logger.info("Obtained correct instance of property - %s.", correct_instance_of)
        # find all triples with this property
        instance_rels = TempTriple.objects.filter(prop=wrong_instance_of)
        logger.info("Found %s wrong triples. Deleting...", len(instance_rels))
        for rel in instance_rels:
            TempTriple.objects.get_or_create(
                subj=rel.obj, obj=rel.subj, prop=correct_instance_of
            )
            rel.delete()

        wrong_instance_of.delete()
        logger.info("Removed wrong instance of property.")

    except Property.DoesNotExist as e:
        logging.info("No property found: %s", repr(e))
