from annot_consistency.models import EntitySummary, ChangeRecord
from typing import List, Dict, Tuple, Optional, Mapping 
import gffutils

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


def build_entities(db: gffutils.FeatureDB) -> Dict[str, Dict[str, EntitySummary]]:
    """
    Read ONE GFF3 release file and build structure needed by diff_entity: entity_type -> entity_id -> EntitySummary
    Only keeps entity types: gene, mRNA, exon.
    """
    entities_feature_type: Dict[str, Dict[str, EntitySummary]] = {"gene": {}, "mRNA": {}, "exon": {}}     # entity types for current fixtures

    for feature in db.all_features(order_by=("seqid", "start")):
        if feature.featuretype not in entities_feature_type:
            continue

        attrs = feature.attributes

        entity_id = choose_entity_id(feature.featuretype, attrs, feature.seqid, feature.start, feature.end, feature.strand)

        parent_id: Optional[str] = None
        if "Parent" in attrs and attrs["Parent"]:
            parent_id = ",".join(attrs["Parent"])

        entities_feature_type[feature.featuretype][entity_id] = EntitySummary(
            entity_type=feature.featuretype,
            entity_id=entity_id,
            seqid=feature.seqid,
            start=feature.start,
            end=feature.end,
            strand=feature.strand,
            parent_id=parent_id,
            attrs={key: ",".join(value) for key, value in attrs.items()})

    return entities_feature_type

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

