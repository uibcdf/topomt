# Straight tube: wide, sparse sampling

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `straight_tube_wide_sparse.pdb`
- **Atoms:** 77 · **Probe:** 1.4 Å
- **Expected by construction:** straight tube, ring radius 6 A and nominal sampling 3.5 A; characterize passage and lateral coverage independently of graph labels
- **DFND families (significant):** 1x channel, 2x pocket
<!-- /AUTO -->

- **Generator:** `cylinder_tube(length=20.0, tube_radius=6.0, wall_spacing=3.5, jitter=0.1, seed=0)`
- **Model:** argon balls of radius 1.88 Å on a perturbed cylindrical array.

The descriptive identifier records construction, not a detected feature or
physical qualification. The header's family counts retain the historical
catalog observation; they are not an independent reference or a new execution.
Both radial size and sampling differ between the two straight-tube inputs.

## Study scope

This wider array has no new independently referenced BenchLab unit. Its earlier
channel/pocket labels do not certify lateral coverage, physical openings or
collision-free paths. Avoid treating a sparse array as an ideal continuous wall.

For the active, separately parameterized narrower input, see
[`straight_tube_narrow_dense`](straight_tube_narrow_dense.md).
