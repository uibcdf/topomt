# CASTp Atom Materialization Audit (2026-04-10)

## Scope

This note records what the historical MKALF code actually does when it reports
the vertex-level content of a pocket, and contrasts that behaviour with the
current native TopoMT implementation. The goal is to avoid introducing ad hoc
rules while investigating the residual `1ubq` mismatch.

## Main Finding

The historical code does **not** build pocket atoms from arbitrary neighbour
atoms near a boundary triangle. Pocket vertices are derived from tetrahedra
that belong to the pocket, then partitioned into interior and regular vertices.

This means that adding a missing atom such as `299` by a reporting rule like
"include the opposite atom of a neighbouring tetrahedron" would be **non
canonical** with respect to MKALF.

## Evidence From the Historical Code

### Pocket printing

`print_pocket.c` prints pocket content through:

- `alf_scan_pocket_t0()` for interior tetrahedra (`iT`)
- `alf_scan_pocket_f0()` for interior triangles (`iF`)
- `alf_scan_pocket_f1()` for regular/mouth triangles (`rF`)
- `alf_scan_pocket_e0()` / `alf_scan_pocket_e1()` for edges (`iE` / `rE`)
- `alf_scan_pocket_v0()` / `alf_scan_pocket_v1()` for vertices (`iV` / `rV`)

So the historical pocket output is explicitly defined at tetrahedron, face,
edge, and vertex level.

### How vertices are selected

`voids.c` shows that:

- `alf_scan_pocket_v0()` and `alf_scan_pocket_v1()` both call
  `compute_vert_in_pocket(begin_pocket, end_pocket)`.
- `compute_vert_in_pocket()` marks vertices from tetrahedra already assigned to
  the pocket union-find.
- Those vertices are then classified as:
  - `iV`: vertex in pocket and interior at `rank2`, and not touched by peeling
  - `rV`: vertex in pocket and either not interior at `rank2` or touched by
    peeling

The relevant logic is therefore:

1. vertices come from tetrahedra in the pocket
2. they are split by `alf_is_interior(ALF_VERTEX, p_rank2, v)` and by the
   touched set induced by the outside component

This is materially different from building a boundary atom set from boundary
faces alone.

## Current Native Behaviour

In `topomt.third_party.castp.core.castp_core.components`:

- `atom_indices` are built from all vertices of tetrahedra in the component
- `component_atom_indices` are the same set
- `boundary_atom_indices` are built from vertices appearing in boundary faces

This has two consequences:

1. `atom_indices` are reasonably close to the historical pocket-vertex notion
   because they come from pocket tetrahedra.
2. `boundary_atom_indices` are **not** a faithful analogue of historical `rV`,
   because MKALF does not define `rV` as "vertices that appear in boundary
   faces". It defines them through pocket vertices plus
   `alf_is_interior(..., rank2)` plus the touched set.

## Consequence for the `1ubq` Residual

The current `1ubq` near-match pocket differs from the CASTp server pocket by a
single atom, `299`.

Known facts:

- `299` is **not** present in any tetrahedron currently assigned to the native
  pocket component.
- `299` does appear in a neighbouring tetrahedron (`2134`) adjacent to a pocket
  tetrahedron (`2133`).
- The shared face `(297, 300, 301)` is currently classified as in-complex, so
  tetrahedron `2134` stays outside the native pocket component.

Therefore, with the current evidence, the faithful question is **not**:

> how do we add atom `299` at reporting time?

The faithful question is:

> should tetrahedron `2134` belong to the pocket according to the canonical
> algorithm, or is this a genuine CASTp 3.0 divergence beyond MKALF 4.1?

## Additional Historical Observation

The historical `.poc` output for `1ubq` shows:

- tetrahedra and interior faces involving `299`
- `rV` entries for `297`, `300`, `301`, and `566`
- no observed `rV 299` entry in the inspected output

This does **not** yet prove whether `299` belongs to the exact same historical
pocket corresponding to the server residual, because pocket numbering/order in
the `.poc` file is not aligned with CASTp server numbering. But it reinforces
the point that the correct next step is local topological audit, not a reporting
patch.

## Implications

### What is justified

- keeping `atom_indices` tied to tetrahedra in the component
- auditing local face/rank classification around tetrahedra `2133` and `2134`
- comparing the native local decision with the historical MKALF output

### What is not justified

- adding neighbouring opposite atoms by heuristic
- redefining `boundary_atom_indices` as a substitute for historical `rV`
- treating the `1ubq` residual as a pure presentation problem

## Recommended Next Step

The next faithful investigation should focus on the local topology around the
shared face `(297, 300, 301)`:

1. verify native `face_rho_rank`, `face_mu1_rank`, and in-complex status
2. identify the corresponding historical pocket in the MKALF `.poc` output
3. determine whether tetrahedron `2134` should canonically enter the pocket

Only after that should we decide whether the residual is:

- a remaining native bug
- a residual difference between MKALF 4.1 and CASTp 3.0
- or a reporting-layer difference in the server
