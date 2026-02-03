
# tests/test_io.py

import json
from pathlib import Path

from annot_consistency.io import (
    ensure_outdir,
    write_changes_tsv,
    write_genome_tracks,
    write_run_json,
    write_summary_tsv,
    write_tracks,
)
from annot_consistency.models import ChangeRecord, EntitySummary


#test to ensure that directory exists
def test_ensure_outdir(tmp_path: Path) -> None:
    outdir = tmp_path / "out"
    ensure_outdir(str(outdir))
    assert outdir.exists()
    assert outdir.is_dir()

#test to check whether the function generates a TSV file with the same name
def test_write_changes_tsv(tmp_path: Path) -> None:
    changes = [
        ChangeRecord("gene", "gene1", "added", "Added gene1"),
        ChangeRecord("exon", "exon1", "changed", "Coords changed"),
    ]
    prefix = "A_B"

    path = write_changes_tsv(str(tmp_path), changes, prefix)

    p = Path(path)
    assert p.exists()
    assert p.name == f"{prefix}_changes.tsv"

    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "Entity_Type\tEntity_ID\tChange_Type\tDetails"
    assert "gene\tgene1\tadded\tAdded gene1" in lines
    assert "exon\texon1\tchanged\tCoords changed" in lines

#test to check whether the function generates a summary file as well as the correct counts
def test_write_summary_tsv(tmp_path: Path) -> None:
    changes = [
        ChangeRecord("gene", "gene1", "added", "Added gene1"),
        ChangeRecord("gene", "gene2", "removed", "Removed gene2"),
        ChangeRecord("exon", "exon1", "changed", "Coords changed"),
    ]
    prefix = "A_B"

    path, counts = write_summary_tsv(str(tmp_path), changes, prefix)

    p = Path(path)
    assert p.exists()
    assert p.name == f"{prefix}_summary.tsv"

    # check returned counts
    assert counts["gene"]["added"] == 1
    assert counts["gene"]["removed"] == 1
    assert counts["gene"]["changed"] == 0
    assert counts["exon"]["changed"] == 1


    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "Entity_Type\tAdded\tRemoved\tChanged\tTotal"

    assert lines[-1].startswith("All_Total\t")

#testing the function to check whether it creates a valid GFF3 file
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
    lines = outpath.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "##gff-version 3"
    assert "ID=gene1" in lines[1]


#testing the function that creates three GFF3 files (added, removed, and changed)
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

    assert Path(added).name == f"{prefix}_added.gff3"
    assert Path(removed).name == f"{prefix}_removed.gff3"
    assert Path(changed).name == f"{prefix}_changed.gff3"

    # the file should contain the GFF3 header
    added_lines = Path(added).read_text(encoding="utf-8").splitlines()
    assert added_lines[0] == "##gff-version 3"

#testing the function to ensure it creates a valid JSON file
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

    p = Path(path)
    assert p.exists()
    assert p.name == f"{prefix}_run.json"

    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["tool"]["name"] == "gffacake"
    assert data["inputs"]["release_a"] == "releaseA.gff3"
    assert data["outputs"]["changes_tsv"] == f"{prefix}_changes.tsv"
