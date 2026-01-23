import json
import datetime
import os
from typing import Any, Dict, List, Optional, Tuple
from annot_consistency.models import EntitySummary, ChangeRecord

# Ensuring output directory exists
def ensure_outdir(outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)

def write_changes_tsv(outdir: str, changes: List[ChangeRecord]) -> str:
    path = os.path.join(outdir, 'changes.tsv')
    with open(path, 'w', encoding = 'utf-8') as handle: # Using encoding for making sure it works on Windows/mac/Linux
        handle.write('Entity_Type\tEntity_ID\tChange_Type\tDetails\n')
        for c in changes:
            handle.write(f'{c.entity_type}\t{c.entity_id}\t{c.change_type}\t{c.details}\n')
    return path 