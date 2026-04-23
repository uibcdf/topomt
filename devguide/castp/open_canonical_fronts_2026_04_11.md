# CASTp Open Canonical Fronts 2026-04-11

## Purpose

This note consolidates the fronts that are still open after:

- the mouth canonicalization passes,
- the vertex-materialization pass,
- the `1ubq` spectrum / rank audit,
- and the later `1ubq` comparison against canonical MKALF pocket printouts.

The goal is to keep a short and current list of what is still:

- non-canonical,
- not yet demonstrated to be canonical,
- or not yet separated cleanly into
  `TopoMT defect` vs `MKALF 4.1 vs CASTp 3.0 divergence`.

Related audit:

- [canonical_gap_hypotheses_2026_04_16.md](canonical_gap_hypotheses_2026_04_16.md)
- [canonical_algorithm_audit_2026_04_17.md](canonical_algorithm_audit_2026_04_17.md)
- [rank_mu_audit_2026_04_17.md](rank_mu_audit_2026_04_17.md)
- [reporting_audit_2026_04_17.md](reporting_audit_2026_04_17.md)
- [checkpoint_2026_04_17_mouth_perimeter_reporting.md](checkpoint_2026_04_17_mouth_perimeter_reporting.md)
- [checkpoint_2026_04_17_feature_area_reporting.md](checkpoint_2026_04_17_feature_area_reporting.md)
- [checkpoint_2026_04_17_rank_mu_pocket_block.md](checkpoint_2026_04_17_rank_mu_pocket_block.md)
- [checkpoint_2026_04_17_canonical_reporting_partitions.md](checkpoint_2026_04_17_canonical_reporting_partitions.md)
- [checkpoint_2026_04_17_pocket_sequence_state_machine.md](checkpoint_2026_04_17_pocket_sequence_state_machine.md)
- [checkpoint_2026_04_17_exact_threshold_ranks.md](checkpoint_2026_04_17_exact_threshold_ranks.md)
- [checkpoint_2026_04_16_rank_sublists.md](checkpoint_2026_04_16_rank_sublists.md)
- [checkpoint_2026_04_16_exact_hidden_predicates.md](checkpoint_2026_04_16_exact_hidden_predicates.md)
- [checkpoint_2026_04_16_master_list_layer.md](checkpoint_2026_04_16_master_list_layer.md)
- [checkpoint_2026_04_16_outward_mouth_orientation.md](checkpoint_2026_04_16_outward_mouth_orientation.md)
- [checkpoint_2026_04_17_enext_edge_facet_order.md](checkpoint_2026_04_17_enext_edge_facet_order.md)
- [checkpoint_2026_04_17_explicit_fnext_step.md](checkpoint_2026_04_17_explicit_fnext_step.md)
- [checkpoint_2026_04_17_mouth_face_records.md](checkpoint_2026_04_17_mouth_face_records.md)
- [checkpoint_2026_04_17_record_identity_for_mouths.md](checkpoint_2026_04_17_record_identity_for_mouths.md)
- [checkpoint_2026_04_17_triangle_indices.md](checkpoint_2026_04_17_triangle_indices.md)
- [checkpoint_2026_04_17_fnext_returns_triangle_index.md](checkpoint_2026_04_17_fnext_returns_triangle_index.md)
- [checkpoint_2026_04_17_clusters_keep_triangle_identity.md](checkpoint_2026_04_17_clusters_keep_triangle_identity.md)
- [checkpoint_2026_04_17_fnext_step_returns_triangle_index_directly.md](checkpoint_2026_04_17_fnext_step_returns_triangle_index_directly.md)
- [checkpoint_2026_04_17_edge_facet_records.md](checkpoint_2026_04_17_edge_facet_records.md)
- [checkpoint_2026_04_17_walk_uses_edge_facet_records.md](checkpoint_2026_04_17_walk_uses_edge_facet_records.md)
- [checkpoint_2026_04_17_initial_mouth_edge_facets.md](checkpoint_2026_04_17_initial_mouth_edge_facets.md)
- [checkpoint_2026_04_17_local_face_identity_preferred.md](checkpoint_2026_04_17_local_face_identity_preferred.md)
- [checkpoint_2026_04_17_enext_on_edge_facets.md](checkpoint_2026_04_17_enext_on_edge_facets.md)

