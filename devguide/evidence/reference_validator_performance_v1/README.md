# Validator performance receiving, version 1

Owner [TopoMT #76](https://github.com/uibcdf/topomt/issues/76).
See the [S1--S8 plan](../../DFND/reference_validator_performance_plan.md),
[face-flux derivation](../../DFND/reference_validator_face_flux.md) and
[structured disposition](summary.json). The eight-stage plan is **not complete**. Candidate executable source is
`34e1549967c95442b60eda108909aa9772b9be8a`; per-attempt fingerprints retain
earlier intermediate scopes.
General original positive-volume precision, broad parallel qualification and
public admission remain open. Native DFND and the original evidence are unchanged.

## Matched serial work

The baseline uses archived executable source
`86b95d371256c1d54500da9c8a05f6ee642a37ac`. The current driver supplies only timing
instrumentation to that source tree. `baseline/` and `candidate_final/` each
retain three sequential measurements on the original tetrahedron 1.4 Å Model,
with 512 box leaves. Every query, partition, request and numerical bound agrees
exactly. The first candidate and separate instrumented call profile are retained
in `candidate/` and `profile/`; their source fingerprints identify their scope.

| Phase | Baseline median seconds | Final candidate median seconds |
| --- | ---: | ---: |
| Complete topology verification | 0.033786 | 0.033231 |
| Queries after that verification | 0.033788 | 0.002551 |
| Fixed-work box integration | 0.613201 | 0.244322 |
| Independent volume checking | 0.204764 | 0.203806 |

These are small fixed-work measurements, not general performance predictions.
The volume request remains unresolved; there is no time-to-requested-precision
speedup claim. The separately successful topology/query workflow demonstrates
actual reuse. These initial short measurements have one-CPU/2 GiB caps and
finite process deadlines; their external runner is retained in `drivers.zip`.
They did not continuously sample aggregate memory. The wider initialization,
checkpoint/fsync and operand-size profile remains S1 follow-up.

## Original tetrahedron face-flux feasibility

`boundary_pilot/` retains the first unrounded rational construction, its source
archive, three certificates and independent verification. `boundary_rounded_pilot/`
retains outward dyadic reduction. The exact original k=24 absolute and relative
requests are preserved in both receipts; error from rounding stays in the bounds.

| Rounded leaf ceiling | Actual triangles | Checked elapsed seconds | Free-volume enclosure, nm³ | Precision |
| --- | ---: | ---: | --- | --- |
| 64 | 63 | 0.171 | [0, 0.0006450252] | Unresolved |
| 512 | 510 | 0.470 | [0.00000775046, 0.00012339860] | Unresolved |
| 4096 | 4095 | 3.714 | [0.00002874752, 0.00006295033] | Unresolved |

The displayed decimals abbreviate the exact outward endpoints in the proofs.
Peak child RSS for the rounded pilot is about 27.5 MiB, with one CPU and 2 GiB.
The original unrounded 4096-ceiling pilot takes 15.749 seconds and builds
very large rational denominators. Rounding reduces that arithmetic growth;
both runs still miss the original target. This is not evidence that four
thousand face triangles solve arbitrary clipped-cell integration.

`checker_capsule.zip` contains the final standalone checker/source, original
Model and rounded 4096-ceiling certificate/receipt. Fresh independent checking
is tested with producer and scientific-package imports blocked. Saved checking
requires no cache, process pool or Rust backend. The historical portable
capsule and its original nineteen Models are preserved separately.

## Two-process feasibility and limits

`parallel_pilot.json` retains three matched one/two-process runs on the same
original tetrahedron. `parallel_execution.json` records two allowed CPUs, a
finite parent envelope, host samples and summed process-group RSS samples.
The complete topology and face partition are identical across configurations.
At this tiny scope process overhead dominates: median topology times are
0.074660 / 0.443759 seconds and boundary times 0.519335 / 1.452739 seconds
for serial / two workers. Parallel execution is opt-in and has no speed claim.

Each worker receives the complete Model, inherits stricter limits and gets a
share of the configured pool CPU budget. Worker AS, bounded queues, parent and
spawn-tracker address-space envelopes are explicit. The pool receipt does not
claim a measured continuous aggregate RSS peak. External five-second summed
RSS samples can miss short peaks and double-count shared pages.
Four-worker receiving, durable partial parallel resume, comprehensive injected
failures and the complete optimized original panel remain unqualified.

## Tests, attempted scopes and remaining work

The first broad run (`tests.json`) stops at its 170-second wall limit, with no
geometric interpretation. The larger bounded run (`tests_complete.json`) finishes
390 tests: 388 pass; a dynamic-verifier observation regression and a test requiring
a stricter 50-second ceiling fail. The observation regression is corrected by
looking up the independent verifier at context construction. The resource-bound
test is rerun under its actual required envelope.

`focused_final.json` then passes all 77 affected tests with one CPU, 2 GiB,
45/50 CPU-second ceilings and a 60-second wall budget: 7.52 pytest / 9.527
elapsed seconds, peak child RSS 160,684 KiB. Across these scopes 390 distinct
tests have passing outcomes, including 16 new performance/face/process controls.
The final corrected candidate is not advertised as one fresh green 390-test
invocation. Ruff/format, local Python-3.11-target mypy, governance, source
fingerprints and documentation checks retain their own final evidence.

The next scientific task is to tighten the face integral with complete cut
geometry and certified higher-order integration, first on this original input.
Keep tiny/asymmetric regions and signed uncertainty. Merely raising triangle
counts, worker counts or arithmetic bits does not qualify S4. All concrete
follow-up remains owned by #76; this work closes no native finding or issue.

Final local checks pass: Ruff/format across 725 files, mypy on 44 modules with
a Python 3.11 syntax target, report/finding indexes and 147 local navigation
links. Strict single-worker Sphinx passes with zero warnings in 19.037 seconds,
peak child RSS 288,668 KiB and notebook execution off. It uses the existing
`topomt-dev` PlantUML/Graphviz tools and bounded JVM settings. The two earlier
PlantUML environment failures and Graphviz diagnostic remain retained; they
were not scientific failures. `documentation_passed.json` records the successful
build. Hosted publication, installed artifacts and other platforms are not
qualified. `fresh_execution.json` independently accepts the saved capsule in
1.920 seconds, with the producer/scientific imports blocked.
