# CASTp Checkpoint 2026-04-10

## Purpose

This checkpoint records the work done after the 2026-04-09 pause, focused on
mouth connectivity, `branched_channel` support, and the question:

- is the remaining gap just "we still do not match MKALF 4.1 closely enough",
  or is there now direct evidence of a deeper CASTp-3.0-vs-MKALF divergence?

Short answer:

- some real implementation defects were fixed;
- one important mouth-clustering defect was corrected;
- but the remaining red cases now point to a genuine CASTp 3.0 evolution gap,
  not just an obviously wrong local heuristic in TopoMT.

Related documents:

- [native_parity_matrix_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/native_parity_matrix_2026_04_10.md)
- [checkpoint_2026_04_10_route_to_parity.md](/home/diego/repos@uibcdf/topomt/devguide/castp/checkpoint_2026_04_10_route_to_parity.md)
- [failure_analysis_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/failure_analysis_2026_04_10.md)
- [canonical_gap_audit_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/canonical_gap_audit_2026_04_10.md)
- [checkpoint_2026_04_10_canonicalization_round2.md](/home/diego/repos@uibcdf/topomt/devguide/castp/checkpoint_2026_04_10_canonicalization_round2.md)
- [atom_materialization_audit_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/atom_materialization_audit_2026_04_10.md)
- [checkpoint_2026_04_11_vertex_materialization.md](/home/diego/repos@uibcdf/topomt/devguide/castp/checkpoint_2026_04_11_vertex_materialization.md)
- [checkpoint_2026_04_11_spectrum_rank_audit.md](/home/diego/repos@uibcdf/topomt/devguide/castp/checkpoint_2026_04_11_spectrum_rank_audit.md)
- [open_canonical_fronts_2026_04_11.md](/home/diego/repos@uibcdf/topomt/devguide/castp/open_canonical_fronts_2026_04_11.md)

---

## What changed in code

### 1. `WeightedDelaunayMesh` now preserves tetrahedron orientation

File:

- [topomt/weighted_delaunay_mesh.py](/home/diego/repos@uibcdf/topomt/topomt/weighted_delaunay_mesh.py)

Problem:

- the weighted mesh stored tetrahedra only as sorted vertex quadruples;
- `face_index` therefore referred to sorted simplices, not geometrically
  oriented simplices;
- this is incompatible with faithful CAST/MKALF-style edge-facet logic.

Fix:

- introduced `_orient_simplex_vertices()`;
- `_regular_triangulation_simplices()` now returns both
  `oriented_simplices` and sorted `simplices`;
- neighbors, simplex centers, volumes, and face extraction now use the
  oriented simplices;
- `get_face_atoms()` still returns sorted atom triples externally.

New regression:

- `tests/test_castp_core.py::test_weighted_delaunay_mesh_preserves_oriented_tetrahedra`

This is a safe substrate fix and should remain.

### 2. Native `branched_channel` support was added

Files:

- [topomt/third_party/castp/core/castp_core/components.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/core/castp_core/components.py)
- [topomt/third_party/castp/_native_impl.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/_native_impl.py)

What changed:

- `n_mouths == 1` → `pocket`
- `n_mouths == 2` → `channel`
- `n_mouths >= 3` → `branched_channel`

New regressions:

- `tests/test_castp_core.py::test_build_castp_feature_records_classifies_branched_channels`
- `tests/test_castp_core.py::test_castp_recovers_branched_channel_for_1a4j_pocket_2`

This is also a safe improvement and should remain.

### 3. Mouth clustering was tightened to follow MKALF more closely

File:

- [topomt/third_party/castp/core/castp_core/mouths.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/core/castp_core/mouths.py)

Old behaviour:

- directly unioned mouth faces that shared shape edges;
- and also used an `Fnext`-style walk for open edges.

Why that was wrong:

- `alf_init_mouths()` in `mkalf/voids.c` does **not** union mouths just because
  they share a shape edge;
- it only initiates connectivity from edge-facets whose edge is **not** in the
  alpha complex at `rank1`;
- therefore the old hybrid over-merged mouths and collapsed some channels into
  pockets.

Current behaviour:

- direct shape-edge union was removed;
- connectivity now comes only from `Fnext` walks around open edges.

This is a genuine correction relative to the historical C logic.

