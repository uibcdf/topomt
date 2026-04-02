**Pocketeer Contract**

Purpose: record the scope of the TopoMT-native `pocketeer` method so the
implemented parity effort stays focused on the same descriptors that the
original project documents.

## Upstream references

- Project site/documentation: <https://pocketeer.readthedocs.io/en/latest/>  
- Source repository/mirror: <https://github.com/cch1999/pocketeer>, local clone at `~/repos@others/pocketeer`

## What TopoMT must reproduce

1. Filtering a protein structure (remove H atoms, water/solvent, hetero atoms) and computing all alpha spheres from Delaunay tessellation in the requested radius range.
2. Labeling spheres by buriedness via SASA (using a polar probe radius), filtering only buried ones, clustering them by graph adjacency, and merging clusters using the merge distance/min sphere count heuristics.
3. Creating pockets with scoring descriptors (number of spheres, centroid, volume, mean radius), running the same probe scoring functions (if applicable), and sorting pockets by score.
4. Exporting atom indices and masks consistent with `Pocket` objects so downstream features can compare atom membership.

## Validation target

- `tests/methods/pocketeer/test_parity.py` compares pocket counts, sphere
  counts, and scores against a reference run produced by
  `~/repos@others/pocketeer` on the audited demo structures.
- We expect the TopoMT method to agree on `find_pockets` outputs to within the same tolerances the upstream project uses (ranking, number of spheres per pocket, volume estimates).

## Practical notes

- Keep this contract updated so reviewers know where the upstream logic lives
  and which local repository serves as the parity fixture.
- When a new helper (e.g., cluster_spheres, scoring metrics) becomes necessary, reflect on whether it belongs in MolSysMT or another shared helper repo before proliferating local copies.
