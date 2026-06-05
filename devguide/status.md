# TopoMT Status

## Summary

TopoMT is in an active implementation-hardening stage.

The project already contains:

- a coherent `Topography`/`Feature` object model;
- a public orchestrator, `get_topography()`;
- several conventional engine integrations and wrapper-backed routes;
- shared geometry, tessellation, and feature-characterization utilities under `topomt.tools`;
- an active `DelaunayMesh` substrate used by several native paths;
- a native DFND implementation that is now executable, tested at the substrate/API level, and documented through focused checkpoints.

The project is not yet a polished stable product. The main remaining gap is not lack of direction; it is validation depth, performance hardening, and deciding which experimental records become public feature APIs.

## Current Priority

The current priority is DFND hardening while preserving the conventional engine integrations as references and comparison targets.

DFND is the native TopoMT method direction. It should not be forced into strict CASTp, fpocket, AlphaSpace2, Pocketeer, or pycasta parity. Those methods remain valuable as external references, loader or wrapper integrations, and qualitative/quantitative comparison baselines.

The immediate DFND work is:

- keep the raw data model traceable and stable;
- keep `get_topography(method='dfnd')` integrated with `Topography`;
- validate `R_residence`, `R_gate`, transit domains, external links, dry components, dry interfaces, dry motifs, and solvent-volume estimates;
- inspect qualitative behavior on small real systems;
- add reporting/filter policy before judging cavity quality;
- profile and optimize query/build performance for larger systems.

## What Is Currently Solid

- `get_topography()` routes DFND and the conventional engines through the same top-level API.
- `DelaunayMesh` is the shared geometric substrate for Delaunay/tetrahedral work.
- DFND now has active geometry, graph-contract, input-policy, Topography, solvent-volume, and real-system stability tests.
- DFND supports the build-once/query-many workflow through `DelaunayFlowNetwork`.
- `R_residence` and `R_gate` are implemented as clearance primitives with active tests.
- DFND raw records separate topological/debug volumes from `volume_solvent_estimate`.
- DFND exposes stable compatibility features for `void_domain`, `pocket_domain`, and `channel_domain`, while provisional families remain available through raw records.
- Dry-side records now include dry components, dry edges, dry interfaces, dry depth, and first candidate dry motifs.
- Probe-radius sweeps on five small real systems obey the expected monotonicity invariants.

Key DFND checkpoints:

- [DFND/implementation_status.md](DFND/implementation_status.md)
- [DFND/checkpoint_dfnd_hardening_stint.md](DFND/checkpoint_dfnd_hardening_stint.md)
- [DFND/checkpoint_probe_radius_sweep.md](DFND/checkpoint_probe_radius_sweep.md)
- [DFND/checkpoint_quality_snapshot.md](DFND/checkpoint_quality_snapshot.md)
- [DFND/checkpoint_dry_interfaces_depth.md](DFND/checkpoint_dry_interfaces_depth.md)
- [DFND/checkpoint_dry_graph_basics.md](DFND/checkpoint_dry_graph_basics.md)
- [DFND/checkpoint_face_identity_external_links.md](DFND/checkpoint_face_identity_external_links.md)
- [DFND/checkpoint_numerical_threshold_policy.md](DFND/checkpoint_numerical_threshold_policy.md)
- [DFND/residence_radius_audit.md](DFND/residence_radius_audit.md)
- [DFND/gate_radius_audit.md](DFND/gate_radius_audit.md)

## Conventional Engine Status

The conventional engines remain important, but they are no longer the only active focus.

- `fpocket4` has strong native/source parity evidence on the audited set, with remaining source-level questions concentrated in raw geometry and build drift rather than final output for the audited local source build.
- `alphaspace2` has native parity coverage for the currently audited reference behavior and a first Vina-aware/contact layer.
- `pocketeer` has a native parity route and wrapper-backed Topography integration.
- `pycasta` has repository-parity coverage on the audited bounded battery, with explicit repository-versus-paper and selection-semantics questions documented.
- CASTp work is currently reference material and historical learning for DFND; strict CASTp3 parity is not the active target.

## What Is Still Weak

- Public user-facing documentation is still sparse.
- Packaging metadata and release-quality checks remain incomplete.
- Performance is acceptable for small systems but still needs profiling and optimization for larger repeated workflows.
- `volume_solvent_estimate` is deterministic and tested, but it is still an estimator, not a publication-grade CASTp-like analytic volume.
- Tiny void/domain reporting policy is not settled.
- Surface-concavity, nonresident-passage, and dry motif utility must be validated before becoming public feature families.
- Dynamic topology is documented but not implemented.
- Cross-engine benchmarks are not yet organized into a stable comparison battery.

## Practical Development Rule

Build new topography work on `get_topography()`, `Topography`, `DelaunayMesh`, `topomt.tools`, and DFND raw records. Keep experimental/provisional DFND records traceable, but do not promote them to stable public feature classes until validation supports that decision.
