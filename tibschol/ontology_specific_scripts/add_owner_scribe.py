"""
Add owner and scribe relations to instances
"""
import logging

import pandas as pd
from apis_core.apis_labels.models import Label
from apis_core.apis_relations.models import Property, TempTriple
from apis_core.apis_vocabularies.models import LabelType
from apis_ontology.models import Instance, Person

logger = logging.getLogger(__name__)


def rename_columns(df):
    new_col_names = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z AA AB AC AD AE AF AG AH AI AJ AK AL AM AN AO AP AQ AR".split()
    col_name_mapping = {}
    for i, c in enumerate(df.columns):
        if i >= len(new_col_names):
            print("not mapping from", c)
            break

        col_name_mapping[c] = new_col_names[i]

    df.rename(col_name_mapping, axis="columns", inplace=True)
    return df


def run():
    def get_instance_object(instance_label):
        try:
            label_object = Label.objects.get(label_type=text_ref, label=instance_label)
            instance = Instance.objects.get(id=label_object.temp_entity.id)
            return instance
        except (Label.DoesNotExist, Instance.DoesNotExist) as e:
            logging.error(
                "Could not find label or instance for label %s in row %s: %s",
                instance_label,
                i,
                repr(e),
            )

    def get_person_object(person_name):
        if not person_name.strip() or "none" in person_name.lower():
            return None
        try:
            p, _ = Person.objects.get_or_create(name=person_name)
            return p
        except Person.MultipleObjectsReturned:
            logging.error("Multiple objects returned for %s", person_name)

    text_ref = LabelType.objects.get(
        name="Ref Nr", description="TibSchol internal reference number"
    )

    scribe_of = Property.objects.get(name="scribe of")
    owner_of = Property.objects.get(name="owner of")
    # Benchmarked version
    df = pd.read_csv(
        # fmt: off
        "apis_ontology/ontology_specific_scripts/data/KDSB Repertoire 20230116 PH.csv"
        # fmt: on
    ).fillna("")
    df = rename_columns(df)
    for i, row in df.iterrows():
        instance = get_instance_object(row.A.strip())
        if not instance:
            logger.error("Instance not found. %s", repr(instance))
            continue
        scribe = get_person_object(row.AP.strip())
        owner = get_person_object(row.AQ.strip())
        if scribe is not None:
            logger.debug("Found scribe %s - %s", scribe, row.AP.strip())
            TempTriple.objects.get_or_create(subj=scribe, obj=instance, prop=scribe_of)
        if owner is not None:
            logger.debug("Found owner %s - %s", scribe, row.AQ.strip())
            TempTriple.objects.get_or_create(subj=owner, obj=instance, prop=owner_of)
