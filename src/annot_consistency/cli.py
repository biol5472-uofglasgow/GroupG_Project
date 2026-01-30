# annot_consistency/cli.py
# CLI for Project 6: compare two annotation releases (A vs B).

import argparse
import os
from pathlib import Path

from annot_consistency.diff import build_entities, diff_entity
from annot_consistency.gffutils_db import load_or_create_db
from annot_consistency.html import write_htmlreport
from annot_consistency.io import (
    ensure_outdir,
    write_changes_tsv,
    write_genome_tracks,
    write_run_json,
    write_summary_tsv,
)
from annot_consistency.logging_utils import logger

# Default output directory: ~/app/gffacake
default_outdir = os.path.join(os.path.expanduser("~"), "app", "gffacake")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare two annotation releases (A vs B)")
    # 3 arguments total (A, B, outdir). outdir optional with default.
    p.add_argument("releaseA", help="Annotation release A in GFF3 format")
    p.add_argument("releaseB", help="Annotation release B in GFF3 format")
    p.add_argument("outDir", nargs="?", default=default_outdir,
                   help=f"Directory for output files (default: {default_outdir})")
    return p.parse_args(argv)

#validate input files
def validate_inputs(release_a: Path, release_b: Path) -> None:
    if not release_a.is_file():
        raise FileNotFoundError(f"releaseA not found: {release_a}")
    if not release_b.is_file():
        raise FileNotFoundError(f"releaseB not found: {release_b}")

    if release_a.suffix.lower() not in {".gff3", ".gff"}:
        raise ValueError(f"releaseA must be a .gff or .gff3 file, got: {release_a.name}")
    if release_b.suffix.lower() not in {".gff3", ".gff"}:
        raise ValueError(f"releaseB must be a .gff or .gff3 file, got: {release_b.name}")


def main(argv=None) -> None:
    args = parse_args(argv)

    release_a = Path(args.releaseA)
    release_b = Path(args.releaseB)
    outdir = Path(args.outDir)

    #validate input files
    validate_inputs(release_a, release_b)

    # ensure outdir exists
    ensure_outdir(str(outdir))

    # prefix
    rel_a = os.path.splitext(os.path.basename(str(release_a)))[0]
    rel_b = os.path.splitext(os.path.basename(str(release_b)))[0]
    prefix = f"{rel_a}_{rel_b}"

    # logging setup
    log_file = outdir / f"{prefix}_annot-consistency.log"
    log = logger(str(log_file))
    log.info("Starting gffacake annotation consistency tool")
    log.info("releaseA=%s", release_a)
    log.info("releaseB=%s", release_b)
    log.info("outDir=%s", outdir)
    log.info("prefix=%s", prefix)

    # DBs stored in in outdir for reuse
    db_path_a = outdir / f"{prefix}_releaseA.db"
    db_path_b = outdir / f"{prefix}_releaseB.db"


    # gffutils loading (load_or_create_db)
    try:
        log.info("Loading/creating gffutils DBs: %s and %s", db_path_a, db_path_b)
        db_a, db_b = load_or_create_db(release_a, release_b, db_path_a, db_path_b)
        log.info("Loaded DBs successfully")
    except Exception:
        log.exception("Failed to load/create gffutils databases")
        raise RuntimeError("Could not load or create gffutils databases")

    # build entities
    log.info("Building entities for release A")
    a_entities = build_entities(db_a)

    log.info("Building entities for release B")
    b_entities = build_entities(db_b)

    # differentiating entities
    log.info("Differentiating entities (A vs B)")
    changes_all, added_all, removed_all, changed_all = diff_entity(a_entities, b_entities)

    log.info(
        "Totals: changes=%d (added=%d removed=%d changed=%d)",
        len(changes_all),
        len(added_all),
        len(removed_all),
        len(changed_all))

    # writing the changes
    try:
        log.info("Writing changes.tsv")
        write_changes_tsv(str(outdir), changes_all, prefix)
    except Exception:
        log.exception("Failed writing changes.tsv")
        raise RuntimeError("Could not write changes.tsv")


    # writing the summary
    try:
        log.info("Writing summary.tsv")
        summary_file, counts= write_summary_tsv(str(outdir), changes_all, prefix)
        summary_result= (summary_file, counts)
    except Exception:
        log.exception("Failed writing summary.tsv")
        raise RuntimeError("Could not write summary.tsv")


    # writing genome browser tracks
    try:
        log.info("Writing genome browser tracks (added/removed/changed)")
        added_path, removed_path, changed_path= write_genome_tracks(
            str(outdir), added_all, removed_all, changed_all, prefix)
    except Exception:
        log.exception("Failed writing genome tracks")
        raise RuntimeError("Could not write genome tracks")


    #  writing run.json
    try:
        log.info("Writing run.json")
        run_json_path=write_run_json(
            outdir=str(outdir),
            tool_name="gffacake",
            tool_version="1.0",
            release_a=str(release_a),
            release_b=str(release_b),
            prefix=prefix)
    except Exception:
        log.exception("Failed writing run.json")
        raise RuntimeError("Could not write run.json")

    # HTML report
    try:
        log.info("Writing HTML report")
        report_path = write_htmlreport(
            outdir=str(outdir),
            summary_result=summary_result,
            prefix=prefix,
            run_json_path=run_json_path,
        )
        log.info("Wrote report: %s", report_path)
    except Exception:
        log.exception("Failed writing HTML report")
        raise RuntimeError("Could not write HTML report")

    log.info("Finished successfully")


if __name__ == "__main__":
    main()

