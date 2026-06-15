# DFND Object Model and Terminology (authoritative)

Recorded on 2026-05-23. This is the **authoritative** reference for how DFND
output is organized and for the words we use. Where any other DFND document or
code field disagrees with this one, this document is the target and the other is
either legacy (pending migration) or wrong. Its purpose is to remove, once and
for all, the confusion between *component*, *motif*, and *feature*.

> **2026-05-26 — `domain` retired.** The earlier ladder had a middle rung,
> *domain* ("the component realized in atoms"). It is gone: a component and its
> realization are a single, 1:1, inseparable object, "domain" collides with the
> biological sense of the word, and "component" is the graph/alpha-complex term of
> art and the only implemented class. The realization (atoms, volume, center) is
> now simply the **spatial representation of the component**, not a named rung. The ladder
> is **`component → feature`**. Wherever older prose still says "domain", read
> "component".

## 1. Two levels, one dividing principle

There are exactly two levels, and they must not leak into each other:

- **`Topography`** — the **public, method-agnostic** level. It holds
  **features** (Pocket, Void, Channel, Mouth, …) as individual objects related by
  parenthood and organized by shape/dimensionality. Every engine (CASTp, fpocket,
  AlphaSpace2, pycasta, DFND) fills this same level. A user of `Topography` must
  be able to work without knowing anything about DFND.
- **`topography.dfnd`** — the **DFND-specific substrate**. It holds the Delaunay
  mesh, the flow network, and its decomposition into components/motifs.

> **Dividing principle.** Ask: *"would a user who knows nothing about DFND need
> this — no graphs, no wet/dry, no connected components, no OCEAN?"* If **no**, it
> belongs under `topography.dfnd`, never at the `Topography` top level.

This is why there are no `dfnd_*` attributes at the `Topography` top level: all
DFND material lives under the single `topography.dfnd` object.

## 2. The terminology ladder: component → feature

A single connected piece of empty space is described at two rungs. Use the
right word for the right rung:

```
component                              →   feature
(the private dfnd object)                  (the public object)

a connected component of the DFN           a Topography object
graph — a set of tetrahedron NODES         promoted from a component:
(+ their faces and edges) together         + units, residues, morphology,
with its spatial representation: the lining        dynamics, annotations
atoms, volume, center, footprint           method-agnostic

"the decomposition produces components"
```

- **component** — the dfnd object. It has two **facets** of the same thing, not
  two objects:
  - a **graph facet** — the output of the *decomposition* (the **D** in DFND): a
    set of tetrahedron nodes plus the faces/edges among them;
  - a **spatial representation** — that component realized in the system: its lining
    atoms, volume, center, spatial footprint.
  Probe-dependent. (There is no separate "domain": a component and its
  realization are one inseparable, 1:1 object — see the 2026-05-26 note above.)
- **feature** — the **public** `Topography` object promoted from a component.

### Two reserved-word rules (the heart of the convention)

1. **The word `feature` is NEVER used inside `dfnd`.** Inside dfnd there are
   components and motifs — never features.
2. **The word `motif` is NEVER used at the `Topography` level.** A motif is a
   dfnd object; when it surfaces publicly it has become a feature.

## 3. motif — sub-structure of a component

