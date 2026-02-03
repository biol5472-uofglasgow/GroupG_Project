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

    # Summary result returned by write_summary_tsv
    summary_path = outdir / f"{prefix}_summary.tsv"
    summary_path.write_text(
        "Entity_Type\tAdded\tRemoved\tChanged\tTotal\n"
        "gene\t1\t0\t2\t3\n"
        "All_Total\t1\t0\t2\t3\n",
        encoding="utf-8",
    )

    counts = {"gene": {"added": 1, "removed": 0, "changed": 2}}
    summary_result = (str(summary_path), counts)

    # changes.tsv is read by the HTML report
    changes_path = outdir / f"{prefix}_changes.tsv"
    changes_path.write_text(
        "Entity_Type\tEntity_ID\tChange_Type\tDetails\n"
        "gene\tgene1\tchanged\tStart: 1 -> 2\n",
        encoding="utf-8",
    )

    # Dummy genome browser tracks (linked in artefacts)
    (outdir / f"{prefix}_added.gff3").write_text("##gff-version 3\n", encoding="utf-8")
    (outdir / f"{prefix}_removed.gff3").write_text("##gff-version 3\n", encoding="utf-8")
    (outdir / f"{prefix}_changed.gff3").write_text("##gff-version 3\n", encoding="utf-8")

    # Generate report
    report_path = write_htmlreport(
        outdir=str(outdir),
        summary_result=summary_result,
        prefix=prefix,
        run_json_path=str(run_json_path),
        title="Test report",
    )

    report = Path(report_path)
    assert report.is_file()
    assert report.name == f"{prefix}_report.html"

    # PNG created by plot_counts
    assert (outdir / f"{prefix}_report.png").is_file()

    html = report.read_text(encoding="utf-8")

    # Basic structural checks
    assert "<h1>" in html
    assert "Provenance" in html
    assert "Overview" in html

    # Output references
    assert f"{prefix}_report.png" in html
    assert f"{prefix}_added.gff3" in html
    assert f"{prefix}_removed.gff3" in html
    assert f"{prefix}_changed.gff3" in html
    assert f"{prefix}_run.json" in html
