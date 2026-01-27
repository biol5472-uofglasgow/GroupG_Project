from dataclasses import dataclass
from typing import Literal, Mapping, Optional

# Restrict types to only these
EntityType = Literal["gene", "mRNA", "exon", 
                     "protein_coding_gene", "five_prime_UTR", "three_prime_UTR",
                      "CDS", "ncRNA", "ncRNA_gene", "pseudogene", "pseudogenic_transcript",
                      "rRNA", "snoRNA", "snRNA", "tRNA"]
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
    strand: str
    parent_id: Optional[str]
    attrs: Mapping[str, str] # Mapping for immutable dict
    score: float        
    pahse: Literal[0,1,2]

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
