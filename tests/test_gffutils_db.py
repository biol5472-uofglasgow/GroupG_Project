from pathlib import Path

from gffutils import FeatureDB

from src.annot_consistency.gffutils_db import load_or_create_db


def test_create_and_check_db(tmp_path: Path) -> None:
    gff_1 = tmp_path.joinpath("test1_gff.gff")
    gff_2 = tmp_path.joinpath("test2_gff.db")
    db_path_1= tmp_path.joinpath("test1_db.db")
    db_path_2 = tmp_path.joinpath("test2_db.db")

    with gff_1.open('w') as f1:
        f1.write('chr1\tfixture\texon\t12\t20\t.\t-\t.\tID=tx1_ex1;Parent=tx1\n')

    with gff_2.open('w') as f2:
        f2.write('chr2\tfixture\tmRNA\t1\t20\t.\t-\t.\tID=tx2;Parent=gene2\n')

    db_1, db_2  = load_or_create_db(gff_1, gff_2, db_path_1, db_path_2)

    assert isinstance(db_1, FeatureDB)
    assert isinstance(db_2, FeatureDB)
    assert len(list(db_1.features_of_type("exon"))) == 1
    assert len(list(db_2.features_of_type("mRNA"))) == 1


