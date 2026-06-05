# hollow_sphere_pocket

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `hollow_sphere_pocket.pdb`
- **Atoms:** 96 · **Probe:** 1.4 Å
- **Expected by construction:** one polar opening -> pocket (1 mouth)
- **DFND families (significant):** 1x pocket
<!-- /AUTO -->

- **Generator:** `hollow_sphere_with_opening(sphere_radius=10.0, wall_spacing=3.5, opening_angle=30.0, jitter=0.1, seed=0)`

## What to observe

A **single pocket** (WET-1, family `pocket`, **`n_mouths=1`**, ~115 nodes): the same
cavity as [`hollow_sphere_void`](hollow_sphere_void.md) but with **one polar
opening** (a 30° cap) removed from the wall. At the public level it is promoted to a
`Pocket` feature with one child `Mouth` at the pole.

## Why

It is the hollow-sphere void with a cap of atoms removed at one pole. That window is
larger than the probe, so the interior is no longer enclosed and opens to OCEAN at
**one** place → exactly 1 mouth = pocket. It isolates the variable "number of
mouths": void (0) → pocket (1) by changing only the opening, with everything else
the same.

## DFND verdict

✅ **Correct.** A single opening → a pocket with one mouth. The clean contrast with
`hollow_sphere_void` (same geometry, 0 mouths) confirms that the void/pocket/channel
discriminant is the **count of mouths to OCEAN**, not the volume or the shape.
