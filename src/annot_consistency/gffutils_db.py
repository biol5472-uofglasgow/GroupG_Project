import gffutils
from typing import tuple
from pathlib import Path
from gffutils.interface import FeatureDB

#Function to load the pre-existing database or create one for gff files 
# If DB exists, it connects to it
# If DB does not exist, it creates a DB using the gff file

def load_or_create_db(gff_file_a: Path, gff_file_b: Path, db_path_a: Path, db_path_b: Path) -> tuple[FeatureDB, FeatureDB]:

    try: 
        db_a = gffutils.FeatureDB(db_path_a)

    except:
        db_a = gffutils.create_db(gff_file_a, dbfn = db_path_a, keep_order = True)        

            
    try:
        db_b = gffutils.FeatureDB(db_path_b)
            
    except:
       db_b = gffutils.create_db(gff_file_b, dbfn = db_path_b, keep_order = True)


    return db_a, db_b

