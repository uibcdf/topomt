---
summary: DFND solvent-volume precision and finite-sample uncertainty are overstated.
issue: uibcdf/topomt#75
status: open
opened: 2026-10-01
closed:
severity: medium
verification: reproduced
area: [dfnd, metrics]
guard:
normative:
blocked_by: []
supersedes: []
---

# DFND solvent-volume precision contract

## What

Fixed-order quadrature is exposed as `exact` and returns no error estimate.
MC normal-approximation widths collapse to zero in all-hit/no-hit samples.
Developer prose overstates these as exact integration or rigorous uncertainty.

## How

At `7bd47faba6179a6e02444331e442acd251572564`, use the tetrahedron with vertices
`(0,0,0)`, `(1,0,0)`, `(0,1,0)`, `(0,0,1)` and an interior ball centered at
`(0.2,0.2,0.2)`, radius 0.1. Analytic empty volume is
`1/6 - 4*pi*0.1**3/3 = 0.16247787646188028`.

| n_quad | computed empty volume |
| ---: | ---: |
| 6 | 0.16246969604365874 |
| 12 | 0.16247674509070278 |
| 24 | 0.16247772687537632 |
| 48 | 0.1624778572018284 |

With radius 0.001, `n_samples=8`, seed 0, MC returns volume `1/6`, error 0,
although analytic empty volume is `0.16666666247787645`. The fixed-order
integral and finite-sample interval need distinct documented accuracy states.

## Why

Consumers need a trustworthy uncertainty contract. #62's occupied-volume gate
cannot inherit false certainty from a denominator or numerical method label.
Semantic maturity is separate from numerical accuracy and biological validation.

## What was refuted

The one-dimensional interval union is analytic; that does not make the complete
quadrature integral exact. Sampling reproducibility does not establish interval
coverage. These findings do not imply all existing volume values are unusable.

## Scope and exclusions

Existing solvent methods, result precision/uncertainty and relevant documentation.
Retain compatibility for current callers through an explicit migration. Do not
implement ligand occupancy, change region definitions or replace the entire engine.

## Acceptance criteria

Define boundary-safe finite-sample uncertainty, convergence/accuracy evidence and
metadata before changing code. Test all-hit/no-hit and partial-hit cases first;
verify analytic examples and sampling coverage. Document quadrature order and
unknown discretization error honestly. Reconcile maturity/metric wording without
conflating numerical error with region/model error.
