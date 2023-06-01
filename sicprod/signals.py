from apis_core.apis_entities.signals import post_merge_with
from apis_core.apis_metainfo.signals import post_duplicate

from django.dispatch import receiver

from apis_bibsonomy.models import Reference

import logging

logger = logging.getLogger(__name__)

@receiver(post_merge_with)
def merge_references(sender, instance, entities, **kwargs):
    for entity in entities:
        logger.info("Moving references from {entity} to {instance}")
        references = Reference.objects.filter(content_type=entity.self_contenttype, object_id=entity.id).update(object_id=instance.id)

@receiver(post_duplicate)
def copy_references(sender, instance, duplicate, **kwargs):
    logger.info("Copying references from {instance} to {duplicate}")
    for ref in Reference.objects.filter(content_type=instance.self_contenttype, object_id=instance.id):
        ref.pk = None
        ref._state.adding = True
        ref.object_id = duplicate.id
        ref.save()
