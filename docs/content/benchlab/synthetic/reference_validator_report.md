# Reference validator: the six-system report

All six current synthetic BenchLab systems were run with their **19 frozen
probe profiles**, dated **2026-11-13**, under [#76](https://github.com/uibcdf/topomt/issues/76).
Every scheduled analysis completed. This report describes the current exact
validator's answers and measured cost; it is not full qualification of the
future connected-region validator.

The important result is the distinction between a verified local fact and a
complete global answer. Points and supplied continuous paths are checked against
every atomic ball. Only the tetrahedron at 1.7 Å receives a complete zero-region
proof in this run. General component enumeration and per-region precision remain
unavailable on the other profiles.

## What was run

Inputs, radii and probes are the unchanged sources from the
[joint six-case review](six_case_review.md). The domain is the closed convex hull
of every atomic center; strict expanded-ball contact is excluded. Received nm
binary64 values are interpreted as exact rationals. Exactness concerns this
declared rigid-ball model and its numbers.

The fixed queries are the origin, six signed coordinate rays ending exactly on
the hull, four additional face-centroid rays for the tetrahedron, the earlier
bent interior tube candidate and the dumbbell's named chamber anchors/axis.
There is no new path search or native DFND execution. Valid-ray counts below
are counts of these specific candidates, **not counts of openings or regions**.

Each saved model and proof is independently checked. An occupied point or an
invalid path never establishes that its entire component is absent. The common
whole-hull route supplies sufficient complete-cover/free tests; otherwise it
reports unknown. For the four-center tetrahedron, a fresh exact partition also
runs on `conv(the same four centers)`, retaining its separate model/proof with
identical atoms, radii, probe and source. This is the same physical hull, not a
bounding-box substitution or general hull-subdivision admission.

## Measured resources by system

All cases use **one CPU and one numerical thread**, sequentially in fresh worker
processes. Times include startup, source receiving, verification, queries and
proof persistence. Each case contains three probe profiles except the closed
shell, which contains four. A larger total is therefore not a direct algorithm
speed comparison between equal tasks.

| System | Probes | Wall time (s) | CPU time (s) | Peak RSS (MiB) | Initial receiving / hull check (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Regular tetrahedron](regular_tetrahedron/index.md) | 3 | 2.469 | 2.448 | 51.43 | 0.422 |
| [Closed shell](closed_shell/index.md) | 4 | 62.124 | 62.056 | 56.59 | 12.394 |
| [Shell with an opening](shell_with_opening/index.md) | 3 | 37.972 | 37.937 | 55.64 | 9.621 |
| [Narrow, densely sampled tube](straight_tube_narrow_dense/index.md) | 3 | 2.973 | 2.936 | 52.07 | 0.872 |
| [Wide, sparsely sampled tube](straight_tube_wide_sparse/index.md) | 3 | 13.422 | 13.339 | 53.38 | 3.492 |
| [Dumbbell](dumbbell/index.md) | 3 | 45.921 | 45.886 | 55.71 | 11.658 |

Total batch wall time: **164.953 s**. Summed worker CPU: **164.602 s**. Maximum worker RSS: **56.59 MiB**.

The host CPU was **Intel Xeon E5-2630 v4 at 2.20 GHz**, Linux x86_64. These are
single samples on shared infrastructure, without an exclusive resource
reservation. Workers had at most 2 GiB address space, 180 CPU seconds and 240
wall seconds. Memory/pressure was monitored every five seconds; no case was
stopped or deferred. The parent's separate peak RSS was 24.77 MiB. Peak memory
is measured per case worker; independent per-probe memory peaks were not measured.

Each case receives/validates its existing original hull proof once and reuses
that immutable geometry across probes. Every persisted probe model independently
rechecks hull equality. Hull construction from scratch is not included. The
following phase totals explain most of the measured cost; small startup,
serialization and shutdown overhead is included only in the complete totals.

| System | Initial receiving / hull check (s) | Saved-model checks, all probes (s) | Queries / proof checks (s) | Extra tetrahedral partitions (s) |
| --- | ---: | ---: | ---: | ---: |
| Regular tetrahedron | 0.422 | 0.011 | 0.113 | 1.748 |
| Closed shell | 12.394 | 48.768 | 0.747 | 0.000 |
| Shell with an opening | 9.621 | 27.666 | 0.505 | 0.000 |
| Narrow, densely sampled tube | 0.872 | 1.317 | 0.600 | 0.000 |
| Wide, sparsely sampled tube | 3.492 | 9.218 | 0.498 | 0.000 |
| Dumbbell | 11.658 | 33.372 | 0.708 | 0.000 |

## All nineteen observations

`Unknown` is an unavailable global answer, not zero regions. The last column is
the probe phase after shared case receiving, including its own saved-model
recheck. Exact CPU and per-phase samples are retained in the downloads.

| System | Probe (Å) | Origin | Valid axis rays | Additional selected checks | Complete component count | Profile time (s) |
| --- | ---: | --- | ---: | --- | --- | ---: |
| Regular tetrahedron | 1.2 | free | 0/6 | 4/4 face rays valid | Unknown | 0.899 |
| Regular tetrahedron | 1.4 | free | 0/6 | — | Unknown | 0.839 |
| Regular tetrahedron | 1.7 | blocked | 0/6 | — | 0 | 0.137 |
| Closed shell | 0.05 | free | 0/6 | — | Unknown | 12.266 |
| Closed shell | 0.2 | free | 0/6 | — | Unknown | 12.371 |
| Closed shell | 1.4 | free | 0/6 | — | Unknown | 12.452 |
| Closed shell | 5 | blocked | 0/6 | — | Unknown | 12.465 |
| Shell with an opening | 1.4 | free | 1/6 | — | Unknown | 9.446 |
| Shell with an opening | 3 | free | 0/6 | — | Unknown | 9.420 |
| Shell with an opening | 5 | blocked | 0/6 | — | Unknown | 9.333 |
| Narrow, densely sampled tube | 1.2 | free | 2/6 | bent interior reference: valid | Unknown | 0.689 |
| Narrow, densely sampled tube | 1.4 | blocked | 0/6 | bent interior reference: valid | Unknown | 0.656 |
| Narrow, densely sampled tube | 2.5 | blocked | 0/6 | bent interior reference: invalid candidate | Unknown | 0.600 |
| Wide, sparsely sampled tube | 1.4 | free | 2/6 | — | Unknown | 3.308 |
| Wide, sparsely sampled tube | 2.5 | free | 2/6 | — | Unknown | 3.241 |
| Wide, sparsely sampled tube | 5 | blocked | 0/6 | — | Unknown | 3.197 |
| Dumbbell | 1.4 | free | 0/6 | chamber axis: valid; chamber anchors free/free | Unknown | 11.365 |
| Dumbbell | 2.2 | blocked | 0/6 | chamber axis: invalid candidate; chamber anchors free/free | Unknown | 11.361 |
| Dumbbell | 6 | blocked | 0/6 | chamber axis: invalid candidate; chamber anchors blocked/blocked | Unknown | 11.388 |

### Regular tetrahedron

At 1.2 Å, the four face-centroid paths are all free; the six coordinate-axis
paths are all blocked. This illustrates why a finite choice of directions can
miss access. At 1.4 Å the origin remains free while the four tested face paths
fail. Those failures alone are not an enclosure proof.

The fresh tetrahedral partition produces rigorous free-volume enclosures. Its
1.7 Å full cover certifies zero components and exact zero volume. The positive
profiles have conservative bounds and no complete component count or requested
precision. Displayed decimal lower bounds are rounded down and upper bounds up;
downloads retain the exact rational endpoints in nm³.

| Probe (Å) | Free-volume lower bound (nm³) | Free-volume upper bound (nm³) | Global count |
| --- | ---: | ---: | --- |
| 1.2 | 1.60632226963e-06 | 0.0135108435400 | Unknown |
| 1.4 | 1.40553198592e-06 | 0.0104941703177 | Unknown |
| 1.7 | 0 | 0 | 0, complete |

### Closed shell

The origin is free at 0.05, 0.2 and 1.4 Å, and occupied at 5 Å. None of the six
fixed axis rays is free. **This does not certify a sealed shell:** the earlier
0.05 Å reference independently establishes 13 access paths along other
directions. Those paths are not replayed by this query policy. Likewise, this
run's occupied 5 Å origin does not replace the older whole-hull cover reference.
Global connected-region count and a precise free volume remain unknown here.

### Shell with an opening

At 1.4 Å the origin and the +Y path to the exact hull boundary are free. At 3 Å
the origin remains free but all six tested axis paths fail. At 5 Å the origin
is occupied. The first result certifies one supplied route; it does not count
all boundary patches. The later failures do not independently prove enclosure
or full exclusion. Earlier complete references retain their separate scopes.

### Narrow, densely sampled tube

At 1.2 Å, both axial rays and the selected bent interior polyline are free.
At 1.4 Å the origin is occupied and those origin-based rays fail, but the bent
polyline remains continuously free against **all 81 atoms**. At 2.5 Å that
candidate also fails. A blocked straight route can coexist with another free
route; rejecting the last tested candidate does not prove all routes absent.
The older complete exclusion reference at 2.5 Å is not reclassified as a newly
computed general-cover certificate by this run.

### Wide, sparsely sampled tube

At 1.4 and 2.5 Å the origin and the two axial hull-reaching rays are free.
Together these rays provide a continuous axis through the finite hull. They do
not enumerate physical ends or disconnected small regions. At 5 Å the origin
is occupied and all tested rays fail. Complete exclusion remains established
by its older separate reference, not by these point/path failures.

### Dumbbell

At 1.4 Å both named chamber anchors are free and their supplied connecting axis
is continuously free. At 2.2 Å both anchors remain free, while the origin is
occupied and that connecting candidate fails. This run **does not certify that
the anchors are disconnected**; that stronger conclusion belongs to the earlier
separator reference. At 6 Å both anchors and the origin are occupied; this is
not a new whole-domain exclusion proof. No global region count is assigned.

## Evidence and next development gate

The run retains **305 checked query outcomes**: **187 accepted proofs** and **118 invalid path candidates**. These are successful checks of their declared outcomes, not that many detected regions. **One of 19 profiles** receives a complete global count; the other **18 remain unknown** under the available routes.

Producer/source and protocol are fixed at
`2b21cb2ee63093734ff71f1f70bd4ede7a53ebbb`. The archive retains exact models,
all proposed certificates and checked outcomes, worker logs/resources, original
inputs/proofs/references and the exact standalone checker source. A manifest
binds every included byte. Saved proof checking needs no DFND or quantity
dependency; full receiving needs the recorded quantity stack and source checkout.

- {download}`Structured summary <artifacts/reference_validator_panel_v1/summary.json>`
- {download}`Frozen protocol <artifacts/reference_validator_panel_v1/protocol.json>`
- {download}`Measured receiving receipt <artifacts/reference_validator_panel_v1/receiving_receipt.json>`
- {download}`Proofs, exact models and checker <artifacts/reference_validator_panel_v1/receiving.zip>`
- {download}`Archive manifest <artifacts/reference_validator_panel_v1/bundle_manifest.json>`

All 355 earlier frozen case files retain their bytes. These observations do not
change DFND, Topography labels or the current #181/#180/#184/#188 dispositions.
There is no third-party speed/accuracy comparison or protein generalization.

The next scientific gate is complete hull-clipped free-region construction,
including separation and boundary incidence, followed by certified per-region
volume precision. Execution of all 19 profiles here is coverage of the current
queries; it does not complete the planned P5 qualification or make the developer
validator a supported public API.
