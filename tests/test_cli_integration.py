from pathlib import Path

from annot_consistency.cli import main

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