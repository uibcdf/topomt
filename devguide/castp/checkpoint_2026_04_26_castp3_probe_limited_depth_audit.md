# CASTp3 Probe-Limited Depth Audit

Date: 2026-04-26

## Context

The CASTp3/CASTpFold line is now isolated in `topomt.third_party.castp3`.
The CASTp1-native baseline remains protected in `topomt.third_party.castp`.

This checkpoint records the audit triggered by the 2PK4 POC-1 discrepancy:
some tetrahedra associated with the CASTp3 server POC-1 region flow inward to
a global sink, but that global sink does not survive the `rank2` probe cutoff.

The explored physical hypothesis was:

- truncate the flow graph to tetrahedra that survive the probe cutoff;
- define the effective sink inside that surviving graph;
- keep inward-flowing accessible tetrahedra even when the deeper global sink is
  outside the probe cutoff.

## CASTp1 Source Audit

The historical CASTp1 implementation does not support that behavior as the
canonical pocket construction.

In `mkalf/voids.c`, `alf_compute_pocket_depths()` computes `pocket_depth`
globally before applying the `rank2` cutoff. For every tetrahedron, the depth
is the sink reached through hidden-triangle links with the largest rho value,
or the infinity marker if the flow reaches an attached hull triangle.

Then `alf_init_pockets(rank1, rank2, do_wrap)` processes tetrahedron rho events
between `rank1 + 1` and `rank2`:

- if `depth[ix] == ix`, the tetrahedron is a sink and is handled as a pocket
  element;
- if `depth[ix] == infinity`, the tetrahedron is unioned with the exterior;
- otherwise the tetrahedron is retained only when
  `alf_is_in_complex(ALF_TETRA, rank2, depth[ix])` is true;
- if the depth/sink is not in the `rank2` shape, the tetrahedron is unioned
  with the exterior.

This means CASTp1 uses a global depth first and the probe cutoff second. It
does not recompute sinks after truncating the flow graph to probe-surviving
tetrahedra.

`alf_init_mouths()` is consistent with this interpretation. Mouth orientation
and the Fnext walk use the same `depth` array and stop when the neighboring
tetrahedron has infinity depth or a depth whose rho is outside `rank2`.

## Paper Audit

The 1998 CASTp descriptions also support the global discrete-flow reading:

- pockets are collections of empty Delaunay simplices gathered by discrete
  flow;
- a depression that flows sequentially to the outside/infinity is not a pocket;
- neighboring empty tetrahedra sharing a triangle belong to the same pocket;
- edge-sharing alone does not force a merge when the flow belongs to different
  sinks.

The paper text does not describe a second pass that redefines sinks after
discarding tetrahedra above the probe cutoff.

## Experimental Result

The probe-limited-depth variant was implemented only in `castp3` and guarded
behind `probe_limited_depth=False` by default.

Observed behavior:

- `2pk4` recovered fragments overlapping server POC-1 but exploded to many
  open components;
- `1crn`, which should remain `0 pockets / 1 void`, produced dozens of small
  pockets;
- `1rop` and `2lyz` also overproduced open pockets.

The failure pattern indicates that truncating depth by the probe cutoff is too
permissive by itself. It converts many local surviving concavities into pockets
instead of preserving the CASTp1 shallow-depression exclusion behavior.

## Rho / Probe-Radius Audit

The tetrahedron `rho` used here is a weighted power value at the weighted
circumcenter, not a centroid distance or a direct Euclidean tetrahedron size.

For the 2PK4 problematic sink, the sink is excluded because its rho is larger
than the beta/probe rank, not because it is geometrically too small in a naive
centroid sense.

A control run without solvent-expanded radii made the CASTp3 parity much worse:
voids disappeared or changed, many extra pockets/channels appeared, and common
server pockets were not recovered. This does not support the hypothesis that
the current main discrepancy is simply "adding the probe twice".

## Current Interpretation

For CASTp1 fidelity, the current baseline approach remains correct:

- compute global pocket depth;
- apply `rank2` to the global sink/depth;
- treat tetrahedra whose global sink does not survive `rank2` as exterior.

For CASTp3 parity, the interpretation has changed after the 2PK4 POC-1 bulb
audit:

- CASTp3 still uses the default solvent probe radius of 1.4 A;
- but that probe radius defines solvent accessibility, mouth context, and the
  molecular surface, not the maximum allowed internal pocket depth;
