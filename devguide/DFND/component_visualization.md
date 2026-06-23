# DFND Component Visualization

Design proposal for a *visual language* that renders wet (and adjacent dry)
components according to what they **mean** — a void is not drawn like a channel,
a channel is not drawn like a pocket, an interface is not drawn like either, and
a static snapshot is not drawn like a trajectory.

Status: current conceptual visual-language document. The static single-frame
DFND language described here is now mostly implemented in
`molsysviewer_topomt`; dynamic trajectory visualization remains a future layer.
This document describes the *what* and user-facing rationale. The implementation
status and remaining engineering gaps live in
[component_visualization_implementation.md](component_visualization_implementation.md).
References tagged `(roadmap §N)` identify the original idea grouping retained
during consolidation.

Related: [object_model.md](object_model.md) (component families),
[feature_definitions.md](feature_definitions.md),
[interfaces.md](interfaces.md) (wet↔dry adjacency, interface classification),
[dry_network_and_convexity.md](dry_network_and_convexity.md),
[numerical_policy.md](numerical_policy.md),
[dynamic_topology.md](dynamic_topology.md),
[4D_and_pharmacophores.md](4D_and_pharmacophores.md),
[../viewer_addon_plan.md](../viewer_addon_plan.md),
[../molsysviewer_topomt_checkpoint.md](../molsysviewer_topomt_checkpoint.md).

---

## 1. Purpose

`show_dfnd_components` now supports both low-level diagnostic modes and a
curated representation per component type. The remaining purpose of this
document is to keep the visual vocabulary explicit: each DFND family should be
drawn by the representation that communicates *its* distinguishing feature — a pocket's mouth, a channel's
through-path and bottleneck, an interface's two-body lining, a protrusion's
convexity, and (for trajectories) a component's persistence over time.

## 2. Scope

In scope: the wet families that carry topographic meaning — `void`, `pocket`,
`channel` — plus the orthogonal **interface** axis (a wet component whose lining
is contributed by two or more bodies), the **mouths/gates** that punctuate them,
the **dry core** and **convexity/protrusion** reading of the surface, the
**dynamic** axis (trajectories), and the **pharmacophoric** reading of a
component. Touched lightly: the non-resident / `percolating` families as
diagnostic context.

Out of scope here: the panel/workbench UI, selection-sync, and export-quality
scene composition (see [../molsysviewer_topomt_checkpoint.md](../molsysviewer_topomt_checkpoint.md)).
The canonical family names are in [object_model.md](object_model.md) and
`topomt/dfnd/families.py` (the single source of truth).

## 3. What exists today

### 3.1 Renderer modes

`molsysviewer_topomt.render.show_dfnd_components` supports these `representation`
values:

| Mode | Draws | Intent |
|---|---|---|
| `auto` | per-family default (`void`/`pocket`→`envelope`, `channel`→`pipe`, interfaces→`contact_sheet`) | user-facing default resolver |
| `envelope` | blob plus mouth caps and gate rings | pocket/void shape and openings |
| `pipe` | channel skeleton tube plus bottleneck cue | channel path and constriction |
| `rings` | HOLE-style clearance rings | channel profile |
| `contact_sheet` | lining split by body | interface composition |
| `scaffold` | dry-core spine | dry context |
| `affinity_spheres` | interaction-typed spheres | local chemistry |
| `tetrahedra` | empty tetrahedra of the component | substrate / debug |
| `cloud` | Gaussian blob over resident spheres | volume / fallback |
| `residence_spheres`, `alpha_spheres` | discrete spheres | skeleton / debug |
| `probe_centers` | spheres at probe centers | skeleton / debug |
| `surface` | atom-driven lining surface | lining |
| `coast_faces` | wet↔dry boundary faces | adjacency / debug |
| `graph` | nodes + edges of the flow network | topology / debug |

Family-specific rendering is therefore implemented for static single-frame views.
The remaining gap is dynamic visualization across frames, where colours and
layers should be keyed by track identity rather than local component ids.

