# argon_cube

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `argon_cube.pdb`
- **Atoms:** 8 · **Probe:** 1.3 Å
- **Expected by construction:** simplest cell: 8 argon at cube vertices, body diagonal = 2*(r_Ar+r_probe); void at probe<1.4, marginal/empty at exactly 1.4 (threshold knife-edge)
- **DFND families (significant):** 1x void
<!-- /AUTO -->

- **Generator:** `argon_cube()` (cube sized for probe 1.4; probed here at 1.3)

## What to observe

A **single void** (WET-1, family `void`, `n_mouths=0`, ~6 nodes): the central
cavity of the 8-atom cube. No dry components (there is no probe-excluded interior
beyond the vertices themselves). This is the minimal calibration cell.

At the canonical **1.4 Å probe**, DFND still reports the same central void
(WET-1, `void`, `n_mouths=0`, 6 resident nodes). This is the intended
knife-edge value: tiny numerical or geometric perturbations can decide whether
the marginal cell remains resident or disappears.

## Why

The 8 atoms sit at the vertices of a cube whose **body diagonal** is set to
`2·(r_Ar + r_probe)` with r_probe = 1.4: exactly the size where a 1.4 Å probe
touches the four opposite corners (knife-edge). With a probe of **1.3** (a touch
smaller) the probe **fits** in the centre and a closed void remains. At exactly 1.4
the result is marginal (void/empty on the edge); above it the cell is empty. It is
the threshold-sensitivity control.

## DFND verdict

✅ **Correct.** It detects the central void and reproduces the expected knife-edge
behaviour (void below 1.4, marginal at 1.4). A good system to check the calibration
of the residence threshold.