## What is now considered reasonably closed

The following should no longer be treated as leading open fronts:

- `mu1` / `mu2` values being inserted into the `spectrum`
- solvent-radius inflation
- `rho0` / weighted vertex size
- the existence of `branched_channel` as a native feature type
- the old direct mouth union by shared shape edge
- implicit mouth-face orientation before the `Fnext` walk
- the `1ubq` fine pocket residual as a primary native bug

The `1ubq` local pocket region is now better interpreted as:

- native output close to canonical MKALF
- but different from CASTp 3.0

So `1ubq` is no longer the best driver for "what TopoMT still does
non-canonically".

## Open fronts that still matter

### 1. Exact rank semantics are still not fully demonstrated

The native path now has exact-ratio infrastructure, and that work improved
parity substantially.

However, it is still not demonstrated that the current rank machinery is fully
equivalent to the historical weighted-event ordering used by MKALF.

Open questions:

- whether the current exact event ordering reproduces all rank separations that
  matter historically
- whether any remaining rank compressions are still present on medium cases

Assessment:

- still open
- still canonical
- no longer speculative

The exact-threshold path is now substantially more consolidated, and the
rank/mu/pocket operational block is no longer a loose collection of
micro-fixes. What remains open here is proof of equivalence, not the old
float-fallback semantics.

### 2. The native `Fnext` walk is still not a literal port of the historical edge-facet structure

The walk is much closer to MKALF than before:

- oriented tetrahedra are preserved
- mouth faces carry simplex/face ownership
- open-edge logic uses `mu1` semantics

But the current Python implementation still does not expose the same exact
edge-facet combinatorics as the historical C data structure.

Assessment:

- still open
- important for fidelity claims
- but no longer the dominant failure pattern on the short battery

### 3. Mouth-seed selection is improved, not yet formally proven identical

Current results strongly suggest that mouth-face seeding is now close to
historical `alf_scan_pocket_f1()` behavior.

But we still do not have a direct audit proving equality of seed sets on a
representative red/green case set.

Assessment:

- open
- secondary to the previous two items
- worth auditing if a remaining red case points back to mouth topology

### 4. Triangulation still differs from DELCX, even when the local residual does not depend on it

For `1ubq`:

- all MKALF tetrahedra are present in the scipy-based triangulation
- plus 29 extra scipy tetrahedra

So the triangulation is not identical, even though the local `1ubq` residual
did not reduce to a "missing tetrahedron" problem.

Assessment:

- still open
- not the best explanation of the current `1ubq` residual
- still relevant for other cases and for a strict fidelity claim

### 5. Reporting is much better, but still not fully canonical

The native output now exposes:

- `iF/rF/iE/rE/iV/rV`
- feature `area`
- mouth area
- mouth perimeter

This closes a substantial part of the reporting gap identified earlier.

Still open:

- whether all canonical CAST-style derived reporting layers are now exposed
- whether any remaining `_native_impl.py` compression still hides meaningful
  MKALF structure

Assessment:

- improved substantially
- no longer one of the largest conceptual gaps
- still not fully closed

### 6. The boundary between "TopoMT bug" and "CASTp 3.0 evolution beyond MKALF" remains open on several server residuals

`1ubq` is now one confirmed example where the native output aligns more closely
with canonical MKALF than with CASTp 3.0 in a local pocket region.

That means the remaining red cases cannot all be treated as native defects by
default.

The open task is now:

- classify each remaining red case as either
  - `still non-canonical in TopoMT`, or
  - `already canonical enough for MKALF, but different from CASTp 3.0`

Assessment:

- still open
- strategically important
- should guide case selection for the next iteration

## What should currently worry us less

These are no longer high-priority canonical concerns:

- a global failure of weighted geometry
- a global failure of `void` logic
- a global failure of mouth taxonomy
- `1ubq` as the main red-case driver

