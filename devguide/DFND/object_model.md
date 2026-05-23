# DFND Object Model and Terminology (authoritative)

Recorded on 2026-05-23. This is the **authoritative** reference for how DFND
output is organized and for the words we use. Where any other DFND document or
code field disagrees with this one, this document is the target and the other is
either legacy (pending migration) or wrong. Its purpose is to remove, once and
for all, the confusion between *component*, *domain*, *motif*, and *feature*.

## 1. Two levels, one dividing principle

There are exactly two levels, and they must not leak into each other:

- **`Topography`** — the **public, method-agnostic** level. It holds
  **features** (Pocket, Void, Channel, Mouth, …) as individual objects related by
  parenthood and organized by shape/dimensionality. Every engine (CASTp, fpocket,
  AlphaSpace2, pycasta, DFND) fills this same level. A user of `Topography` must
  be able to work without knowing anything about DFND.
- **`topography.dfnd`** — the **DFND-specific substrate**. It holds the Delaunay
  mesh, the flow network, and its decomposition into components/domains/motifs.

> **Dividing principle.** Ask: *"would a user who knows nothing about DFND need
> this — no graphs, no wet/dry, no connected components, no OCEAN?"* If **no**, it
> belongs under `topography.dfnd`, never at the `Topography` top level.

This is why there are no `dfnd_*` attributes at the `Topography` top level: all
DFND material lives under the single `topography.dfnd` object.

## 2. The terminology ladder: component → domain → feature

A single connected piece of empty space is described at three rungs. Use the
right word for the right rung:

```
component            →   domain                →   feature
(the graph)              (the atoms)               (the public object)

a connected component    that component realized   a Topography object
of the DFN graph:        in the molecular system:  promoted from a domain:
a set of tetrahedron      its lining atoms,         + units, residues,
NODES (+ their faces      volume, center, the       morphology, dynamics,
and edges)                region of space it        annotations
                          occupies
"the decomposition"      "the atoms of the         method-agnostic
produces components       component"
```

- **component** — the pure **graph** object. The output of the *decomposition*
  (the **D** in DFND). A set of tetrahedron nodes plus the faces/edges among them.
  Probe-dependent.
- **domain** — that component **realized in the system**: its atoms (lining),
  volume, center, spatial footprint. A **facet of the component**
  (`component.domain`), not a separate registry. *"The domain of the component."*
- **feature** — the **public** `Topography` object promoted from a domain.

### Two reserved-word rules (the heart of the convention)

1. **The word `feature` is NEVER used inside `dfnd`.** Inside dfnd there are
   components, domains, and motifs — never features.
2. **The word `motif` is NEVER used at the `Topography` level.** A motif is a
   dfnd object; when it surfaces publicly it has become a feature.

## 3. motif — sub-structure of a domain

A **motif** is a named sub-structure *of a domain* (it lives in the domain, the
atoms rung): a **throat/bottleneck**, a **chamber**, a **depth-region**, a
**mouth**. Motifs are how a single domain has internal parts.

The mouth illustrates the full ladder cleanly:

```
external_link          →   external_mouth        →   Mouth
(graph: component↔OCEAN)    (motif: the mouth's       (feature, 1D, child of the
                            atoms/geometry)            promoted concavity feature)
```

## 4. The `topography.dfnd` object tree

```
topography.dfnd
├── raw                 # full raw records (provenance / debug)
├── mesh                # probe-INDEPENDENT geometry — built once
│   ├── atoms           # vertices: coords, radii, local→global index map
│   ├── tetrahedra      # geometry + R_residence + per-tet solvent volume
│   └── faces           # geometry (atom triple, area, face id) + R_gate
└── dfn                 # probe-DEPENDENT network for one probe
    ├── parameters      # probe_radius, transit_policy, gate_intrusion_policy, epsilon, radii_model
    ├── graph           # nodes (wet/dry state, transit_role, flags; ref mesh tetra),
    │                   #   edges (permeable faces, transit edges), OCEAN
    └── components       # the decomposition registry (see §5)
```

**Lifecycle = the reason mesh and dfn are siblings.** `mesh` is probe-independent
(the clearances `R_residence`, `R_gate` are geometric, computed once). `dfn`
(graph + components) is recomputed when the probe changes. Splitting them this way
makes the invalidation boundary explicit.

## 5. `dfn.components` — a registry that mirrors `Topography`

