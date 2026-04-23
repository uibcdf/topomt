# Checkpoint 2026-04-20: Pre-Parity Baseline for Native CASTp

## Purpose

This checkpoint freezes the current interpretation of the native CASTp path
before running the next round of parity tests against CASTp server fixtures.

The goal of this stage is not to claim full server parity. The goal is to state
which algorithmic fronts are now intentionally aligned with the historical
CAST/MKALF workflow, which fronts are deliberately excluded, and how upcoming
parity failures should be interpreted.

## Current Target

The current target is:

- a native, independent CASTp implementation;
- maximally faithful to the classical CAST/MKALF algorithm;
- excluding DELX/SoS for the moment;
- without local ad hoc rules introduced only to satisfy individual fixtures.

The next parity tests should therefore be read as tests of the current
non-DELX native algorithm against the server data, not as a final proof of
literal CASTp identity.

## Fixed Policy Decisions

### 1. DELX/SoS remains out of scope for this checkpoint

The native implementation still uses the current Python regular triangulation
substrate rather than the historical DELCX + exact predicates + symbolic
perturbation stack.

This remains the largest known structural gap.

Implication for parity:

- a parity failure may still be caused by a different regular triangulation;
- this must not immediately be interpreted as a pocket/mouth logic bug;
- triangulation-level residuals should be separated from downstream topology
  residuals when possible.

### 2. Hydrogens are respected if present in the input PDB

The native geometry path no longer applies a hard heavy-atom filter.

This follows the classical `pdb2alf` behavior more closely:

- `ATOM` records are read;
- `HETATM` records are read;
- hydrogen atoms receive the historical fallback radius when no table entry is
  found.

For now, no special rule such as "keep only polar hydrogens" is implemented.
If CASTp 3.0 server applies such a policy, it must be established from a
specific source or from reproducible fixture evidence before being encoded.

Implication for parity:

- input structures without explicit hydrogens are unaffected;
- input structures with explicit hydrogens now follow the current agreed policy:
  preserve them;
- future server-specific hydrogen normalization remains a possible later
  compatibility layer, not part of this checkpoint.

### 3. Metrics are a separate reporting front

The current metrics layer reports geometric quantities from the native
tetrahedral and triangular representation.

This is useful and MKALF-like for the current topological implementation, but
it should not yet be treated as full parity with the CASTp server reporting
layer.

In particular, `volbl`/server outputs may use additional analytical surface or
volume calculations beyond simple native tetrahedron/triangle aggregation.

Implication for parity:

- mismatches in areas, volumes, mouth areas, or mouth perimeters should not be
  used by themselves to reject the current topological implementation;
- the first parity pass should prioritize feature counts and composition:
  tetrahedra, triangles, atoms, mouths, and feature classification;
- metric parity should be tracked separately.

### 4. CASTp 3.0 server parity remains partly uncertain

The current executable reference for the historical algorithm is MKALF.
The CASTp 3.0 server may contain additional postprocessing or reporting rules
not visible in MKALF 4.1.

Known risk areas include:

- final pocket/channel/branched-channel classification;
- possible server-side mouth normalization;
- possible input cleanup policies;
- possible metric postprocessing.

Implication for parity:

- a server mismatch does not automatically prove a violation of MKALF;
- if MKALF and server differ, the difference must be documented before deciding
  whether the native implementation should follow MKALF or CASTp 3.0 behavior.

## Algorithmic Fronts Now Considered Closed Enough for Parity

The following fronts should no longer be treated as leading known blockers
before running parity.

### Input defaults

Native defaults now follow the historical PDB2ALF-style setup:

- `selection='all'`
- `solvent_radius=1.4`
- `radii_model='castp_param'`
- hydrogens preserved when selected

`protor` remains available explicitly, but it is no longer the default native
CASTp radius model.

### Exact rank event construction

The native rank layer now:

- builds the spectrum from `rho` events only;
- keeps `mu1` and `mu2` out of the spectrum;
- uses exact ratio ordering for tetrahedron, face, edge, and vertex `rho`
  events;
- uses exact threshold ranking for `base_rank` and `probe_rank`;
- keeps the final global `+infinity` rank in the MKALF-style rank range.

The previous critical float shortcut for deciding whether face/edge `rho`
events enter the spectrum has been removed. A face or edge is skipped as an
attached event only when its `rho` value is exactly `0.0` in the native state.

### Attachedness and hidden predicates

The native path now distinguishes the two historical contexts:

- spectrum construction treats degenerate hidden predicates as attached;
- discrete-flow `hidden_triangle` treats degenerate hidden predicates as not
  hidden, following MKALF's explicit handling.