The earlier large taxonomic mouth bias has been reduced sharply enough that the
next phase should focus on smaller, more discriminating cases.

## Recommended next step

The next implementation / audit round should focus on 3-5 remaining red cases
that still look like plausible native non-canonical behavior after excluding
`1ubq` as a primary driver.

The next case set should be chosen to answer:

1. which residuals still look like genuine TopoMT canonical gaps
2. which residuals already look like `MKALF 4.1 vs CASTp 3.0`
3. whether any surviving gap points back to
   - exact rank semantics,
   - literal `Fnext` combinatorics,
   - or triangulation / SoS

## Current recommended diagnostic set

Based on the current native-vs-server parity after the latest canonicalization
rounds, and after the first MKALF-side classification pass, the best next set
is now:

- `4CHA`
- `3PTB`
- `1TCD`
- `1AKE`

Reserve cases:

- `2CBA`
- `3KS3`
- `1HIV`

Why these and not `1UBQ`:

- `1UBQ` is no longer a good primary driver for native defects, because its
  main fine residual now aligns more closely with canonical MKALF than with
  CASTp 3.0.

Why these and not `1TCD` / `3PTB` first:

- `1TCD` and `3PTB` still mix open-feature residuals with non-zero `void`
  residuals.
- the recommended set above keeps `void` parity either exact or very close,
  making the remaining gaps easier to interpret as open-feature / canonical
  issues.

Observed current signal:

- `4CHA`: `void 27/28`, `channel 1/1`, `branched_channel 0/2`, `pocket 19/25`
- `3PTB`: `void 14/15`, `channel 1/1`, `pocket 11/12`
- `1TCD`: `void 35/36`, `channel 6/6`, `branched_channel 2/2`, `pocket 32/34`
- `1AKE`: `void 19/19`, `channel 5/5`, `branched_channel 1/2`, `pocket 19/21`
- `2CBA`: `void 11/11`, `channel 2/3`, `pocket 15/17`
- `3KS3`: `void 10/10`, `channel 3/4`, `pocket 12/14`
- `1HIV`: `void 3/3`, `channel 1/1`, `pocket 11/13`

## First MKALF-side classification update

The first explicit MKALF-side classification pass already changes the priority
of some medium red cases.

### `2CBA`

At the canonical MKALF zero crossing:

- `rank1 = 27425`
- `rank2 = 30995`

the native output aligns **better** with MKALF than the CASTp 3.0 server does:

- native pockets exact in MKALF: `14/18`
- server pockets exact in MKALF: `11/17`
- native channels exact in MKALF: `2/2`
- server channels exact in MKALF: `2/3`

So `2CBA` is no longer a good primary driver for native corrections.

### `1AKE`

At the canonical MKALF zero crossing:

- `rank1 = 42087`
- `rank2 = 49273`

the picture is more mixed, but still does not point cleanly to a native-only
defect:

- native pockets exact in MKALF: `15/20`
- server pockets exact in MKALF: `14/21`
- native channels exact in MKALF: `3/5`
- server channels exact in MKALF: `3/5`
- both server and native branched channels: `0/2` exact in MKALF

So `1AKE` remains useful, but now more as a mixed control case than as the
cleanest bug-driver.

### Consequence

After this first MKALF-side pass, `4CHA`, `3PTB`, and `1TCD` become more
attractive next targets than `2CBA`.

### `4CHA`

At the canonical MKALF zero crossing:

- `rank1 = 44635`
- `rank2 = 51099`

neither the server nor the native output has any exact pocket/channel match
against the canonical MKALF pocket sets.

This makes `4CHA` less clean than expected as a direct implementation target.

The first closeness pass is mixed:

- server pockets are slightly closer to MKALF on average
- native branched channels are slightly closer to MKALF on average

So `4CHA` should currently be treated as:

- informative,
- but not yet a clean driver for a specific correction.

### Practical reprioritization

After the first MKALF-side classification of `2CBA`, `1AKE`, and `4CHA`, the
next best cases to prioritize are now:

- `3PTB`
- `1TCD`