A **motif** is a named sub-structure *of a component* (a geometric motif over the
component's atomic structure): a **throat/bottleneck**, a **chamber**, a
**depth-region**, a **mouth**. Motifs are how a single component has internal
parts.

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
    ├── parameters      # mesh_config + query + reporting + identity keys
    ├── graph           # nodes (wet/dry state, transit_role, flags; ref mesh tetra),
    │                   #   edges (permeable faces, transit edges), OCEAN
    │                   #   .neighbors(node_id, side=None|'wet'|'dry')   ← §10
    └── components       # the decomposition registry (see §5)
                        #   .coast_faces  (wet↔dry contact faces)         ← §10
```

`mesh.neighbors(tetra_id)` gives the bare (probe-independent) face-adjacency;
`dfn.graph.neighbors` adds the wet/dry filter (probe-dependent). See §10.

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
  `nonresident_passage`, `degenerate_subprobe`, `percolating` (wet) and
  `dry_bank` (dry). `percolating` is the wall-less resident override
  (`n_wall_faces == 0`); it promotes to a `Percolating` feature with `shape_type`
  `neutral` and gets no `Mouth` child.
- **wet and dry are unified under `component`.** `side` is **derived from
  `family`** via a `_SIDE_BY_FAMILY` registry, mirroring how `BaseFeature` derives
  `shape_type`/`dimensionality` from `feature_type`.
- The `Components` registry is atomic: component IDs are unique and immutable
  while registered; re-adding the same object is idempotent; duplicate objects
  are rejected; and explicit `replace`, `rename`, and `remove` operations keep
  indexes, adjacency, wet/dry lining references, and coast-face references
  coherent. `copy(deep=True)` produces an independent semantic registry copy.

## 6. The `Component` object — mirrors `BaseFeature` + `Pocket`/`Void`/`Channel`

**`Component`** (base, ≡ `BaseFeature`):
- `component_id` (local rank label), `component_index` (local collection
  position), `node_count_rank`, deprecated compatibility alias `size_rank`,
  `family`, `side` (derived), `flags`, `_dfn` back-ref;
- exact/contextual identity: `support_key`, `component_key`;
- internal implementation label: `graph_label`;
- **graph facet**: `node_indices` (tetrahedra), `boundary_face_ids`;
- **spatial representation (atoms)**: `atom_indices`, `volume`, `center`;
- **motifs**: the component's sub-structures.

Atom-index fields follow the authoritative two-space contract:
`atom_indices` always refers to the original molecular system, while
`local_atom_indices` and `face_atoms_local` index the selected DFND mesh and its
coordinate arrays. Public APIs and MolSysMT queries use the former; kernels and
geometry use the latter. Generic addon-owned payloads declare
`atom_index_space` explicitly. See
[`checkpoint_atom_index_spaces_2026_06_14.md`](checkpoint_atom_index_spaces_2026_06_14.md).

The fields above follow the authoritative
[`component_identity_contract.md`](component_identity_contract.md):
`component_id`, `component_index`, and ranks are local to one result;
`support_key` identifies exact tetrahedral support; `component_key` identifies
that support and classification in one result context; temporal continuity uses
`track_id` and a lineage graph in a separate dynamic layer.

**`WetComponent`** (≡ concavity classes): `resident_node_indices`,
`transit_connector_node_indices`, `external_link_ids`, `external_link_keys`,
`n_mouths`, `mouth_area`,
`has_residence`, `has_open_interior`, `volume_topological_resident`,
`volume_solvent_estimate`; the interface descriptor `is_interface` /
`interface_family` / `lining_bodies` / `lining_body_split` (§10,
[`interfaces.md`](interfaces.md)); and the wet→dry adjacency `dry_lining` (§10).

**`DryComponent`**: `interface_ids`, `neighbor_component_ids`,
`dry_depth_{min,max,mean}` (+ per-node), `motif_ids`, `motif_keys`; and the
dry→wet adjacency
`wet_lining` + the named view `interface_walls` (§10).

Two subclasses (not one per family) because the wet families differ only by the
`family` label, not by structure. Motif slots and registries exist on both sides;
both wet-component motifs (such as canonical mouths and depth regions) and
dry-component motifs are fully built and supported (see
[`component_motifs.md`](component_motifs.md)).

The canonical **family-name strings** (`void` / `pocket` / `channel` / … /
`dry_bank`) and the `side` they map to live in one place — `topomt/dfnd/families.py`
— and every consumer (the classifier in `graph.py`, `components._SIDE_BY_FAMILY`,
`interfaces.py`, the viewer palette/filters) imports them from there rather than
re-typing literals, so renaming a family is a one-line change. (The `channel`
family was named `multi_external_link` until 2026-06.)

## 7. Promotion: dfnd → Topography (not 1:1)

A single component yields a **feature subgraph**, not one feature:

```
WetComponent(family='pocket', id='WET-3')   ──▶  Pocket   (feature.source_id = component_key)
   ├── external_mouth motif                 ──▶  Mouth    (child via connect_features)
   ├── throat motif                         ──▶  Neck     (child)
   └── chamber motif                        ──▶  sub-Pocket (nested child)
```

- The **component** promotes to the concavity **feature** (`Void`/`Pocket`/`Channel`).
- The component's **motifs** promote to **child features** (`Mouth`, throat→`Neck`,
  chamber→sub-`Pocket`), wired with `connect_features`. The feature parenthood
  *is* the component's motif structure.
- A promoted parent feature carries `source_id = component_key`. A promoted
  child keeps its own contextual source identity (`external_link_key` for a
  mouth) and carries `parent_component_key`, making feature → component →
  tetrahedra → atoms traceable without treating a local
  rank label as structural identity.
- Provisional families (`surface_concavity`, `nonresident_passage`,
  `degenerate_subprobe`) and the dry interfaces are **not** promoted yet (no
  feature class for them); they remain available under `topography.dfnd`.

## 8. Relation to existing vocabulary (migration)

This model **supersedes** the older, inconsistent wording in which the wet
graph-component was a *"transit/concavity domain"* and the dry one a *"dry
component"*. Going forward:

- the dfnd object (either side) is a **`component`**, with a graph facet and a
  geometry/atoms facet (no separate "domain" — see §2);
- the **public** object is a **`feature`**;
- sub-structures of a component are **`motifs`**.

The rename is **complete — zero legacy** (done while the project is early, before
the contract spread further):

| legacy | new |
|---|---|
| `dfnd_*` attributes on `Topography` | single `topography.dfnd` |
| wet "transit/concavity domain" | `component` (`WetComponent`) |
| "dry component" | `component` (`DryComponent`, family `dry_bank`) |
| the middle rung "domain" (component realized in atoms) | retired — the **spatial representation** of the `component` (`atom_indices`, `volume`, `center`) |
| atoms of a domain | `component` spatial representation (`atom_indices`, …) |
| raw field `concavity_domains` / `transit_domains` | `wet_components` (single key) |
| record field `domain_family` | `family` |
| family strings `void_domain` / `pocket_domain` / `channel_domain` / … | `void` / `pocket` / `channel` / … (no `_domain` suffix) |
| record field `domain_id` (component's own) | `id` |
| `domain_id` referencing the parent (external links, residence regions) | `component_id` (local compatibility) + `component_key` (contextual provenance) |
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
  (`Pocket`/`Void`/`Channel`) with local `feature.component_id` and contextual
  `source_id = component_key`; each mouth motif (external link) promotes to a child
  `Mouth` feature wired via `connect_features` (parent concavity → child mouth).
  §7.

Beyond the four phases (also done):

- **Probe re-query.** `DFNDData.at_probe(probe_radius, **overrides)` recomputes
  the dfn/components at a new probe **reusing the cached mesh** (the expensive
  Delaunay + clearances are not rebuilt). `topography.dfnd.network` exposes the
  network. Realizes the mesh-once / dfn-per-probe lifecycle.
- **Wet motifs (canonical layer).** Each `WetComponent` carries its topological
  depth (`topological_depth`), `depth_regions`, and `motifs` (`external_mouth` +
  `depth_region`), per [`component_motifs.md`](component_motifs.md) §3.
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

## 10. Wet↔dry adjacency (neighbors, coast, lining)

The wet and dry sides touch along a shared boundary. Navigating it — *which dry
tetrahedra border this wet one; which dry bank lines this pocket; what is the dry
wall of an interface* — is exposed in four layers, each reusing the one below.
The topology (who borders whom) is probe-independent and lives on `mesh`; the
wet/dry split is probe-dependent and lives on `dfn`. Nothing is duplicated per
record: the single `(N, 4)` Delaunay adjacency array backs all of it.

**Layer 0 — tetrahedron neighbors (the primitive).**

- `mesh.neighbors(tetra_id, include_ocean=False) -> list[int]` — bare face-
  neighbors (probe-independent topology; `-1` = OCEAN / convex hull).
- `dfn.graph.neighbors(node_id, side=None|'wet'|'dry') -> list[int]` — the same,
  filtered by the neighbor's residence side. Answers, in one call, *which dry
  tetrahedra border this wet one* (`side='dry'`) and the reverse (`side='wet'`).

No `Tetrahedron`/`Node` class and no stored `neighbors` attribute: tetrahedra are
records, and the accessor reads the shared adjacency array (O(1)). Storing
neighbors per record would duplicate that array and mis-level the wet/dry split
(it is per-probe, not geometry).

**Layer 1 — coast faces.** `dfn.components.coast_faces` is the materialized
wet↔dry contact: every internal face whose two tetrahedra sit in components of
opposite `side`. Each record carries `wet_tetrahedron_id` / `dry_tetrahedron_id`,
`wet_component_id` / `dry_component_id`, their contextual
`wet_component_key` / `dry_component_key`, `atom_indices`, `area`, `R_gate` and
`permeability_state`. This is the real *wall surface* (the per-face area, summed,
is the contact area).

**Layer 2 — per-component lining (bidirectional, symmetric).** Built from the
coast and attached to the typed components:

- `WetComponent.dry_lining` → `{DRY-id: {tetrahedron_ids, contact_face_ids,
  area}}` — the dry banks (and their wall tetrahedra) that line this wet region.
- `DryComponent.wet_lining` → `{WET-id: {tetrahedron_ids, contact_face_ids,
  area}}` — the symmetric reverse: the wet regions this bank lines.

So any wet component reaches its dry detail and any dry bank reaches its wet
regions, both in O(1), with the contact area shared and consistent on both sides.

**Layer 3 — `interface_wall` (a named view).** `DryComponent.interface_walls` is
`wet_lining` restricted to the wet components that are interfaces (`is_interface`,
§ [`interfaces.md`](interfaces.md)). No extra computation — it closes the wet/dry
symmetry of an interface: the wet half is the channelway
(`WetComponent.lining_bodies` → its banks), the dry half is each bank's wall
against it (`DryComponent.interface_walls` → the wet interface).

Implementation: `mesh.neighbors` / `graph.neighbors` in `data.py`;
`coast_faces` + `*_lining` + `interface_walls` in `components.py`
(`_attach_coast_and_lining`); areas use `tools.tessellation` triangle area and
need coordinates (the `network`, threaded into `build_components`).
