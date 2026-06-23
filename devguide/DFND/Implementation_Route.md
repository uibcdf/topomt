# DFND Implementation Route

This document defines the current route to make DFND the production-ready
native TopoMT topography method.

The older route assumed DFND had to be built from scratch. The repository now
contains an active implementation under topomt/dfnd/, so the work should focus on hardening, validation, performance, and disciplined API promotion.

## 1. Fix the Canonical Contract

Goal: make the method definition unambiguous before changing behavior.

Tasks:

1. Keep standard Delaunay as the baseline substrate.
2. Keep atomic radii in `R_residence` and `R_gate`, not in a weighted triangulation.
3. Adopt feature_definitions.md as the canonical DFN, external-link,
   concavity-component, and feature-construction contract.
4. Treat COAST as a mixed-boundary metadata label: at least one permeable face and at least one non-permeable face.
5. Record every non-default tolerance as an explicit parameter.
6. Follow abstract_contract.md, numerical_policy.md, metrics_contract.md, and input_policy.md while those policies are refined.
7. Treat data_model_v1.md and toy_systems_v1.md as the immediate implementation contract.
8. Treat validation_plan.md as the credibility boundary before external claims.

Exit criteria:

- the docs state one canonical interpretation;
- implementation choices can be checked against that interpretation;
- the v1 data model and toy-system list are explicit enough to drive tests.

## 2. Implement the v1 Raw Data Model

Goal: create the minimal records needed before feature-level integration.

Tasks:

1. Add raw records for parameters, tetrahedra, faces, wet network,
   concavity components, external links, dry components, dry interfaces, and raw
   DFND output.
2. Keep semantic `TopographyFeature` conversion downstream.
3. Preserve atom ids, atom indices, tetrahedron ids, face ids, thresholds,
   flags, and policy parameters in raw records.
4. Ensure raw records can be created without invoking PDB-specific or
   third-party-provider logic.

Exit criteria:

- `dfnd(...)` can expose or return a reproducible raw record;
- every primary classification decision is traceable to fields in the raw
  record;
- no public convexity, boundary, or mixed feature class is required yet.

## 3. Stabilize the Geometry Kernels

Goal: make the physical quantities reliable.

Tasks:

1. Add unit tests for `tetrahedron_residence_radius` on simple tetrahedral geometries.
2. Add unit tests for `face_gate_radius` on open, closed, tangent,
   collinear, and near-threshold faces. Keep `check_face_permeability` as a
   scalar compatibility wrapper only while older call sites exist.
3. Verify units and radius conventions at the MolSysMT boundary.
4. Add regression tests for degenerate tetrahedra and sliver-like cases.
5. Decide whether numerical failures return zero, nan, or flagged records.
6. Audit whether the current face-plane `R_gate` model is exact or approximate
   for unequal atomic radii.
7. Run synthetic sweeps to test whether `wet_coast` and `wet_sealed` are
   realizable under the current `R_residence` and `R_gate` definitions.

Exit criteria:

- geometry tests are active, not skipped;
- near-threshold behavior is documented and reproducible;
- unequal-radii `R_gate` status is documented;
- `wet_coast`/`wet_sealed` feasibility is known or explicitly bounded.

## 4. Validate Mesh and Face Identity

Goal: ensure every `R_gate` belongs to the intended Delaunay face and is not
computed redundantly.

A Delaunay triangulation contains tetrahedra with shared faces. If we compute
`R_gate` independently for the four faces of every tetrahedron, every internal
shared face is evaluated twice. `R_residence` is tetrahedron-specific and should
be computed once per tetrahedron, but `R_gate` is face-specific and should be
computed once per unique face.

Tasks:

1. Test the neighbor-to-face convention in DelaunayMesh.
2. Confirm that `face_r_gates_per_tet_face[i, face_idx]` matches
   `mesh.get_face_atoms(i, face_idx)`.
3. Confirm that shared faces use one consistent sorted atom triplet key.
4. Compute and cache `R_gate` once per unique face key, then map the cached
   value back to each tetrahedron-face slot that references that face.
5. Add tests for boundary faces and internal shared faces.
6. Store face identifiers explicitly where needed for diagnostics and dynamic
   tracking.

Exit criteria:

- external-link boundary faces and gate values are traceable to exact atom triplets;
- no feature classification depends on implicit face-order assumptions;
- each unique Delaunay face has one canonical `R_gate` record;
- internal shared faces do not trigger redundant `R_gate` calculations.

## 5. Implement Component Classification Cleanly

Goal: classify concavity components according to the canonical contract.

