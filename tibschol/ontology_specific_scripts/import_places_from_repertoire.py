'''import places from
'''
import logging

import pandas as pd
from apis_ontology.models import Place

logger = logging.getLogger(__name__)

def rename_columns(df):
    new_col_names = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z AA AB AC AD AE AF AG AH AI AJ AK AL AM AN AO".split()
    col_name_mapping = {}
    for i, c in enumerate(df.columns):
        if i >= len(new_col_names):
            print("not mapping from", c)
            break

        col_name_mapping[c] = new_col_names[i]

    df.rename(col_name_mapping, axis="columns", inplace=True)
    return df

def import_places(places):
    logger.info("Importing %s places...", len(places))
    for place in places:
        if not place or "no place" in place:
            logger.info("Not importing - %s", place)
            continue
        Place.objects.get_or_create(name=place.strip())

def run():

    logger = logging.getLogger(__name__)
    # Benchmarked version
    df = pd.read_csv(
        # fmt: off
        "apis_ontology/ontology_specific_scripts/data/KDSB Repertoire 20230116 PH.csv"
        # fmt: on
    ).fillna("")
    df = rename_columns(df)
    import_places(df.AM.unique())  # Import places from column M
    import_places(df.AN.unique())  # Import places from column N
    import_places(df.AO.unique())  # Import places from column O

    # New version
    df = pd.read_csv(
        # fmt: off
        "apis_ontology/ontology_specific_scripts/data/KDSB Repertoire New.csv"
        # fmt: on
        ).fillna("")
    df = rename_columns(df)
    import_places(df.AM.unique())  # Import places from column M
    import_places(df.AN.unique())  # Import places from column N
    import_places(df.AO.unique())  # Import places from column O