### 3.2 Viewer primitives already available

`molsysviewer.shapes` already exposes more than the renderer uses. Confirmed:

- `add_pocket_blob` — Gaussian/metaball volume (used by `cloud`).
- `add_pocket_surface` — atom/sphere-driven surface (used by `surface`).
- `add_set_alpha_spheres`, `add_sphere` — discrete spheres.
- `add_tetrahedra`, `add_triangle_faces` — meshes (used by `tetrahedra`/`coast_faces`).
- `add_links` — graph edges, with `color_by`/`color_map` (used by `graph`).
- **`add_channel_tube`** — a variable-radius swept tube from `centers` + `radii`,
  with `color_by` / `solvent_distances` / `color_map`; used by DFND `pipe`.
- **`pharmacophore`** shape — `add_interaction_sites`,
  `add_pharmacophore_features`; used by `show_dfnd_pharmacophore`.
- `displacements`, `anisotropy_ellipsoids`, `signal` — dynamic/scalar overlays,
  with `color_by`; reserved for future trajectory visualization.

Additional primitives now available upstream:

- clipping/section support (`scene.set_clip_planes`/`add_section`) exists in
  `molsysviewer`; DFND also has `carve_voids` as an opacity-focus workflow.
- scalar surface colouring (`set_color_by_values`) exists and is used by
  `show_dfnd_convexity`.
- ring rendering exists (`add_rings`) and is used by the DFND `rings` profile.

Still not a static single-frame primitive: the 2D–3D synchronized trajectory
widget needed for dynamic event timelines.

Per-vertex / per-element **scalar coloring** (`color_by`/`color_map`) *is* broadly
available, so heatmap-style coloring of tubes, links, and displacements is in
reach even though a molecular-surface curvature projection is not.

### 3.3 Component data already available

Each `Component` (`topomt/dfnd/components.py`) already carries the fields a richer
rendering needs:

- local label/topology: `component_id`, `family`, `side`, `node_indices`,
  `resident_node_indices`, `boundary_face_ids`, `atom_indices`, `center`.
- mouths/gates: `n_mouths`, `external_link_ids`, and (in the graph records)
  per-mouth `mouths` / `mouth_face_clusters` with `area_geometric`,
  `R_gate_min`, `R_gate_max`. A mouth is a **face cluster with a gate radius**,
  not a set of atoms — there is no `mouth_atom_indices`.
- metrics: `volume_topological_resident`, `volume_solvent_estimate`,
  `n_wall_faces`, `has_open_interior`.
- interface: `is_interface`, `interface_family`, `lining_bodies`,
  `lining_body_split` — body composition is already resolved on the component,
  ready to color.

The palette (`_TYPE_PALETTE`) currently assigns: `pocket`→blue (`0x3B82F6`),
`void`→green (`0x10B981`), `channel`→amber (`0xF59E0B`),
`percolating`→purple (`0x8B5CF6`), `dry_bank`→slate (`0x64748B`). There is **no**
entry for `interface` and **no** reserved accent for mouths/gates. §11 proposes a
fixed colour-blind-safe (Okabe–Ito) replacement that fixes all of these.

## 4. Survey of reference tools

Studied under `~/repos@others` and `~/repos@others/scripts_view_pockets`; HOLE,
MOLE, SurfNet and P2Rank are added from the roadmap's references.