- a pocket may be accessible through a 1.4 A mouth and still contain internal
  bulbs/sinks larger than 1.4 A;
- therefore `probe_rank` must not be used as the default `beta_rank` depth
  cutoff in the CASTp3 path.

For 2PK4 POC-1, the CASTp3 server `bulb.json` contains 18 bulbs for Pocket 1.
Mapped onto the native protein-only ProtOr geometry:

- all 18 bulbs fall inside native tetrahedra;
- 17/18 bulbs lie in the basin whose global sink is tetrahedron 3819;
- the largest server bulb has radius 2.2217 A;
- native tetrahedron 3819 has `sqrt(rho) = 2.2217 A`;
- native `probe_rank` corresponds to `sqrt(rho) ~= 1.398 A`.

This means the server is not avoiding the deep sink. It is reporting precisely
the deep bulb/sink region that the previous native CASTp3 default discarded by
cutting pockets at `probe_rank`.

The implemented CASTp3 correction is:

- keep `alpha_rank` defaulting to `geometry.base_rank`;
- when `beta_rank` is not provided, use `_geometry_max_rank(geometry)` instead
  of `_probe_rank(geometry, probe_radius)`;
- keep explicit `beta_rank` available for diagnostics;
- keep `probe_limited_depth=False` and experimental.

Mini-parity after this correction (`selection=protein-only`, `radii_model=protor`,
CASTpFold oracle):

| Case | Native pockets | Oracle pockets | Exact pocket matches | Native voids | Oracle voids | Exact void matches |
|---|---:|---:|---:|---:|---:|---:|
| 1crn | 0 | 0 | 0 | 1 | 1 | 1 |
| 1rop | 3 | 3 | 3 | 0 | 0 | 0 |
| 2lyz | 6 | 6 | 5 | 6 | 6 | 6 |
| 2pk4 | 3 | 3 | 1 | 4 | 4 | 4 |

For 2PK4, the best native component corresponding to server POC-1 is now a
strict subset of the oracle atom list:

- native: `{32, 34, 455, 461, 463, 464, 576, 584, 585, 587, 588, 602}`;
- oracle: native plus `{578, 601}`;
- no extra atoms are introduced.

The remaining 2PK4 difference is therefore a CASTp3 lining/rim atom reporting
difference rather than failure to detect the deep pocket core.

Follow-up inspection:

- missing atoms `{578, 601}` are exactly part of CASTp3/CASTpFold `Mouth 1`;
- they do not belong to any retained native pocket component after the
  `beta_rank=max_rank` correction;
- their adjacent tetrahedra are mostly exterior/INF-side tetrahedra;
- CASTp3 appears to include mouth/rim atoms from the exterior side of the
  opening in the pocket `.poc` atom list.

This should be solved as a canonical mouth/rim reporting problem, not by
expanding the pocket tetrahedron component locally.

Rejected local shortcut:

- adding all atoms opposite mouth faces on the exterior side makes 2PK4 POC-1
  exact;
- but it over-includes atoms in 2PK4 POC-2 and POC-3;
- therefore CASTp3 is not simply reporting every exterior-side opposite atom;
- the missing rule is more likely the mouth rim / opening-polygon atom
  selection, which must be reconstructed from the canonical mouth geometry.

Accepted reporting correction:

- CASTp3 pocket atom lists include exterior-side opposite atoms only for
  attached mouth faces (`face_rho_rank == 0`);
- this is consistent with the mouth/rim opening geometry and avoids the false
  positives produced by adding all exterior-side opposite atoms;
- for mouth atom reporting, the native CASTp3 path now uses:
  - atoms from non-attached mouth faces;
  - plus exterior-side opposite atoms from attached mouth faces;
  - with a fallback to attached exterior atoms if all faces are attached.

2PK4 validation after this correction:

- POC-1 atom set exact;
- POC-2 atom set exact;
- POC-3 atom set exact;
- Mouth 1 atom set exact;
- Mouth 2 atom set exact;
- Mouth 3 atom set exact.

Mini-parity after the `beta=max_rank` and attached-mouth reporting corrections:

| Case | Pockets native/oracle/exact | Voids native/oracle/exact | Mouths native/oracle/exact |
|---|---:|---:|---:|
| 1crn | 0 / 0 / 0 | 1 / 1 / 1 | 0 / 0 / 0 |
| 1rop | 3 / 3 / 3 | 0 / 0 / 0 | 3 / 3 / 3 |
| 2lyz | 6 / 6 / 5 | 6 / 6 / 6 | 6 / 6 / 5 |
| 2pk4 | 3 / 3 / 3 | 4 / 4 / 4 | 3 / 3 / 3 |

