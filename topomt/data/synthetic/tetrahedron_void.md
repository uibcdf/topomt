# tetrahedron_void

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `tetrahedron_void.pdb`
- **Atoms:** 4 · **Probe:** 1.4 Å
- **Expected by construction:** minimal 4-atom cell (sanity baseline)
- **DFND families (significant):** (none significant)
<!-- /AUTO -->

- **Generator:** `tetrahedron(edge=6.0)`

## What to observe

The smallest possible cell: **a single** Delaunay tetrahedron (4 atoms → 1 tetra).
The 1.4 Å probe fits inside (resident), but the component comes out as family
`percolating` with `n_mouths = 1` and **1 node** — below the significance threshold
(≥5 nodes), which is why the family summary reads "(none significant)".

## Why

With only 4 atoms, the **four faces** of the single tetrahedron lie on the convex
hull (all face OCEAN). A probe sitting inside is not *enclosed*: every face is an
exit. So DFND does not call it a void (0 mouths, closed) but `percolating` / open.
The name "tetrahedron_**void**" is aspirational; the geometric reality of a 4-atom
cell is an **open** cavity.

## DFND verdict

✅ **Correct** (and instructive). DFND is not fooled by the name: a 4-atom cell
encloses nothing, and it classifies it as open (`percolating`), not as a void. It is
the sanity baseline: it confirms that "void" requires *enclosure* (internal faces
that seal it), not merely that the probe fits.
