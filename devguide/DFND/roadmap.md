# DFND Roadmap

Forward-looking roadmap recorded on 2026-05-22. It captures where DFND stands now
and the prioritized next directions. It complements
[`Implementation_Route.md`](Implementation_Route.md) (the original "build and
harden the primitives" route, now largely accomplished) and
[`strategic_assessment.md`](strategic_assessment.md) (why these priorities).

## Where We Are (done)

- **Geometric primitives**: `R_residence` (tetrahedron) and `R_gate` (face)
  defined as *clipped largest-empty-ball/circle* active-set solvers, plus a
  solvent-volume estimate. All **validated bit-for-bit** against scalar oracles
  and Monte-Carlo references. See
  [`residence_radius_audit.md`](residence_radius_audit.md),
  [`gate_radius_audit.md`](gate_radius_audit.md).
- **Classifier**: residence × access two-axis families (void / pocket /
  surface_concavity / channel(channel) / nonresident_passage /
  degenerate_subprobe), unit-tested.
- **Pipeline**: `DelaunayFlowNetwork` builds the mesh, residence/gate/volume
  (all vectorized), face dedup, the wet/dry edge graph, and `get_topography`
  emits raw records + families. Warm build ≈ 4.3 s for `3ptb` (1629 atoms).
- **Tests**: green; 2 documented skips (`nonresident_passage`,
  `degenerate_subprobe` — covered by the classifier unit test).
- **Synthetic battery (Phase A, done)**: 65 catalogued dummy-atom PDBs with
  known-by-construction topography — success, interface, and pathological tiers —
  built by `devtools/dfnd/build_synthetic_catalog.py`, asserted in
  `tests/test_dfnd_synthetic_benchmarks.py` / `_interface_features.py` /
  `_pathological.py`. Design: [`synthetic_benchmarks.md`](synthetic_benchmarks.md);
  per-case review playbook: [`synthetic_review_guide.md`](synthetic_review_guide.md).
- **Failure map**: ~25 pathological systems pin current failure modes as
  regression markers, grouped into four diseases (segmentation fragmentation,
  sampling/packing sensitivity, threshold instability, quantification/radius/
  bodies). See [`pathological_systems.md`](pathological_systems.md).
- **Interface prototype**: `topomt/dfnd/interfaces.py` derives interface features
  by the multi-body-lining rule (dry banks + wet gap). See
  [`interfaces.md`](interfaces.md).

The leverage has shifted from correctness/speed to **demonstrating usefulness**
and **fixing the failure modes the synthetic battery exposed** before real
systems.

## Priority 1 — Validation (synthetic first, then real)

**Why**: the project's real risk is validation, not primitive correctness
([`strategic_assessment.md`](strategic_assessment.md)).
[`validation_plan.md`](validation_plan.md) is written but not executed.

### Phase A — Synthetic benchmark with known ground truth (DONE)

A parametric generator (`topomt/dfnd/synthetic.py`) and a catalog builder
(`devtools/dfnd/build_synthetic_catalog.py`) produce 65 dummy-atom PDBs in
`topomt/data/synthetic/` with topography known by construction, asserted by the
three synthetic test files. Design: [`synthetic_benchmarks.md`](synthetic_benchmarks.md).

Outcome: DFND recovers the known family and volume on the clean shapes, and the
**failure modes are documented and pinned** rather than hidden — see
[`pathological_systems.md`](pathological_systems.md). The exit criterion is met:
known answer recovered, or a documented/understood failure mode. The remaining
Phase-A-adjacent work is the next priority — *fixing* those failure modes (above
all the segmentation disease) — and an optional controlled CASTp/fpocket run on
the same PDBs.

### Phase B — First real-system validation

First tasks:
- Run DFND on `3ptb` (known benzamidine site) and a few small structures.
- Check whether a `pocket`/`channel` component lands on the known site: distance
  from component center to ligand center (DCC), overlap with ligand-contact
  residues, top-N success.
- Use `volume_solvent_estimate`, not `volume_topological`, for any volume claim.

Exit criteria: a small reproducible report showing DFND recovers known sites (or
a documented, understood failure mode). Unlocks Priorities 2 and 3.

## Priority 2 — Clean DFND → `Topography` integration

**Why**: [`implementation_status.md`](implementation_status.md) notes
`get_topography` returns raw dicts, not a populated `Topography`, and the
`dfnd(...)` ↔ `Topography` wiring is incomplete. The
[`Pertinence_Analysis.md`](Pertinence_Analysis.md) vision is
`afn.get_topography(probe_radius=...)` → a `Topography` populated with
`Pocket`/`Channel`/`Void` features.

First tasks:
- Map raw concavity-component records to the `topomt.features` classes.
- Propagate metrics (residence margins, volume estimate, external links/mouths,
  atoms/residues) into the feature objects.
- Resolve the `get_topography(method=dfnd)` call-shape mismatch.

Exit criteria: DFND output consumable as a `Topography` object by the rest of
TopoMT and by users, with traceable provenance.

## Priority 3 — A differentiating-capability prototype

**Why**: the strongest dimension for DFND is functional originality, not static
pocket volume (where CASTp is already validated). Aim the first publication-facing
result here.

Candidates (pick one to prototype):
- **MD trajectory tracking**: per-frame DFND + atom/tetrahedron/face identity to
  follow a cryptic or gated site across frames. See
  [`dynamic_topology.md`](dynamic_topology.md) (documented, not implemented).
- **Dry side**: `DryComponent` / `DryInterface` / `dry_depth` end-to-end — the
  wet/dry symmetry few tools offer. See
  [`dry_network_and_convexity.md`](dry_network_and_convexity.md).

Exit criteria: one concrete case where DFND captures something static
volume-detectors miss (e.g. a non-resident gating throat across an MD ensemble).

## Priority 4 — Hardening and coverage (lower leverage)

- Validate the provisional `surface_concavity` family on real systems
  (real shallow dents vs surface noise/slivers).
- Deterministically construct the two skipped end-to-end toys
  (`nonresident_passage`, `degenerate_subprobe`) if full end-to-end coverage is
  wanted.
- Profile the `get_topography` per-component loops at scale.

## Deferred / Out of Scope for Now (documented elsewhere)

- **Large-system (capsid) scaling**: chunked batching is the required change;
  edge deduplication is *not* worth it (scale-invariant ~1%). See
  [`scaling_large_systems.md`](scaling_large_systems.md).
- **GPU/CUDA**: feasible and well-matched to the per-tetra/per-face kernels; a
  numba.cuda kernel would also remove the capsid memory wall. See
  [`gpu_cuda_feasibility.md`](gpu_cuda_feasibility.md).

## Suggested Order

Priority 1 first (cheap, decisive). Its result decides whether to invest in
Priority 2 (make it usable) or jump to Priority 3 (where DFND is distinctive).
Priority 4 and the deferred items follow as needed. Performance work (scaling,
GPU) is only triggered by a concrete large-system or throughput need.
