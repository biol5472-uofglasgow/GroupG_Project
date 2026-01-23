import json
import datetime
import os
from typing import Any, Dict, List, Optional, Tuple
from annot_consistency.models import EntitySummary, ChangeRecord

# Ensuring output directory exists
def ensure_outdir(outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)

# Writing function to be used in cli.py to write changes.tsv file
def write_changes_tsv(outdir: str, changes: List[ChangeRecord]) -> str:
    '''
    Gives a tab separated file with each row having the entity type(Gene, Transcript or Exon), the ID for that entity,
    the type of change (added, removed or changed (one or more attributes)) and exactly what was changed in the details
    '''
    path = os.path.join(outdir, 'changes.tsv')
    with open(path, 'w', encoding = 'utf-8') as handle: # Using encoding for making sure it works on Windows/mac/Linux
        handle.write('Entity_Type\tEntity_ID\tChange_Type\tDetails\n')
        for c in changes:
            handle.write(f'{c.entity_type}\t{c.entity_id}\t{c.change_type}\t{c.details}\n')
    return path 

# Writing function to be used in cli.py to write summary.tsv file
def write_summary_tsv(outdir: str, changes: List[ChangeRecord]) -> str:
    '''
    Gives the counts for number of changes by entity type and the type of changes along with the total number of
    changes (addition and removals included) for that entity
    '''
    counts = Dict[str, Dict[str, int]] = {}
    for c in changes:
        et = c.entity_type
        if et not in counts:
            counts[et] = {'added': 0, 'removed': 0, 'changed': 0}
        if c.change_type in counts[et]:
            counts[et][c.change_type] += 1
    
    path = os.path.join(outdir, 'summary.tsv')
    with open(path, 'w', encoding = 'utf-8') as file:
        file.write('Entity_Type\tAdded\tRemoved\tChanged\tTotal\n')
        all_added = 0
        all_removed = 0
        all_changed = 0

        for et in sorted(counts.keys()):
            a = counts[et]['added']
            r = counts[et]['removed']
            ch = counts[et]['changed']
            total = a + r + ch

            all_added += a
            all_removed += r
            all_changed += ch

            file.write(f'{et}\t{a}\t{r}\{ch}\{total}\n')
        
        all_total = all_added + all_removed + all_changed

        file.write(f'All_Total\t{all_added}\t{all_removed}\t{all_changed}\{all_total}')
    
    return path

# Writing function to create the genome browser loadable tracks as gff3 files
def write_genome_tracks(outdir: str, 
                        added: List[EntitySummary], 
                        removed: List[EntitySummary], 
                        changed: List[EntitySummary]) -> Tuple[str, str, str]:
    '''
    Gives three genome browser loadable tracks as gff3 files named added.gff, removed.gff and changed.gff 
    '''
    added_path = os.path.join(outdir, 'added.gff3')
    removed_path = os.path.join(outdir, 'removed.gff3')
    changed_path = os.path.join(outdir, 'changed.gff3')

    return added_path, removed_path, changed_path

