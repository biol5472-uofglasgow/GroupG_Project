# tests/test_io.py

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

from annot_consistency import io
from annot_consistency.models import ChangeRecord, EntitySummary

@pytest.fixture
def sample_changes() -> List[ChangeRecord]:
    return [
        ChangeRecord(entity_type="gene", entity_id="gene1", change_type="added", details="Added gene1"),
        ChangeRecord(entity_type="gene", entity_id="gene2", change_type="removed", details="Removed gene2"),
        ChangeRecord(entity_type="exon", entity_id="exon1", change_type="changed", details="Coords changed"),
    ]


