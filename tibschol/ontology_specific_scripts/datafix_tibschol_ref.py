import logging

from apis_ontology.models import Instance, Work
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)


def correct_extracted_tibschol_ref_data(instance: Instance):
    if not instance.tibschol_ref:
        return
    try:
        set_num, vol_num, sbtext_num = instance.tibschol_ref.split("_")
        set_num = f"Set {set_num.lstrip('0')}"
        vol_num = vol_num.lstrip("0")
        sbtext_num = sbtext_num.lstrip("0")

        if set_num != instance.set_num:
            print(
                f"{instance.tibschol_ref} Set: Expected '{set_num}', found {instance.set_num}"
            )
            instance.set_num = set_num
        if vol_num != instance.volume:
            print(
                f"{instance.tibschol_ref} Volume: Expected {vol_num}, found {instance.volume}"
            )
            instance.volume = vol_num
        if sbtext_num != instance.sb_text_number:
            print(
                f"{instance.tibschol_ref} SBText: Expected '{sbtext_num}', found {instance.sb_text_number}"
            )
            instance.sb_text_number = sbtext_num

        instance.save()

    except ValueError as ve:
        logger.error(
            "Could not split %s for instance %s", instance.tibschol_ref, instance
        )


def run():
    for instance in Instance.objects.all():
        correct_extracted_tibschol_ref_data(instance)