| Tool | Geometric primitive | Grouping / coloring | Communicates |
|---|---|---|---|
| CASTp (`CASTpyMOL_v3.py`) | lining-atom *selection* per pocket; mouth caps | one selection object per pocket | which residues line it; the portal |
| fpocket (`*.pml`) | alpha-spheres as small spheres | one color per pocket | discrete shape / location |
| fpocket (`*.tcl`, VMD) | QuickSurf over alpha-spheres | Glass3, color by ResId | volume as a soft translucent blob |
| AlphaSpace2 (`View.py`) | alpha+beta pseudo-atoms; d-pockets (`write_trajectory`) | scalar in b-factor/occupancy, **probe type in `element`** | druggability / dynamics |
| MayaChemTools Cavities | molecular surface in **cavity mode** | cavity color or hydrophobicity | buried cavities |
| MayaChemTools Fpockets | lining surface + spheres, hierarchical groups | hydrophobicity / charge | multi-pocket exploration |
| MayaChemTools Interfaces | per-chain surface + contact residues + electrostatics | interface vs non-interface | contact between bodies |
| CAVER / MOLE | **variable-radius spheres/tube along the centerline**; bottleneck | one color per tunnel; `origins.pdb` = mouths | channel path and **bottleneck** |
| HOLE | **stacked orthogonal rings**, radius color-coded | green/amber/red by clearance | pore profile without obstructing lining |
| SurfNet | **wireframe density isosurface** | contour | volume without hiding internal ligand |
| P2Rank | **surface heatmap** of ligandability | hot/cold per surface point | where binding is likely |
| pocketeer (`vis.py`) | spheres (atomworks) | rainbow/grayscale/red_blue | quick multi-pocket summary |
| pycasta (`pymol_vis.py`) | protein `surface` + pocket `mesh` | slate + orange | alpha-shape mesh over the surface |

## 5. The shared visual vocabulary

The reusable building blocks, with the `molsysviewer` primitive each maps to.

| # | Primitive | What it shows | Tools | Viewer primitive |
|---|---|---|---|---|
| 1 | **Lining** (optionally bicolor inner/outer) | the atoms/residues that line it | CASTp, MayaChemTools, pycasta | `add_pocket_surface` (DFND `surface`) |
| 2 | **Discrete spheres** | the alpha/probe-sphere skeleton | fpocket, AlphaSpace2, pocketeer | `add_set_alpha_spheres` (DFND `residence_spheres`) |
| 3 | **Blob / metaball** | a smooth union of those spheres | fpocket QuickSurf, CAVER void | `add_pocket_blob` (DFND `cloud`) |
| 3b | **Wireframe isosurface** | volume without hiding internal content | SurfNet | `add_pocket_blob` wireframe mode *(to confirm)* |
| 4 | **Variable-radius centerline tube** | a channel's path + bottleneck | CAVER / MOLE | **`add_channel_tube`** (unused) |
| 4b | **Stacked orthogonal rings** | the pore clearance profile | HOLE | line geometry / `add_links` *(to build)* |
| 5 | **Mouth cap / gate ring** | the portal closing the chamber | CASTp | `add_triangle_faces` (cap) + ring *(to build)* |
| 6 | **Scalar → color/size** | score, gate radius, depth, probe type, persistence | AlphaSpace2, CAVER, P2Rank | `color_by`/`color_map`, `pharmacophore`, `signal` |
| 7 | **Streamlines / flow particles** | transport direction along the graph | (dynamic) | `displacements` / animated `add_links` *(to build)* |
| 8 | **Skeleton cylinders** | the dry hydrophobic core / scaffold | — | `add_links` as thick cylinders |

Two organizing patterns are equally important:

- **Color by component identity** — each component its own color (universal).
- **Switchable hierarchical grouping** — MayaChemTools nests
  chain→pocket→{surface, spheres, residues} layers that toggle independently;
  the `layer_tag`/`tag_prefix` mechanism is the hook for it.

## 6. Per-family visual language

Map each family to the primitive that shows *its* distinguishing feature, with a
sensible default plus on-demand secondaries.

