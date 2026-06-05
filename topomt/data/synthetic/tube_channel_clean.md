# tube_channel_clean

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `tube_channel_clean.pdb`
- **Atoms:** 81 · **Probe:** 1.4 Å
- **Expected by construction:** narrow, densely-walled tube -> single clean channel (2 mouths) with minimal side-pocket noise; canonical two-mouth-channel fixture
- **DFND families (significant):** 1x channel, 1x pocket
<!-- /AUTO -->

- **Generator:** `cylinder_tube(length=20.0, tube_radius=3.5, wall_spacing=2.5, jitter=0.1, seed=0)`

## What to observe

A **single channel** running end to end through the tube, catalogued as family
`channel` with **`n_mouths = 2`** (the two open ends at z = ±10). Next to it, a
**single small side-pocket** — expected noise.

At the public level it is promoted to a `Channel` feature with two child `Mouth`s.

## Why

This is the *sealed* version of the tube: a narrow radius (3.5 Å) and a dense wall
(`wall_spacing = 2.5`, ~9 atoms per ring). At that density the lateral windows
between wall atoms fall below the 1.4 Å probe, so the lumen does not leak sideways
and the only openings to OCEAN are the two ends → a channel with two mouths.

The residual side-pocket is unavoidable with a **single-layer wall**: among four
neighbouring wall atoms there is always a gap where the probe sits (a resident
tetrahedron) without being part of the lumen. "1 channel + 1 pocket" is the
cleanest result achievable without a double-layer wall.

## DFND verdict

✅ **Correct.** The lumen is identified as a channel (family `channel`) with two
mouths, exactly as designed. The side-pocket is expected geometric noise from the
single-layer wall, not an error.

> History (fixed): the channel family used to be named `multi_external_link`, but
> `_SIDE_BY_FAMILY` in `topomt/dfnd/components.py` expected the key `channel`, so
> **every channel was silently dropped from `components.wet`** (it was still in the
> raw output and the public features, just not the typed view). It was resolved by
> renaming the raw family to `channel` (a single source of truth). This system is
> the regression fixture
> (`tests/test_dfnd_wet_dry_adjacency.py::test_two_mouth_channel_appears_in_typed_components`).
