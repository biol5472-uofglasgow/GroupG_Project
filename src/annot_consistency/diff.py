from collections.abc import Mapping

import gffutils

from annot_consistency.models import ChangeRecord, EntitySummary


def choose_entity_id(featuretype: str,
                    attrs: Mapping[str, list[str]],
                    seqid: str,
                    start: int,
                    end: int,
                    strand: str,) -> str:
    """
    Prefer ID=; if missing, create a fallback ID.
    diffing uses entity IDs as dict keys; if an exon has no ID, we choose a stable key.
    attrs comes from gffutils; values are lists because GFF3 can store multiple values per key.
    """
    entity_id = attrs.get("ID", [])
    if entity_id:
        return entity_id[0]  # gffutils stores ID as a list; first element is the ID

    parents = attrs.get("Parent", [])       # if no ID, use parent as fallback option
    if parents:
        tidy_parent: list[str] = []
        for p in parents:
            if p:
                tidy_parent.append(p)

        tidy_parent.sort()
        parent = ",".join(tidy_parent)
        return f"{featuretype}|parent={parent}|{seqid}:{start}-{end}:{strand}"

    return f"{featuretype}|{seqid}:{start}-{end}:{strand}"      # final fallback if no id or parent


def build_entities(db: gffutils.FeatureDB) -> dict[str, dict[str, EntitySummary]]:
    """
    Read ONE GFF3 release file and build structure needed by
    diff_entity: entity_type -> entity_id -> EntitySummary
    Only keeps entity types: gene, mRNA, exon.
    """
    entities_feature_type: dict[str, dict[str, EntitySummary]] = {
        "gene": {},
        "mRNA": {},
        "exon": {},
        "protein_coding_gene": {},
        "CDS": {},
        "five_prime_UTR": {},
        "three_prime_UTR": {},
        "ncRNA": {},
        "ncRNA_gene": {},
        "pseudogene": {},
        "pseudogenic_transcript": {},
        "rRNA": {},
        "snoRNA": {},
        "snRNA": {},
        "tRNA": {}
        }
    # entity types for current fixtures

    for feature in db.all_features(order_by=("seqid", "start")):
        if feature.featuretype not in entities_feature_type:
            continue

        attrs = feature.attributes

        entity_id = choose_entity_id(feature.featuretype, attrs, feature.seqid,
                                    feature.start, feature.end, feature.strand)

        parent_id: str | None = None
        if "Parent" in attrs and attrs["Parent"]:
            parent_id = ",".join(attrs["Parent"])

        # create immutable summary object for diffing; store it under its feature type
        # and stable entity_id key.
        entities_feature_type[feature.featuretype][entity_id] = EntitySummary(
            entity_type = feature.featuretype,
            entity_id = entity_id,
            seqid = feature.seqid,
            source = feature.source,
            start = feature.start,
            end = feature.end,
            score = feature.score,
            strand = feature.strand,
            phase = feature.frame,
            parent_id = parent_id,
            attrs = {key: ",".join(value) for key, value in attrs.items()})

    return entities_feature_type

# Writing function for checking through each attribute in the signature if they are different
def changed_details(a: EntitySummary, b: EntitySummary) -> str:
    '''
    Gives a string out joined from a list of strings based on the differences
    between the signatures of release A and release B
    '''
    parts: list[str] = []
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

# Get delta coordinates
def deltas_coords(a: EntitySummary, b: EntitySummary) -> tuple[int, int]:
    """
    get start and end deltas for release A and release B.
    calculates coordinate displacement of the same genomic entity;
    """
    delta_start = b.start - a.start
    delta_end = b.end - a.end
    return delta_start, delta_end

def delta_of_deltas(delta_start: int, delta_end: int) -> int:
    """
    The largest coordinate shift the entity has went between the two releases
    applies absolute values to remove direction; selects the maximum of the two magnitude
    """
    return max(abs(delta_start), abs(delta_end))


