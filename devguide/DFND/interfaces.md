# DFND Interfaces

Design note recorded on 2026-05-22. It defines what an *interface* is in DFND,
how it relates to the wet concavity families and the dry network, and how to
extract it from what `get_topography` already returns. It is grounded in the
synthetic block systems (`two_blocks`, `three_blocks`, `interface_pocket` in
`topomt/dfnd/synthetic.py`; tests in `tests/test_dfnd_synthetic_benchmarks.py`).

Related: [`feature_definitions.md`](feature_definitions.md) (wet families),
[`dry_network_and_convexity.md`](dry_network_and_convexity.md) (dry side),
[`synthetic_benchmarks.md`](synthetic_benchmarks.md) (the block battery).
An interface is the `Mixed`/2D `Interface` feature of the original topography
taxonomy (`topomt/features/_feature_constants.py`,
[`architecture.md`](../architecture.md): `MixedFeature` = `Wall` / `Separator` /
`LiningRegion` / `Interface`).

## 1. An interface has two coupled halves

An interface between two (or more) bodies is **not** a single object. It is:

- **Dry half — the banks.** Each body contributes a *bank*: a `DryComponent`
  (its probe-excluded interior). An interface has **≥2 dry banks**. The boundary
  of each bank toward the gap is already emitted as a `DryInterface` record
  (`interface_kind = 'dry_permeable_contact'`, with `target_dry_component_id`
  linking the two banks).
- **Wet half — the channelway.** The wet space between the banks. Its defining
  property is **not** its mouth topology but its **lining**: its walls are
  contributed by *different bodies*. It is "neither pocket nor channel" in the
  ordinary sense precisely because its banks belong to distinct bodies.

The interface is the dry banks **and** the wet region between them, together.
This is the wet/dry symmetry of DFND applied to the contact between bodies.

## 2. Interface is an orthogonal axis, not a new wet family

The wet family axis (`void` / `pocket` / `channel` /
`surface_concavity`) counts **mouths to OCEAN**. Whether a region is an interface
is a **separate axis** that counts **how many bodies line it**. They are
independent, so the cross-product is meaningful (consistent with the secondary
axes of [`feature_definitions.md`](feature_definitions.md) §6 — interface is a
descriptor, not a replacement for the primary family):

| | lining = 1 body | lining ≥ 2 bodies |
|---|---|---|
| 0 mouths + residence | void | **interface void** (buried inter-body cavity) |
| 1 mouth | pocket | **interface pocket** |
| ≥2 mouths | channel | **interface channelway** |
| open, no residence | surface_concavity | **bare interface** (open solvent slab between two faces) |

The "space that is neither pocket nor channel" is the bottom-right / open cases:
a wet region whose mouth topology would read as `surface_concavity` (or as open
OCEAN), but whose multi-body lining marks it an interface.

## 3. Operational discriminator

DFND needs **no new substrate family**. The interface is *derived* from records
`get_topography` already returns:

> A wet `component` is an **interface region** when its `atom_indices`
> (its lining) receive a substantial contribution from **≥2 distinct bodies**.

The pieces are all present:
- `component['atom_indices']` — the lining atoms of each wet component;
- `dry['components']` — the dry banks (and their atoms/tetrahedra);
- `dry_interfaces[...]['target_dry_component_id']` — which two banks touch.

A buried interface cavity is a `pocket`/`void` component whose lining spans two
banks; a bare interface (e.g. two flat blocks across an open slab) has no bounded
wet component at all — it is captured purely by the dry banks facing each other.

## 4. The body-definition question (decisive)

"How many bodies" can be defined two ways, and they disagree:

1. **Emergent (dry-component connectivity).** Two bodies are two `DryComponent`s
   *only if a probe-resident (wet) layer threads between them*. This is native to
   DFND but **fuses tightly-packed bodies into one**: the inter-body slab is
   itself dry (sub-probe), so the dry network bridges across it.
2. **Chemical (input labels).** Chain / `molecule` identity from the molecular
   system: always two bodies for a dimer, robust, but not emergent from geometry.

**Measured threshold (synthetic blocks, half = 7 Å, spacing = 3.2 Å, probe
1.4 Å):**

| gap between facing faces | dry components |
|---:|---|
| 0–4 Å | **1** (dry network bridges the gap) |
| ≥ 5 Å | **2** (a wet layer separates the banks) |

So the emergent route works only once the gap admits a resident wet layer
(≈ probe diameter). For tight interfaces (the common protein-protein case) the
banks fuse and emergent bodies vanish — there, **chain labels are required**.

Recommendation: support both. Default to dry-component banks for the native,
label-free story; fall back to / cross-check with chain identity when present.
Crucially, the **multi-body-lining** signal of §3 is robust even when the dry
banks fuse: in `interface_pocket` the two blocks merge into one dry component,
yet the carved cavity's lining still spans both halves and flags the interface.

## 5. What the synthetic systems show

- `two_blocks` (gap 5 Å): **two dry banks** (~601 / 593 tetra) **and** a wet
  pocket in the gap lined ~equally by both bodies (56 left / 61 right atoms) —
  both halves of the interface at once. At gap 2 Å (`two_blocks_fused`) the banks
  fuse to one body: the fusion regime.
- `three_blocks` (gap 5 Å): **three dry banks**, two interfaces.
- `interface_pocket`: a cavity carved at the contact plane appears as a wet
  pocket/void whose lining is shared (≈ 49 left / 51 right) — the protein-protein
  interface cavity. Single-body surface-texture pockets, by contrast, have all
  their lining on one side (e.g. 21/0) and are easily separated.

## 6. Extraction prototype (implemented)

`topomt/dfnd/interfaces.py` post-processes `get_topography` output (it does not
touch the `R_residence` / `R_gate` substrate). Tests:
`tests/test_dfnd_interface_features.py`.

