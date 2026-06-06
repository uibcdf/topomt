# DFND Component Visualization — Implementation Proposal

The *how* for [component_visualization.md](component_visualization.md) (the
*what*). It turns that design into an ordered, testable build plan anchored to the
current `molsysviewer_topomt.render` code, the real `molsysviewer.shapes`
primitives, and the DFND data already on the `Component`/`raw` records.

Status: **in progress** (updated 2026-06-06). Phases 0–5 are implemented and
pushed (topomt `main`); Phase 6 is partial (dry-core scaffold done). The two
generic upstream primitives this plan needed — `add_rings` and `focus_with_fade`
— are implemented and pushed in `molsysviewer`. Remaining work is upstream
(more molsysviewer primitives) or core (dynamic identity). Per-phase status in
the build-order table (§12); phasing follows
[component_visualization.md §14](component_visualization.md) and its gap list
(§13).

## Implementation status (2026-06-06)

Done and on `main`:

- **Phase 0** — Okabe–Ito CVD-safe palette + `representation='auto'` per-family
  dispatch (channel→pipe, pocket/void→envelope; interface→contact_sheet).
- **Phase 1** — `envelope`: blob + per-mouth gate ring + translucent mouth cap.
- **Phase 2** — `pipe`: channel centerline tube (`topomt/dfnd/centerline.py`) +
  real bottleneck ring.
- **Phase 3** — `contact_sheet`: interface lining split per body.
- **Phase 4** — `rings`: HOLE-style clearance profile (green/amber/red @ 1.15 Å).
- **Phase 5** — `carve_voids` (focus-with-fade), `show_dfnd_labels`,
  `affinity_spheres` (via `molsysmt.physchem`), `top_n` visibility.
- **§7** — `scaffold`: dry-core MST spine.
- **molsysviewer** — `add_rings` shape, `focus_with_fade` primitive (both pushed).

Remaining:

- **Legend** primitive (molsysviewer) → the colour legend of Phase 5.
- **Curvature surface coloring** primitive (molsysviewer) → convexity heatmap (§7).
- **Clipping-plane**, **2D–3D synced widget** primitives (molsysviewer).
- **Pharmacophore interaction-site map** (§9) — topomt, via the `pharmacophore`
  shape + `physchem` (trackable now, not yet built).
- **Dynamic topology** (§8) — **blocked on DFND core**: no cross-frame component
  identity exists yet.
- **molsysmt** — `physchem` should treat `DUM` dummy atoms/groups as neutral
  (proposal filed) so affinity typing works on dummy systems too.

---

## 1. Current code, briefly

`molsysviewer_topomt/render/_components.py` (539 lines) holds
`show_dfnd_components(view, topography, *, representation='tetrahedra', …)`. It:

1. resolves the topography and `dfnd_data = topography.dfnd`;
2. selects components from `dfnd_data.dfn.components.wet` / `.dry` (filtered by
   `component_types`, `component_ids`, `interfaces_only`);
3. dispatches on `representation` through an `if/elif` chain
   (`tetrahedra`, `cloud`, `residence_spheres`/`alpha_spheres`, `probe_centers`,
   `surface`, `coast_faces`, `graph`);
4. each branch builds geometry via small `_component_*` helpers that return
   `(centers, radii)` (or `None, None`) and calls a `view.shapes.add_*` primitive,
   appending tagged layers.

Helpers already present: `_component_node_indices`,
`_component_residence_spheres(comp, tetra_map, …)`,
`_component_alpha_spheres(comp, mesh, …)`. The palette is `_TYPE_PALETTE`.

Data available without new core work (confirmed):

- `Component`: `family`, `resident_node_indices`, `atom_indices`, `center`,
  `n_mouths`, `external_link_ids`, `is_interface`, `lining_bodies`,
  `lining_body_split`, `volume_solvent_estimate`.
- `raw`/graph records: per-tetra `center` + `R_residence`; per-mouth
  `mouth_face_clusters` with `faces`, `R_gate_min/max`, `area_geometric`; gate
  centers (`face_gate_radius_batch`).
- adjacency for paths: `data.Mesh.neighbors` / `Graph.neighbors`, and
  `experimental._resident_permeable_graph(raw, resident_ids)` which already
  builds an `nx.Graph` over resident tetrahedra with an edge per permeable face.

Viewer primitives (confirmed): `add_pocket_blob`, `add_pocket_surface`,
`add_set_alpha_spheres`, `add_sphere`, `add_tetrahedra`, `add_triangle_faces`,
`add_links`, `add_channel_tube(centers, radii, color_by, color_map, …)`,
`pharmacophore.add_*`, `displacements`/`signal`; plus `selections.add_selection`
+ `layers.set_alpha` (void carving) and `annotations.add_label_*` (labels).

