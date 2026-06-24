# DFND Taxonomy & Kernel/Catalog Architecture — Decision Record

Status: **decided (design)**, implementation pending. Supersedes the implicit
"families as kernel types" model. Operational counterparts:
[`feature_definitions.md`](feature_definitions.md),
[`metrics_contract.md`](metrics_contract.md),
[`component_motifs.md`](component_motifs.md),
[`known_limitations.md`](known_limitations.md).

This records a design conversation that re-grounded how DFND names and
characterizes wet components. The driving principle: **be consistent, clear and
honest ourselves** rather than inherit the pocket community's loaded, inconsistent
vocabulary.

## 1. The core rule

Everything DFND produces sorts into exactly one of three kinds:

1. **Identity** — what makes a component *the same component* across queries and
   trajectory frames. It is the **atom support** (`support_key`), already
   family-blind (`component_key = (result_key, side, support_key)`; lineage matches
   by support/Jaccard). Family is **not** part of identity.
2. **Observable (grounded measurement)** — what the kernel measures and stores.
   Per-face and per-tet raw data only (§3). Continuous or count-valued; never a
   thresholded name.
3. **Name (catalog predicate)** — every human/community label is a **predicate or
   threshold over observables**, computed in the public catalog (layer 0), never
   stored in the kernel.

The test for "where does X belong?": *Is X a name put on a threshold over a
measurement?* → catalog. *Is X a measurement?* → kernel observable. *Does X define
the component's role in the flow graph (mouths + residence)?* → it is the primary
classification, still **derived** from observables, and it lives in the catalog.

Consequence: **`family` (void/pocket/channel), `percolating`/`exposed`,
`interface`, `open`/`occluded`, `shallow`/`buried` all leave the kernel.** The
kernel has **no classification logic and no stored labels** — only data + helpers.

## 2. Why (robustness)

Identity is already atom-based, so a component that seals (1 mouth → 0 mouths in a
trajectory) is *the same track*; only its derived classification changes. The old
model bucketed by `family` and instantiated `Pocket`/`Void`/`Channel` classes, so
the same physical cavity appeared to *die as a pocket and be born as a void* —
contradicting the continuous lineage track. Separating **stable identity (atoms)**
from **derived classification (per query)** turns label flicker near a threshold
from tracking-corruption into an **observable signal** (gate breathing, cryptic
pockets). See §9 gap-list item on marginality.

## 3. Kernel contract — grounded data only

The kernel emits, per **wet component**:

- **Identity:** `support_key` (atoms).
- **Per boundary face:** `{ permeable?, other_side ∈ {ocean, dry, wet} (+ which
  component), R_gate, atoms }`.
- **Per tetrahedron / node:** `R_residence`, residence margin (`R_residence −
  probe`), gate margins, etc.
- **Per-feature geometry/metrics** already defined elsewhere: topological volume,
  precise solvent volume, hierarchy (merge-tree throats/chambers), centerline, …

No `family`, no signature label (`YK` was considered and **rejected** — it is just
`f(resident, n_mouths)`, derivable, so storing it is denormalization), no
`percolating`/`interface` flags, no `classify`.

Even the **topological signature `(n_mouths, resident)` is derived**, not stored:
`n_mouths` is a connected-cluster count over permeable boundary faces.

## 4. Derived helpers (computed from §3, not stored)

- `n_mouths` = connected clusters of permeable boundary faces.
- `n_connected_walls` = connected clusters of **all** non-permeable boundary faces
  (one "wall" is a connected physical structure; **cluster first, then
  characterize** — do not pre-split by other-side type). `n_connected_walls == 0`
  ⟺ percolating/exposed.
- **Per-wall characterization** (after clustering): its composition (how much
  coast/exterior/septum), which dry bodies it touches.
- `n_dry_contacts` = distinct dry components across the walls (= `len(lining_bodies)`).
- `n_septa` = walls whose other side is another **wet** component (§6).
- **Morphometrics:** `occlusion = interior_radius / mouth_radius`,
  `occlusion_gap`/`enclosable`, `buriedness`, per-mouth occlusion (§ channels),
  `deepest_chamber` (supporting, lattice-sensitive).

## 5. The catalog (public layer 0)

`classify()` is the **single source of truth** for naming — one deterministic
partition over the derived signature + morphometrics:

```
not resident         → degenerate_subprobe (0) / surface_concavity (1) / nonresident_passage (≥2)
n_connected_walls==0 → percolating
n_mouths == 0        → void
n_mouths == 1        → pocket if occlusion>1 else groove
n_mouths == 2        → channel
n_mouths ≥ 3         → junction (info the old "channel/branched_channel" collapsed)
```

Orthogonal **modifiers** (tags, not a partition): `interface` (`n_dry_contacts ≥
2`), `buried` (`buriedness ≥ τ`), per-mouth constriction, marginal (§9). Community
nouns are **derived views**; thresholds (e.g. `occlusion = 1`, `τ_depth`) are a
**tunable layer-0 policy**, not kernel-fixed.

User queries are unchanged in spirit — "how many pockets?" = `count(classify(c) ==
'pocket')`; the family buckets `result['wet']['pockets']` become **derived views**.

`feature_type` on the public feature objects **is** this classification and **is**
the stable contract the viewer consumes (§8).

