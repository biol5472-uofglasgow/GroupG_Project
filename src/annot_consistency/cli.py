# annot_consistency/cli.py
# CLI for Project 6: compare two annotation releases (A vs B).


import argparse
import os
from pathlib import Path


from annot_consistency.io import ensure_outdir, write_changes_tsv, write_summary_tsv ,write_genome_tracks, write_run_json
from annot_consistency.logging_utils import logger
from annot_consistency.gffutils_db import load_or_create_db
from annot_consistency.diff import build_entities, diff_entity



# Default output directory: ~/app/gffacake
default_outdir = os.path.join(os.path.expanduser("~"), "app", "gffacake")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare two annotation releases (A vs B)")
    # 3 arguments total (A, B, outdir). outdir optional with default.
    p.add_argument("releaseA", help="Annotation release A in GFF3 format")
    p.add_argument("releaseB", help="Annotation release B in GFF3 format")
    p.add_argument(
        "outDir",
        nargs="?",
        default=default_outdir,
        help=f"Directory for output files (default: {default_outdir})",
    )
    return p.parse_args(argv)



def main(argv=None) -> None:
    args = parse_args(argv)

    release_a = Path(args.releaseA)
    release_b = Path(args.releaseB)
    outdir = Path(args.outDir)

    # Input validation (raising specific error types)
    if not release_a.is_file():
        raise FileNotFoundError(f"releaseA not found: {release_a}")
    if not release_b.is_file():
        raise FileNotFoundError(f"releaseB not found: {release_b}")

    # Optional validation: ensure file extensions look like GFF3/GFF
    if release_a.suffix.lower() not in {".gff3", ".gff"}:
        raise ValueError(f"releaseA must be a .gff or .gff3 file, got: {release_a.name}")
    if release_b.suffix.lower() not in {".gff3", ".gff"}:
        raise ValueError(f"releaseB must be a .gff or .gff3 file, got: {release_b.name}")

    # Ensure outdir exists
    ensure_outdir(str(outdir))

    # Logging setup 
    log_file = outdir / "annot-consistency.log"
    log = logger(str(log_file))
    log.info("Starting gffacake annotation consistency tool")
    log.info("releaseA=%s", release_a)
    log.info("releaseB=%s", release_b)
    log.info("outDir=%s", outdir)

    # DBs persisted in outdir for reuse
    db_path_a = outdir / "releaseA.db"
    db_path_b = outdir / "releaseB.db"


    # gffutils loading (load_or_create_db)
    try:
        log.info("Loading/creating gffutils DBs: %s and %s", db_path_a, db_path_b)
        db_a, db_b = load_or_create_db(release_a, release_b, db_path_a, db_path_b)
        log.info("Loaded DBs successfully")
    except Exception:
        log.exception("Failed to load/create gffutils databases")
        raise RuntimeError("Could not load or create gffutils databases")




    # write_summary_tsv

    try:
        log.info("Writing summary.tsv")
        write_summary_tsv(str(outdir), changes_all)
    except Exception:
        log.exception("Failed writing summary.tsv")
        raise RuntimeError("Could not write summary.tsv")

    
    # write_genome_tracks

    try:
        log.info("Writing genome browser tracks (added/removed/changed)")
        write_genome_tracks(str(outdir), added_all, removed_all, changed_all)
    except Exception:
        log.exception("Failed writing genome tracks")
        raise RuntimeError("Could not write genome tracks")


    #  write_run_json
    
    try:
        log.info("Writing run.json")
        write_run_json(
            outdir=str(outdir),
            tool_name="gffacake",
            tool_version="1.0",
            release_a=str(release_a),
            release_b=str(release_b),
            outdir_str=str(outdir),
            extra={
                "n_changes": len(changes_all),
                "n_added": len(added_all),
                "n_removed": len(removed_all),
                "n_changed": len(changed_all),
                "db_a": str(db_path_a),
                "db_b": str(db_path_b),
            },
        )
    except Exception:
        log.exception("Failed writing run.json")
        raise RuntimeError("Could not write run.json")

    log.info("Finished successfully")


if __name__ == "__main__":
    main()