---

## New parity evidence

### Green

#### `2PK4`

This case remained a strong green reference earlier in the audit:

- `void`: exact parity
- `pocket`: exact parity

It still serves as evidence that the native geometry and component assembly are
not globally broken.

#### `1A4J Pocket 2`

`Pocket 2` in the oracle is a `branched_channel`, and the native method now
recovers it as:

- `feature_type = branched_channel`
- `n_mouths = 3`

This is the best current evidence that the native path can express the
`branched_channel` feature family correctly.

### Red

#### `1STP Pocket 7`

New regression test:

- `tests/test_castp_core.py::test_castp_recovers_channel_for_1stp_pocket_7`

Oracle:

- `feature_type = channel`
- `n_mouths = 2`
- atom set = `[846, 848, 854, 865]`

What was observed during the audit:

1. before tightening `mouths.py`, the native method found the same atom set but
   classified it as:
   - `pocket`
   - `n_mouths = 1`

2. after removing direct shape-edge union, the same atom set became:
   - `branched_channel`
   - `n_mouths = 3`

So the defect is now sharply localized:

- TopoMT is not failing to find the feature;
- it is failing to reproduce the CASTp 3.0 mouth partition for that feature.

This is a better failure than before because it is narrower and more explicit.

---

## What was tested and ruled out

### 1. Changing pocket assembly globally to `rank1 = probe_rank`

This was tested again during this session and reverted.

Result:

- it degraded component assembly and moved the native output away from the
  server oracle on `1STP`;
- therefore it should not be adopted as a blanket fix.

Status:

- current code still uses `rank1 = base_rank` for pocket assembly;
- the regression expectation in `tests/test_castp_core.py` was restored
  accordingly.

### 2. "If we just match MKALF more literally, we will automatically match CASTp 3.0"

This is no longer tenable as a general assumption.

Evidence from this session:

- the historical `delcx` + `mkalf` binaries in `tools/mkalf/bin/` were used
  successfully on a generated `1STP` `.dat` file;
- `mkalf -A` produced pocket printouts for both:
  - `rank 8828 rank2 12584`
  - `rank 8535 rank2 12584`
- the resulting historical pocket sections do not line up cleanly with the
  CASTp 3.0 server `Pocket 7` channel of four lining atoms.

Interpretation:

- MKALF 4.1 remains essential as a historical algorithmic reference;
- but for at least some small pocket/channel cases, CASTp 3.0 is not just
  "MKALF with the same mouth semantics exposed differently".

This is consistent with the 2026-04-09 finding that `1HIV POC-11` is present in
CASTp 3.0 but not in MKALF 4.1.

---

## Practical conclusions

### Safe improvements now in place

These should be kept:

- oriented weighted tetrahedra in `WeightedDelaunayMesh`
- `branched_channel` classification and tests
- removal of direct shape-edge mouth union

### Remaining red zone

The remaining red zone is now very specific:

- CASTp 3.0 mouth partitioning for small open features;
- especially how 3 mouth triangles become 2 mouths in `1STP Pocket 7`.

At this point, the problem is not well-described as "more trial and error in
TopoMT mouths.py". The next useful work should be one of:

1. inspect newer CASTp 3.0-specific code or artefacts, if obtainable;
2. extract more information from CASTp 3.0 outputs to infer which mouth
   triangles are grouped together;
3. compare the server output against the historical MKALF printout on more
   small cases to characterize the exact evolution pattern.

---

## Recommended restart point

Resume from this question:

> What additional rule, beyond MKALF 4.1 `alf_init_mouths`, causes CASTp 3.0 to
> report `1STP Pocket 7` as a 2-mouth channel instead of a 1-mouth pocket or a
> 3-mouth branched channel?

Do **not** restart from:

- "try another local clustering heuristic"
- "switch everything to `probe_rank`"
- "assume MKALF 4.1 is the final oracle"

Those paths have already been tested enough to know they are insufficient.

Related matrix document:

- [native_parity_matrix_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/native_parity_matrix_2026_04_10.md)
- [checkpoint_2026_04_10_route_to_parity.md](/home/diego/repos@uibcdf/topomt/devguide/castp/checkpoint_2026_04_10_route_to_parity.md)
- [failure_analysis_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/failure_analysis_2026_04_10.md)