## 2. Architecture decisions

- **D1 — keep `show_dfnd_components` as the single entry point.** Add the new
  modes as `representation` values (`envelope`, `pipe`, `rings`, `contact_sheet`,
  `affinity_spheres`, `scaffold`, `wire_contour`, `heatmap`) alongside the debug
  ones, rather than new public functions. Callers stay stable.
- **D2 — add a per-family default resolver.** Introduce `representation='auto'`
  (and make it the default over time) that maps each component's `family` to its
  primary representation via a `_DEFAULT_REPRESENTATION_BY_FAMILY` dict, resolved
  *per component* inside the selection loop (a void and a channel in the same call
  then render differently). Explicit `representation=` still overrides for all.
- **D3 — pure geometry derivations live on the DFND side, viewer-free.** The
  centerline ordering, per-station radius, gate-cap triangulation, and ring
  sampling depend only on DFND data, not on the viewer. Put them in a stable
  `topomt/dfnd/geometry_viewer.py` (promoted from `experimental`) so they are
  unit-testable without a `View`. The render layer only maps their output to
  `add_*` calls.
- **D4 — palette as data.** Replace `_TYPE_PALETTE` with the fixed Okabe–Ito
  table from [component_visualization.md §11](component_visualization.md) in a
  small module next to `families.py` (single source of truth), including the
  interface body colours and the reserved `#F0E442` mouth accent.
- **D5 — module size.** `_components.py` is already large; as the per-family
  builders land, split it into `render/_components/` with one module per
  family-primitive (`_tube.py`, `_caps.py`, `_contact_sheet.py`, …) re-exported
  from the package, mirroring the earlier `render.py` → `render/` split.
- **D6 — split general vs DFND-specific across the two packages.** Apply the rule
  from [what_should_move_to_molsysmt.md](../what_should_move_to_molsysmt.md): a
  reusable geometry/style/UX primitive that *any* molecular system would want
  belongs **upstream in `molsysviewer`** (keeping it complete and versatile);
  only the logic that *derives geometry/scalars from DFND semantics* stays in
  `molsysviewer_topomt`. This already holds — `add_channel_tube` and the
  `pharmacophore` shape live in `molsysviewer`; topomt only feeds them. New
  generic primitives this plan needs should first be proposed in
  MolSysViewer's
  `devguide/pending_proposals/topomt_requested_visualization_primitives.md` and
  built there, not hardcoded here.

  | Piece | Lives in | Why |
  |---|---|---|
  | variable-radius tube (`add_channel_tube`), `pharmacophore` shape | molsysviewer (exists) | generic |
  | labels (`annotations.add_label_*`), `color_by`/`color_map`, `set_alpha`, `add_triangle_faces`, `add_links` | molsysviewer (exists) | generic |
  | **ring / stacked-ring shape** (HOLE), accent/bottleneck ring | molsysviewer (**new**) | any pore/channel viz wants it |
  | **focus-with-fade** (dim the representation outside a selection) | molsysviewer (**new**) | generic isolate/focus UX, not DFND |
  | **clipping-plane** primitive | molsysviewer (**new**) | generic sectioning |
  | **per-vertex surface scalar / curvature coloring** | molsysviewer (**new**) | generic surface analysis |
  | **legend** overlay; CVD-safe **palette catalog** (Okabe–Ito) | molsysviewer (**new**) | reusable by any addon |
  | **2D–3D synced plot widget** | molsysviewer (**new**) | generic trajectory-inspection UX |
  | per-family default resolver; family→palette mapping | molsysviewer_topomt | DFND families |
  | channel **centerline** derivation (resident permeable graph + shortest path) | molsysviewer_topomt | DFND graph |
  | **mouth caps** from `mouth_face_clusters`/`R_gate`; ring **sampling** along the centerline | molsysviewer_topomt | DFND records |
  | interface **body-split** from `lining_body_split` | molsysviewer_topomt | DFND records |
  | top-N **visibility** by `volume_solvent_estimate`; affinity **typing** | molsysviewer_topomt | DFND metrics |
  | `show_dfnd_components` dispatch | molsysviewer_topomt | DFND entry point |

  The recurring shape: **`molsysviewer` renders given geometry/scalars;
  `molsysviewer_topomt` derives that geometry/scalars from DFND semantics.** When
  a phase below needs a "new" molsysviewer primitive, that upstream work is a
  prerequisite — track it in the proposal doc so `molsysviewer` grows with the
  ecosystem instead of topomt accreting one-off viewer code.

## 3. Phase 0 — shared infrastructure (no new geometry)

Smallest first; everything later depends on it.

- **Okabe–Ito palette module** (D4): constants + `color_for(family)` /
  `interface_body_colors(n)` / `MOUTH_ACCENT`. Swap `_TYPE_PALETTE` to import it.
