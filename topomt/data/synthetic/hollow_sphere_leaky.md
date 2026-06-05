# hollow_sphere_leaky

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `hollow_sphere_leaky.pdb`
- **Atoms:** 89 · **Probe:** 1.8 Å
- **Expected by construction:** wall seals a 1.8 A probe, leaks a 1.0 A probe (sweep)
- **DFND families (significant):** 1x void
<!-- /AUTO -->

- **Generator:** `hollow_sphere(sphere_radius=12.0, wall_spacing=4.5, jitter=0.1, seed=0)`

## What to observe

A **probe-sweep** system. At **probe 1.8 Å** (the catalogue value): a **single**
enclosed void (WET-1, family `void`, `n_mouths=0`, ~120 nodes) — the wall seals.
At the canonical **1.4 Å probe**, the same shell is already open: DFND reports a
single `channel` component with 3 mouths (~146 nodes, ~140 resident nodes). With a
**small probe (≈1.0 Å)** it leaks more strongly: the wall windows let the small
probe through and the cavity opens as a many-mouth channel. The wall comes out
heavily fragmented into dry components (spacing 4.5 Å, a loose wall).

## Why

The sphere is large (radius 12) and the wall is **deliberately loose**
(`wall_spacing = 4.5`): its windows are an intermediate size. A 1.8 Å probe does not
fit through them → the cavity is sealed (void). A 1.0 Å probe does → it leaks. The
sealing depends on the **probe/window ratio**, not just on the wall existing: the
same system is a void or not depending on the probe.

## DFND verdict

✅ **Correct.** It reproduces the expected probe dependence (seals at 1.8, leaks at
1.0), showing that sealing is a **probe-dependent** property of the ratio between
the probe radius and the wall-window size. It is the system that validates the
probe sweep in `at_probe(...)`.