| Family | Primary representation | Secondary / on-demand | Rationale |
|---|---|---|---|
| **void** (0 mouths, buried) | closed translucent **blob** (`add_pocket_blob`) **+ opacity carving** — fade (α≈0.1) the molecular representation *outside* the component, exposing the cavity natively (*roadmap §1.4*) | clip plane (when available); wireframe isosurface (*roadmap §1.2*) | a buried closed volume is invisible under cartoon/spacefill; carving exposes it without manual camera work |
| **pocket** (1 mouth) | **blob** + **mouth cap** (triangulated portal face cluster, translucent) + gate ring at `R_gate` (*roadmap §1.1*) | bicolor lining wall (warm inner / neutral outer, *roadmap §1.1*); affinity spheres (*roadmap §1.3*); depth→color | the mouth is what distinguishes a pocket from a void; the cap shows exactly where a ligand enters |
| **channel** (≥2 mouths) | **`add_channel_tube`** along the centerline, radius = local `R_gate`/free radius, **+ bright bottleneck ring** at the narrowest gate (*roadmap §2.1*) | **HOLE stacked rings** color-coded by clearance (*roadmap §2.2*); flow streamlines (*roadmap §2.3*); lumen blob | path/length/bottleneck, which an amorphous blob hides; rings keep the lining visible for ion channels |
| **interface** (multi-body lining) | family blob/tube **+ per-body contact sheet** split by body from `lining_body_split` — bicolor for two banks, one color per body for 3+-body junctions (*roadmap §3.1*) | electrostatics / hydrophobicity | the point is *which bodies* line it and their shape complementarity |
| **dry_bank** (context) | slate, low-opacity surface or hidden | **hydrophobic scaffold** cylinders through packed-core centroids (*roadmap §3.2*) | usually scaffold/context, but the scaffold view exposes the mechanical "spine" |
| **non-resident** (`degenerate_subprobe`, `surface_concavity`, `nonresident_passage`) and **`percolating`** | **diagnostic style**: hidden by default; desaturated/wireframe when shown | spheres for inspection | usually artifacts/pathologies; visible only on demand and visually demoted |

Notes:

- **void vs pocket** differ only by the mouth cap/gate accent — same blob, the
  pocket additionally lights its single mouth. This keeps the two visually
  adjacent (a pocket *is* a void with one opening) while still distinguishable.
- **channel** offers two complementary reads: the solid **tube** (shape and
  bottleneck at a glance) and the **HOLE ring profile** (clearance along the axis
  without hiding the coordinating residues). The clearance color thresholds from
  HOLE are concrete and worth reusing: green for `R > 1.15 Å` (admits water),
  amber for tight constrictions, red for closed bottlenecks `R < 1.15 Å`.
- **interface** is an *orthogonal* axis, not a fifth family: a pocket, void, or
  channel can each be an interface, so its rendering *composes* with the family
  rendering (e.g. a pocket-blob whose lining is split into per-body colors —
  two for a bipartite contact, more for 3+-body junctions like
  `three_blocks_interface` / `three_body_junction`) rather than replacing it.
  See [interfaces.md](interfaces.md).
- **non-resident / percolating** families are demoted, not hidden forever: a user
  debugging a pathology needs them, but they must never compete with real
  findings.

## 7. Convexity and the dry core

The families above describe *concave* topography (cavities). The surface also has
*convex* features — ridges, protrusions, knobs — and an inaccessible packed core.
Both have synthetic fixtures already (`tetrahedron_spike*`, the two-block
interfaces) and deserve a representation (*roadmap §3.2, §3.3*).

- **Convexity heatmap** — project a curvature scalar onto the molecular surface:
  valleys (concave pockets) cold, ridges (convex protrusions/loops) hot. A clean,
  non-cluttered surface summary that needs no extra mesh. **Requires a per-vertex
  surface-coloring primitive not yet confirmed in the viewer** (see §3.2); the
  scalar coloring machinery (`color_by`) exists but the curvature-projection slot
  does not.
- **Hydrophobic scaffold** — the dry bank rendered as thick cylinders connecting
  the centroids of packed hydrophobic residues, i.e. the folding "spine". Maps to
  `add_links` styled as cylinders; data comes from the dry network
  ([dry_network_and_convexity.md](dry_network_and_convexity.md)).

## 8. Dynamic / trajectory visualization

DFND targets MD trajectories ([dynamic_topology.md](dynamic_topology.md),
[4D_and_pharmacophores.md](4D_and_pharmacophores.md)), so a static snapshot is
half the story. AlphaSpace2's *d-pockets* (`write_trajectory`) are the reference;
the viewer already has dynamic overlays (`displacements`, `anisotropy_ellipsoids`,
`signal`).

