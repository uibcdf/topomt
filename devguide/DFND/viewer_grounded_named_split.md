# Viewer grounded/named split — design (the viewer mirrors kernel/catalog)

Status: **design / proposal** (2026-06-24). Not yet implemented — this is the
artifact to review before touching viewer code. Authoritative companions:
[`taxonomy_architecture_decision.md`](taxonomy_architecture_decision.md) (the
kernel/catalog rule), [`feature_catalog.md`](feature_catalog.md) (the feature
sheet), [`component_visualization.md`](component_visualization.md) (the existing
render surface this reorganizes).

## 1. The principle

The kernel/catalog decision split DFND into **grounded data** (the kernel: only
measured/topological facts) and **names** (the catalog/layer-0: every
classification name). The viewer must mirror that exact boundary:

- **Component renderer = a library of grounded primitives.** It renders a DFND
  *component*'s geometry by grounded property only (topology, boundary taxonomy,
  clearance, centerline, depth). **No feature names** — no `pocket`, `channel`,
  `groove`, `interface` in the renderer.
- **Feature renderer = named features that compose primitives.** A *feature*
  (catalog: `void`/`pocket`/`open_concavity`/`groove`/`channel`/`interface`/…)
  picks a default composition of grounded primitives, with per-feature styles,
  labels, and colours. This is the **only** layer that knows names.

This is the same drift we fixed in the kernel (`family`-in-kernel), now on the
viewer side: named representation modes had accreted inside the grounded renderer.

## 2. The proof (named modes already reduce to grounded primitives)

Every "named" representation mode in `render/_components.py` already *is* a
grounded primitive — the names are redundant feature-intent labels:

| Named mode | What it actually is (grounded) |
| --- | --- |
| `groove_ribbon` | a literal alias of `pipe` + ribbon style (`_CHANNEL_REPRESENTATION_ALIASES`) |
| `groove_floor` | "permeable component faces" → **is** `permeable_faces` |
| `groove_walls` | lining atoms as a surface → **is** `lining_surface` |
| `groove_width_profile` | HOLE-style width rings along the centerline |
| `groove_depth_profile` | residence envelope coloured by depth → **is** `depth_map` |
| `channel_tube/solid/lumen/tunnel/profile/ribbon/blob` | a tube along the centerline (styles of one primitive) |
| `interface_ribbon` | a flattened tube through face centroids → a `ribbon` over a face-path |
| `interface_lining_surface` / `interface_surface` | lining split by body → `lining_surface` / `contact_sheet` |
| `pocket_cutaway` / `interface_cutaway` | a section plane (the latter with an interface normal) → `cutaway` |
| `pocket_depth_map` | → `depth_map` |

The geometry is grounded; `groove`/`channel`/`interface`/`pocket` is the
*classification* that selects it. Strip the names down, lift the selection up.

## 3. B1 — the grounded primitive library (component renderer, name-free)

The ~50 current modes collapse to this inventory. The **collapse table** (what
disappears as a duplicate/alias):

| Grounded primitive | Absorbs (named modes that disappear) |
| --- | --- |
| `tube` | channel_tube/solid/profile/lumen/tunnel/blob/wire_blob, pipe |
| `ribbon` | channel_ribbon, groove_ribbon (≡ pipe+ribbon), interface_ribbon |
| `lining_surface` | groove_walls, interface_lining_surface, interface_surface |
| `permeable_faces` | groove_floor (≡ permeable component faces) |
| `depth_map` | groove_depth_profile, pocket_depth_map |
| `width_profile` | groove_width_profile (HOLE rings) |
| `contact_sheet` | interface lining split by dry bank |
| `faces` (by taxonomy) | interface_faces/contact_faces, mouth_faces, coast_faces, permeable/impermeable_faces, semantic_faces, mouth_stubs |
| `links` | interface_links |
| `cutaway` | pocket_cutaway, interface_cutaway (= cutaway + interface_normal) |
| `rings` | rings, mouth_rings, bottleneck_rings |
| volumetric | tetrahedra, cloud, envelope, blob, surface, wire_contour, scalar_isosurface, shape_ellipsoids, clearance_map/wire |
| dry side | dry_faces (dry_interface/blocked), dry_depth_map, dry_shell, dry_cage, scaffold |
| network | graph |

