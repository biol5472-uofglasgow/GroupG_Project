# annot_consistency/cli.py
#
# CLI for Project 6: compare two annotation releases (A vs B).
# Uses:
#   - gffutils DBs via load_or_create_db()
#   - EntitySummary + ChangeRecord models
#   - io writers for outputs


import argparse
import os
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Tuple

import gffutils

from annot_consistency.models import EntitySummary, ChangeRecord
from annot_consistency import io
from annot_consistency.logging_utils import logger as build_logger
from annot_consistency.gffutils_db import load_or_create_db


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


def _first_attr(feature: gffutils.Feature, key: str) -> Optional[str]:
    vals = feature.attributes.get(key)
    if not vals:
        return None
    return str(vals[0])


def _entity_id(feature: gffutils.Feature) -> str:
    # Prefer stable GFF3 ID attribute; fallback to gffutils internal ID
    return _first_attr(feature, "ID") or str(feature.id)


def _parent_id(feature: gffutils.Feature) -> Optional[str]:
    return _first_attr(feature, "Parent")


def _attrs_mapping(feature: gffutils.Feature) -> Mapping[str, str]:
    """
    Flatten the dict[str, list[str]] -> dict[str, str] by taking the first value per attribute.
    """
    flat: Dict[str, str] = {}
    for k, v in feature.attributes.items():
        if v:
            flat[str(k)] = str(v[0])
    return flat

# Helper function used to sort features consistently by genomic location and ID
def _feature_sort_key(f):
    return (str(f.seqid), int(f.start), int(f.end), _entity_id(f))


def _collect_entities(db, featuretypes, entity_label):

    feats = []
    for ft in featuretypes:
        feats.extend(list(db.features_of_type(ft)))

    feats.sort(key=_feature_sort_key)

    out = {}
    for f in feats:
        eid = _entity_id(f)
        out[eid] = EntitySummary(
            entity_type=entity_label,
            entity_id=eid,
            seqid=str(f.seqid),
            start=int(f.start),
            end=int(f.end),
            strand=str(f.strand) if f.strand else ".",
            parent_id=_parent_id(f),
            attrs=_attrs_mapping(f),
        )

    return out



def _diff(entity_type: str, a_map: Dict[str, EntitySummary], b_map: Dict[str, EntitySummary]) -> Tuple[List[ChangeRecord], List[EntitySummary], List[EntitySummary], List[EntitySummary]]:
    """
    Differentiate entities by ID:
      - added: in B not A
      - removed: in A not B
      - changed: in both but signature differs (seqid/start/end/strand/parent_id)
    """
    changes: List[ChangeRecord] = []
    added: List[EntitySummary] = []
    removed: List[EntitySummary] = []
    changed: List[EntitySummary] = []

    a_ids = set(a_map.keys())
    b_ids = set(b_map.keys())

    for eid in sorted(b_ids - a_ids):
        e = b_map[eid]
        added.append(e)
        changes.append(ChangeRecord(
                entity_type=entity_type,  
                entity_id=eid,
                change_type="added",      
                details=f"Added in release B at {e.seqid}:{e.start}-{e.end}({e.strand})"))

    for eid in sorted(a_ids - b_ids):
        e = a_map[eid]
        removed.append(e)
        changes.append(ChangeRecord(
                entity_type=entity_type,  
                entity_id=eid,
                change_type="removed",    
                details=f"Removed in release B; was {e.seqid}:{e.start}-{e.end}({e.strand})"))

    for eid in sorted(a_ids & b_ids):
        ea = a_map[eid]
        eb = b_map[eid]
        if ea.signature() != eb.signature():
            diffs: List[str] = []
            if (ea.seqid, ea.start, ea.end) != (eb.seqid, eb.start, eb.end):
                diffs.append(f"coords {ea.seqid}:{ea.start}-{ea.end} -> {eb.seqid}:{eb.start}-{eb.end}")
            if ea.strand != eb.strand:
                diffs.append(f"strand {ea.strand} -> {eb.strand}")
            if (ea.parent_id or "") != (eb.parent_id or ""):
                diffs.append(f"parent {ea.parent_id} -> {eb.parent_id}")

            changed.append(eb)
            changes.append(
                ChangeRecord(
                    entity_type=entity_type,  
                    entity_id=eid,
                    change_type="changed",    
                    details="; ".join(diffs) if diffs else "signature changed"))

    return changes, added, removed, changed


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
    io.ensure_outdir(str(outdir))

    # Logging setup 
    log_file = outdir / "annot-consistency.log"
    log = build_logger(str(log_file))
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

    # Collect EntitySummary objects
    log.info("Collecting entity summaries from both releases")

    genes_a = _collect_entities(db_a, ["gene"], "gene")
    genes_b = _collect_entities(db_b, ["gene"], "gene")

    # Accept common transcript featuretype variants
    tx_a = _collect_entities(db_a, ["transcript", "mRNA", "mrna"], "transcript")
    tx_b = _collect_entities(db_b, ["transcript", "mRNA", "mrna"], "transcript")

    ex_a = _collect_entities(db_a, ["exon"], "exon")
    ex_b = _collect_entities(db_b, ["exon"], "exon")

    log.info("Counts A: genes=%d transcripts=%d exons=%d", len(genes_a), len(tx_a), len(ex_a))
    log.info("Counts B: genes=%d transcripts=%d exons=%d", len(genes_b), len(tx_b), len(ex_b))

    # Differentiating A vs B
    log.info("Differentiating releases A vs B")
    changes_all: List[ChangeRecord] = []
    added_all: List[EntitySummary] = []
    removed_all: List[EntitySummary] = []
    changed_all: List[EntitySummary] = []

    for etype, a_map, b_map in [
        ("gene", genes_a, genes_b),
        ("transcript", tx_a, tx_b),
        ("exon", ex_a, ex_b),
    ]:
        c, a, r, ch = _diff(etype, a_map, b_map)
        changes_all.extend(c)
        added_all.extend(a)
        removed_all.extend(r)
        changed_all.extend(ch)
        log.info("%s: added=%d removed=%d changed=%d", etype, len(a), len(r), len(ch))

    log.info(
        "Totals: changes=%d (added=%d removed=%d changed=%d)",
        len(changes_all),
        len(added_all),
        len(removed_all),
        len(changed_all),
    )

    # write_changes_tsv
    try:
        log.info("Writing changes.tsv")
        io.write_changes_tsv(str(outdir), changes_all)
    except Exception:
        log.exception("Failed writing changes.tsv")
        raise RuntimeError("Could not write changes.tsv")


    # write_summary_tsv

    try:
        log.info("Writing summary.tsv")
        io.write_summary_tsv(str(outdir), changes_all)
    except Exception:
        log.exception("Failed writing summary.tsv")
        raise RuntimeError("Could not write summary.tsv")

    
    # write_genome_tracks

    try:
        log.info("Writing genome browser tracks (added/removed/changed)")
        io.write_genome_tracks(str(outdir), added_all, removed_all, changed_all)
    except Exception:
        log.exception("Failed writing genome tracks")
        raise RuntimeError("Could not write genome tracks")


    #  write_run_json
    
    try:
        log.info("Writing run.json")
        io.write_run_json(
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

