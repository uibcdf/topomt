# Reference-validator P1: certified analytic volume precision

Owner [#76](https://github.com/uibcdf/topomt/issues/76); first consumer #181.
This complements the [one-ball topology controls](reference_validator_p1_feasibility.md)
under the [implementation plan](physical_reference_validator_implementation.md).
It is an integration feasibility prototype, not the complete validator or P5
per-region volume qualification.

The [separate center-hull route](reference_validator_hull_checkpoint.md) now
checks geometric hull identity and box intersections. It does not extend this
analytic volume formula to clipped spherical boundaries; the admission below
still applies. Original-source domain receiving awaits managed resources.

## Admitted geometry and coverage proof

Every expanded source ball must be **strictly inside** an axis-aligned,
full-dimensional box. After exact containment reduction, each positive-overlap
cluster must have one or two maximal balls; distinct clusters have disjoint
interiors. This covers empty inputs, separate/tangent balls, nested/coincident
balls, unequal partial pairs and several separate pair clusters.

Every source atom remains accounted for by a retained maximal ball or an
explicit covering-ball map. Common-probe expansion is exact. Coincident
representatives use the smaller source ID. Squared rational predicates decide
containment and tangency. The checker validates all source coverage, each
containment, canonical maximality, every inter-cluster disjointness obligation
and each partial-pair classification independently of producer search.

Triple clusters and three-ball overlap chains are unsupported, even without a
simultaneous triple intersection. Domain contact/clipping is unsupported by this
analytic route. It rejects these geometries; it does not discard balls or replace
a hull by a box. The earlier partition checker retains its different scope.

## Trusted analytic and arithmetic derivation

Integrating circular sections gives sphere volume `4*pi*R^3/3` and spherical-cap
volume `pi*h^2*(R-h/3)`. For a partial pair of radii `a,b`, distance `d>0`, put
`s=a+b`, `t=a-b`. The radical plane is at
`x=(d^2+a^2-b^2)/(2*d)` from the first center. Add caps of heights `a-x` and
`b-(d-x)` to obtain:

```text
V_intersection/pi = (s-d)^2 * (d^2+2*s*d-3*t^2) / (12*d)
V_union = pi * (4*(a^3+b^3)/3 - V_intersection/pi)
```

Disjoint cluster interiors make their volumes additive. Nested balls do not
change the union. Tangent boundaries/zero-radius points have zero volume;
that measure fact does not establish connectivity. Subtract the complete
occupied-union volume from the exact box volume.

All irrational evaluations have explicit enclosures:

- For rational squared distance `q>=0`, compute
  `n=floor(sqrt(floor(q*2^(2*b))))` using integer `isqrt`. Then
  `n/2^b <= sqrt(q) < (n+1)/2^b`; exact lower-square equality makes a point
  interval. No float constructs the bounds. If the coarse lower endpoint is
  zero, retain the lens range `[0,min(V_a,V_b)]` instead of dividing by zero
  or merging distinct centers.
- Use `pi=16*atan(1/5)-4*atan(1/239)`. For `A=atan(1/5)`, addition gives
  `tan(2*A)=5/12`, `tan(4*A)=120/119`, and
  `tan(4*A-atan(1/239))=1`. The angle is between 0 and `pi/2`, hence `pi/4`.
  Bound each arctangent by a finite alternating sum and its signed next-term
  remainder. Integrating the finite geometric identity for `1/(1+x^2)` proves
  the remainder bound on the positive interval. The
  [NIST arctangent series](https://dlmf.nist.gov/4.24.E3) documents the series;
  empirical convergence does not supply our error estimate.

Exact Fraction interval addition, subtraction, multiplication, squaring and
division enclose all operand combinations. Intersect lens bounds with its
known `[0,min(V_a,V_b)]` range and free volume with `[0,V_box]`. Those are
physical inequalities, not numerical epsilons.

Producer/checker share these **declared trusted elementary formulas and interval
primitives**. The checker verifies geometric admission and recomputes endpoints;
it does not trust the producer's grouping or claimed bounds. This is not a second
independent cap-formula implementation or a machine-checked proof of Python.
Independent analytic fixture formulas provide additional controls.

## Precision contract and finite stopping

`VolumeRequest` records absolute tolerance in `nm**3`, dimensionless relative
tolerance, or both. At least one is enabled; values are finite/nonnegative.
The saved reader validates both units and canonical rationals. This developer
numerical contract performs no implicit conversion/application-policy change;
public quantity receiving remains P6 work.

Every enabled constraint must pass on `[L,U]`: `U-L <= absolute_tolerance` and
`U-L <= relative_tolerance*L` with `L>0`. Certified `[0,0]` has explicit relative
handling; `L=0<U` cannot pass relative precision. Negative/reversed bounds are
rejected. Zero error remains literal: an empty obstacle family has exact box
volume, while a positive sphere's irrational volume is not rounded to exactness.

The producer increases constant/distance refinement geometrically until success
or both finite ceilings: 0..512 arctangent terms, 0..4096 distance bits, at most
512 atoms. A stopped result retains valid bounds with `precision_status=unresolved`
and `stop_reason=refinement_limit`. No radius, atom or tolerance changes to fit
the budget. The certificate stores actual/maximum refinement and the request;
the checker rejects inconsistent budgets, false containment/disjointness,
unaccounted atoms, altered units or endpoints. Same-model refinements nest the
bounds. This prototype adds no persistent analytic-volume resume; partition
resume keeps its own contract. Volume resolution supplies no topology label.

Portable rational numerators/denominators have an explicit 20,000-decimal-digit
ceiling each. Chunked conversion supports high-refinement controls without
changing Python's global integer-string limit. Oversized records are rejected
before unbounded conversion; canonical earlier model/certificate bytes stay
unchanged. A regression retains the maximal 512-term/4096-bit unresolved pair
certificate with JSON round-trip and checking. This operational ceiling is
not a physical size cutoff.

## Frozen precision controls and diagnostic

The [pre-execution protocol](../evidence/reference_validator_analytic_volume_v1/protocol.json)
freezes five geometries at `k=8,16,24,32`, requiring absolute error
`V_box*2^-k` **and** relative error `2^-k`:

| Model in `[-4,4]^3` | Independent total-free-volume formula |
| --- | --- |
| Unit sphere | `512-4*pi/3` |
| Two separated unit spheres | `512-8*pi/3` |
| Nested/coincident balls, maximal radius 2 | `512-32*pi/3` |
| Two unit spheres at distance 1 | `512-9*pi/4` |
| Two unit spheres at distance `sqrt(2)` | `512-(4/3+5*sqrt(2)/6)*pi` |

Three more profiles freeze exact zero-error success for no obstacles, an
unresolved zero-budget pair attempt and unresolved zero-error for a positive
sphere at finite budget. Expected dispositions/formulas are controls, not
inputs to the numerical formulas/checker.

Other tests cover unequal caps, separate clusters, probe expansion, exact
translation/scaling/source order, near tangency/coincidence at `2^-80` differences,
coarse bounds, corruption, saved reading and CLI overwrite rejection. The saved
checker imports no producer, DFND, NumPy, gmpy2/MPFR, mpmath or SymPy.

An **optional diagnostic** compares pi/sqrt intervals to MPFR at 1024 bits using
downward/upward rounding. The [gmpy2 context documentation](https://gmpy2.readthedocs.io/en/latest/contexts.html)
and [MPFR interface](https://gmpy2.readthedocs.io/en/latest/mpfr.html) describe the
consumed controls. Explicit context managers preserve the prior policy. The
capture records actual provider versions. This is secondary evidence, not a
runtime dependency or the geometric proof; no shared environment is changed.

## Retained receiving and checks

Source/protocol `580f1c016db48cc7041d9731ddc88501b87fd45a` produces the
[original receipt](../evidence/reference_validator_analytic_volume_v1/receiving/receipt.json).
Twenty ladder profiles pass both requested tolerances, including all five
models at k=24 and k=32. Exact empty-obstacle volume passes zero error. The two
deliberate unresolved profiles preserve their enclosures and requested errors.
The retained original models/certificates/verification records and optional
constant audit occupy 71 JSON files, 129,323 bytes, with raw checksums.

The explicit audit uses gmpy2 2.3.2 and MPFR 4.2.2 at 1024 bits. The capture
uses one CPU and a 2 GiB address ceiling (0.28 seconds as a bounded process,
peak RSS 27,112 KiB); its receipt retains the distinct internal measurement.
These are finite resource receipts for small controls, not speed comparisons.

The final selection passes 161 tests: prior 106, 53 new volume controls and two
codec controls. Both optional MPFR diagnostics actually execute in this source
receiving. Saved proofs are also checked with all numerical engines blocked.
Repository Ruff/format, scoped mypy on 21 source files (3.11 syntax, actual 3.14
dependency target), report indexes and offline finding checks pass. The existing
`topomt-dev` prefix supplies mypy; no environment is changed. Tests use one CPU,
2 GiB and 12.64 seconds (peak RSS 95,060 KiB). All 355 original six-case files
are checked unchanged. This is selected Linux source evidence, not full-suite,
installed-package, supported-minor or platform qualification.

## Disposition and next work

This demonstrates validated analytic integration on a precisely admitted
decomposition, as an alternative to boundary-cell volume convergence. It does
not select the general architecture or qualify arbitrary intersections, hull
clipping, exhaustive multi-ball regions, boundary patches or per-region targets.
The nineteen original six-case profiles retain their scopes: these boxes cannot
substitute for their atomic-center hulls. No native #181 correction follows.

Under #76, continue the general construction/clipping decision and its validated
boundary integration strategy using these controls. P1 remains partial; broader
P2/P3/P4/P5/P6 gates remain open. Host/source/model provenance is retained;
automatic public attribution and API/package admission remain P6. No execution
of DFND, SBL or CGAL is claimed.