The 7 `channel_*` and the `groove_*` variants become **style parameters** of a
primitive (`tube(style=...)`, `ribbon(style=...)`), not separate modes. The
boundary-face primitives key on the **grounded boundary taxonomy** (mouth / coast
/ constriction / wall — all anatomically grounded, not classification names; see
`taxonomy_architecture_decision.md` §4). `representation='auto'` already keys on
the grounded `component.signature` bucket (done — `refactor(viewer)` `f59f168`).

## 4. B2 — the feature → primitive composition map (named layer)

The single "with names" table; it lives in the feature layer:

| Feature (catalog) | default | `style=` → primitives |
| --- | --- | --- |
| `void` | envelope | blob, surface, depth_map |
| `pocket` | envelope | cutaway, blob, depth_map |
| `open_concavity` (generic) | envelope | — |
| `groove` | ribbon | floor (=permeable_faces), walls (=lining_surface), width_profile, depth_profile (=depth_map) |
| `dish` | envelope | depth_map |
| `funnel` | envelope + rings | width_profile (taper) |
| `cleft` | cutaway | walls (=lining_surface), depth_map (V-wedge between flanks) |
| `channel` | tube | lumen/tunnel/solid/profile (tube styles), width_profile |
| `branched_channel` | tube | (branch-aware) |
| `interface` | contact_sheet | links, ribbon, cutaway(interface_normal), faces |
| `mouth` (boundary 1D) | mouth_rings | mouth_faces |
| `neck` / constriction | bottleneck_rings | — |
| convex candidates `convexity`/`ridge`/`spike` | peak_patches / ridge_lines / spikes | — (diagnostic, see §6) |
| motif `chamber` / `throat` | envelope(sub) / bottleneck_rings | — |

### 4.1 `open_concavity` leaves (the refinement targets)

`open_concavity` (1 mouth, occlusion ≤ 1) refines into morphological leaves, each
held generic until its quantitative discriminator lands (`feature_catalog.md` §
recipe; register in `output_status` as `provisional`):

| Leaf | Distinct morphology | Grounded discriminator (pending) |
| --- | --- | --- |
| `groove` | elongated, single axis, U-section furrow | elongation + axis |
| `cleft` | the gap **between two lobes**; two flanking convexities; deep V/wedge section | depth + two flanking dry banks / V-section asymmetry |
| `dish` | shallow, round | roundness + low depth |
| `funnel` | tapering aperture → interior | aperture/interior taper ratio |

`cleft` is its own leaf (not folded into `groove`): the discriminating physics is
*flanked-by-two-lobes + V-wedge*, orthogonal to groove's *elongation+axis*.

## 5. The public API

```python
# the 90% case: dispatch by classification['name'], each type's default style
show_features(view, topography, *, feature_types=None, styles=None)
#   styles={'groove': 'walls', 'channel': 'tube'}  -> optional per-type override

# the expert case: one feature type with its full, validated style vocabulary
show_groove(view, topography,    *, style='ribbon')   # {ribbon, floor, walls, width_profile, depth_profile}
show_channel(view, topography,   *, style='tube')     # {tube, lumen, tunnel, solid, profile, blob}
show_interface(view, topography, *, style='contact_sheet')  # {contact_sheet, links, ribbon, cutaway}
show_pocket(view, topography,    *, style='envelope') # {envelope, cutaway, blob}
show_void(view, topography,      *, style='envelope')
# ... open_concavity leaves: show_cleft / show_dish / show_funnel when promoted
```

- `show_features` = convenience + dispatch. The styles are **not lost**: they
  become each feature's natural `style=` vocabulary (with per-type validation) and
  the `styles=` override of the dispatcher. Thin `show_<feature>` wrappers call
  `show_features` filtered to one type.
- All of them delegate to the **grounded primitive library** (§3). The
  feature→composition map (§4) is the only table with names.
- **Names**: `show_dfnd_*` is reserved for the grounded primitives (component
  layer); `show_<feature>` / `show_features` for the named layer.