Weighted hidden predicates now use fixed-point determinant machinery rather
than simple geometric float tests.

### Rank table semantics

Membership and interior tests now go through centralized MKALF-like helpers:

- `rho != 0 -> rho <= rank`
- `rho == 0 -> mu1 <= rank`
- `interior -> mu2 <= rank`

Invalid or absent edges are not treated as implicitly present in the alpha
complex.

### Master-list and pocket construction

Pocket construction now follows the rank-driven structure of
`alf_init_pockets`:

- scan tetrahedron `rho` events by rank;
- use non-wrapping max-rho pocket depths;
- delay tetrahedra by sink;
- handle same-rank sink cases explicitly;
- union through faces not in the `rank1` alpha complex.

The previous empty-tetrahedron prefilter shortcut is no longer the admission
rule for pockets.

### Voids

Void construction follows the descending complement scan of `alf_find_voids`:

- descending global rank scan;
- tetrahedron insertion;
- first triangle event unions;
- explicit exterior component.

The final global rank range now uses the MKALF-style global rank count rather
than the maximum tetrahedron `rho` rank.

### Mouth construction

Mouth construction is now much closer to `alf_init_mouths`:

- mouth seeds carry explicit triangle identity;
- outward orientation is computed relative to pocket depth and `rank2`;
- mouth walks use edge-facet `Enext`/`Fnext` semantics;
- walks stop when the next tetrahedron is outside the `rank2` pocket shape;
- mouth clustering is now global before assigning mouths back to pockets.

The last point matters because MKALF builds one global `mouth_uf`, then counts
mouth components per pocket. The previous native path clustered mouths inside
each component independently.

### Reporting partitions

Native records now expose MKALF-like partitions:

- `iT`
- `iF` / `rF`
- `iE` / `rE`
- `iV` / `rV`
- mouth face and triangle identity where available

These are intended to support parity analysis at the level of composition, not
only feature counts.

## Remaining Known Limitations Before Parity

### 1. DELX/SoS

This is the only known primary algorithmic gap intentionally left open at this
checkpoint.

It may affect:

- tetrahedron identities;
- neighbor graph;
- exact degeneracy handling;
- attachedness;
- discrete-flow paths;
- mouth topology.

### 2. Full server metric reporting

Native area/volume values are not yet guaranteed to reproduce the full CASTp
server metric layer.

This should be handled as a separate metric-parity front.

### 3. CASTp 3.0-specific postprocessing

Some server behavior may not be present in MKALF 4.1. This is especially
relevant for:

- mouth normalization;
- final channel classification;
- input cleanup;
- reporting conventions.

These should be investigated only after observing parity residuals, not guessed
up front.

## Pre-Parity Verification

The non-parity CASTp test battery was run with the known server/oracle parity
tests excluded:

```bash
pytest -q tests/test_castp_core.py -k "not castp_voids_parity_1hiv and not castp_voids_parity_1tcd and not castp_recovers_branched_channel_for_1a4j_pocket_2 and not castp_recovers_channel_for_1stp_pocket_7 and not castp_short_green_battery_exact_feature_parity"
```

Result:

```text
70 passed
```

A control search also confirmed that the current CASTp core no longer contains:

- the previous hard hydrogen filter in the native geometry path;
- the previous `np.isclose` gates for face/edge `rho` event admission.

## Interpretation Rules for the Next Parity Pass

The next parity pass should classify failures into separate buckets:

1. **Triangulation residuals**: likely DELX/SoS or regular triangulation
   differences.
2. **Topological residuals**: different tetrahedron, face, edge, vertex, mouth,
   or feature composition after accounting for triangulation.
3. **Classification residuals**: same or similar composition but different
   `pocket` / `channel` / `branched_channel` label due to mouth count or server
   postprocessing.
4. **Metric residuals**: area, volume, mouth area, or perimeter mismatches.
5. **Input residuals**: atom materialization differences, including hydrogens,
   alternate locations, hetero atoms, or server-specific cleanup.

Only bucket 2 should be treated as direct evidence of a remaining non-DELX
algorithmic bug in the native topology path.

## Current Judgement

At this checkpoint, the native CASTp implementation is sufficiently close to
the historical non-DELX/MKALF workflow to start parity testing.

The correct expectation is not perfect server parity yet. The correct
expectation is a sharper failure analysis:

- if counts and composition improve, the recent canonicalization work is
  validated;
- if failures cluster in triangulation-sensitive cases, DELX/SoS becomes the
  next major front;
- if failures cluster in metrics only, the `volbl`/server reporting layer
  becomes a separate front;
- if failures cluster in mouths/classification with similar geometry, CASTp
  3.0-specific mouth postprocessing should be investigated.