## 6. Face & constriction taxonomy

A constriction/boundary face is `(other side) × (does the probe pass?)`:

| | probe passes (permeable) | probe blocked (non-permeable) |
| --- | --- | --- |
| other side = OCEAN | **mouth** (opening to exterior) | **exterior wall** |
| other side = interior region | **throat / angostura** (passable narrowing inside one cavity) | **septum** (narrowing so tight it splits two cavities) |

- **septum ≠ mouth.** A septum is a **throat in its closed state** — the same
  physical constriction, seen when the probe no longer fits, so it separates two
  cavities. Its `R_gate` is **the probe radius at which the two cavities merge**.
- Vertical pairs are the same face at different probe: a mouth seals into an
  exterior wall; a throat closes into a septum. This unifies the boundary taxonomy
  with the merge-tree throats: throats *inside* a cavity and septa *between*
  cavities are one feature family across the probe threshold.

## 7. Dry side — dual scheme, reserved

Same rule applies symmetrically (identity = atoms; measurements; catalog
predicates; no stored dry-family — `DRY_BANK` → implicit `side=dry`). But the dry
**content is dual**, not a copy: it is walls/dividers/cores, not cavities.

- Dry signature (dual): `n_wet_contacts`, `exterior_exposure` (surface bank vs
  buried core), `n_coast_clusters`, `face_depth`.
- Dry catalog (its own names): `surface_bank`, `buried_core`, `septum`/divider.
- **`interface` is a bilateral relation object** between a wet component and its
  lining banks, characterized from both sides.

Dry is secondary to pocket characterization and **less mature**; full spec is
**deferred** but the symmetric slot is **reserved** so it cannot be bolted on
incoherently.

## 8. Migration & compatibility

- **No two sources of truth, ever.** Migrate by **inversion**: extract `classify()`
  as the single definition and make any legacy `family`/`feature_type` **computed
  from it** (an atomic switch), not assigned in parallel. The inversion also
  **proves the grounded signature is complete** (if `classify()` cannot reproduce a
  family, that family encoded something missing from the observables).
- **Compatibility is a layer-0 responsibility, not the kernel's.** Verified: the
  viewer (`molsysviewer_topomt`) already consumes layer-0 `feature_type` from
  feature objects (`payloads.py`, `panels/pockets.py`), **not** kernel `family`;
  its only kernel coupling is raw geometry (`dfnd.selectors`, `dfnd.centerline`),
  orthogonal to naming. So the kernel refactor is **invisible** to the viewer.
- Morphology evolves in layer 0: **additive first** (`feature_type='pocket'` kept,
  `morphology` added as an attribute, so no silent break of the "pocket" bucket),
  then **coordinated re-typing** (`feature_type='groove'`, narrow "pocket" to
  occluded) at the viewer's pace.
- The **unification of `Pocket`/`Void`/`Channel` into one parameterized feature
  class** (so a sealing component never changes object class) is the layer-0
  coordinated end-step with the collaborator.

## 9. The seven gaps (resolution / debt)

| # | Gap | Resolution / status |
| --- | --- | --- |
| 1 | **Real-system validation** | The empirical gate. Untested on real proteins; all evidence is synthetic. Protocol: 3–5 PDBs with known sites; check detection (DCA≤4Å), spurious junk, morphology sanity, stability. **Deferred until §1–8 are locked, then it is the #1 action.** It is what turns "coherent" into "correct". |
| 2 | **Marginality / confidence** | Emit per-component `mouth_margin`/`residence_margin` (data exists as deltas); `classify()` returns name + `marginal` flag (within slack of a class-flipping boundary). Dual purpose: confidence **and** the dynamic breathing signal. `percolating` is the most fragile (binary) → flag marginal when one wall-face from flipping. |
| 3 | **Aperture for channels (≥2 mouths)** | The global `occlusion = interior/max_mouth` already generalizes as **enclosability** for any mouth count. Add **per-mouth occlusion** (`interior/R_gate(mouth)`) for asymmetric entrance constriction; **beadedness = the merge-tree**, already applies to channels. No new measurement. |
| 4 | **Dry side** | §7. Dual scheme reserved, full spec deferred. |
| 5 | **Exterior walls vs coast** | Corrected: walls = connected clusters of **all** non-permeable faces (cluster first, characterize after); other-side type is a per-face/per-wall attribute, **not** a pre-split. Cluster counts are **derived helpers**, not stored observables. |
| 6 | **Two sources of truth** | §8 inversion. |
| 7 | **Compatibility / viewer** | §8 — articulated through layer 0; viewer already consumes `feature_type`. |

## 10. Open debts (honest)

- **Real-system validation** (gap 1) — the dominant unknown; ~55–60% practical
  confidence until measured.
- **Elongation metric** — "groove" currently means "open dent" (`occlusion ≤ 1`);
  a true elongated furrow needs an aspect-ratio measure DFND does not yet compute.
  `elongated` is a future sub-label.
- **Hierarchy lattice-noise** — `deepest_chamber`/access descriptors are confounded
  by lattice artifacts on gridded synthetics; supporting descriptors, not standalone
  classifiers (component_motifs.md / Q25).
- **Dry-side maturity** (gap 4).
