# DFND Taxonomy & Kernel/Catalog Architecture — Decision Record

Status: **decided (design)**; building-block measurements implemented, the
architectural re-grounding pending (§10). Supersedes the implicit
"families as kernel types" model. Operational counterparts:
[`feature_definitions.md`](feature_definitions.md),
[`metrics_contract.md`](metrics_contract.md),
[`component_motifs.md`](component_motifs.md),
[`known_limitations.md`](known_limitations.md) — these still describe the old
model and are reconciliation debt (§11).

Driving principle: **be consistent, clear and honest ourselves** rather than
inherit the pocket community's loaded, inconsistent vocabulary.

## 1. The core rule

Everything DFND produces sorts into exactly one of three kinds:

1. **Identity** — what makes a component *the same component* across queries and
   trajectory frames. It is the **atom support** (`support_key`), already
   family-blind (`component_key = (result_key, side, support_key)`; lineage matches
   by support/Jaccard). Family is **not** part of identity.
2. **Observable (grounded measurement)** — what the kernel measures and stores:
   per-face and per-tet raw data only (§3). Continuous or count-valued; never a
   thresholded name.
3. **Name (catalog predicate)** — every human/community label is a **predicate or
   threshold over observables**, computed in the public catalog (layer 0, §5),
   never stored in the kernel.

Test for "where does X belong?": *a name put on a threshold over a measurement?*
→ catalog. *a measurement?* → kernel observable. *the component's role in the flow
graph (mouths + residence)?* → the primary classification, still **derived** from
observables, in the catalog.

Consequence: **`family`, `percolating`/`exposed`, `interface`, `open`/`occluded`,
`shallow`/`buried`, `branched` all leave the kernel.** The kernel has **no
classification logic and no stored labels** — only data + helpers.

## 2. Why (robustness)

Identity is atom-based, so a component that seals (1 mouth → 0 mouths in a
trajectory) is *the same track*; only its derived classification changes. The old
model bucketed by `family` and instantiated `Pocket`/`Void`/`Channel` classes, so
the same cavity appeared to *die as a pocket and be born as a void* — contradicting
the continuous lineage track. Separating **stable identity (atoms)** from **derived
classification (per query)** turns label flicker near a threshold from
tracking-corruption into an **observable signal** (gate breathing, cryptic
pockets — §7).

## 3. Kernel contract — grounded data only

The kernel emits, per **wet component**:

- **Identity:** `support_key` (atoms).
- **Per boundary face:** `{ permeable?, other_side ∈ {ocean, dry, wet} (+ which
  component), R_gate, atoms }`.
- **Per tetrahedron / node:** `R_residence`, residence margin (`R_residence −
  probe`), gate margins, etc.
- **Per-feature geometry/metrics** defined elsewhere: topological & precise solvent
  volume, merge-tree hierarchy, centerline/skeleton, …

No `family`, no signature label (`YK` was considered and **rejected** — it is just
`f(resident, n_mouths)`, derivable, so storing it is denormalization), no
`percolating`/`interface` flags, no `classify`. Even the topological signature
`(n_mouths, resident)` is **derived** (a connected-cluster count over faces).

## 4. Derived helpers (computed from §3, not stored)

- `n_mouths` = connected clusters of permeable boundary faces.
- `n_connected_walls` = connected clusters of **all** non-permeable boundary faces.
  **Cluster first, then characterize** — a wall is one connected physical
  structure; do not pre-split by other-side type. `n_connected_walls == 0` ⟺
  percolating/exposed.
- **Per-wall characterization** (after clustering): composition (coast / exterior /
  constriction), which dry bodies it touches.
- `n_dry_contacts` = distinct dry components across the walls (= `len(lining_bodies)`).
- **Constrictions** = walls whose other side is another **wet** component (§6) — a
  closed throat; its `R_gate` is a merge radius (§7).
- **Morphometrics:** `occlusion = interior_radius / mouth_radius` (enclosability,
  any mouth count), `occlusion_gap`/`enclosable`, **per-mouth occlusion**
  (`interior / R_gate(mouth)`), `buriedness`, `deepest_chamber` (supporting,
  lattice-sensitive).
- **Characteristic radii** (§7): `residence_death_radius`, `seal_radius`, merge &
  split radii — probe values at which the classification changes.

## 5. The catalog (public layer 0)

`classify(component, probe)` is the **single source of truth** for naming —
**probe-parameterized** (§7) — and returns **`{name, confidence, marginal}`**: every
name is a threshold over a continuous measurement, so **every name carries a margin**
(confidence is universal, not a special case; §7 ties the margin to the
characteristic radii).

