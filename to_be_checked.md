- PyCAST
https://github.com/giorgioluciano/pycasta
https://www.csbj.org/article/S2001-0370(25)00318-6/fulltext


CASTp, fpocket, MOLE, KVFinder, PyVOL

Fpocket: fast, robust single-structure pocket discovery; great for batch runs & descriptors. 
PMC

MDpocket: conformational ensembles/MD; maps pocket persistence and cryptic sites. 
PubMed

CASTp: careful geometric/topological measurement of cavities/channels (alpha-shape orthogonal spheres), good for validation. 
PMC
+1

AlphaSpace(2.0): fragment-centric mapping at concave/PPIs; helpful for ligand design beyond small-molecule clefts. 
ACS Publications
+1

Pocket-to-Concavity (P2C): refinement on top of alpha-sphere pockets to correct “over-estimated” cavities. 
OUP Academic

Wrap Fpocket from Python: call the fpocket/mdpocket binaries via subprocess or use the BioExcel Building Blocks (biobb_vs) wrappers to orchestrate runs and filter results. 
biobb-vs.readthedocs.io
+1

MDpocket utilities: the fpocket/MDpocket manual ships a small Python script (createMDPocketInputFile.py) to prep trajectory snapshots; MDpocket also reads common MD formats (XTC/DCD/NetCDF). 
fpocket.sourceforge.net
+1

PockDrug: https://pockdrug.rpbs.univ-paris-diderot.fr/cgi-bin/index.py?page=home
