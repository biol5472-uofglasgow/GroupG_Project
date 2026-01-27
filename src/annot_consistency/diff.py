from annot_consistency.models import EntitySummary, ChangeRecord
from typing import List, Dict, Tuple, Optional, Mapping 

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

def build_entities(gff: str) -> Dict[str, Dict[str, EntitySummary]]:
    """
    Read ONE GFF3 release file and build structure needed by diff_entity: entity_type -> entity_id -> EntitySummary
    Only keeps entity types: gene, mRNA, exon.
    """
    entities_featuretype: Dict[str, Dict[str, EntitySummary]] = {"gene": {}, "mRNA": {}, "exon": {}}     # entity types for current fixtures

    with open(gff, "r") as file:
        for line in file:
            if not line or line.startswith("#"):        #ignore gff comments
                continue

            line = line.rstrip("\n")
            cols = line.split("\t")
            if len(cols) != 9:      # gff must have 9 columns
                raise ValueError(f"Invalid GFF3 line (expected 9 columns): {line}\ncol={cols}")

            seqid, source, featuretype, start, end, score, strand, phase, attr_s = cols
            if featuretype not in entities_featuretype:   # ignore features not being diff   
                continue

            start = int(start)
            end = int(end)
            attrs = parse_attrs(attr_s)     # attributess into dict
            entity_id = choose_entity_id(featuretype, attrs, seqid, start, end, strand)     # dict key for membership downstream
            parent_id: Optional[str] = attrs.get("Parent")      
            
            # Summary object for one gff feature
            entities_featuretype[featuretype][entity_id] = EntitySummary(
                entity_type=featuretype,
                entity_id=entity_id,
                seqid=seqid,
                start=start,
                end=end,
                strand=strand,
                parent_id=parent_id,
                attrs=attrs)

    return entities_featuretype 

# Writing function for checking through each attribute in the signature if they are different
def changed_details(a: EntitySummary, b: EntitySummary) -> str:
    '''
    Gives a string out joined from a list of strings based on the differences between the signatures of release A and release B
    '''
    parts: List[str] = []
    if a.seqid != b.seqid:
        parts.append(f'seqid: {a.seqid} -> {b.seqid}')
    if a.source != b.source:
        parts.append(f'Source: {a.source} -> {b.source}')
    if a.entity_type != b.entity_type:
        parts.append(f'Entity Type: {a.entity_type} -> {b.entity_type}')
    if a.start != b.start:
        parts.append(f'Start: {a.start} -> {b.start}')
    if a.end != b.end:
        parts.append(f'End: {a.end} -> {b.end}')
    if a.strand != b.strand:
        parts.append(f'Strand: {a.strand} -> {b.strand}')
    if a.parent_id != b.parent_id:
        parts.append(f'Parent ID: {a.parent_id} -> {b.parent_id}')
    if a.phase != b.phase:
        parts.append(f'Phase: {a.phase} -> {b.phase}')
    if a.score != b.score:
        parts.append(f'Score: {a.score} -> {b.score}')
    
    return '; '.join(parts)

def diff_entity(a_entities: Dict[str, Dict[str, EntitySummary]],
                b_entities: Dict[str, Dict[str, EntitySummary]]) -> Tuple[
                    List[ChangeRecord], List[EntitySummary], List[EntitySummary], List[EntitySummary],
                ]:
    '''
    Compares the two extracted release files A and B, then two lists
    One list for the changes.tsv and another list for the tracks added, removed and changed gff files
    '''
    changes: List[ChangeRecord]
    added: List[EntitySummary]
    removed: List[EntitySummary]
    changed: List[EntitySummary]

    for entity_type in ('gene', 'mRNA', 'exon'):
        a_map = a_entities.get(entity_type, {})
        b_map = b_entities.get(entity_type, {})
        
        a_id = set(a_map.keys())
        b_id = set(b_map.keys())

        # Added entities: If the ID is present only in release B and not in release A
        for e_id in b_id - a_id:
            added.append(b_map[e_id])
            changes.append(ChangeRecord(entity_type = entity_type, entity_id = e_id, change_type = 'added',
                                        details = 'Entity present only in release B'))
        
        # Removed entities: If the ID is present only in release A and not in release B
        for e_id in a_id - b_id:
            removed.append(a_map[e_id])
            changes.append(ChangeRecord(entity_type = entity_type, entity_id = e_id, change_type = 'removed',
                                        details = 'Entity present only in release A'))
        
        # Changed entities: First check if the entities are present in both, then see if signatures are different
        for e_id in (a_id & b_id):
            a = a_map[e_id]
            b = b_map[e_id]
            if a.signature() != b.signature():
                # Using the release B signatures for track output
                changed.append(b)
                changes.append(ChangeRecord(entity_type = entity_type, entity_id = e_id, change_type = 'changed',
                                        details = changed_details(a, b)))
        
    return changes, added, removed, changed