- **Legend / labels** move to the feature layer (they show names):
  `show_feature_legend`, `show_feature_labels`.

## 6. Convex side = diagnostic, not promoted

The convex/boundary/point taxonomy already lives in `feature_catalog.md`
(`generic_convexity` → protrusion/dome/spine/knob/bulge/ridge_cap/buttress/
pinnacle; `buried_core`; `ridge` under **boundary**; `generic_point`), and
`dry_network_and_convexity.md` keeps it as **candidate motifs / diagnostics, not
final features**, until scoring/geometry/stability rules exist — matching our "do
not promote a shape-type speculatively" rule. Consequences for the viewer:

- The convex renders are a **diagnostic layer**, named to the catalog vocabulary,
  *not* `show_features` dispatch targets (there are no promoted convex features to
  dispatch to yet).
- Mapping: `show_dfnd_convexity` = the convexity **field/substrate** (not a
  feature); `peak_patches` → `generic_convexity` relief (dome/knob/bulge/
  protrusion/pinnacle); `ridge_lines` → `ridge` (a **boundary** feature, the
  convex crest *between* concavities); `spikes` → `pinnacle`/`protrusion`
  (convexity) or `apex`/`ridge_tip` (point 0D).
- They become `show_features` targets later, when convex promotion is built.

## 7. Chemistry overlay = separate layer

`show_dfnd_pharmacophore` and `affinity_spheres` are a **physicochemical /
druggability overlay**, orthogonal to topology — not feature renders. They move to
a separate chemistry-overlay surface (`show_pharmacophore`, `show_affinity`),
applicable on top of any feature.

## 8. What was checked for rescue (and where it went)

Reviewed the superseded `feature_definitions.md` secondary axes:

- **Concavity morphology**: `groove`✓ `tunnel`✓ `pore`✓ `multi_chamber`/`branched`✓
  (now channel leaves / chamber motifs). `cleft` — **rescued** as its own
  `open_concavity` leaf (§4.1). `shallow_depression` ≈ `dish`.
- **Dynamics** (`cryptic`/`transient`/`persistent`/`gated`/`breathing`) → the
  **dynamic identity layer** (lineage/tracks), outside the static catalog by the
  taxonomy decision. (`cryptic` already appears as a `pocket` leaf under dynamics.)
- **Function** (`ligand_binding`/`catalytic`) → **out**: function ≠ shape, not a
  topological feature.

The convex vocabulary was **not** lost in the supersede — the new catalog already
absorbed it (§6).

## 9. Migration plan (phased; pre-release, so renaming is free)

1. **Grounded primitive library** — 🔶 the clean collapses are done (groove_walls→
   lining_surface, groove_width_profile→width_profile, {pocket,groove}_depth→depth_map,
   channel_*→tube, interface_links→links, interface_faces→coast (kernel) +
   shore_faces/beach_faces). Remaining: groove_floor/interface_ribbon/cutaways are
   feature-STYLED (not pure primitives) — they live as `show_features` styles (2).
2. **Feature renderer** — ✅ `show_features` (dispatch by `feature_type` → default
   grounded representation, `styles=` for a type's vocabulary); the payload carries
   `classification`. Optional sugar: per-feature `show_<feature>` wrappers.
3. **Legend/labels** → feature layer; **chemistry overlay** → separate (§7) — ⏳.
4. **Convex diagnostics** — rename to catalog vocabulary (§6); keep diagnostic — ⏳.
5. **`open_concavity` leaves** — 🔶 `groove` landed (elongation metric + provisional
   threshold, `output_status`); `funnel` needs a robust taper metric (the naive
   depth-profile is dominated by corner artifacts — a cylinder reads as tapered);
   `cleft`/`dish` ⏳.

## 10. Open items

- `tube` styles: collapse the 7 `channel_*` to `tube(style=…)` (recommended).
- `width_profile` vs `depth_map`: two distinct primitives (width-along-path vs
  depth-field), confirmed.
- Exact public names of the chemistry-overlay and convex-diagnostic functions.
- Whether `show_features` should also accept grounded buckets (it inherits the
  back-compat shim from the component renderer).
