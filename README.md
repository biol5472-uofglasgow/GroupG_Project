# Group G, Project 6 - Two-release annotation comparison (A vs B)
Contributors: Almarc Astorga, Ishwar Bijumon, Krishna Sameer Krothapalli, Saheshnu Sai Balaji Pillai

## Purpose of project
This project compares two genome annotation releases of the same organism (Release A vs Release B) to identify differences; it will produce a HTML report which includes: a summary outputs describing additions; removals; and changes across entity types between releases.

In version 1.1, a live change request was implemented to update the changes output for inclusion of a new change category: genomic coordinate shift above a threshold (based on user input). 

## Inputs
### Required 
- 'release_A.gff3': annotation release A in GFF3 format  
- 'release_B.gff3': annotation release B in GFF3 format  
### Optional 
- coordinate shift threshold: 

### Outputs
- 'changes.tsv': one row per difference (gene/transcript/exon; added/removed/changed)
- 'run.json':
- 'added.gff3': entities present in B but not A
- 'removed.gff3': entities present in A but not B
- 'changed.gff3': entities present in both but with signature differences
- 'summary.tsv': change counts by category and entity type for reporting 
- 'HTML page': includes provenance, overview, summary plot, counts table, artefacts and detailed changes

### Entity types
We track changes for:
- '"gene" 
- "mRNA" 
- "exon" 
- "protein_coding_gene"
-  "five_prime_UTR"
-  "three_prime_UTR"
-  "CDS"
-  "ncRNA"
-  "ncRNA_gene"
-  "pseudogene"
-  "pseudogenic_transcript"
- "rRNA"
-  "snoRNA"
-  "snRNA"
-  "tRNA"

### Change types
- 'added'
- 'removed'
- 'changed'

### Example of changed details


# Installation
### How to install 

...

### Requirements
- Python 3.10+ recommended  
- Suggested library; 'gffutils' (optional but recommended); for indexing and querying GFF3  
- Standard library modules as needed; 'argparse'; 'json'; 'csv'; 'logging'  