The components registry is built with the **same pattern** as `Topography`, so
there is one mental model for both levels.

| `Topography` (public) | `dfn.components` (substrate) |
|---|---|
| `Mapping[FeatureID, BaseFeature]` | `Mapping[ComponentID, Component]` |
| `_features` | `_components` |
| `_by_type`, `_by_shape`, `_by_dimensionality` | `_by_family`, `_by_side` |
| `_children_of` / `_parents_of` (`connect_features`) | nesting via `connect_components`; plus boundary relations `external_links`, `interfaces` |
| `get_features(by=, value=, grouped_by=)` | `get_components(by=, value=, grouped_by=)` |
| `get_feature_by_id`, `children_of`, `parents_of` | `get_component_by_id`, `neighbors_of`, `external_links_of` |
| `info()`, `to_records()`, `__repr__` | same |

- `_by_side`: `wet` / `dry`.
- `_by_family`: `void`, `pocket`, `channel`, `surface_concavity`,
  `nonresident_passage`, `degenerate_subprobe` (wet) and `dry_bank` (dry).
- **wet and dry are unified under `component`.** `side` is **derived from
  `family`** via a `_SIDE_BY_FAMILY` registry, mirroring how `BaseFeature` derives
  `shape_type`/`dimensionality` from `feature_type`.

## 6. The `Component` object — mirrors `BaseFeature` + `Pocket`/`Void`/`Channel`

**`Component`** (base, ≡ `BaseFeature`):
- `component_id`, `family`, `side` (derived), `flags`, `_dfn` back-ref;
- **component facet (graph)**: `node_indices` (tetrahedra), `boundary_face_ids`;
- **domain facet (atoms)**: `atom_indices`, `volume`, `center`;
- **motifs**: the domain's sub-structures.

**`WetComponent`** (≡ concavity classes): `resident_node_indices`,
`transit_connector_node_indices`, `external_link_ids`, `n_mouths`, `mouth_area`,
`has_residence`, `has_open_interior`, `volume_topological_resident`,
`volume_solvent_estimate`.

**`DryComponent`**: `interface_ids`, `neighbor_component_ids`,
`dry_depth_{min,max,mean}` (+ per-node), `motif_ids`.

Two subclasses (not one per family) because the wet families differ only by the
`family` label, not by structure. Motif slots exist on both sides; today only dry
motifs are built (wet-domain motifs are designed in
[`domain_motifs.md`](domain_motifs.md) but not yet implemented).

## 7. Promotion: dfnd → Topography (not 1:1)

A single component yields a **feature subgraph**, not one feature:

```
WetComponent(family='pocket', id='WET-3')   ──▶  Pocket   (feature.source_id = 'WET-3')
   ├── external_mouth motif                 ──▶  Mouth    (child via connect_features)
   ├── throat motif                         ──▶  Neck     (child)
   └── chamber motif                        ──▶  sub-Pocket (nested child)
```

- The **domain** promotes to the concavity **feature** (`Void`/`Pocket`/`Channel`).
- The domain's **motifs** promote to **child features** (`Mouth`, throat→`Neck`,
  chamber→sub-`Pocket`), wired with `connect_features`. The feature parenthood
  *is* the component's motif structure.
- Each feature carries `source_id = component_id` (and, for child features, the
  motif id) as provenance → traceable feature → domain → component → tetrahedra →
  atoms.
- Provisional families (`surface_concavity`, `nonresident_passage`,
  `degenerate_subprobe`) and the dry interfaces are **not** promoted yet (no
  feature class for them); they remain available under `topography.dfnd`.

## 8. Relation to existing vocabulary (migration)

This model **supersedes** the older, inconsistent wording in which the wet
graph-component was a *"transit/concavity domain"* and the dry one a *"dry
component"*. Going forward:

- the **graph object** (either side) is a **`component`**;
- its **atoms** are its **`domain`**;
- the **public** object is a **`feature`**;
- sub-structures of a domain are **`motifs`**.

The rename is **complete — zero legacy** (done while the project is early, before
the contract spread further):

