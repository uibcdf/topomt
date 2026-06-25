# Checkpoint — long pause (2026-06-25)

Resume point after a long working stint. Everything is **committed, pushed, and green**.
This file is the *where-we-are / what-remains / how-to-resume*, so picking the work back
up is easy and error-free. Authoritative companions:
[`taxonomy_architecture_decision.md`](taxonomy_architecture_decision.md) (the rule),
[`feature_catalog.md`](feature_catalog.md) (the sheet),
[`viewer_grounded_named_split.md`](viewer_grounded_named_split.md) (the viewer design),
[`chemistry_overlay_analysis.md`](chemistry_overlay_analysis.md) (the deferred chemistry).

## 1. State of the world

- Branch **`main`**, pushed to `origin` (github.com:uibcdf/topomt). Working tree clean
  except the collaborator's `sandbox/` notebooks (untouched, not ours).
- **Phases 1–5 of the kernel/catalog refactor: DONE.** Tasks #32–#36 complete.
- **#37 (viewer grounded/named split + morphology leaves): DONE** (the implementable
  scope). **#38 (research) is the open backlog.**
- Tests **green across the FULL suite**, including the slow `test_dfnd_real_system_stability`
  (real proteins) and `tests/methods` (castp) -- both confirmed passing with the
  morphology/zoo changes. Resume is genuinely error-free.

## 2. What is done (the major arcs)

- **Kernel/catalog split**: `classify.py` is the single naming source; `family` is
  **retired as a stored kernel fact** (a derived property over the grounded signature);
  `side` is intrinsic to the subclass.
- **Grounded views**: `component.signature`, `characteristic_radii`, per-threshold
  `confidence`, and the name-free component renderer (keys on `signature`, not family).
- **coast / shore / beach** (decision §6): `coast` = a tetrahedron permeability class;
  `shore` = a non-permeable wet-dry **wall**; `beach` = a permeable wet-dry face (the
  probe wets through). The **past-beach** contact is recovered (`beach_pocket`,
  `volume_solvent_accessible`), and **`accessible_atom_indices`** = the ligand
  interaction surface (lining ∪ past-beach kissed atoms). The render keys on the kernel
  `kind` (single source) via `shore_faces`/`beach_faces`.
- **feature_type IS the classification** (§5.2): `open_concavity` / `groove` / `cleft`
  registered in the zoo with their classes; the bridge promotes by classification.
- **Morphology leaves / motifs** (all PROVISIONAL thresholds — see §4):
  - `groove` — **leaf**: an elongated open concavity (`morphometrics['elongation']`).
  - `cleft` — **leaf**: a DEEP open canyon (`morphometrics['buriedness']`); validated on
    real lysozyme (1hel cleft → `cleft`, buriedness 13). Checked before groove.
  - `funnel` — **motif**: the access zone that directs solvent inward (a steady,
    appreciable narrowing gradient, `morphometrics['funnel']`); fires once per real
    protein (the access funnel). NOT a leaf.
  - `dish` / the tapering-cone — **descriptors, not names** (low elongation/buriedness;
    the `occlusion` descriptor). `cleft`-as-interface was rejected (a real intra-protein
    cleft is one dry bank).
- **Viewer feature renderer**: `show_features` dispatches by `feature_type` to a grounded
  representation, **a view-per-representation** (`result.details['by_representation']`;
  per-representation clear/hide/show; rendered_ids in feature order).
- **Chemistry overlay**: separated as a surface (`show_pharmacophore` / `show_affinity`,
  fed by `molsysmt.physchem`); the pharmacophore now aggregates over
  `accessible_atom_indices`. Full design in `chemistry_overlay_analysis.md`.

## 3. What remains — #38 (research + polish, NOT session-closeable)

1. **Real-PDB validation of the provisional thresholds** (the dominant unknown, §12):
   a panel of PDBs with known sites to validate/tune groove τ, funnel gradient/steadiness,
   cleft buriedness; and **normalise `buriedness`** (it is a raw topological-depth count,
   so the cleft threshold is system/discretization-dependent).
2. **Convex side → features**: promote the convex catalog (`peak_patches`/`ridge_lines`/
   `spikes` → `generic_convexity`/`ridge`/...); the convex taxonomy is still un-promoted
   (`dry_network_and_convexity.md`).
3. **Chemistry polish**: consolidate the implementation into `_chemistry.py`; expose
   `feature.lining_chemistry` as data (over `accessible_atom_indices`); molsysmt
   `physchem_support_dummy_atoms`.
4. **Optional**: `show_<feature>` wrappers; cleanup of deprecated feature-styled modes
   (groove_floor/interface_ribbon/cutaways already reachable via `show_features` styles).
5. **Minor reconciliation debt** (low priority, in `taxonomy_architecture_decision.md`
   §8/§11, not lost): the prose `septum → constriction` rename; the dry-side **dual
   scheme** (§8, reserved); unifying `Pocket`/`Void`/`Channel`/`OpenConcavity`/`Groove`/
   `Cleft` into one parameterized class (optional, §5.2); `output_status` `kind='family'`
   → catalog framing (cosmetic — not broken).

## 4. Provisional thresholds (so they are not lost)

| Name | Constant (file) | Value | Calibrated against |
| --- | --- | --- | --- |
| `groove` (elongated) | `_GROOVE_ELONGATION` (classify.py) | 2.5 | surface_groove 4.7 vs round ~1.2 |
| `cleft` (deep) | `_CLEFT_BURIEDNESS` (classify.py) | 10 | 1hel cleft 13 vs groove ~6 |
| `funnel` (steady narrowing) | `_FUNNEL_GRADIENT` / `_FUNNEL_STEADINESS` (components.py) | 0.4 / 0.8 | cone (−0.6, 0.96) vs tube (−0.03, 0.16) |

All registered `provisional` in `output_status.py`. Fixtures: `synthetic.surface_groove`,
`synthetic.surface_cleft`, `synthetic.surface_funnel`.

## 5. How to resume (the recipe)

1. **Confirm green** (12 cores, the machine stays usable):
   ```
   python -m pytest tests/ -q -p no:cacheprovider -n 12 \
     --ignore=tests/test_dfnd_real_system_stability.py --ignore=tests/methods
   ```
   Morphology-focused: `tests/test_dfnd_classify.py tests/test_dfnd_morphometrics.py
   tests/test_dfnd_boundary.py tests/test_molsysviewer_topomt_addon.py`.
2. **Read the plan**: this file §3 (#38) + the task list (#38). The *why* is in the four
   companion docs above.
3. **A real-PDB run** (the validation entry point) works out of the box:
   ```python
   import molsysmt as msm
   from topomt.get_topography import get_topography
   sys = msm.convert('pdb_id:1hel', to_form='molsysmt.MolSys')
   sys = msm.remove(sys, selection='not (group_type=="amino acid")')
   topo = get_topography(sys, method='dfnd', probe_radius=1.4)
   # inspect topo[fid].feature_type / .morphometrics / .accessible_atom_indices
   ```
4. **Estimated success** (honest, last assessed): core characterization ~78–80% (the
   site appears, geometry faithful); morphological naming ~55–65% (grounded metrics,
   provisional thresholds — #38 validation is where this number moves). Chemistry: the
   next axis. "Appears ≠ druggable" — the bar is *the site is characterised*, not ranked.

## 6. Anything in-flight? — No.

No half-done edits. The last stint closed the feature-renderer view-per-representation
work (`6424905`). The only non-committed files are the collaborator's `sandbox/` notebooks.
Safe to pause.
