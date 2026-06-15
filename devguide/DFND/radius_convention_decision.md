# Atomic-radius convention vs hydrogen policy (DFND decision record)

Status: open decision, recommendation pending approval.
Scope: how DFND sources atomic radii and how that interacts with
`hydrogen_policy`. This is a calibration/convention decision, not a code defect
and not a case of duplicating `molsysmt`.

## Summary

DFND builds its mesh on heavy atoms by default (`hydrogen_policy='exclude'`,
`topomt/dfnd/config.py:30`) but requests bare van der Waals radii by default
(`radii_model='vdw'`, `config.py:31`), which are passed straight to
`molsysmt.physchem.get_atomic_radius(definition=radii_model)`
(`topomt/dfnd/graph.py:92-97`). Bare vdW radii ignore the volume that the
implicit hydrogens still occupy in a heavy-atom-only model. `molsysmt` already
offers the consistent alternative, `definition='protor'` (implicit-hydrogen-aware
ProtOr united-atom radii, `molsysmt/physchem/get_atomic_radius.py:58-62`).

The default pair `exclude` + `vdw` therefore embodies no explicit scientific
convention. This document records the impact, the blocker that prevents a naive
default flip, and a low-risk recommendation.

## How radii reach the result

`R_gate` and `R_residence` are largest-empty-sphere clearances between atoms
(`topomt/dfnd/core/clearance.py:131-197`): conceptually
`radius = min(||center - atom|| - r_atom)` (`clearance.py:191`). They are
monotonically decreasing in atom radii — larger atoms give smaller clearances.
Thresholding compares clearances against `probe_radius` (default `1.4`,
`graph.py:377`): `permeable(F) = R_gate >= R_probe - slack`,
`resident(T) = R_residence >= R_probe - slack` (`graph.py:432-436`). So larger
radii produce fewer permeable faces and fewer resident tetrahedra, i.e. smaller
and fewer wet components.

## Quantitative impact (Å)

| Element | vdW | ProtOr | Δ |
|---|---|---|---|
| C (aliphatic CHn) | 1.70 | 1.88 | +0.18 |
| C (aromatic C3H0) | 1.70 | 1.61 | -0.09 |
| N | 1.55 | 1.64 | +0.09 |
| O (carbonyl O1H0) | 1.52 | 1.42 | -0.10 |

ProtOr is **not** "vdW plus a constant": carbon grows substantially, nitrogen
grows slightly, and oxygen shrinks. It is atom-type and residue specific. In
proteins the abundant, most-grown carbon dominates, so switching vdW -> ProtOr
makes cavities smaller and slightly fewer and closes marginal gates.

The dominant +0.18 Å shift **far exceeds the tolerance bands** (numerical
`epsilon` ~1e-6; a typical `permeability_tolerance` ~0.05). Switching the radius
model is therefore not a fine adjustment: it rewrites topology, component IDs,
rankings, and volumes for any protein system.

## Blocker: ProtOr is protein-specific

ProtOr radii (`molsysmt/physchem/atoms/protor.py`) cover protein heavy atoms by
atom type, and the lookup needs `residue_name`/`atom_name`
(`_infer_protor_type_for_atom`). The table has no noble gases and no arbitrary
elements. DFND's synthetic benchmarks use noble-gas dummy atoms
(He/Ne/Ar/Kr/Xe, radius encoded by element symbol; `topomt/dfnd/synthetic.py:14`,
`:98`). Consequently:

> `radii_model='protor'` cannot be the global default: it would break the
> synthetic systems and any non-protein system (no assignable ProtOr type).

This rules out a simple default flip and reframes the decision as making the
radius convention explicit and system-appropriate.

## Which convention does DFND target?

The current default (bare vdW on heavy atoms) matches none of the established
conventions:

- Physical packing / volume (Tsai–Gerstein) -> ProtOr / united-atom radii.
- CASTp parity (pursued on other TopoMT paths) -> CASTp's own radius set with
  probe 1.4.
- Current -> bare vdW, an unexamined middle ground.

The real question is which convention DFND commits to for **protein** analysis.
That question is left open here and should be resolved before adopting options
B or C below.

## Already covered: provenance / comparability

`radii_model` is a field of `DFNDMeshConfig`, so it enters `substrate_key`
(`graph.py:182-187`) and therefore `result_key`. Two results computed with
different radius models are already non-comparable by identity, so the dynamic
lineage layer and any future cache will not conflate them. The infrastructure to
support multiple radius conventions without corrupting provenance already exists;
only the policy decision and a couple of guards are missing.

## Options

**A. Keep vdW as the universal default; document and offer ProtOr for proteins.**
(Recommended.)
- vdW stays the safe default (works for any element).
- Document that for protein cavity analysis with hydrogens excluded,
  `radii_model='protor'` is the physically consistent choice.
- Validate `radii_model in {'vdw','protor','provided'}` in `config.py`
  (`'provided'` is the direct-radii path paired with
  `hydrogen_policy='provided_atoms'`). Done as part of this work.
- Raise an informative error when ProtOr is requested on a system it cannot
  type, instead of an opaque `KeyError`.
- Cost: docs + two guards. Risk: none (current numbers unchanged).

**B. Auto-select the radius model from the system** (ProtOr for standard
proteins, vdW otherwise).
- More "correct" without user thought.
- Cost: protein-detection heuristic + re-calibration of protein benchmarks.
- Risk: silently changes protein results; conflicts with reproducibility.
- Not recommended now.

**C. Commit to ProtOr for proteins and re-calibrate.**
- Major scientific decision: re-validate `R_gate`/`R_residence`, probe defaults,
  and all protein benchmarks.
- Only if the goal is physical packing rather than CASTp parity.
- Deferred until the convention question above is resolved.

## Recommendation

Adopt **Option A** now. It is the only zero-risk path and keeps the door open:
vdW universal by default, ProtOr available and documented for protein +
hydrogen-excluded analysis, `radii_model` validated, and an informative error
when ProtOr cannot type a system. The deeper question (physical packing vs CASTp
parity as the reference convention for proteins) is recorded as open and
resolved before considering options B or C.

Key point: DFND is not duplicating `molsysmt` here — it uses the radius API
correctly and even parameterizes the model. The only issue is that the default
pair (`exclude` + `vdw`) encodes no explicit scientific convention, and
`molsysmt` already provides the pieces to fix that without touching the engine.

## References

- `topomt/dfnd/config.py:30-31` — `hydrogen_policy`, `radii_model` defaults.
- `topomt/dfnd/graph.py:92-97` — radius sourcing via `get_atomic_radius`.
- `topomt/dfnd/core/clearance.py:131-197` — largest-empty-sphere clearances.
- `topomt/dfnd/graph.py:432-436` — permeability/residence thresholding.
- `molsysmt/physchem/get_atomic_radius.py:58-62` — `vdw` vs `protor` branch.
- `molsysmt/physchem/atoms/protor.py` — ProtOr table and type inference.
- `topomt/dfnd/synthetic.py:14,98` — noble-gas dummy atoms in benchmarks.
