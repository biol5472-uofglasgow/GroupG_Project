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

def test_write_summary_tsv(tmp_path: Path) -> None:
    changes = [
        ChangeRecord("gene", "gene1", "added", "Added gene1"),
        ChangeRecord("gene", "gene2", "removed", "Removed gene2"),
        ChangeRecord("exon", "exon1", "changed", "Coords changed"),
    ]
    prefix = "A_B"

    path, counts = write_summary_tsv(str(tmp_path), prefix, changes)

    assert Path(path).exists()
    assert counts["gene"]["added"] == 1
    assert counts["gene"]["removed"] == 1
    assert counts["exon"]["changed"] == 1

def test_write_tracks(tmp_path: Path) -> None:
    entities = [
        EntitySummary(
            entity_type="gene",
            entity_id="gene1",
            seqid="chr1",
            start=10,
            end=50,
            strand="+",
            parent_id=None,
            attrs={"ID": "gene1"},
            score=0.0,
            phase=0,
            source="test",
        ),
        EntitySummary(
            entity_type="exon",
            entity_id="exon1",
            seqid="chr1",
            start=15,
            end=20,
            strand="+",
            parent_id="tx1",
            attrs={"ID": "exon1", "Parent": "tx1"},
            score=1.0,
            phase=1,
            source="test",
        ),
    ]

    outpath = tmp_path / "track.gff3"
    write_tracks(str(outpath), entities)

    assert outpath.exists()
    first_line = outpath.read_text().splitlines()[0]
    assert first_line == "##gff-version 3"


def test_write_genome_tracks(tmp_path: Path) -> None:
    entity = EntitySummary(
        entity_type="gene",
        entity_id="gene1",
        seqid="chr1",
        start=1,
        end=10,
        strand="+",
        parent_id=None,
        attrs={"ID": "gene1"},
        score=0.0,
        phase=0,
        source="test",
    )

    prefix = "A_B"

    added, removed, changed = write_genome_tracks(
        str(tmp_path),
        [entity],
        [],
        [],
        prefix,
    )

    assert Path(added).exists()
    assert Path(removed).exists()
    assert Path(changed).exists()

def test_write_run_json(tmp_path: Path) -> None:
    prefix = "A_B"

    path = write_run_json(
        tool_name="gffacake",
        tool_version="1.0",
        release_a="releaseA.gff3",
        release_b="releaseB.gff3",
        outdir=str(tmp_path),
        prefix=prefix,
    )

    assert Path(path).exists()

    data = json.loads(Path(path).read_text())
    assert data["tool"]["name"] == "gffacake"
    assert data["inputs"]["release_a"] == "releaseA.gff3"