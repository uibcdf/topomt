# DFND Project Checkpoint

Date: 2026-05-21

## 1. Strategic Decision

DFND is the native TopoMT method for molecular topography.

It should be developed as a transparent TopoMT-owned method, not as a clone of CASTp, fpocket, AlphaSpace2, Pocketeer, pycasta, or any other external engine. Those methods remain valuable as references, validation cases, comparison baselines, and integration targets.

## 2. Canonical Method Direction

The current canonical DFND direction is:

- standard Delaunay triangulation of atomic centers;
- atomic radii entering explicitly through tetrahedron residence clearance (`R_residence`);
- atomic radii entering explicitly through face-gate clearance (`R_gate`);
- separation of residence, transit, and contact;
- transit domains classified by external-link count and resident content;
- explicit raw records for tetrahedra, faces, transit/concavity domains, residence regions, external links, dry components, dry interfaces, and dry motifs;
- dry-side analysis as an internal candidate layer, not yet a public feature taxonomy;
- no weighted Delaunay baseline unless a future physical need is demonstrated.

## 3. Documentation State

The most relevant current documents are:

- `Overview.md`: conceptual overview;
- `feature_definitions.md`: canonical DFN, external-link, and domain-family semantics;
- `abstract_contract.md`: object layers, invariants, and edge cases;
- `residence_transit_contract.md`: separation of residence, transit, and contact;
- `metrics_contract.md`: volume, area, and metric naming policy;
- `input_policy.md`: atom, radius, and selection policy;
- `implementation_status.md`: current code status;
- `api_contract_v1.md`: public/raw API boundary;
- `checkpoint_dfnd_hardening_stint.md`: current hardening checkpoint;
- `checkpoint_probe_radius_sweep.md`: monotonicity sweep over small real systems;
- `checkpoint_quality_snapshot.md`: first qualitative domain snapshot.

## 4. Code State

The repository contains an active DFND implementation under `topomt/dfnd/`.

Implemented and tested at the engineering-contract level:

- `DelaunayFlowNetwork` construction from MolSysMT-backed input or arrays;
- defensive input checks before triangulation;
- `R_residence` and `R_gate` clearance primitives;
- deterministic local `volume_solvent_estimate`;
- face identity and unique gate mapping;
- build-once/query-many probe-radius workflow;
- vectorized per-query thresholding and transit-edge filtering;
- access-by-residence domain classification;
- external-link clustering;
- dry components, dry edges, dry interfaces, face depth, and first candidate dry motifs;
- `dfnd(...)` raw-first API;
- `get_topography(method='dfnd')` compatibility feature conversion;
- small real-system stability and monotonicity sweeps.

Still not production/publication-ready:

- biological cavity quality has not yet been benchmarked;
- tiny-domain and near-threshold reporting filters are not finalized;
- `volume_solvent_estimate` is not a high-precision analytic volume;
- provisional surface-concavity, nonresident-passage, and dry-motif records are not stable public feature classes;
- dynamic topology is documented but not implemented.

## 5. Immediate Priority

The next DFND phase should continue implementation hardening:

1. profile residual build/query costs;
2. inspect qualitative behavior on selected small real systems;
3. define reporting/filter policy for tiny voids and marginal domains;
4. validate dry motif utility before exposing public feature classes;
5. build a stable comparison battery against external engines without requiring strict semantic parity.
