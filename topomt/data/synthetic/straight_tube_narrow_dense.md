# Straight tube: narrow, dense sampling

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `straight_tube_narrow_dense.pdb`
- **Atoms:** 81 · **Probe:** 1.4 Å
- **Expected by construction:** straight tube, ring radius 3.5 A and nominal sampling 2.5 A; independent BenchLab references and unresolved physical/public receiving
- **DFND families (significant):** 1x channel, 1x pocket
<!-- /AUTO -->

- **Generator:** `cylinder_tube(length=20.0, tube_radius=3.5, wall_spacing=2.5, jitter=0.1, seed=0)`
- **Model:** argon balls of radius 1.88 Å on a perturbed cylindrical array.

The descriptive identifier records construction, not a detected feature or
physical qualification. The header's family counts retain the historical
catalog observation; they are not an independent reference or a new execution.
Both radial size and sampling differ between the two straight-tube inputs.

## Current independent study

The canonical BenchLab unit is
[`straight_tube_narrow_dense`](../../../docs/content/benchlab/synthetic/straight_tube_narrow_dense/index.md).
It restores full-precision generator coordinates after loading this rounded
PDB topology. Its independent references concern those exact captured balls:
two end patches and a bent route at 1.2/1.4 Å, and finite-hull exclusion at 2.5 Å.

Initial native receiving is incomplete: physical arrangement work exhausts its
budget (#180), and local/public candidates require all-atom qualification (#181).
The selected 1.4 Å graph skeleton collides despite a different valid independent
route; general certified paths remain #76. The additional local concavity is
not independently established as a physical side-pocket.
