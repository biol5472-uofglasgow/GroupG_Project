from dataclasses import dataclass
from typing import Literal, Mapping

# Restrict types to only these
EntityType = Literal["gene", "transcript", "exon"]
ChangeType = Literal["added", "removed", "changed"]

#Dataclasses to be immutable
@dataclass(frozen=True)
class EntitySummary:
    """
    Object for comparing immutable attributes of a GFF entity (gene, transcript, exon).
    Used for diffing releases.
    """
    entity_type: EntityType
    entity_id: str
    seqid: str
    start: int
    end: int
    strand: str | None      # NULL if none
    parent_id: str | None   # NULL if none
    attrs: Mapping[str, str] # Mapping for immutable dict

    def signature(self) -> tuple:
        """
        Defines what counts as 'changed' for this entity.
        Compares entity properties
        """
        return (
            self.seqid,
            self.start,
            self.end,
            self.strand,
            self.parent_id,
        )

@dataclass(frozen=True)
class ChangeRecord:
    """
    Object output for one change per entity type; one row in changes.tsv
    """
    entity_type: EntityType
    entity_id: str
    change_type: ChangeType
    details: str