**Data precondition.** Every reading below assumes the DFND dynamic layer emits
components with `track_id` segments and a lineage graph across frames. A
continuous cavity keeps the same track identity as it breathes or changes
accessibility; merges and splits connect different tracks through lineage
events. `component_id` remains a local per-result rank label and must not drive
temporal color. That tracking is core work, not rendering — it is currently a *design*
([dynamic_topology.md](dynamic_topology.md)), not an implemented output. The
viewer can only render persistence/events once the model produces them; until
then this section is a target, not a wiring task.

Target readings:

- **Persistence as opacity/color** — a component surviving most frames is solid;
  a transient one is faint (d-pocket occupancy → alpha or a ramp).
- **Identity tracking across frames** — a track keeps its color/id over time
  so the eye follows the same cavity; mouth opening/closing shows as the gate
  accent appearing/disappearing.
- **Volume pulsation** — the blob/tube breathes with `volume_solvent_estimate`
  per frame; `signal`/`displacements` carry the scalar.
- **Flow streamlines** — animated particles/arrows along the graph edges show
  transport direction and paths of least resistance (*roadmap §2.3*).
- **2D–3D synchronized widget** (*roadmap §5*) — an interactive 2D plot
  (matplotlib/bokeh/bqplot) of pocket volume or `R_gate` over time, embedded
  beside the 3D view; clicking a time point drives the 3D frame, and pocket
  **events (birth/merge/split/collapse)** are marked on the timeline. This lets
  the quantitative trace guide visual inspection.
- **Transition cueing for merge/split events** — when a topological event is
  *imminent*, telegraph it before the ids change: render the about-to-merge (or
  splitting) components with a **blended intermediate color** of their two source
  colors, so the researcher sees the event coming rather than a jarring id swap.
  Two caveats: (a) this lives in the **dynamic-tracking layer**, not in
  `components.py` (which is the static per-frame model); (b) it needs the core to
  **detect events with look-ahead**, a step *beyond* the §8 identity precondition.
  Feasibility: the **blend** is doable now via `set_color`; a striped two-color
  pattern is aspirational (the shapes have no stripe/pattern style).
- **Time-averaged vs per-frame** — offer both: a consensus blob (where the cavity
  *usually* is) and a scrubable per-frame view.

The static language in §6 is built to extend into time rather than fight it.

## 9. Pharmacophoric / probe-type representation

A wet component is not only a shape — its lining implies *interaction
preferences*. AlphaSpace2 encodes a `best_probe_type` per beta-cluster; the
viewer exposes a `pharmacophore` shape (`add_pharmacophore_features`,
`add_interaction_sites`). Connects to
[4D_and_pharmacophores.md](4D_and_pharmacophores.md). Two levels:

- **Affinity spheres** (*roadmap §1.3*, the simple route) — color each residence
  sphere by the physicochemical environment of its lining atoms: hydrophobic
  (yellow, drug-favorable), polar H-bond donor/acceptor (blue), charged
  (red/blue). A pharmacophore/druggability map *inside* the cavity volume, using
  only `add_set_alpha_spheres` + `color_by`.
- **Interaction-site map** (the full route) — place typed interaction features
  (donor/acceptor/hydrophobic/aromatic/charged) at lining sub-regions via the
  `pharmacophore` shape. Composes with the dynamic axis (a *dynamic pharmacophore*
  = sites weighted by persistence).

Chemistry typing is out of scope here; the representation slot and the viewer
primitive both already exist.

## 10. Triangulation stability for reproducible and dynamic rendering

(*roadmap §4*, reconciled with [numerical_policy.md](numerical_policy.md).)

