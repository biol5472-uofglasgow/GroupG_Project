# gFFACAKE
***A two-release annotation comparison software (A vs B)***

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
-  "rRNA"
-  "snoRNA"
-  "snRNA"
-  "tRNA"

### Change types
- 'added'
- 'removed'
- 'changed'

### Example of changed details
![Changed details on the HTML webpage](images/DetailedChanges.png)

# Installation
## How to install and run the software
### Option 1: Docker



### Option 2: Python + UV
Required- Python 3.10+ and uv (python environment manager)
1. Install Python

To check if Python is installed, run the following command in terminal:
```bash
python3 --version
```
If not installed:

for macOS (Homebrew)-
```bash
brew install python
```

for Ubuntu/Debian-
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

for Windows-
Download from:
https://www.python.org/downloads/

Make sure python or python3 works in your terminal after installation.

2. Install uv

To install uv using pip, run the following command in terminal:
```bash
pip install uv
```
To verify installation:
```bash
uv --version
```
3. Clone the repository 

Run the following command in terminal :
```bash
git clone https://github.com/biol5472-uofglasgow/GroupG_Project.git
cd GroupG_Project
```
or use SSH key : git@github.com:biol5472-uofglasgow/GroupG_Project.git

4. Install dependencies

Use uv to install dependencies from pyproject.toml . Run the following command in terminal :
```bash
uv sync
```
This will create a virtual environment and install all required packages.

5. Running the program from the command line

Enter the following in the terminal:
```bash
uv run gffACAKE <releaseA.gff3> <releaseB.gff3> [outDir]
```
Where:
- releaseA.gff3 = first annotation file
- releaseB.gff3 = second annotation file
- outDir (optional) = directory for output files (default directory: ~/app/gffacake)


# How the software works


### Requirements
- Python 3.10+ recommended  
- Docker Version 27.1.1
- gffutils

