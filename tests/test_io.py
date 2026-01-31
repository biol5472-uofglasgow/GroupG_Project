# tests/test_io.py

# tests/test_io.py

import json
from pathlib import Path

from annot_consistency.io import (
    ensure_outdir,
    write_changes_tsv,
    write_summary_tsv,
    write_tracks,
    write_genome_tracks,
    write_run_json,
)
from annot_consistency.models import ChangeRecord, EntitySummary


def test_ensure_outdir(tmp_path: Path) -> None:
    outdir = tmp_path / "out"
    ensure_outdir(str(outdir))
    assert outdir.exists()
    assert outdir.is_dir()


def test_write_changes_tsv(tmp_path: Path) -> None:
    changes = [
        ChangeRecord("gene", "gene1", "added", "Added gene1"),
        ChangeRecord("exon", "exon1", "changed", "Coords changed"),
    ]
    prefix = "A_B"

    path = write_changes_tsv(str(tmp_path), changes, prefix)

    assert Path(path).exists()
    assert Path(path).name == f"{prefix}_changes.tsv"



