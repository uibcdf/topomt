# hollow_sphere_void

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `hollow_sphere_void.pdb`
- **Atoms:** 103 · **Probe:** 1.4 Å
- **Expected by construction:** one enclosed void (0 mouths)
- **DFND families (significant):** 1x void
<!-- /AUTO -->

- **Generator:** `hollow_sphere(sphere_radius=10.0, wall_spacing=3.5, jitter=0.1, seed=0)`

## What to observe

A **single void** (WET-1, family `void`, **`n_mouths=0`**, ~114 nodes): the interior
cavity of the hollow sphere, fully enclosed. The wall shows up split into several
dry components (the probe-excluded interior, fragmented by the wall sampling). Zero
mouths to the exterior.

## Why

A spherical shell of radius 10 Å with a well-sampled wall (spacing 3.5 Å) seals a
1.4 Å probe: there is no window in the wall larger than the probe, so the interior
solvent is trapped → a 0-mouth void. It is the canonical buried-cavity case, the
opposite of a pocket (1 mouth) or a channel (≥2 mouths).

## DFND verdict

✅ **Correct.** An enclosed cavity catalogued as a void with zero mouths, exactly as
designed. Together with [`hollow_sphere_pocket`](hollow_sphere_pocket.md) (the same
sphere with one opening → a pocket) it forms the minimal void↔pocket pair that
validates the mouth count.
