import json
from datetime import timezone, datetime
import os
from typing import Any, Dict, List, Tuple
from annot_consistency.models import EntitySummary, ChangeRecord

# Ensuring output directory exists
def ensure_outdir(outdir: str) -> None:
    '''
    Creates an output directory if it doesn't exist
    '''
    os.makedirs(outdir, exist_ok=True)

# Writing function to be used in cli.py to write changes.tsv file
def write_changes_tsv(outdir: str, changes: List[ChangeRecord]) -> str:
    '''
    Gives a tab separated file with each row having the entity type(Gene, Transcript or Exon), the ID for that entity,
    the type of change (added, removed or changed (one or more attributes)) and exactly what was changed in the details
    One row per entity
    '''
    path = os.path.join(outdir, 'changes.tsv')
    with open(path, 'w', encoding = 'utf-8') as handle: # Using encoding for making sure it works on Windows/mac/Linux
        handle.write('Entity_Type\tEntity_ID\tChange_Type\tDetails\n')
        for c in changes:
            handle.write(f'{c.entity_type}\t{c.entity_id}\t{c.change_type}\t{c.details}\n')
    return path 

# Writing function to be used in cli.py to write summary.tsv file
def write_summary_tsv(outdir: str, changes: List[ChangeRecord]) -> Tuple[str, Dict[str, Dict[str, int]]]:
    '''
    Gives the counts for number of changes by entity type and the type of changes along with the total number of
    changes (addition and removals included) for that entity
    '''
    counts: Dict[str, Dict[str, int]] = {}
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

            file.write(f'{et}\t{a}\t{r}\t{ch}\{total}\n')
        
        all_total = all_added + all_removed + all_changed

        file.write(f'All_Total\t{all_added}\t{all_removed}\t{all_changed}\{all_total}')
    
    return path, counts

# Writing function to load the files that are created using the function below
def write_tracks(path: str, entities: List[EntitySummary]) -> None:
    with open(path, 'w', encoding='utf-8') as track:
        track.write('##gff-version 3\n')
        for e in entities:
            # setting up column 9 of gff3 file
            attrs_parts = [f'ID = {e.entity_id}']
            if e.parent_id:
                attrs_parts.append(f'Parent={e.parent_id}')
            attrs = ';'.join(attrs_parts)

            track.write(f'{e.seqid}\tgffACAKE\t{e.entity_type}\t{int(e.start)}\t{int(e.end)}\t{float(e.score)}\t{e.strand}\t{e.phase}\t{attrs}\n')

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

    write_tracks(added_path, added)
    write_tracks(removed_path, removed)
    write_tracks(changed_path, changed)

    return added_path, removed_path, changed_path

# Writing function to create the run.json metadata records
def write_run_json(tool_name: str, tool_version: str, release_a: str, release_b: str, outdir: str) -> str:
    '''
    Gives a record of tool metadata, timestamp, inputs used and the output filenames
    '''
    payload: Dict[str, Any] = {'tool': {'name':tool_name, 'version': tool_version},
                               'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                               'inputs': {'release_a': release_a, 'release_b': release_b},
                               'outputs': {'outdir': outdir, 'changes_tsv': 'changes.tsv', 'run_json': 'run.json',
                                           'added_gff3': 'added.gff3', 'removed_gff3': 'removed.gff3', 'changed_gff3': 'changed.gff3',
                                           'summary_tsv': 'summary.tsv'}}
    
    path = os.path.join(outdir, 'run.json')
    with open(path, 'w', encoding = 'utf-8') as jsonfile:
        json.dump(payload, jsonfile, indent = 2, sort_keys = True)
        jsonfile.write('\n')
        
    return path