- `body_labels_from_dry_components(topography, n_atoms)` — native route: assign
  each atom to its dry bank (largest component wins shared atoms).
- `classify_interface_components(components, body_labels, ...)` — tag each wet component
  with `n_lining_bodies`, the per-body `lining_body_split`, `minority_fraction`,
  and `is_interface` / `interface_family` (interface_void / interface_pocket /
  interface_channelway / bare_interface).
- `annotate_interfaces(topography, n_atoms, body_labels=None)` — convenience
  wrapper returning only interface components; derives bodies from the dry network
  when `body_labels` is None, or accepts explicit chain-like labels.

Validated on the synthetic battery: the native route flags the wet gap of two
separated blocks (lining ~57/60); a single body yields no interface; a tightly
packed `interface_pocket` is **missed** by the native route (banks fuse) but
recovered with explicit labels as an interface pocket + a buried interface void;
the three-body junction cavity reports three lining bodies — confirming the
section 4 analysis end to end.

## 7. Feature-layer status (updated 2026-06-05)

**Done.** The native (dry-bank) interface classification is now wired into the
promotion path (`api.py::dfnd_to_topography`): every typed wet component carries
`is_interface` / `interface_family` / `lining_bodies` / `lining_body_split`
(`components.py::_attach_interface_labels`), and those flags are copied onto the
public concavity features. `components.wet_interfaces` lists the flagged ones.
The wet↔dry contact is materialized too (the *coast* and per-component *lining*,
see object_model.md §10): `WetComponent.dry_lining`, `DryComponent.wet_lining`,
and `DryComponent.interface_walls` (the dry banks' wall against a wet interface),
which closes the symmetry of §1.

**Still to build.** Ingesting input chain/`molecule` labels as a body source for
the promotion path (today it uses the native dry-bank route, so it inherits the
fusion limit of §4); and realizing the **bare** interface (no wet component) from
the `dry_permeable_contact` faces between two banks (area, normal, `R_gate`).

## 8. Session notes (2026-06-04): mouth signal, localization, catalog gap

Findings from a `two_blocks_interface` walkthrough, recorded so they are not
re-derived:

- **Catalog gap — now closed (see §7).** This was the gap: `dfnd_to_topography`
  used not to call the classification, so the gap region was promoted as a plain
  `Pocket` with no `is_interface` flag and its interface identity was invisible.
  It is now wired in (the orthogonal-axis approach of §2 was kept — the mouth
  family is untouched, the interface descriptor rides alongside it). On
  `two_blocks_interface` the gap component (`WET-1`) comes out
  `is_interface=True`, `interface_family='interface_pocket'`,
  `lining_bodies=['DRY-1','DRY-2']`, and those flags reach the public feature.

- **Mouth signal (sharper, but narrower than lining).** The external link of the
  gap component is itself split across both banks (rim atoms ~18 in DRY-1 / ~19
  in DRY-2). So "a mouth whose rim spans >=2 dry banks" is a clean, localized
  interface signal. It is a *complement*, not a replacement, for the §3 lining
  criterion: lining also catches buried interfaces (no mouth), which the mouth
  signal misses. Good fit for the **bare interface / open slab** row of §2.

- **Why the gap component wraps everything.** In a finite system (no sea level)
  the single wet component spans the whole exterior of both bodies *plus* the
  gap: it is the interface slab (a hub) with ~18 shallow surface rafts hanging
  off it. Removing the slab shatters the rest into those rafts.

- **Localization is only partial (experimental).** `topomt/dfnd/experimental.py`
  (`localize_interface_core` via betweenness; `peel_surface_rafts` via pendant
  peeling) localizes the slab vs the rafts, but neither gives a crisp boundary:
  the slab **grades into the exterior at the gap rim**, so there is no clean
  graph cut. Exploratory only; not wired into `get_topography`.

## 9. Atom/residue ownership (Q17, decided)

How atoms/residues are owned across the four Q17 contexts — `component lining`,
`external_link lining`, `dry wall`, `separator`.

**Membership is overlapping and role-based — the canonical truth.** A component's
`atom_indices` is the union of the vertices of its tetrahedra (`graph.py`).
Because an atom's *star* (its incident tetrahedra) can split across components,
an atom belongs to **every** component its star touches:

- a thin-septum atom lines **two distinct wet components** (two cavities);
- a junction atom belongs to **two dry banks** — this *is* the interface signal
  (`lining_bodies >= 2`, `lining_body_split`);
- a cavity-wall atom is in the **wet lining and the dry wall** at once.

Multi-membership is the norm at boundaries, not the exception, so forcing
exclusive ownership would be unfaithful. The four contexts are **orthogonal
roles/layers** (coast / lining / interface), not competing claims.

**Presentation is context-aware and honest — never a hidden majority collapse:**

| Context | A multi-component atom is treated as |
| --- | --- |
| Hover / inspection | **multi-component**: report every component it belongs to |
| Render of one component | belonging to **that** component (in that view it does) |
| Render of two+ components | a distinct **`shared`** key/marker — never adjudicated to one |
| Counts / areas | **exclusive vs shared** reported separately (e.g. *A: 56 + 5 shared*), not flattened |

`lining_body_split` records the per-body split; honest presentation *keeps* it
rather than collapsing it.

**Forced single-owner is the exception, not the model.** Only when a downstream
consumer genuinely needs a disjoint partition (e.g. a non-overlapping molsysmt
selection for another tool) is each shared atom assigned to one owner, by an
**explicit documented tie-break** (majority of its star, or largest component),
and a `shared` group is still exposed. `body_labels_from_dry_components`
(largest-bank-wins) is exactly such a derived view, for colouring — not the
canonical ownership.