## 2LYZ Residual

After the `beta=max_rank` and attached-mouth reporting corrections, the only
small-system residual in the current mini-battery is 2LYZ Pocket/Mouth 4.

Oracle:

- `Pocket 4`: `{483, 484, 485, 486, 487, 488, 504, 787}`;
- `Mouth 4`: `{483, 485, 486, 487, 488, 504, 787}`;
- `MouthInfo Ntri`: 6.

Native:

- pocket atom report: `{485, 487, 488, 504, 787}`;
- component/core atoms: `{487, 488, 504, 787}`;
- mouth atom report: `{485, 487, 488, 504, 787}`;
- native seed mouth faces: 4.

Local geometry:

- the immediate attached-mouth correction adds atom `485`, which is correct;
- missing oracle atoms `{483, 484, 486}` are not in the retained component;
- they sit in a small blocked/exterior tetrahedral sheet adjacent to the
  attached mouth face;
- oracle `Mouth 4` includes `483` and `486`, but not `484`;
- oracle `Pocket 4` includes all three `{483, 484, 486}`;
- nearby false-positive candidates such as `489`, `490`, and `812` show that a
  broad "include neighboring exterior sheet" rule is unsafe.

Additional audit:

- growing the exterior sheet through attached faces (`face_rho_rank == 0`) is
  not a valid rule: from the attached neighbor it expands into a very large
  exterior molecular sheet rather than a local mouth patch;
- CASTp1 `alf_scan_pocket_f1()` only seeds mouth triangles from tetrahedra that
  are already in the pocket union-find component; the native CASTp3 copy is
  consistent with that CASTp1 behavior;
- CASTp1 `print_pockets()` emits the combinatorial pocket structure as
  `iT/rF/iF/rE/iE/rV/iV`; the CASTp3 server `.poc` and `.mouth` PDB-style files
  are therefore a higher-level atom-reporting export, not the same raw output
  as the historical `print_pockets()` face list;
- the server `MouthInfo` reports `Ntri = 6` for this mouth, while the native
  CASTp1-like seed set has 4 faces; therefore the residual is likely not a
  missing pocket tetrahedron but a CASTp3 reporting/contribution layer for the
  mouth opening;
- the residual is concentrated around TRP62. The current ProtOr assignments in
  the native code are chemically plausible for that region (`CB=C4H2`,
  aromatic bridge carbons as `C3H0`, protonated aromatic carbons as `C3H1`,
  `NE1=N3H1`), so there is no current evidence that this specific mismatch is
  caused by an obvious ProtOr typing error.

Current interpretation:

- 2LYZ Pocket/Mouth 4 likely requires reconstruction of the CASTp3
  mouth-opening reporting/contribution patch beyond the CASTp1 seed faces;
- this is not solved by the attached-opposite rule alone;
- no broader local rule should be introduced until we can distinguish the
  oracle mouth patch from nearby blocked tetrahedra without oracle knowledge.

Remaining CASTp3-specific work is now more likely:

- a CASTp3-specific preprocessing/reporting policy;
- a modern shallow-depression criterion;
- a post-processing or merging rule for adjacent open regions;
- or a subtle difference in modern alpha-shape/rank/radius construction.

The probe-limited-depth route should remain experimental until a CASTp3 source
or documentation reference supports it. It should not replace the default
CASTp3 construction.

## Next Work Items

1. Keep `probe_limited_depth=False` as the default.
2. Keep CASTp3 default pocket depth unbounded by `probe_rank`
   (`beta_rank=max_rank` unless explicitly overridden).
3. Continue CASTp3 parity work from the CASTp1-like baseline plus ProtOr radii.
4. Investigate the remaining 2LYZ one-pocket / one-mouth atom-set mismatch.
5. Investigate CASTp3's shallow-depression exclusion, especially the server
   statement that at least one pocket cross-section must be larger than the
   mouth opening.
6. Investigate whether CASTp3 merges or reports open regions differently from
   CASTp1 when components share edges/atoms but not pocket tetrahedra.
7. Avoid introducing local pocket-retention rules unless they can be tied to
   CASTp3 documentation, the 1998 algorithm, or an executable reference.
