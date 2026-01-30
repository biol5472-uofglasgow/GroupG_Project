import logging
import dataclasses
import pytest
from annot_consistency.logging_utils import logger
from annot_consistency.models import EntitySummary, ChangeRecord

#### Unit testing for logger and models ####

## logger test ##
def test_logger(test_path):
    # create temporary log file path
    log_file = test_path / "test.log"

    # create logger and output message
    log = logger(str(log_file))
    log.info("the numbers mason, what do they mean")

    # Test suite 1; logger identity and level
    assert isinstance(log, logging.Logger)
    assert log.name == "gffACAKE"
    assert log.level == logging.DEBUG
    assert log.propagate is False

    # Suite 2: handler configs
    assert len(log.handlers) == 1
    handler = log.handlers[0]
    assert isinstance(handler, logging.FileHandler)
    assert handler.level == logging.DEBUG

    # Suite 3: formatter configs
    format = handler.formatter
    assert format is not None
    assert "%(levelname)s" in format
    assert "%(asctime)s" in format
    assert "%(message)s" in format

    # Suite 4: message written to file
    output = log_file.read_text()
    assert "INFO" in output
    assert "the numbers mason, what do they mean" in output 

#### models testing ####

# EntitySummary stores values correctly
def test_ES_storing():
    test_ES = EntitySummary(
        entity_type="gene",
        entity_id="gene5",
        seqid="chrviii",
        start=100,
        end=400,
        strand="+",
        parent_id=None,
        attrs={"ID": "gene3"},
        score=1,
        phase=0,
        source="test",
    )

    assert test_ES.entity_type == "gene"
    assert test_ES.entity_id == "gene5"
    assert test_ES.seqid == "chrviii"
    assert test_ES.start == 100
    assert test_ES.end == 400
    assert test_ES.strand == "+"
    assert test_ES.parent_id is None
    assert test_ES.attrs["ID"] == "gene3"
    assert test_ES.score == 1
    assert test_ES.phase == 0
    assert test_ES.source == "test"

# ChangeRecord stores values correctly
def test_CR_storing():
    CR= ChangeRecord(
        entity_type="exon",
        entity_id="exon3",
        change_type="changed",
        details="start coordinate changed")

    assert CR.entity_type == "exon"
    assert CR.entity_id == "exon3"
    assert CR.change_type == "changed"
    assert CR.details == "start coordinate changed"


# EntitySummary is immutable
def test_ES_immutable():
    ES=EntitySummary(
        entity_type="gene",
        entity_id="gene5",
        seqid="chrviii",
        start=100,
        end=400,
        strand="+",
        parent_id=None,
        attrs={"ID": "gene3"},
        score=1,
        phase=0,
        source="test",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        ES.start = 5000

# ChangeRecord is immutable
def test_CR_immutable():
    CR= ChangeRecord(
        entity_type="exon",
        entity_id="exon3",
        change_type="changed",
        details="start coordinate changed")
    
    with pytest.raises(dataclasses.FrozenInstanceError):
        CR.details = "changed"

# Signature returns expected values
def test_signature_storing():
    test_ES = EntitySummary(
        entity_type="gene",
        entity_id="gene5",
        seqid="chrviii",
        start=100,
        end=400,
        strand="+",
        parent_id=None,
        attrs={"ID": "gene3"},
        score=1,
        phase=0,
        source="test",
    )
    assert test_ES.signature() == (
        "chrviii",
        100,
        400,
        "+",
        None,
        1,
        0,
        "test")

# signature changes only when a signature field changes
def test_signature_FieldChange():
    test_ES = EntitySummary(
        entity_type="gene",
        entity_id="gene5",
        seqid="chrviii",
        start=100,
        end=400,
        strand="+",
        parent_id=None,
        attrs={"ID": "gene3"},
        score=1,
        phase=0,
        source="test",
    )
    test_ES_modified = EntitySummary(
        entity_type="gene",
        entity_id="gene5",
        seqid="chrviii",
        start=100,
        end=400,
        strand="+",
        parent_id=None,
        attrs={"ID": "gene3"},
        score=5,
        phase=1,
        source="Dragovich, Kravchenko, Steiner",
    )
    assert test_ES.signature() != test_ES_modified.signature()