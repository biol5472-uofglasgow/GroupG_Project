from pathlib import Path

import gffutils
from gffutils import FeatureDB

#Function to load the pre-existing database or create one for gff files
# If DB exists, it connects to it
# If DB does not exist, it creates a DB using the gff file

def load_or_create_db(
    gff_file_a: Path,
    gff_file_b: Path,
    db_path_a: Path,
    db_path_b: Path) -> tuple[FeatureDB, FeatureDB]:

    try:
        db_a = gffutils.FeatureDB(str(db_path_a))

    except ValueError:
        db_a = gffutils.create_db(str(gff_file_a), dbfn = str(db_path_a),
                                  keep_order = True, merge_strategy="create_unique" )


    try:
        db_b = gffutils.FeatureDB(str(db_path_b))

    except ValueError:
       db_b = gffutils.create_db(str(gff_file_b), dbfn = str(db_path_b),
                                 keep_order = True, merge_strategy="create_unique")


    return db_a, db_b