with `1AKE` and `4CHA` kept as mixed-control cases.

### `3PTB`

At the canonical MKALF zero crossing:

- `rank1 = 21311`
- `rank2 = 24052`

the signal is mixed but still useful:

- server pockets exact in MKALF: `7/12`
- native pockets exact in MKALF: `6/11`
- server channels exact in MKALF: `1/1`
- native channels exact in MKALF: `1/1`
- server voids exact in MKALF: `14/14`
- native voids exact in MKALF: `15/15`

Interpretation:

- `3PTB` is still a reasonable diagnostic case;
- it does not collapse cleanly into either
  `native defect`
  or
  `MKALF vs CASTp 3.0`.

### `1TCD`

At the canonical MKALF zero crossing:

- `rank1 = 51915`
- `rank2 = 58406`

the native output aligns at least as well as the server with canonical MKALF,
and slightly better on pockets / voids:

- server pockets exact in MKALF: `19/34`
- native pockets exact in MKALF: `20/34`
- server channels exact in MKALF: `3/6`
- native channels exact in MKALF: `3/6`
- server branched channels exact in MKALF: `1/2`
- native branched channels exact in MKALF: `1/2`
- server voids exact in MKALF: `35/36`
- native voids exact in MKALF: `36/36`

So `1TCD` should no longer be treated as a strong primary driver for native
corrections. It now looks closer to:

- another case where the native implementation already tracks MKALF at least as
  well as the server does.

## Recent Structural Closures

The following fronts should no longer be treated as open at the same level:

- tetrahedron admission through a precomputed empty mask
- non-exact `hidden1` / `hidden2`
- absence of a Python-level master-list view
- pocket construction with `rank2 = max_rank` instead of the canonical
  beta / probe threshold
- pocket depth built with wrapping semantics instead of canonical
  `compute_tetra_depth()` semantics
- duplicated local `rho/mu1/mu2` membership logic instead of canonical
  rank-table helpers
- non-canonical ordering in hull-edge `mu2` zeroing during `edge_mus`
- mouth-seed selection using extra depth/beta-side filters instead of a literal
  `alf_scan_pocket_f1()` rule
- `Fnext` walk missing the historical stop condition for tetrahedra outside the
  `rank2` shape
- manual reconstruction of the next `Fnext` state instead of using a
  neighbor-owned edge-facet record

See also:

- `checkpoint_2026_04_16_rank_sublists.md`
- `checkpoint_2026_04_16_exact_hidden_predicates.md`
- `checkpoint_2026_04_16_master_list_layer.md`
- `checkpoint_2026_04_16_probe_rank_beta.md`
- `checkpoint_2026_04_16_pocket_depth_semantics.md`
- `checkpoint_2026_04_16_rank_table_semantics.md`
- `checkpoint_2026_04_16_mu_propagation.md`
- `checkpoint_2026_04_16_f1_seed_selection.md`
- `checkpoint_2026_04_16_rank2_stop_in_fnext.md`
- `checkpoint_2026_04_17_triangle_indices.md`
- `checkpoint_2026_04_17_fnext_returns_triangle_index.md`
- `checkpoint_2026_04_17_clusters_keep_triangle_identity.md`
- `checkpoint_2026_04_17_fnext_step_returns_triangle_index_directly.md`
- `checkpoint_2026_04_17_edge_facet_records.md`
- `checkpoint_2026_04_17_walk_uses_edge_facet_records.md`
- `checkpoint_2026_04_17_initial_mouth_edge_facets.md`
- `checkpoint_2026_04_17_local_face_identity_preferred.md`
- `checkpoint_2026_04_17_enext_on_edge_facets.md`
- `checkpoint_2026_04_17_fnext_uses_neighbor_owned_edge_facet.md`
- `checkpoint_2026_04_17_walk_starts_from_edge_facet.md`
- `checkpoint_2026_04_17_fnext_returns_edge_facet_only.md`
- `checkpoint_2026_04_17_fnext_input_records_get_triangle_identity.md`
- `checkpoint_2026_04_17_fnext_input_uses_any_available_triangle_identity.md`