3D meshes must not flicker between identical or near-identical conformations
(lattices, helices) or across adjacent MD frames. The visualization layer must
not invent a separate geometric correction for this. In particular,
**coordinate perturbation (jitter ~1e-5 Å)** must not be adopted blindly. DFND
already perturbs *symbolically* through its epsilon policy
(`epsilon_length = 1e-6`, `epsilon_relative = 1e-8`, generous tie-breaking), so
an explicit `1e-5 Å` coordinate jitter is both larger than `epsilon_length` and
redundant with — possibly contradictory to — the existing degeneracy handling.
The *goal* (stable, reproducible meshes across frames) is right; the mechanism
must be the existing symbolic policy, not added coordinate noise. Cross-check any
change here against [numerical_policy.md](numerical_policy.md) first.

Net: the visualization layer should *consume* a triangulation that
`numerical_policy` already makes stable. It should not hide or perturb geometry
as a substitute for a physical or topological explanation.

## 11. Cross-cutting conventions

- **Default palette (colour-blind safe, Okabe–Ito).** The current `_TYPE_PALETTE`
  (§3.3) pairs green (void) + amber (channel), risky for red–green colour-vision
  deficiency. Replace it with this fixed Okabe–Ito assignment so implementation
  makes no arbitrary choices:

  | Role | Colour | Hex |
  |---|---|---|
  | `pocket` | blue | `#0072B2` |
  | `void` | sky blue | `#56B4E9` |
  | `channel` | orange | `#E69F00` |
  | `interface` body A | vermillion | `#D55E00` |
  | `interface` body B | bluish green | `#009E73` |
  | `percolating` | reddish purple | `#CC79A7` |
  | `dry_bank` | grey | `#999999` |
  | **mouth/gate accent** | yellow | `#F0E442` |

  Notes: `pocket` (blue) and `void` (sky blue) are deliberately two blues — a
  pocket *is* a void with one opening, so they stay adjacent and are separated by
  luminance plus the mouth primitive, not hue alone. The mouth accent is yellow
  (not red) because vermillion is already interface body A. For 3+-body
  junctions, extend body A/B with the remaining Okabe–Ito hues (yellow is
  reserved for gates, so use blue/orange tints as needed). **Never rely on hue
  alone** — always pair colour with the primitive (blob vs tube vs rings).
- **Translucency by default** (~0.3–0.4 alpha) so the protein stays visible.
- **Void opacity carving** — to expose a buried void without a clipping plane,
  fade the molecular representation *outside* the component to α≈0.1 via a
  selection + `set_alpha`. Anchor the kept-opaque region to the component's own
  geometry (its `atom_indices`/lining plus a margin, or its bounding box plus
  padding), **not** a fixed radius like 10 Å — a fixed cutoff over-hides large
  voids and under-hides small ones.
- **Mouths and gates as a first-class primitive** — render the mouth **face
  cluster** (`mouth_face_clusters`) as a translucent cap plus a ring sized at
  `R_gate`, reusable by pocket and channel. Anchored to real gate geometry, not
  atoms.
- **Optional scalar → gradient** — `R_gate`, depth, or per-frame persistence
  mapped via `add_channel_tube(color_by=...)` / `color_map` / `signal`, to reveal
  the bottleneck or the most stable region.
- **Labels, legend, and metrics in the scene** — each component should show its
  `component_id`, `family`, mouth count, and a metric
  (`volume_solvent_estimate`, `mouth_area`, `R_gate_min`) as an optional label,
  with a family legend on the scene.
- **Default visibility by relevance** — with many components (catalog systems
  reach 5–14 features), show the top-N by `volume_solvent_estimate` (or
  significance) solid by default and leave the rest as toggleable layers,
  mirroring fpocket/AlphaSpace2 which rank by score and display the top.
  Non-resident / `percolating` families start hidden (§6).
- **Nested components** — concentric features (`nested_spheres`,
  `onion_shells_3`, `pocket_in_pocket`) must stay distinguishable: render the
  outer container as wireframe / lower opacity and the inner as solid, or step
  opacity by nesting depth, so two concentric blobs do not merge into one
  unreadable shape. (DFND does not track genus/hierarchy yet, so this is a
  rendering-side cue, not a claimed topological relation — see
  [known_limitations.md](known_limitations.md).)
