from pathlib import Path

from annot_consistency.cli import main

def test_cli_integration_custom_sample(tmp_path: Path) -> None:
    release_a = tmp_path / 'sample_a.gff3'
    release_b = tmp_path / 'sample_b.gff3'