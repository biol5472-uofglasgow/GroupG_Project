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
