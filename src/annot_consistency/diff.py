from typing import Dict, Optional, Mapping
from annot_consistency.models import EntitySummary

def parse_attrs(attrs: str) -> Dict[str, str]:
    """
    Parse GFF3 column 9 (attributes) into a simple dict.
    Stable entity ID parsed
    """
    attrs = attrs.strip()
    if not attrs or attrs == ".":       # . = empty attribute in gff3
        return {}

    parsed_attrs: Dict[str, str] = {}
    for row in attrs.split(";"):
        row = row.strip()
        if not row:
            continue

        if "=" not in row:
            parsed_attrs[row] = ""      # attributes may exist with no values, ensure consistency for downstream analysis
            continue

        key, value = row.split("=", 1)        # only split at the first '=' to ensure only 2 elements 
        parsed_attrs[key.strip()] = value.strip()
    return parsed_attrs

def choose_entity_id(featuretype: str, attrs: Mapping[str, str], seqid: str, start: int, end: int, strand: str,) -> str:
    """
    Prefer ID=; if missing, create a fallback ID.
    diffing uses entity IDs as dict keys; if an exon has no ID, we choose a stable key.
    """
    entity_id = attrs.get("ID")
    if entity_id:       # if exists, use this ID
        return entity_id

    parent = attrs.get("Parent")        # If no ID, revert to parent ID
    if parent:
        parent_list = parent.split(",")     # split Parent into individual IDs
        tidy_parent = []
        for row in parent_list:
            if row != "":
                tidy_parent.append(row)   # remove empty values
        tidy_parent.sort()               # sort to prevent false positives of feature has more than 1 parent
        parents = ",".join(tidy_parent)
        return f"{featuretype}, parent={parents}|{seqid}:{start}-{end}:{strand}"     # parent ID alone is not stable enough

    return f"{featuretype}|{seqid}:{start}-{end}:{strand}"        # Final fallback if no parents: feature type + genomic location 