def diff_entity(a_entities: dict[str, dict[str, EntitySummary]],
                b_entities: dict[str, dict[str, EntitySummary]],
                threshold: int | None = None) -> tuple[
                    list[ChangeRecord],
                    list[EntitySummary],
                    list[EntitySummary],
                    list[EntitySummary],
                ]:
    '''
    Compares the two extracted release files A and B, then two lists
    One list for the changes.tsv and
    another list for the tracks added, removed and changed gff files
    Threshold:
    - start_threshold if abs(start_B - start_A) > threshold
    - end_threshold if abs(end_B - end_A) > threshold
        = high_shift True if either threshold exceeded
    - if signature differs but no threshold exceeded, continue with change_type="changed"
    '''
    if threshold is not None and threshold < 0:
        raise ValueError("threshold must be > 0 ")
    changes: list[ChangeRecord] = []
    added: list[EntitySummary] = []
    removed: list[EntitySummary] = []
    changed: list[EntitySummary] = []

    for entity_type in ("gene", "mRNA", "exon",
                    "protein_coding_gene", "five_prime_UTR", "three_prime_UTR",
                    "CDS", "ncRNA", "ncRNA_gene", "pseudogene", "pseudogenic_transcript",
                    "rRNA", "snoRNA", "snRNA", "tRNA"):
        a_map = a_entities.get(entity_type, {})
        b_map = b_entities.get(entity_type, {})

        a_id = set(a_map.keys())
        b_id = set(b_map.keys())

        # Added entities: If the ID is present only in release B and not in release A
        for e_id in b_id - a_id:
            added.append(b_map[e_id])
            changes.append(ChangeRecord(
                entity_type = entity_type,
                entity_id = e_id,
                change_type = 'added',
                details = 'Entity present only in release B',
                )
            )
        # Removed entities: If the ID is present only in release A and not in release B
        for e_id in a_id - b_id:
            removed.append(a_map[e_id])
            changes.append(ChangeRecord(
                entity_type = entity_type,
                entity_id = e_id,
                change_type = 'removed',
                details = 'Entity present only in release A',
                )
            )
        # Changed entities: First check if the entities are present in both,
        # then see if signatures are different
        for e_id in (a_id & b_id):
            a = a_map[e_id]
            b = b_map[e_id]
            if a.signature() == b.signature():
                continue
            changed.append(b)
            # No threshold exceeded: other signature changes
            if threshold is None:
                changes.append(
                    ChangeRecord(
                        entity_type = entity_type,
                        entity_id = e_id,
                        change_type = 'changed',
                        details = changed_details(a,b),
                        high_shift = False
                    )
                )
            else:
                # Delta logic:
                delta_start, delta_end = deltas_coords(a, b)
                delta_shift= delta_of_deltas(delta_start, delta_end)

                # Check threshold: based on user input for threshold
                start_exceeds = abs(delta_start) > threshold
                end_exceeds = abs(delta_end) > threshold
                start_and_end_exceeds = (abs(delta_shift)) > threshold
                high_shift = start_exceeds or end_exceeds or start_and_end_exceeds
                high_shift_details: str 

                if start_exceeds:
                        high_shift_details = (
                            f"start_delta={delta_start};\
                            threshold={threshold}"
                        )
                elif end_exceeds:
                        high_shift_details = (
                            f"end_delta={delta_end};\
                            threshold={threshold}"
                        )
                elif start_and_end_exceeds:
                        high_shift_details = (
                            f"start_delta={delta_start};\
                                end_delta={delta_end};\
                            delta_of_deltas={delta_shift};\
                            threshold={threshold}"
                        )
                else:
                        high_shift_details = changed_details(a, b)

                if high_shift:
                    changes.append(
                        ChangeRecord(
                            entity_type=entity_type,
                            entity_id=e_id,
                            change_type="changed",
                            details=high_shift_details,
                            high_shift=True,
                        )
                    )
    return changes, added, removed, changed