Tasks:

1. Build the transit backbone from resident-transit nodes and non-resident transit connectors connected by permeable faces.
2. Identify residence regions inside each transit component.
3. Identify permeable boundary or hull contacts from transit components to `OCEAN`.
4. Cluster those contacts into `external_links` by boundary-face connectivity.
5. Classify components as:
   - Void component: zero external links and at least one resident node;
   - Degenerate subprobe component: zero external links and no resident nodes; raw/filter label;
   - Pocket component: exactly one external link and at least one resident node;
   - Surface concavity component: exactly one external link and no resident nodes;
   - Multi-external-link component: two or more external links and at least one resident node; `Channel` remains a public shorthand only after morphology/path interpretation;
   - Nonresident passage component: two or more external links and no resident nodes; provisional raw label.
6. Keep local labels (`open`, `coast`, `sealed`) as metadata and do not let
   them alter backbone connectivity by themselves. Transit state is derived
   separately from residence and permeable-contact count.
7. Report atoms, tetrahedra, external-link faces, derived mouth descriptors,
   volumes, and gate summaries consistently.
8. Build the dry graph from finite non-resident tetrahedra connected through
   non-permeable faces.
9. Extract dry components, dry interfaces, terminal contacts, transit connectors, and face depth as raw records.
10. Keep component-motif and dry-motif analysis separate from primary
   classification. Start with topological depth, external-link paths, and dry
   interface signatures before enabling capacity-based chamber, throat, rim, or
   protrusion candidates.

Exit criteria:

- feature classification is deterministic;
- every void, provisional surface-concavity, pocket, and multi-external-link component has enough metadata
  for debugging and comparison.

## 6. Integrate with Topography

Goal: make DFND a normal TopoMT method, not a special dictionary-only path.

Tasks:

1. Fix get_topography(method=dfnd) so it passes the molecular system and method
   parameters correctly.
2. Decide whether dfnd returns a Topography object directly or whether a wrapper
   converts raw DFND records into Topography.
3. Populate Void, SurfaceConcavity, Pocket, Channel, and derived Mouth or
   ExternalLink descriptors with metrics and provenance.
4. Preserve raw DFND diagnostics for advanced users.
5. Add public examples once the API is stable.

Exit criteria:

- users can call topomt.get_topography(..., method=dfnd) successfully;
- output follows the same object model as other TopoMT methods.

## 7. Activate Tests

Goal: keep the active DFND coverage meaningful and expand it toward validation-quality tests.

Tasks:

1. Unskip and update tests/test_dfnd_pockets.py only after the API contract is
   correct.
2. Implement the toy systems listed in toy_systems_v1.md before real-system
   smoke tests.
3. Add small synthetic tests where expected transit components, residence regions,
   voids, surface concavities, pockets, multi-external-link components, external
   links, dry components, dry interfaces, terminal contacts, transit connectors,
   and face depth are known by construction.
4. Add small real-system smoke tests.
5. Add monotonic probe-radius tests for component accessibility.
6. Add tests for external-link clustering, dry-interface extraction, derived
   mouth descriptors, and channel classification.

Exit criteria:

- DFND tests run in normal CI or in a clearly marked optional test group;
- deferred/skipped tests remain explicit and do not represent the main DFND validation path.

## 8. Benchmark and Compare

Goal: evaluate DFND without forcing it to imitate another method.

Tasks:

1. Reuse the curated CASTp and CASTpFold and fpocket systems as comparison
   cases.
2. Compare counts, atom ownership, external-link counts, derived mouth
   descriptors, volumes, and qualitative site localization.
3. Track where DFND intentionally differs because of `R_residence` and `R_gate`
   semantics.
4. Follow validation_plan.md for small real-system validation and later
   quantitative benchmarks.
5. Build a small benchmark table for stable regression tracking.

Exit criteria:

- DFND has transparent comparison reports;
- differences are categorized as bugs, parameter effects, or intended method
  differences.

## 9. Dynamic Topology Phase

Goal: exploit the native DFND advantage for trajectories.

Tasks:

1. Add stable tetrahedron and face identifiers.
2. Run DFND frame by frame on a small trajectory.
3. Match features across consecutive frames.
4. Build DynamicFeature records.
5. Report lifetime, persistence, volume series, external-link series, derived mouth descriptors, and gate events.

Exit criteria:

- DFND can track at least one pocket through a short trajectory;
- topological events are reported explicitly.


Implementation note: `wet_open` must be exposed as `has_open_interior`, but it must not decide the primary component family.
