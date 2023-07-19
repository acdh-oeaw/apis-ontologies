import logging

import pandas as pd
from apis_core.apis_labels.models import Label
from apis_core.apis_relations.models import Property, Triple
from apis_core.apis_vocabularies.models import LabelType
from apis_ontology.models import Instance, Work
from tqdm.auto import tqdm


def rename_columns(df):
    new_col_names = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z AA AB AC AD AE AF AG AH AI AJ AK AL AM AN".split()
    col_name_mapping = {}
    for i, c in enumerate(df.columns):
        if i >= len(new_col_names):
            print("not mapping from", c)
            break

        col_name_mapping[c] = new_col_names[i]

    df.rename(col_name_mapping, axis="columns", inplace=True)
    return df


def run():
    logger = logging.getLogger(__name__)

    df = pd.read_csv(
        # fmt: off
        "apis_ontology/ontology_specific_scripts/data/KDSB Repertoire 20230116 PH.csv"
        # fmt: on
    ).fillna("")
    df = rename_columns(df)
    # Reference label type
    text_ref, _ = LabelType.objects.get_or_create(
        name="Ref Nr", description="TibSchol internal reference number"
    )
    instance_of = Property.objects.get(name="has as an instance")

    missing_rows = []
    unlinked_works = []
    for i, row in tqdm(df.iterrows()):
        # Use label
        label = row.A.strip()
        try:
            label_object = Label.objects.get(label_type=text_ref, label=label)
            instance = Instance.objects.get(id=label_object.temp_entity.id)
            if str(row.C).strip():
                instance.set_num = f"Set {str(row.C)[0]}"

            instance.volume = f"{row.D}".strip()
            instance.sb_text_number = f"{row.E}".strip()
            instance.pp_kdsb = f"{row.F}".strip()
            instance.num_folios = f"{row.G}".strip()
            instance.signature_letter = f"{row.K}".strip()
            instance.signature_number = f"{row.L}".strip()
            instance.drepung_number = f"{row.M}".strip()
            instance.provenance = f"{row.N}".strip()
            instance.save()
            logger.info("%s, Updated instance", instance.id)
            work = Work.objects.get(
                id=Triple.objects.get(subj=instance, prop=instance_of).obj.id
            )
            work.subject = f"{row.H}".strip()
            work.save()
            logger.info("%s, Updated work", work.id)

        except Label.DoesNotExist:
            missing_rows.append(f"{i} - {label}")
        except Triple.DoesNotExist:
            unlinked_works.append(f"{i} - {label}")
        except Exception as e:
            logger.error("%s, Exception %s\n---\n%s", i, repr(e), row)
            continue

    if missing_rows:
        print("Missing rows from input file", ", ".join(missing_rows))
    if unlinked_works:
        print("Unlinked works for", ", ".join(unlinked_works))
