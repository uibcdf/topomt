# DFND Checkpoint: Query Hardening, Metrics, and Dry Motifs

Date: 2026-05-21

## Scope

This checkpoint records the implementation-hardening stint after the first
probe-radius sweep. The goal was not to change DFND semantics, but to make the
current implementation faster to query, easier to inspect, and better covered by
engineering tests.

## 1. Query-Time Optimization

`DelaunayFlowNetwork` now follows the intended build-once/query-many model more
closely:

- gate-intrusion suspicion is computed once during geometry initialization;
- residence thresholding is vectorized per query;
- face permeability thresholding is vectorized per query;
- internal transit-edge filtering uses precomputed source/target face indices.

This preserves the current marginal policy: equality within `epsilon` remains a
conservative closed/non-resident state with a `marginal` flag.

The practical effect is that repeated probe-radius sweeps no longer recompute
fixed gate-intrusion geometry in every query. Build time can increase, but query
time drops substantially for repeated-radius workflows.

## 2. Probe-Radius Monotonicity Tests

The real-system multi-radius test now reuses one `DelaunayFlowNetwork` per
system and checks monotonicity on `1crn` and `1rop`:

- resident tetrahedra do not increase when the probe radius increases;
- permeable face slots do not increase when the probe radius increases;
- aggregate resident `volume_solvent_estimate` does not increase when the probe
  radius increases.

The broader report remains in `checkpoint_probe_radius_sweep.md`.

## 3. Qualitative Domain Snapshot

A new engineering snapshot was generated at the default `1.4 Å` probe radius:

- `devtools/dfnd/run_quality_snapshot.py` builds one network per system;
- `devguide/DFND/checkpoint_quality_snapshot.md` reports domain-family counts
  and the largest resident domains by solvent-volume estimate.

The current observation is that each small system has a dominant pocket-like
resident domain plus varying numbers of small void domains. This should drive
future reporting/filter policy, not immediate changes to the core graph
semantics.

## 4. Topography Integration

`get_topography(method='dfnd')` still converts only stable compatibility
families to public features:

- `void_domain` -> `Void`;
- `pocket_domain` -> `Pocket`;
- `multi_external_link_domain` -> `Channel` shorthand.

The returned `Topography` object now also exposes convenience references to raw
and provisional DFND records:

- `dfnd_concavity_domains`;
- `dfnd_external_links`;
- `dfnd_dry_components`;
- `dfnd_dry_interfaces`;
- `dfnd_dry_motifs`;
- `dfnd_surface_concavities`;
- `dfnd_nonresident_passages`;
- `dfnd_degenerate_subprobe_domains`.

These are references to the raw/result records, not independent feature APIs.

## 5. Solvent-Volume Estimate Tests

`volume_solvent_estimate` remains a deterministic local estimator, not an exact
CASTp-like molecular volume. It is now covered by unit tests for:

- unit tetrahedron volume;
- full empty volume when local radii are zero;
- zero empty volume when local spheres cover the tetrahedron;
- bounded intermediate estimates;
- batch/scalar consistency.

## 6. First Dry Motif Layer

A first internal dry-motif layer is now derived from dry components,
dry interfaces, and dry depth. The current motif records are candidates only:

- `dry_boundary_shell`;
- `dry_ocean_exposed_shell`;
- `dry_resident_lining`;
- `dry_core_candidate`.

They are reported in `raw['dry_motifs']` and `dry['motifs']`, and exposed on
`Topography` as `dfnd_dry_motifs`. They are not public `TopographyFeature`
objects yet.

## Remaining Work

The next practical work items are:

- profile the residual query cost inside raw-record/domain construction;
- decide reporting filters for tiny void domains;
- inspect the dominant pocket domains geometrically/visually;
- study convergence/resolution policy for `volume_solvent_estimate`;
- validate whether dry motif candidates are useful on real structures before
  promoting them to a public feature taxonomy.
