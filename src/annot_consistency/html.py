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

def write_htmlreport(outdir: str, changes: list[ChangeRecord], summary_result: tuple[str, dict[str, int]],
                     run_json_path: str, title: str = 'Two release annotation consistency report') -> str:
    '''
    Generate report.html and report.png. Takes in outdir: output directory, changes: ChangeRecord list from diff stage 
    (taken from counts in io, used in cli), summary_result: (summary_path, counts) returned by io.write_summary_tsv(),
    run_json_path: path returned by io.write_run_json() and a title: HTML title.
    '''
    summary_path, counts = summary_result
    plot_counts(outdir, counts)

    entity_types = sorted(counts.keys())
    total_added = sum(counts[et].get('added', 0) for et in entity_types)
    total_removed = sum(counts[et].get('removed', 0) for et in entity_types)
    total_changed = sum(counts[et].get('changed', 0) for et in entity_types)
    total_all = total_added + total_removed + total_changed

    run_meta = dict[str, object] = {}