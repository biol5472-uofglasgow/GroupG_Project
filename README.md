# GroupG_Project
HELLO I AM UNDER THE WATER

Contributors: Almarc Astorga, Ishwar Bijumon, Krishna Sameer Krothapalli, Saheshnu Sai Balaji Pillai

# Project 6: Two-release annotation consistency (A vs B)

### Goal: Purpose of project
This project compares two genome annotation releases (Release A vs Release B, or more) to identify differences; it will produce a  "issues ledger" and summary outputs describing additions; removals; and changes across entity types between releases
### Process: What are the projects inputs and outputs
### Inputs; required 
- 'release_A.gff3': annotation release A in GFF3 format  
- 'release_B.gff3': annotation release B in GFF3 format  
### Outputs; required
- 'changes.tsv': one row per difference (gene/transcript/exon; added/removed/changed)
- 'run.json': ... 

### Optional outputs 
- 'added.gff3'; entities present in B but not A; ...
- 'removed.gff3'; entities present in A but not B; ...
- 'changed.gff3'; entities present in both but with differences;
- BED equivalents; ... 
- 'summary.tsv'; change counts by category and entity type for reporting  
### Entity types
We track changes for:
- 'gene'
- 'transcript'
- 'exon'

### Change types
- 'added'
- 'removed'
- 'changed'

### Example of changed details
...

# Installation
### How to install and run 

# MacOS / Linux #

1. Open a terminal window in the directory containing the two input GFF files you wish to compare 

2. Copy-Paste and run the following docker command onto the command line to run gffACAKE on your GFF files:
**docker run --rm -v "$PWD:/data" ghcr.io/group_g_project/gffACAKE:0.5.0/data/release_A.gff /data/release_B.gff**


	  
# Windows #

1. Open a Powershell window in the directory containing the two input GFF files you wish to compare 

2. Copy-Paste and run the following docker command onto the command line to run gffACAKE on your GFF files:
**docker run --rm -v ${PWD}:/data ghcr.io/group_g_project/gffACAKE:0.5.0/data/release_A.gff /data/release_B.gff**


### Requirements
- Docker