### 5.1 Primary vs modifier — the criterion

An axis is **primary** (noun-determining) if it changes *the kind of thing*; a
**modifier** is an adjective on that noun (an "interface pocket" is still a pocket).

- **Primary** (determine the noun): `n_mouths`, `resident`, `exposed`, and — for
  1-mouth — `occlusion`.
- **Modifier** (adjectives): `interface`, `buried`, `branched`, per-mouth occlusion.

### 5.2 Primary classification

A **total** function of `(resident, n_mouths, exposed[, occlusion])`:

```
NON-resident (no residence → occlusion undefined):
  n_mouths == 0           → degenerate_subprobe (sealed sub-probe cluster, diagnostic)
  n_mouths == 1           → surface contact / dent (the cell formerly surface_concavity)
  n_mouths ≥ 2            → empirically non-occurring (nonresident_passage retired)
RESIDENT:
  n_connected_walls == 0  → percolating
  n_mouths == 0           → void
  n_mouths == 1           → pocket (occlusion>1) | groove (occlusion≤1)
  n_mouths ≥ 2            → channel
```

- **`resident` is a PRIMARY axis, not a modifier** — it changes the noun
  (void↔degenerate, pocket↔contact, channel↔passage). The non-resident side is the
  *compositional* `(n_mouths × ¬resident)` of the same signature (a residence-lost
  shadow, §7), but **not** a set of negation-defined catch-all families. The
  `(≥2 × ¬resident)` cell is empirically infeasible (proven), so
  **`nonresident_passage` is retired** as a curated family; `classify` stays total
  by composition without maintaining a vacuous family.
- **`occlusion` is name-determining only for 1-mouth** (pocket vs groove are
  different *kinds* — an enclosable binding site vs an open surface feature) and a
  **modifier for channels** (an occluded/beaded channel is still a channel). The
  asymmetry is **principled by the criterion**: enclosability crosses a kind-boundary
  where it is the defining property (1-mouth), and is an adjective where through-ness
  dominates (≥2).

### 5.3 Orthogonal modifiers (adjectives; do not change the noun)

`interface` (`n_dry_contacts ≥ 2`), `buried` (`buriedness ≥ τ`), `branched`
(centerline skeleton has branch points — subsumes the old `branched_channel`, now
"channel + branched"; a 2-mouth tube can be branched via a dead-end side branch,
every ≥3-mouth cavity is branched; `junction`/`hub` = optional alias for `n_mouths ≥
3`, a label over the exact `n_mouths` measurement, not a separate type), per-mouth
occlusion.

**Modifiers inherit their input's maturity:** `branched` rides the (experimental)
centerline; `deepest_chamber` is lattice-sensitive; `occlusion`/`buriedness` are
robust. So `classify` confidence is **per-output**, not uniform.

Community nouns are **derived views**; thresholds (`occlusion = 1`, `τ`) are a
**tunable layer-0 policy**, not kernel-fixed. "how many pockets?" =
`count(classify(c, probe).name == 'pocket')`; the family buckets become derived
views. `feature_type` on public feature objects **is** this classification and **is**
the stable contract the viewer consumes (§9).

### 5.4 Generic features and continuous refinement

The catalog assigns the **most specific name it can justify with today's metrics**,
defaulting to a **generic feature per shape-type** when it cannot yet refine to a
leaf. Refinement is **first-class and continuous**: a 1-mouth open concavity is the
generic `open_concavity` (we measure aperture, not shape); when an elongation/axis
metric lands it refines to the leaf `groove` (or `dish`/`funnel`), or stays generic.
The generics are a small backbone -- one-ish per shape-type (concavity, convexity,
mixed, boundary, point) -- created **when DFND promotes components in that
shape-type**, not speculatively. Even today's names (`void`/`pocket`/`channel`) are
coarse levels, refinable further. The authoritative sheet (every feature by
shape-type, its generic, refined leaves + the metric that refines each, the
component correspondence, and the motifs) is
[`feature_catalog.md`](feature_catalog.md); the backbone is recorded in code as
`classify.GENERIC_FEATURE_BY_SHAPE_TYPE`. ('groove' was renamed to the generic
`open_concavity` to stop over-claiming elongation -- the elongation debt, §12.)

## 6. Face & constriction taxonomy

A boundary face is `(other side) × (does the probe pass?)`:

