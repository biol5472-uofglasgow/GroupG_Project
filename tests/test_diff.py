from src.annot_consistency.diff import changed_details
from src.annot_consistency.models import EntitySummary
from typing import Mapping, Literal

#### tests for choosing the entity ID ####
# ID is present - priority
# Parent also present
def test_first_id() -> None:
    attrs: Mapping[str, List[str]] = {"ID": ["exon123"], "Parent": ["tx10"]}
    e_id = choose_entity_id("exon", attrs, "chr1", 100, 200, "-")
    assert e_id == "exon"

# ID not present; Parent taken as fall back
def test_parent_fallback() -> None:
    attrs: Mapping[str, List[str]] = {"Parent": ["tx20", "", "tx1"]}
    e_id = choose_entity_id("mRNA", attrs, "chr1", 100, 200, "+")
    assert e_id == "mRNA|parent=tx1,tx2|chr1:10-20:+"

# ID and parent not present; final fallback option
def test_final_fallback() -> None:
    attrs: Mapping[str, List[str]] = {}
    e_id = choose_entity_id("gene", attrs, "chrVII", 1000, 1000, "+")
    assert e_id == "gene|chrVII:1-100:+"

#### Tests for building entity structure ####

# create test DB and features
# TestFeature = one row of GFF file
@dataclass
class TestFeature:
    featuretype: str
    seqid: str
    start: int
    end: int
    strand: str
    attrs: Mapping[str, List[str]]
    score: float
    phase: Literal[0,1,2]
    source: str

# TestDB  for gffutils.featureDB
class TestDB:
    def __init__(self, features: List[TestFeature]) -> None:
        self._features = features

    def all_features(self, order_by: Any = None) -> Iterator[TestFeature]:
        # build_entities for order_by=("seqid","start");
        for feature in sorted(self._features, key=lambda x: (x.seqid, x.start)):
            yield feature

# Test for filtering, IDs/keys, parent handling and attrs joining as expecteed
def test_expected_types_and_builds_summaries() -> None:
    features = [
        TestFeature("gene", "chr1", 1, 100, "+", "fixture", 0.0, 0, {"ID": ["gene1"]}),     # a gene with a normal ID
        TestFeature("mRNA", "chr1", 5, 80, "+", "fixture", 0.0, 0, {"ID": ["tx1"], "Parent": ["gene1"]}),   # transcript has ID and Parent
        TestFeature("exon", "chr1", 5, 20, "+", "fixture", 0.0, 0, {"Parent": ["tx1", "", "tx0"]}), # exon has no ID, fallback is forced;  "" to check empty parents are filtered in the fallback key
        TestFeature("CDS",  "chr1", 5, 20, "+", "fixture", 0.0, 0, {"ID": ["cds1"], "Parent": ["tx1"]}),    # ignores feature types outside
    ]
    out = build_entities(TestDB(features))

    # check the overall structure is correct
    assert set(out) == {"gene", "mRNA", "exon"} 

    # gene was stored correctly
    assert "gene1" in out["gene"]
    assert out["gene"]["gene1"].parent_id is None
    assert out["gene"]["gene1"].attrs["ID"] == "gene1"

    # mRNA parent behaviour and attrs join
    assert "tx1" in out["mRNA"]
    assert out["mRNA"]["tx1"].parent_id == "gene1"
    assert out["mRNA"]["tx1"].attrs["Parent"] == "gene1"

    # exon fallback ID and Parent handling
    exon_key = "exon|parent=tx0,tx1|chr1:5-20:+"
    assert exon_key in out["exon"]
    assert out["exon"][exon_key].parent_id == "tx1,,tx0"
    assert out["exon"][exon_key].attrs["Parent"] == "tx1,,tx0"


def make_EntitySummary_instance(entity_type: str, entity_id: str, seqid:str, start:int,
                        end:int, strand:str, parent_id:str, attrs:Mapping[str,str], score:float, phase:Literal[0,1,2],
                        source:str):
    
    return EntitySummary(
        entity_type = entity_type,
        entity_id = entity_id,
        seqid = seqid,
        start = start,
        end = end,
        strand = strand,
        parent_id = parent_id,
        attrs = attrs,
        score = score,
        phase = phase,
        source = source

    )

# Function to test the changed_details function
def test_changed_details() -> None:

    # Creating instances of the EntitySummary class to compare with each other
    a_instance = make_entity_summary_instance("mRNA", "tx1", "chr1", 5, 80, "+", "gene1",
                                              {'ID':'tx1', 'Parent':'gene1'}, 0.0, 0, "fixture")
    b_instance = make_entity_summary_instance("mRNA", "tx2", "chr2", 1, 20, "-", "gene2",
                                              {'ID':'tx2', 'Parent':'gene2'}, 0.0, 0, "fixture")

    # Applying the changed_details function to the instances
    change = changed_details(a_instance, b_instance)

    # Asserting all the changes occuring from instance a to b
    assert "seqid: chr1 -> chr2" in change
    assert "Start: 5 -> 1" in change
    assert "End: 80 -> 20" in change
    assert "Parent ID: gene1 -> gene2" in change
    assert "Strand: + -> -" in change
    assert "Entity Type:" not in change
    assert "Score:" not in change
    assert "Phase:" not in change

# Function to test the diff_entity function
def test_diff_entity() -> None:

    # Creating entities to compare each other with
    a_entities = {
        "gene" : {
            "gene1": make_entity_summary_instance("gene", "gene1", "chr1", 5, 80, "+", None,
                                                  {'ID':'gene1', 'Name':'GeneOne'}, 0.0, 0,
                                                  "fixture"),
            "gene2": make_entity_summary_instance("gene", "gene2", "chr2", 1, 20, "+", None,
                                                  {'ID':'gene2', 'Name':'GeneTwo'}, 0.0, 0,
                                                  "fixture")
        },
        "mRNA" : {},
        "exon" : {}

    }


    b_entities = {
        "gene" : {
            "gene2": make_entity_summary_instance("gene", "gene2", "chr2", 1, 25, "+", None,
                                                  {'ID':'gene2', 'Name':'GeneTwo'}, 0.0, 0,
                                                  "fixture"),
            "gene3": make_entity_summary_instance("gene", "gene3", "chr2", 36, 55, "-", None,
                                                  {'ID':'gene3', 'Name':'GeneThree'}, 0.0, 0,
                                                  "fixture")
        },
        "mRNA" : {},
        "exon" : {}

    }

    # Applying the diff_entity function to the entities
    changes, added, removed, changed = diff_entity(a_entities, b_entities)

    # Asserting length of the entities and checking for the correct added/changed/removed entity
    assert len(added) == 1
    assert {e.entity_id for e in added} == {"gene3"}

    assert len(removed) == 1
    assert {e.entity_id for e in removed} == {"gene1"}

    assert len(changed) == 1
    assert {e.entity_id for e in changed} == {"gene2"}

    assert len(changes) == 3


    # Asserting the correct change types associated with the correct entities in the changes var
    change_types = {(c.entity_id, c.change_type) for c in changes}
    assert ("gene1", "removed") in change_types
    assert ("gene2", "changed") in change_types
    assert ("gene3", "added")   in change_types
