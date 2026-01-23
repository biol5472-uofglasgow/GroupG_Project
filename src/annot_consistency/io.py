import json
import datetime
import os
from typing import Any, Dict, List, Optional, Tuple
from annot_consistency.models import EntitySummary, ChangeRecord

# Ensuring output directory exists
def ensure_outdir(outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)