| legacy | new |
|---|---|
| `dfnd_*` attributes on `Topography` | single `topography.dfnd` |
| wet "transit/concavity domain" | `component` (`WetComponent`) |
| "dry component" | `component` (`DryComponent`, family `dry_bank`) |
| atoms of a domain | `component` domain facet (`atom_indices`, …) |
| raw field `concavity_domains` / `transit_domains` | `wet_components` (single key) |
| record field `domain_family` | `family` |
| family strings `void_domain` / `pocket_domain` / `multi_external_link_domain` / … | `void` / `pocket` / `multi_external_link` / … (no `_domain` suffix) |
| record field `domain_id` (component's own) | `id` |
| `domain_id` referencing the parent (external links, residence regions) | `component_id` |
| method `_classify_domain` | `_classify_component` |
| view key `degenerate_subprobe_domains` | `degenerate_subprobes` |

The raw engine dictionary (`topography.dfnd.raw`, from
`DelaunayFlowNetwork.get_topography`) now uses the ladder vocabulary too. Internal
loop variables (`domain_index`, `nodes_by_label`, …) are implementation detail,
not contract, and are left as-is.
See [`synthetic_review_guide.md`](synthetic_review_guide.md) for the review flow
and [`Glossary.md`](Glossary.md) for per-term definitions (being aligned to this
ladder).

## 9. Implementation status (phased)

- **Phase 1 — DONE.** All DFND substrate is attached to a single
  `topography.dfnd` (`DFNDData` in `topomt/dfnd/data.py`) with the
  `raw / mesh / dfn{ parameters, graph, components }` tree above; the nine
  legacy `dfnd_*` top-level attributes are removed; consumers (`api.py`,
  `molsysviewer_topomt/render.py`, `devtools/dfnd/run_stability_report.py`) and
  tests are migrated. **The mesh/dfn separation is real**: `mesh.tetrahedra` /
  `mesh.faces` expose geometry only (`R_residence`, `R_gate`, volumes, atoms),
  while `dfn.graph.nodes` / `dfn.graph.faces` expose the probe-dependent state
  only (residence/transit/permeability), with identity keys shared for
  cross-reference; `raw` keeps the full records. (The build-mesh-once-and-reswap-
  probe *performance* benefit still needs a future re-query API on `DFNDData`.)
- **Phase 2 — DONE.** Typed `Component`/`WetComponent`/`DryComponent` and the
  `Components` registry (`topomt/dfnd/components.py`) mirroring `Topography`: a
  `Mapping[ComponentID, Component]` with `_by_side`/`_by_family` indexes,
  `get_components(by=, value=, grouped_by=)`, `by_family`, `neighbors_of`, `info`.
  `side` is derived from `family`. `dfn.components` is now this registry; each
  component carries its graph facet (`node_indices`) and domain facet
  (`atom_indices`, `volume`, `center`). §5–§6.
- **Phase 3 — DONE (mouths).** A wet domain promotes to its concavity feature
  (`Pocket`/`Void`/`Channel`) with `feature.component_id` / `source_id` pointing
  to the dfnd component, and each mouth motif (external link) promotes to a child
  `Mouth` feature wired via `connect_features` (parent concavity → child mouth).
  §7.

Beyond the four phases (also done):

- **Probe re-query.** `DFNDData.at_probe(probe_radius, **overrides)` recomputes
  the dfn/components at a new probe **reusing the cached mesh** (the expensive
  Delaunay + clearances are not rebuilt). `topography.dfnd.network` exposes the
  network. Realizes the mesh-once / dfn-per-probe lifecycle.
- **Wet motifs (canonical layer).** Each `WetComponent` carries its topological
  depth (`topological_depth`), `depth_regions`, and `motifs` (`external_mouth` +
  `depth_region`), per [`domain_motifs.md`](domain_motifs.md) §3.
- **Throat/chamber/bottleneck (experimental).** A first attempt is implemented via
  a capacity merge tree scored by persistence: `WetComponent.throat_candidates`,
  `chamber_candidates`, `bottleneck` (validated on the dumbbell — one throat at
  the neck, two chambers). Ranked descriptors, not a classifier, gated by
  `min_persistence`. This merge tree is also the seed for the Disease-1
  segmentation fix.
- **Phase 4 — DONE (full rename, zero legacy).** The engine contract, the
  object-model layer, the tests, the devtools and the Glossary all use the ladder
  vocabulary; no `domain_family` / `concavity_domains` / `*_domain` family strings
  remain in code (§8). A few design docs (`feature_definitions.md`,
  `residence_transit_contract.md`, `Algorithm.md`) still use the older spellings
  in prose and point here as the authority — a pure-prose sweep that can follow.
