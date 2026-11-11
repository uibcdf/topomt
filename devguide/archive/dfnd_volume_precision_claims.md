---
summary: DFND solvent-volume precision and finite-sample uncertainty are overstated.
issue: uibcdf/topomt#75
status: resolved
opened: 2026-10-01
closed: 2026-11-10
severity: medium
verification: measured
area: [dfnd, metrics]
guard: tests/test_dfnd_volume_precision_contract.py
normative:
blocked_by: []
supersedes: []
---

# DFND solvent-volume precision contract

## Resolution — 2026-11-10

Resolved in source `b7b5a60d8d46b84ca2a9f44bcb01eeac98a4b8b2` for the
recorded uncertainty/precision contract. `measure_region_volume` and the public
`DFNDData.solvent_volume_measurement` retain conditional intervals, numerical
availability and recoverable finite support. Legacy tuple results remain.

- Sampling uses a 95% Clopper–Pearson interval; scalar error encloses its two
  asymmetric endpoints. Sampled all-hit/no-hit no longer means zero error.
  Zero is reserved for separately established geometric full/empty domains.
- Bounded order refinement requires two successive comparisons and retains all
  orders, convergence state and explicit work ceiling. Differences are a
  convergence diagnostic, not a rigorous integration bound. Legacy fixed-order
  `exact` values are preserved, explicitly with unknown quadrature error.
- Carrier, bare empty and probe-center integrals are distinct; the latter
  expands all relevant atomic radii, including nonlocal intruders. No globally
  accessible or swept-volume integral is claimed. Public quantities retain
  source/support mapping, query identity and detached scientific attribution.
- The frozen protocol at `8fd2906` predates these changes. Formal receiving at
  `1ae6958` gives 125/128 nominal 95% intervals covering the analytic control,
  above the predeclared 90% diagnostic threshold. Exact finite-binomial guards
  also pass. Analytic unit-ball and checked bare tetrahedron quadrature controls
  meet their 1e-4 carrier-volume target; actual errors are retained separately
  from estimated convergence.
- Independent Cartesian integration at `6f39143` imports no TopoMT and uses
  524,288 points per distinct support/probe with Hoeffding 99.9% bounds. All eight
  frozen domain rows meet the declared interval-width/overlap criteria through
  actual public receiving at `e7f4f41`. Identical domains reuse their reference.
  Reference half-widths are 0.56–0.81% of carrier volume, not a relative-free-volume guarantee.
- A separate paired reference at `d7aad00` compares cap deletion on the same
  parent hull. Bare/probe-center gains are positive with their own conditional
  intervals. Natural child hulls are not silently substituted as equal domains.

Evidence: [predeclared protocol](../DFND/volume_validation_protocol_v1.json),
[formal analytic/calibration receipt](../evidence/volume_precision_sampling_v1.json),
[reader explanation and per-case records](../../docs/content/benchlab/synthetic/volume_measurements.md).
The guard protects both endpoint false certainty and honest quadrature state;
public/unit/support and real-Ackredit selected/reused/absence/failure/read tests
cover the receiving boundary. Initial numerical/attribution selector: 64 passed;
subsequent numerical/documentation/status/lifecycle selector: 41 passed / one existing skip.
Ruff/format and scoped core/data/test typing pass. Strict whole Sphinx build
passes with zero warnings (15.056 s, 278,848 KiB peakRSS), one worker/CPU; final
exact-source publication has its separate reader checkpoint.

A second receiving exports clean committed source `834bdc1` into a managed
`/tmp` directory and verifies that TopoMT is imported there, with the committed
version-file digest. Strict Sphinx and local navigation pass: 86 HTML pages,
7,471 targets, zero warnings, 17.334 s / 287,656 KiB. The
[clean-source receipt](../evidence/volume_documentation_receiving_v1.json)
retains the observed cached package-version string separately from the source
SHA; this is no release-version or installed-delivery claim. The temporary
source copy is cleaned and the human worktree version stays untouched.

This is a **source-bound correction**, not qualification of every installed
release, all numerical settings, a certified general quadrature bound, physical
support/model error, global accessible volume or biological accuracy. The fast
local four-ball stencil remains explicitly provisional. Wider references and
geometry/path acceptance retain #76; installed/matrix receiving remains #16/#58.
The maintained card/hub/register and current method/case explanations are
reconciled in the same delivery; historical values and original notebooks stay.

## Historical defect and earlier documentary correction

Fixed-order quadrature is exposed as `exact` and returns no error estimate.
MC normal-approximation widths collapse to zero in all-hit/no-hit samples.
Developer prose originally overstated these as exact integration or rigorous
uncertainty. Under #173 (2026-11-09), the public/developer explanations and source
docstrings are reconciled: the legacy method name and numeric error calculation
are unchanged. This remains an open numerical accuracy/uncertainty finding,
not a current claim that the corrected text still makes those overstatements.

Source implementation continuation — 2026-11-10: test-first changes replace the
sampling width with a boundary-safe Clopper–Pearson interval and add bounded
order-refinement diagnostics while preserving fixed-order compatibility.
Structured public measurements retain observable/support/units and attribution.
The frozen [qualification protocol](../DFND/volume_validation_protocol_v1.json)
predates these changes. Initial numerical, public and real-Ackredit selector:
64 passed, 13.02 s pytest / 14.75 s wall, peak RSS 539,252 KiB, one CPU/thread.
At that pre-capture checkpoint, independent references and repeated-seed
receiving were pending. The completed source resolution above supersedes that
historical pending state.

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

## Comparative finding navigation — 2026-11-08

The public [measurement chapter](../../docs/content/dfnd/measurements.md) now
explains the actual supports/estimators and the current uncertainty limits.
#170's documentation delivery does not correct the numerical methods or close
this precision issue.

The [maintained finding card](https://github.com/uibcdf/topomt/discussions/154#discussioncomment-19482187) carries the current
scoped conclusion and dated correction/review history. This report retains its
technical evidence; before manuscript reuse follow the
[comparative-finding lifecycle](../comparative_findings.md) and review the actual
target profile. Historical observations and source fixes do not automatically
describe every current release.
