import gffutils
import os


#Function to load the pre-existing database or create one for gff files 
# If DB exists, it connects to it
# If DB does not exist, it creates a DB using the gff file
def load_or_create_db(gff_file_a, gff_file_b,  db_path_a, db_path_b):

    if os.path.isfile(db_path_a):
        db_a = gffutils.FeatureDB(db_path_a)
        
    else:
        db_a = gffutils.create_db(gff_file_a, dbfn = db_path_a, keep_order = True)           
            
    
    if os.path.isfile(db_path_b):
        db_b = gffutils.FeatureDB(db_path_b)
            
    else:
       db_b = gffutils.create_db(gff_file_b, dbfn = db_path_b, keep_order = True)

    return db_a, db_b

