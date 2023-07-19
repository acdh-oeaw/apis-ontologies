'''Convert the volume and set number fields to integer.'''
import logging

from apis_ontology.models import Instance

logger = logging.getLogger(__name__)

def run():
    for instance in Instance.objects.all():
        if instance.volume:
            instance.volume = instance.volume.rstrip(".0")
        if instance.sb_text_number:
            instance.sb_text_number = instance.sb_text_number.rstrip(".0")

        instance.save()