- **Per-family default resolver** (D2): `_DEFAULT_REPRESENTATION_BY_FAMILY`
  (`void→envelope`, `pocket→envelope`, `channel→pipe`, `interface axis→compose`,
  `non-resident/percolating→hidden/diagnostic`); a `_resolve_representation(comp,
  requested)` used in the loop; accept `representation='auto'`.
- **Tests**: palette returns the fixed hexes; resolver picks the right mode per
  family; `auto` on a mixed system yields per-component modes.

## 4. Phase 1 — mouth/gate caps + per-family `envelope`

Makes pocket/void/channel distinguishable using mostly existing primitives.

- **Geometry (D3)**: `mouth_caps(component, raw)` → list of `{cap_faces (vertex
  triangles), gate_center, R_gate}` from `mouth_face_clusters`. The cap is the
  triangulated mouth face cluster; the ring is a circle of radius `R_gate` at the
  gate center, normal along the mouth axis.
- **Render**: `envelope` = blob (`add_pocket_blob`) + for each mouth a translucent
  cap (`add_triangle_faces`) and an accent ring (`add_links` circle) in
  `MOUTH_ACCENT`. Void → blob only (0 mouths); pocket → blob + 1 cap.
- **Tests**: pocket emits exactly one cap layer, void none; cap colour = accent;
  ring radius matches `R_gate`.

## 5. Phase 2 — channel `pipe` (highest value)

- **Centerline (D3)**: `channel_centerline(component, raw)`:
  1. build `g = _resident_permeable_graph(raw, set(resident_node_indices))`
     (promote from `experimental`);
  2. endpoints = the resident tetrahedra adjacent to each of the two mouths
     (owners of the mouth-cluster faces);
  3. `path = nx.shortest_path(g, a, b)` (or weighted by inter-center distance);
  4. `centers = [tetra center for t in path]`,
     `radii = [R_residence(t) for t in path]` (or local `R_gate` at the gates).
- **Render**: `add_channel_tube(centers, radii, color_by='clearance',
  color_map=…)`; **bottleneck ring** at the minimum-radius station / lowest
  `R_gate` mouth, drawn in a bright accent.
- **>2 mouths**: pick the two mouths with the largest `area_geometric` for the
  primary path; expose the rest as secondary branches later (document the policy,
  do not silently drop).
- **Degenerate**: no path / single resident node → fall back to `cloud` and flag.
- **Tests**: a synthetic two-mouth channel (`tube_channel_clean`) yields one
  `add_channel_tube` with ≥2 centers and radii bounded by `R_residence`; the
  bottleneck station is the global radius minimum.

## 6. Phase 3 — interface `contact_sheet`

- **Geometry**: from `lining_body_split` / `lining_bodies`, partition
  `atom_indices` per body.
- **Render**: one `add_pocket_surface` per body subset, coloured from
  `interface_body_colors(n)`; bicolor for two banks, N colours for
  `three_blocks_interface` / `three_body_junction`. Compose over the family
  primitive (the pocket/channel still renders; the lining is the body-split
  overlay).
- **Tests**: a two-block interface emits two surface layers in the two body
  colours; a three-body junction emits three.

## 7. Phase 4 — `rings` (HOLE profile) + scalar→gradient

- **Geometry**: sample stations along the Phase-2 centerline; at each, a circle
  perpendicular to the local tangent with radius = local clearance.
- **Render**: ring lines (`add_links`) coloured by the HOLE thresholds (green
  `R>1.15 Å`, amber constriction, red `R<1.15 Å`). Generalize the `color_by`
  plumbing so any per-station/per-node scalar (gate radius, depth, persistence)
  maps to colour/radius across families.
- **Tests**: ring colours follow the thresholds on a tube with a known
  constriction.

## 8. Phase 5 — affinity spheres, labels/legend, void carving

- **Void opacity carving**: `selections.add_selection` of atoms *outside* the
  component geometry (its `atom_indices` + adaptive margin or bbox + padding, not
  a fixed 10 Å) + `layers.set_alpha(0.1)`. Pure viewer; no core work.
- **Labels/legend**: `annotations.add_label_*` with `component_id`, `family`,
  `n_mouths`, a metric (`volume_solvent_estimate`, `R_gate_min`); a static family
  legend.
- **Affinity spheres** (`affinity_spheres`): colour residence spheres by lining
  environment. Needs a chemistry-typing input; ship a stub typing first
  (hydrophobic/polar/charged from element/residue) and refine later.
- **Default visibility by relevance**: render top-N by `volume_solvent_estimate`
  solid, rest as toggleable layers; demote non-resident/percolating.

## 9. Phase 6 — blocked or larger (dynamic, pharmacophore, convexity)

