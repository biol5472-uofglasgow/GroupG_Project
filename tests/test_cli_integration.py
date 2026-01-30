import pathlib
import sys
from pathlib import Path

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from src.annot_consistency.cli import main


def test_cli_integration_custom_sample(tmp_path: Path) -> None:
    release_a = tmp_path / 'sample_a.gff3'
    release_b = tmp_path / 'sample_b.gff3'

    release_a.write_text(
        "gff-version 3\n"
        'chr1\tsrcA\tprotein_coding_gene\t1.0\t100\t0\t+\t2\tID=gene1\n'
        'chr1\tsrcA\tmRNA\t1\t100\t.\t+\t.\tID=tx1;Parent=gene1\n'
        'chr1\tsrcA\tCDS\t10\t40\t.\t+\t0\tID=cds1;Parent=tx1\n',
        encoding='utf-8'
    )

    release_b.write_text(
        "gff-version 3\n"
        'chr1\tsrcB\tprotein_coding_gene\t1\t100\t0\t-\t2\tID=gene1\n'
        'chr1\tsrcA\tmRNA\t1\t60\t5.0\t+\t.\tID=tx1;Parent=gene1\n'
        'chr1\tsrcB\tCDS\t10\t40\t.\t+\t1\tID=cds1;Parent=tx1\n',
        encoding='utf-8'
    )

# Test fixture releases
def test_cli_fixtures(tmp_path: Path) -> None:
    fixture = Path("tests/fixture_releases")
    gff_a = fixture / "release_A.gff3"
    gff_b = fixture / "release_B.gff3"
    outdir = tmp_path / "output"
    outdir.mkdir()

    main([str(gff_a), str(gff_b), str(outdir)])

    # expected prefix
    release_a = gff_a.stem
    release_b = gff_b.stem
    prefix = f"{release_a}_{release_b}"

    # Test: expected output files exist
    added_gff = outdir / f"{prefix}_added.gff3"
    removed_gff = outdir / f"{prefix}_removed.gff3"
    changed_gff = outdir / f"{prefix}_changed.gff3"

    assert added_gff.exists()
    assert removed_gff.exists()
    assert changed_gff.exists()

    # Test: check changes.tsv/summary/run.json/report
    assert (outdir / f"{prefix}_changes.tsv").exists()
    assert (outdir / f"{prefix}_summary.tsv").exists()
    assert (outdir / f"{prefix}_run.json").exists()
    assert (outdir / f"{prefix}_report.html").exists()
