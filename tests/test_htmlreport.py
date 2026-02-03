import json
from pathlib import Path

from annot_consistency.htmlreport import plot_counts, write_htmlreport


def test_plot_counts_writes_png(tmp_path: Path) -> None:
    counts = {
        "gene": {"added": 1, "removed": 2, "changed": 3},
        "mRNA": {"added": 0, "removed": 1, "changed": 0},
    }

    outdir = tmp_path / "out"
    outdir.mkdir(parents=True, exist_ok=True)

    png_path = plot_counts(str(outdir), counts, prefix="A_B")

    p = Path(png_path)
    assert p.is_file()
    assert p.name == "A_B_report.png"

def test_write_htmlreport_writes_html_and_references_outputs(tmp_path: Path) -> None:
    outdir = tmp_path / "out"
    outdir.mkdir(parents=True, exist_ok=True)

    prefix = "releaseA_releaseB"

    # Minimal run.json payload expected by write_htmlreport
    run_json_path = outdir / f"{prefix}_run.json"
    payload = {
        "tool": {"name": "gffacake", "version": "1.0"},
        "timestamp_utc": "2026-01-01T00:00:00+00:00",
        "inputs": {
            "release_a": "releaseA.gff3",
            "release_b": "releaseB.gff3",
        },
        "outputs": {
            "outdir": str(outdir),
            "changes_tsv": f"{prefix}_changes.tsv",
            "summary_tsv": f"{prefix}_summary.tsv",
            "run_json": f"{prefix}_run.json",
            "added_gff3": f"{prefix}_added.gff3",
            "removed_gff3": f"{prefix}_removed.gff3",
            "changed_gff3": f"{prefix}_changed.gff3",
            "report_html": f"{prefix}_report.html",
            "report_png": f"{prefix}_report.png",
        },
    }
    run_json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")