- **Switchable layers** — each (component × primitive) as its own
  tagged/toggleable layer (`layer_tag`/`tag_prefix`).
- **Face semantics, not geometric hiding** — face renderers expose DFND meaning
  directly: permeability, semantic role (`transit_face`, `blocked_face`,
  `mouth_face`, `boundary_face`, `coast_face`), `R_gate`, gate margin when the
  probe radius is known, incident tetrahedra, and component ids when available.
  Colouring can use component, permeability, role, or gate margin; the viewer
  must not hide faces merely because their geometry looks visually awkward.

## 12. Representation mode names

A concrete naming for the extended `representation` parameter, reconciling the
roadmap's modes (*roadmap §6*) with the per-family defaults of §6. Family defaults
are applied when the caller passes nothing; the explicit names are overrides.

| Name | Family fit | Primitive |
|---|---|---|
| `envelope` | pocket, void | blob + mouth cap / bicolor wall |
| `wire_contour` | pocket, void | wireframe isosurface |
| `affinity_spheres` | pocket, void | residence spheres colored by environment |
| `pipe` | channel | `add_channel_tube` + bottleneck ring |
| `rings` | channel | HOLE stacked-ring profile |
| `contact_sheet` | interface | per-body body-split surface (bicolor / N-body) |
| `scaffold` | dry_bank | hydrophobic-core cylinders |
| `heatmap` | surface/convexity | curvature projection (needs viewer support) |

These coexist with the existing debug modes (`tetrahedra`, `cloud`, `graph`, …).

## 13. Remaining gaps versus the current implementation

The static single-frame vocabulary is implemented. Remaining gaps are narrower:

1. **Dynamic axis** — render trajectories with stable `track_id` colours/layers,
   event timelines, and merge/split/open/close cues once a trajectory driver
   supplies tracked DFND results.
2. **2D–3D synced trajectory widget** — generic MolSysViewer UI primitive for
   coupling timelines or scalar plots to scene selection.
3. **Branched channel view** — expose secondary mouths in >2-mouth channels
   without implying a validated max-capacity navigability path.
4. **Wireframe isosurface** (`wire_contour`) — optional mode, still dependent on
   confirming or extending `add_pocket_blob` wireframe support.

## 14. Current implementation status

The original static phasing has landed: per-family defaults, `envelope`, `pipe`,
`contact_sheet`, `rings`, `affinity_spheres`, labels/legend, void carving,
`scaffold`, convexity, pharmacophore rendering, and top-N visibility are
implemented. The implementation-level status is maintained in
[component_visualization_implementation.md](component_visualization_implementation.md).

## 15. Cross-references

- Family definitions and single source of truth:
  [object_model.md](object_model.md), `topomt/dfnd/families.py`.
- Interface axis: [interfaces.md](interfaces.md).
- Wet↔dry adjacency and dry network:
  [dry_network_and_convexity.md](dry_network_and_convexity.md).
- Numerical / triangulation policy: [numerical_policy.md](numerical_policy.md).
- Dynamic / 4D / pharmacophores: [dynamic_topology.md](dynamic_topology.md),
  [4D_and_pharmacophores.md](4D_and_pharmacophores.md).
- Addon plan and checkpoint: [../viewer_addon_plan.md](../viewer_addon_plan.md),
  [../molsysviewer_topomt_checkpoint.md](../molsysviewer_topomt_checkpoint.md).
- Reference tools studied: `~/repos@others/{AlphaSpace2,fpocket,pocketeer,pycasta}`,
  `~/repos@others/scripts_view_pockets/{CASTpyMOL_v3.py,PyMOLVisualize*.html,caver-pymol-plugin-3.0.3}`.
- Viewer primitives: `molsysviewer.shapes` (`add_channel_tube`, `pharmacophore`,
  `add_pocket_blob`, `add_pocket_surface`, `add_set_alpha_spheres`, `displacements`).
