# DFND Feature Catalog — the sheet (components → features, by shape-type)

The authoritative, at-a-glance sheet: every public **feature**, organized by
**shape-type**, with its **generic** placeholder, its **refined leaves**, its
direct **correspondence to a DFND component** (the grounded signature), and the
**motifs** (sub-structures). Authoritative target/rule:
[`taxonomy_architecture_decision.md`](taxonomy_architecture_decision.md); ladder
and terminology: [`object_model.md`](object_model.md); formal model:
`castp/ideas_paper_1998/topomt_topological_feature_types_*`.

## The principle (generic → refined leaf)

A **component** (kernel: grounded `(n_mouths, resident, n_wall_faces, …)` +
measurements) is promoted to a **feature** (public). The catalog assigns the
**most specific name it can justify with today's metrics**, defaulting to a
**generic per shape-type** when it cannot yet refine. **Refinement is a
first-class, continuous process**: a feature held as a generic (`open_concavity`)
becomes a leaf (`groove`) when the quantitative metric that distinguishes it
(elongation/axis) lands -- or stays generic. Generics are a small backbone
(one-ish per shape-type), not a zoo; the leaves hang off them. Even today's
"leaf" names (`void`/`pocket`/`channel`) are coarse levels, refinable further with
chemistry/dynamics. Status: ✅ implemented · 🔶 partial · ⏳ future.

## Concavity (the negative space: wet resident components)

Component correspondence: a **wet resident component**, by `(n_mouths, occlusion)`.

| Component signature | Generic | Refined leaves (refining metric) | Status |
| --- | --- | --- | --- |
| `0 mouths, resident` | **`void`** *(a.k.a. `enclosed_cavity`)* | sealed-water / gas-pocket / packing-defect *(chemistry, dynamics)* | ✅ generic / ⏳ leaves |
| `1 mouth, resident, occlusion > 1` | **`pocket`** *(occluded)* | buried / surface / cryptic *(buriedness, dynamics)* | ✅ generic / ⏳ leaves |
| `1 mouth, resident, occlusion ≤ 1` | **`open_concavity`** *(open)* | **`groove`** (elongation+axis) 🔶 / `dish` (roundness) ⏳ / `funnel` (taper) ⏳ | ✅ generic / 🔶 `groove` provisional (elongation threshold, S12) |
| `≥2 mouths, resident` | **`channel`** | tunnel / pore / branched (centerline branching) | ✅ generic / ⏳ leaves |

Non-resident shadow (same signature, residence lost at a larger probe) -- generic
**`non_resident_contact`**: `(0,¬res)` = `degenerate_subprobe`, `(1,¬res)` = a
non-resident contact/dent (was `surface_concavity`), `(≥2,¬res)` = empirically
non-occurring (retired). These are compositions, not separate families.

## Solid side: convexity + buried cores (the dry components) ⏳

Component correspondence: the **dry side** (dry banks). It carries two generics: a
surface **convexity** (relief bulging out) and an internal **buried core** (solid,
*not* convex, not a cavity). Neither is promoted to a feature yet.

| Component | Generic | Refined leaves | Status |
| --- | --- | --- | --- |
| dry bank, surface relief | **`generic_convexity`** | protrusion / dome / spine / knob / bulge / ridge_cap / buttress / pinnacle | ⏳ future (no promotion yet) |
| dry bank, fully internal | **`buried_core`** | (packing core / hydrophobic core) | ⏳ future |

## Mixed (two-body lining) 🔶

Component correspondence: a **wet component with `n_dry_contacts ≥ 2`** (an
interface), or a dry **septum** bank between two cavities.

| Component | Generic | Refined leaves | Status |
| --- | --- | --- | --- |
| wet, `n_dry_contacts ≥ 2` | **`interface`** *(generic_mixed)* | patch / joint / saddle / trench | 🔶 detected (n_dry_contacts) / ⏳ promotion |

## Boundary (1D, children of a feature)

Component correspondence: a **face cluster** on a component's boundary.

| Component element | Generic | Refined leaves | Status |
| --- | --- | --- | --- |
| permeable cluster → OCEAN | **`mouth`** | — | ✅ |
| non-permeable wet↔wet constriction | **`neck`** *(constriction / closed throat)* | — | 🔶 measured (n_septa) / ⏳ feature |
| coast / exterior wall cluster | **`generic_boundary`** | base_rim / lip / furrow / seam / isthmus / edge_loop / branch_line / hinge_line / ridge | ⏳ |

`ridge` is a 1D crest line (a convex boundary *between* concavities) -- it lives
here (boundary), not in the convexity surface patches; `spine`/`ridge_cap` (2D
relief) stay under convexity.

## Point (0D) ⏳

Component correspondence: a distinguished **node/atom** of a component.

| Component element | Generic | Refined leaves | Status |
| --- | --- | --- | --- |
| residence/depth extremum | **`generic_point`** *(Feature0D)* | depth-point / pit / apex / summit / bifurcation / saddle_point / ridge_tip | ⏳ (depth_region motif exists) |

## Neutral

`percolating` (resident, `n_connected_walls == 0`): a fully porous/exposed region,
not a concavity. ✅

## Motifs (sub-structure of one component -- not standalone features)

A **motif** is a named sub-structure of a component (`object_model.md` §3). This is
where "features inside features" live (a sub-pocket is a chamber motif, the L1.3
resolution).

| Motif | What | Status |
| --- | --- | --- |
| `external_mouth` → `Mouth` | the mouth's atoms/geometry (promotes to a 1D boundary feature) | ✅ |
| `chamber` | a sub-cavity (merge-tree basin) -- a feature-inside-a-feature | 🔶 provisional |
| `throat` / `bottleneck` | an internal constriction (merge-tree saddle); the closed form is a `neck` boundary | 🔶 provisional |
| `depth_region` | a topological-depth layer | ✅ |

**Chamber roles** (refinements of a `chamber` motif by its position in the
hierarchy -- the relocated `vestibule`/`ampulla`/`alcove` vocabulary): `vestibule`
= a shallow antechamber near the mouth before a deeper constriction; `ampulla` =
a dilated bulb chamber behind a neck; `alcove` = a side recess off the main path.
⏳ future (ride the chamber hierarchy + depth; see component_motifs.md / Q25).

## How to extend (the recipe)

To add a refined leaf: (1) add the **quantitative metric** that distinguishes it
(e.g. elongation/axis for `groove`); (2) register the leaf name in
`output_status` (status `provisional` until validated); (3) refine in the catalog
`classify` from the generic. To add a new shape-type's generic: do it **when DFND
promotes components in that shape-type** (concavity now; convexity/mixed when their
promotion is built), not speculatively.