These are not pure rendering tasks; they wait on DFND core or new viewer support:

- **Dynamic axis** — persistence/identity/pulsation, streamlines, the 2D–3D
  synced widget, and merge/split transition cueing (colour blend). **Blocked on**
  the core emitting cross-frame component identity and, for transition cueing,
  look-ahead event detection ([dynamic_topology.md](dynamic_topology.md)).
- **Pharmacophoric interaction-site map** — `pharmacophore.add_pharmacophore_features`;
  needs interaction typing ([4D_and_pharmacophores.md](4D_and_pharmacophores.md)).
- **Convexity heatmap** — needs a per-vertex surface-curvature-projection
  primitive not yet in the viewer; the dry-core **scaffold** (`scaffold`,
  `add_links` cylinders) *is* doable here from the dry network.
- **Triangulation stability** — consume a numerically stable triangulation
  ([numerical_policy.md](numerical_policy.md)) and add render-time **sliver
  filtering**; do **not** inject coordinate jitter.

## 10. Testing strategy

- **Geometry helpers (D3) unit-tested without a viewer** — `channel_centerline`,
  `mouth_caps`, ring sampling on the synthetic catalog (`tube_channel_clean`,
  `two_blocks_interface*`, `nested_spheres`), asserting on coordinates/radii.
- **Render branches via `DummyView`** — the existing pattern (`view.messages`
  capturing `op` + `options`): assert the right `add_*` op, layer tags, colours,
  and per-family `auto` dispatch. Headless, fast, distributable (`-n 12`, the
  12-core cap).
- **Regression anchors** — extend `tests/test_dfnd_wet_dry_adjacency.py` and the
  addon tests; tie each phase to a catalog fixture with a known verdict.

## 11. Open design decisions

1. **`representation='auto'` as the eventual default?** — yes long-term, but flip
   the default only after Phases 1–3 land so existing callers do not change
   behaviour mid-stream.
2. **Where the geometry module lives** — `topomt/dfnd/geometry_viewer.py`
   (promoted from `experimental`) vs a render-local `_geometry.py`. Recommend the
   DFND side so non-viewer consumers (exporters, tests) can reuse it.
3. **>2-mouth channel policy** — primary path between the two widest mouths now,
   branches later; needs sign-off so the rendering is not seen as dropping mouths.
4. **Ring primitive** — reuse `add_links` circles vs request a dedicated ring
   shape upstream in `molsysviewer`.
5. **Affinity typing source** — stub from element/residue vs depend on an external
   pharmacophore typing.

## 12. Build order (summary)

| Phase | Deliverable | New `representation` | Status |
|---|---|---|---|
| 0 | palette + per-family resolver | `auto` | ✅ done |
| 1 | mouth caps + envelope | `envelope` | ✅ done (blob + gate ring + cap) |
| 2 | channel tube + bottleneck | `pipe` | ✅ done (centerline + real bottleneck ring) |
| 3 | interface body-split | `contact_sheet` | ✅ done |
| 4 | HOLE rings + scalar gradient | `rings` | ✅ done |
| 5 | carving, labels, affinity, visibility | `affinity_spheres`, `carve_voids`, `show_dfnd_labels`, `top_n` | ✅ done (legend pending, upstream) |
| 6 | dry-core scaffold | `scaffold` | ✅ done |
| 6 | convexity heatmap | `heatmap` | ⏳ needs curvature-coloring primitive (upstream) |
| 6 | pharmacophore map | — | ⏳ trackable now (`pharmacophore` shape + `physchem`) |
| 6 | dynamic topology | — | ⛔ blocked on DFND core (cross-frame identity) |

Upstream primitives (molsysviewer): `add_rings` ✅, `focus_with_fade` ✅ (both
pushed); `legend`, `curvature coloring`, `clipping-plane`, `2D–3D widget` ⏳.

## 13. Cross-references

- Design (the *what*): [component_visualization.md](component_visualization.md).
- Family model: [object_model.md](object_model.md), `topomt/dfnd/families.py`.
- Interface localization (betweenness core / rafts):
  `topomt/dfnd/experimental.py`.
- Numerical / triangulation policy: [numerical_policy.md](numerical_policy.md).
- Dynamic / pharmacophores: [dynamic_topology.md](dynamic_topology.md),
  [4D_and_pharmacophores.md](4D_and_pharmacophores.md).
- Where general vs specific code belongs:
  [../what_should_move_to_molsysmt.md](../what_should_move_to_molsysmt.md).
  The upstream primitives in §2 D6 are logged in MolSysViewer's own
  `devguide/pending_proposals/topomt_requested_visualization_primitives.md`.
- Current renderer: `molsysviewer_topomt/render/_components.py`.