| Other side | passes (permeable) | blocked (non-permeable) |
| --- | --- | --- |
| OCEAN | **mouth** (opening to exterior) | **exterior wall** |
| another cavity (wet) | *(impossible — would merge them)* | **constriction** (closed throat) |
| solid (dry) | *(impossible — blocked)* | **coast** (lining) |

`throat` (internal, permeable, within one cavity — the merge-tree narrowings) and
`constriction` (boundary, non-permeable, between two cavities) are the **same
feature family, different state**; a throat *closes* into a constriction as the probe
grows. A constriction's `R_gate` is **the probe radius at which the two cavities
merge** (§7).

**"septum" is reserved for the SOLID side** — a dry divider **bank** (anatomically a
septum is a solid dividing wall). It is *not* the empty-space wet↔wet pinch (that is
a constriction). The two are mutually exclusive at the face level: a solid divider
gives **coast** on both sides + a septum bank; an empty pinch gives a **constriction**
face with no solid between.

## 7. Probe-relativity (a first-class property)

Classification is **probe-parameterized**: a component's name is `classify(c,
probe)`. Because `R_gate`/`R_residence` are **probe-independent**, the **entire
classification trajectory across probe is determined by one query** — no sweep
needed; the per-face/per-tet values encode the whole probe axis. The trajectory is a
step function whose **major** transitions are the component's **characteristic
radii**:

```
residence_death_radius = max R_residence        → above: loses residence (degenerate)
seal_radius            = max mouth R_gate        → above: loses mouths (becomes void)
merge radii            = constriction R_gates    → merges with neighbours
split radii            = internal throat R_gates → splits internally
```

These four are the major transitions; the **full** trajectory is determined by the
*entire sorted set* of face `R_gate` and tet `R_residence` values — mouth clusters
also split/merge (changing `n_mouths`) at intermediate face values, so the spectrum
is finer than these four radii. A complete characterization is a **classification
spectrum over probe** ("groove for probe < a, pocket on [a,b), void above b"), free
from the grounded data.

This is the formal home for enclosability (pocket→void), constriction = merge radius
(§6), the "redundant probe sweep", and gate-breathing/cryptic pockets (the
characteristic radii **changing across frames**). Probe and time are **sibling
axes**, sharing the atom-based lineage matcher.

**Margin units are heterogeneous** (the §5 confidence is *not* a single quantity).
For the **topological** transitions (residence, mouths) the margin is a probe-radius
distance to the nearest characteristic radius. For the **morphological/porosity**
thresholds it is in their own units — `|occlusion − 1|` (a ratio; its probe
transition is membership-dependent, not one of the four simple radii) and the
wall-face count for `percolating`. A marginal classification still means the probe
sits near *some* transition, but "confidence" is per-threshold, not one number in
one unit.

## 8. Dry side — dual scheme, reserved

The rule applies symmetrically (identity = atoms; measurements; catalog predicates;
no stored dry-family — `DRY_BANK` → implicit `side=dry`). The dry **content is dual**,
not a copy — walls/dividers/cores, not cavities:

- Dual signature: `n_wet_contacts`, `exterior_exposure` (surface bank vs buried
  core), `n_coast_clusters`, `face_depth`.
- Dry catalog names: `surface_bank`, `buried_core`, **`septum`** (a solid divider
  bank lining exactly 2 wet cavities — §6).
- **`interface`** is a bilateral relation object between a wet component and its
  lining banks, characterized from both sides.

Dry is secondary and less mature; full spec is **deferred**, the symmetric slot
**reserved** so it cannot be bolted on incoherently.

## 9. Migration & compatibility

- **No two sources of truth, ever.** Migrate by **inversion**: extract `classify()`
  as the single definition; make any legacy `family`/`feature_type` **computed from
  it** (atomic switch), not assigned in parallel. The inversion also **proves the
  grounded signature is complete** (if `classify()` cannot reproduce a family, that
  family encoded something missing from the observables).
- **Compatibility is a layer-0 responsibility, not the kernel's.** Verified: the
  viewer (`molsysviewer_topomt`) already consumes layer-0 `feature_type` from feature
  objects (`payloads.py`, `panels/pockets.py`), **not** kernel `family`; its only
  kernel coupling is raw geometry (`dfnd.selectors`, `dfnd.centerline`), orthogonal
  to naming. So the kernel refactor is **invisible** to the viewer.
- Morphology evolves in layer 0: **additive first** (`feature_type='pocket'` kept,
  `morphology` added as attribute → no silent break of the "pocket" bucket), then
  **coordinated re-typing** (`feature_type='groove'`, narrow "pocket" to occluded) at
  the viewer's pace. Unifying `Pocket`/`Void`/`Channel` into one parameterized class
  (so a sealing component never changes object class) is the coordinated end-step.

## 10. Implementation status

**Done (committed this session) — validated building blocks, NOT final placement:**

- merge-tree sub-chamber hierarchy (`_attach_capacity_motifs`) — resolves L1.3.
- throat/chamber/bottleneck promoted to provisional (`output_status`).
- morphometrics: `occlusion`/`enclosable`/`occlusion_gap`/`buriedness`/`deepest_chamber`.

Re-homing (§4): the derived views are now **proper derived helpers** — `signature`,
`characteristic_radii`, and `family` itself are read-only properties computed from
the grounded inputs (no longer kernel facts sitting beside a stored `family`).
`morphometrics`/hierarchy are still computed at build time and cached on the
component (a legitimate caching of a derived value); the conceptual re-grounding is
done (they are derived-from-grounded, not identity), the physical lazification is an
optional cleanup.

**Landed (kernel side, committed):**

- the kernel/catalog split; `classify()` single source; the boundary-face partition
  + derived wall/constriction/`n_dry_contacts` helpers; non-resident
  compositionalization (retire `nonresident_passage`).
- **`family` retired as a stored kernel fact** (`d2eff71`): it is a derived property
  over the grounded signature (`WetComponent.family = classify_topology(n_mouths,
  n_resident_nodes, n_wall_faces)`; `DryComponent.family = DRY_BANK`); `side` is now
  intrinsic to the subclass (the more fundamental axis), not derived from `family`.
- **characteristic radii** as a derived view (`component.characteristic_radii`:
  residence_death/seal/merge/split) + **per-threshold confidence** in `classify`
  (`{name, confidence, marginal}`); per-mouth occlusion; marginality.
- the grounded name-free `component.signature` (the renderer keys on it, not family).

**Pending — the catalog/viewer migration (its own effort, `viewer_grounded_named_split.md`):**

- **`feature_type` re-typing** from `classification` (decision §5.2): deliberately
  deferred (it needs `open_concavity`/`groove`/… registered in the feature zoo
  `_feature_constants`, plus payload/renderer/tests). This **is** the feature-layer
  migration; the bridge already carries `classification` additively (front 1.a).
- the viewer grounded/named split (component primitives vs named features),
  `show_features` API, chemistry overlay, convex diagnostics.
- `septum` → `constriction` rename (+ dry `septum`); `output_status` `kind='family'`
  → catalog framing (cosmetic; not broken); dry-side dual scheme.
- **real-system validation** (§12).

## 11. Reconciliation debt

The decision contradicts docs/code that still encode the old model. Reconcile by
**reframing (not deleting)** — the old definitions survive as the derived
catalog/classification layer. The debt is **broad**, not three files:

- `feature_definitions.md §5` + `Glossary.md` + `Algorithm.md` + `Overview.md`:
  families become the **derived topological signature** the catalog refines
  (`pocket` topological → `pocket`(occluded)/`groove`(open)). Align `feature_definitions.md
  §5.2.1` morphology (`pocket` = occluded).
- `interfaces.md`: `interface` is a bilateral relation/modifier (`n_dry_contacts ≥
  2`), not a wet family.
- `known_limitations.md`: **L1.1** (`nonresident_passage`) is now *retired* (infeasible
  cell), **L3.1** (`surface_concavity` catch-all) is now *signature-defined* — update both.
- `metrics_contract.md`: metrics are **kernel observables**; naming is catalog — add
  the pointer.
- `output_status.py`: it registers families as `kind='family'` and the guard couples
  to kernel families. Reframe it to **track catalog outputs** (the `classify` names),
  the guard verifying `classify` is total / nothing unclassified.

## 12. Open debts (honest)

- **Real-system validation** — the dominant unknown; all evidence is synthetic. The
  empirical gate (~55–60% practical confidence until measured). Protocol: 3–5 PDBs
  with known sites — detection (DCA≤4Å), spurious junk, morphology sanity, stability.
  **The #1 action once §1–9 are locked.**
- **Elongation metric** — `groove` means "open dent" (`occlusion ≤ 1`); a true
  elongated furrow needs an aspect-ratio measure DFND does not yet compute
  (`elongated` = future sub-label).
- **Hierarchy lattice-noise** — `deepest_chamber`/access descriptors are confounded
  by lattice artifacts on gridded synthetics; supporting descriptors, not standalone
  classifiers (component_motifs.md / Q25).
- **Dry-side maturity** (§8).
