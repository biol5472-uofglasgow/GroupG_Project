from src.annot_consistency.diff import changed_details, choose_entity_id, build_entities
from src.annot_consistency.models import EntitySummary
from typing import Mapping, Literal, List

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

def test_changed_details():
    a = make_EntitySummary_instance("mRNA", "tx1", "chr1", 5, 80, "+", "gene1", {'ID':'tx1', 'Parent':'gene1'}, 0.0, 0, "fixture")
    b = make_EntitySummary_instance("mRNA", "tx2", "chr2", 1, 20, "-", "gene2", {'ID':'tx2', 'Parent':'gene2'}, 0.0, 0, "fixture")

    change = changed_details(a,b)

    assert "seqid: chr1 -> chr2" in change
    assert "Start: 5 -> 1" in change
    assert "End: 80 -> 20" in change
    assert "Parent ID: gene1 -> gene2" in change    
    assert "Strand: + -> -" in change
    assert "Entity Type:" not in change
    assert "Score:" not in change
    assert "Phase:" not in change



