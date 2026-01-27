from typing import Dict, Optional
from annot_consistency.models import EntitySummary
from annot_consistency.models import ChangeRecord

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