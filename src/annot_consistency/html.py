from annot_consistency.models import ChangeRecord
import json
import os
from datetime import datetime
from typing import dict, list, tuple
import matplotlib as plt

def plot_counts(outdir: str, counts: dict[str, dict[str, int]]) -> str:
    '''
    Creates a bar plot of the counts of the different changes types per entity type,
    saved as a png file to be used in the html report
    '''
    entity_types = sorted(counts.keys())
    added = [counts[et].get('added', 0) for et in entity_types]
    removed = [counts[et].get('removed', 0) for et in entity_types]
    changed = [counts[et].get('changed', 0) for et in entity_types]

    x = list(range(len(entity_types)))

    plt.figure()
    plt.bar(x, added, label = 'Added')
    plt.bar(x, removed, bottom=added, label="removed")
    bottoms = [a + r for a, r in zip(added, removed)]
    plt.bar(x, changed, bottom=bottoms, label="changed")
    plt.xticks(x, entity_types, rotation=45, ha="right")
    plt.ylabel("Count")
    plt.title("Change counts by entity type")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(outdir, "report.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()

    return plot_path