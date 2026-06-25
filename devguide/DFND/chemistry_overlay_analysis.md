# Chemistry overlay — analysis (a deferred, not forgotten, layer)

Status: **analysis / parked** (2026-06-25). The physicochemical layer is real and
partly implemented, but **deferred** while the topology/morphology work lands. This
file narrates *what it is, how it is fed, where it sits today, and the target* so it
is not lost. Companion: the grounded/named split (`viewer_grounded_named_split.md` §7
puts chemistry as a **separate overlay**, orthogonal to topology).

## 1. What it is, and why it is a third axis

TopoMT's two axes so far are **grounded geometry** (where the cavity is, its shape) and
**named features** (what it is — pocket/void/channel/groove/cleft, funnel motif). The
chemistry overlay is the **third, orthogonal axis**: *the physicochemical character of
a cavity's lining*. It answers the question topology cannot:

> "A ligand sitting in this pocket/cleft — what can it interact with **chemically**?"

It is the chemical complement to the geometric `accessible_atom_indices` (the *which
atoms* of the interaction surface): the overlay says *of what character* those atoms
are (hydrophobic / polar / charged / H-bond acceptor). Together they make the
characterization a **druggability / interaction map**, not just a geometric one.

It is **orthogonal**: a hydrophobic pocket and a charged pocket are the *same* topology
(`pocket`) with *different* chemistry. So chemistry is an overlay, never a feature type.

## 2. How it is fed — molsysmt (`molsysmt.physchem`)

The chemistry source is **molsysmt**, per residue/group:

- `physchem.get_hydrophobicity(molsys, element='group')` — the **Eisenberg** scale per
  residue;
- `physchem.get_charge(molsys, element='group')` — the **charge at pH 7** per residue;
- mapped group→atom via `msm.get(molsys, element='atom', group_index=True)`.

So the raw chemistry is a **per-residue (hydrophobicity, charge)** pair, lifted to
per-atom. molsysmt owns this; TopoMT only consumes it. (Dependency note: dummy-atom
systems — e.g. `DUM` — have **no** physchem entry, so the overlay returns `None` and is
skipped; there is a pending molsysmt proposal `physchem_support_dummy_atoms`.)

## 3. Classification — (hydrophobicity, charge) → kind

The per-atom `(hydrophobicity, charge)` is classified into an **affinity / pharmacophore
kind** (`_affinity_color_for_scalars`, `_atom_pharmacophore_kinds`):

| Condition | kind |
| --- | --- |
| `charge > +0.5` | **positive** |
| `charge < -0.5` | **negative** |
| `hydrophobicity > 0` | **hydrophobic** |
| else | **polar / acceptor** |

(Charge dominates over hydrophobicity. Thresholds are simple and tunable.)

## 4. Aggregation — per cavity

Two renderings consume the per-atom kinds:

- **`show_dfnd_pharmacophore`** — one **interaction-site glyph** at each cavity's
  centre, typed by the **dominant** kind of its lining atoms
  (`Counter(lining).most_common(1)`), via `view.shapes.add_interaction_sites`.
- **`affinity_spheres`** (a component-render *mode*) — the residence spheres **coloured**
  per-atom by the affinity kind (a continuous map of the lining's character).

Both aggregate over `component.atom_indices` (the residence lining). **Gap:** they
should aggregate over **`accessible_atom_indices`** (lining ∪ past-beach kissed atoms —
§ coast/shore/beach) so the chemistry covers the *full* interaction surface, not just
the residence lining.

## 5. Where it sits today, and the target

**Today** the chemistry is **mixed into the component renderer** (`render/_components.py`):
`show_dfnd_pharmacophore` is a `show_dfnd_*` function and `affinity_spheres` is a
representation mode of `show_dfnd_components`. That couples the orthogonal chemistry axis
to the topology renderer.

**Target** (the grounded/named/chemistry split, design phase 3): a **separate chemistry
overlay surface** —

- `show_pharmacophore(view, topography, …)` — the interaction-site glyphs;
- `show_affinity(view, topography, …)` — the affinity colouring;

— that is **independent of** the grounded primitives and the named feature renderer, and
**composes on top of any feature/component**. The overlay should:

1. consume `accessible_atom_indices` (the full interaction surface, not just the lining);
2. expose the per-cavity dominant character + the per-atom kinds as data (not only a
   render), so panels / scoring can use it;
3. degrade cleanly when chemistry is unavailable (dummy systems) — already the case.

## 6. Why this matters (the not-forgetting)

The chemistry overlay is what turns DFND's honest **geometric** characterization into a
**functional / druggability** read: which cavities are hydrophobic drug-favourable
pockets, which are charged recognition sites, what a ligand can H-bond. It is the
chemical half of the central use case (the geometric half — `accessible_atom_indices` —
already landed). Deferring it is fine; losing it is not.

## 7. Open items

- **Separate the overlay** (`show_pharmacophore` / `show_affinity`) out of the component
  renderer (design phase 3).
- **Run on `accessible_atom_indices`** (lining + past-beach), not just the lining.
- **Per-cavity chemistry as data** on the feature (e.g. `feature.lining_chemistry` =
  {dominant_kind, kind_fractions}) — additive, so panels/scoring consume it.
- **molsysmt**: the `physchem_support_dummy_atoms` proposal (dummy systems currently skip
  chemistry).
- Validate the (hydrophobicity, charge) thresholds against known druggable sites.
