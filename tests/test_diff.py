from collections.abc import Mapping
from typing import Literal

from src.annot_consistency.diff import changed_details, diff_entity
from src.annot_consistency.models import EntitySummary


# Making a function to create instances of the EntitySummary class
def make_entity_summary_instance(entity_type: str, entity_id: str, seqid:str, start:int,
                        end:int, strand:str, parent_id:str | None, attrs:Mapping[str,str],
                        score:float, phase:Literal[0,1,2], source:str) -> EntitySummary:

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
