# Straight-tube evidence v1

This is the first independently referenced receiving stage for
[the straight tube](../../index.md), owned by
[#178](https://github.com/uibcdf/topomt/issues/178). The original source observation
is `b07a20ed0ee1533cc16a0b6e30ace73c2ab09ac4`. No original external detector,
server submission or protein characterization is part of this stage.

## Model and protocol order

`input.json` is the full-precision, quantity-aware 81-ball model (`qrec/0.3`),
SHA-256 `2c389178d86bc2eb3cbbfd97e12aa14d70a71acb8759c1cb3061c2ef1a67a4b2`.
`input.pdb` is the unchanged rounded catalog topology; its hash is retained in
the input. Native receiving restores coordinates from JSON and checks assigned
argon radii (1.88 Å) and source IDs (0–80). Coordinates, radii, probe and length
outputs are explicitly Å; the public query's normalized internals are nm.

The catalog generator is an existing, already studied development input. This
stage is retrospective characterization, not a blind held-out benchmark.

| Step / source | Files | Meaning |
| --- | --- | --- |
| `d3cec53` | `input.json`, `input.pdb`, `protocol.json` | Freeze input, three probes, all query policies and initial reference budgets before new queries. |
| `5e0943e` / `70dfec2` | `reference_certificate.json`, `reference_verification.json`, `reference_receipt.json` | First reference requires the origin. Its 1.395730210 Å bottleneck cannot establish the 1.4 Å passage. Preserved, not substituted for the later witness. |
| `70dfec2` / `85c0753` | `passage_v2_protocol.json`, `reference_v2_*.json` | Freeze removal of only the origin constraint, then capture/verify the bent all-segment witness: clearance 1.440735021 Å. |
| `70dfec2` | `boundary_1.2A_attempt.json` | Generic convex-nerve discovery exhausts 4,000 solver calls. No partial patch count accepted. |
| `70dfec2` / `85c0753` | `boundary_*A_v2_protocol.json`, `boundary_*A_v2_*.json` | Freeze wall-first partition before accepted discovery; all-atom positive wall covers, complete end-face nerves, seams and vertices establish two end patches. |
| `cabd622` | `native_protocol.json`, `native_initial_attempt.json` | Freeze accepted independent-reference identities before new native/public receiving. Initial direct `boundary_tolerance` keyword is a study caller mistake, rejected before DFND; the setting belongs in DFNDQuery. |
| `b07a20e` | `native_observations.json` | Actual typed-query public results, full raw/typed support audit, candidate-path segment checks, per-Topography attribution and full completed-operation attribution. |
| Reader delivery | `notebook_protocol.json`, notebook receipts | Freeze all code/prose before executing the separate system/native notebooks. Run All reads evidence and recomputes observations in memory. |

The initial notebook-table attempts and prior cell protocols are retained in
`notebook_initial_attempt.json` / `notebook_protocol_initial.json` and
`notebook_protocol_parent_table.json`. A native-link Mouth has a parent relation
and no region `component_id` or region support key. Corrected presentation
displays that relationship without altering the native result or references.

The final visual review also found that rich `text/markdown` table outputs
rendered as literal pipes under Sphinx. `notebook_protocol_markdown_tables.json`
preserves that earlier cell protocol. Current notebooks emit escaped semantic
HTML tables, render in both Jupyter and Sphinx, and fold their long code inputs
on the web. Later HTML-reader receipts identify the revised cells; the input,
reference certificates and original native observations are unchanged.

The typed-query investigation also found a missing public argument adapter,
separately fixed under [#179](https://github.com/uibcdf/topomt/issues/179) at
`b07a20e`. Scientific query defaults and kernels are unchanged by that correction.
Complete source revisions for each capture are inside its receipt.

## Reference replay

Use the complete download and its source-development environment. The independent
modules are `devtools/verify_tube_passage.py` and
`devtools/verify_tube_boundary.py`, with their included convex-face/ball-cover
helpers. They import no TopoMT; the system notebook checks that this remains true.
Replay checks retained complete certificates rather than repeating discovery
or trusting its score. `system.ipynb` and `dfnd.ipynb` can each start from a fresh
kernel with this case directory as working directory.

Reference claims are limited to the exact captured ball input, positive decision
margin 1e-6 Å, stated finite hull and explicit unbounded path tails. The bound
4.083579632 Å is sufficient for the 2.5 Å exclusion, not the exact covering radius.
The infinite axis clearance is not the globally optimal passage bottleneck.
Free aperture area, global optimal path, ideal cylindrical volume and physical
free-volume precision are unavailable.

## Source observations and pending targets

`native_observations.json` retains the original `unresolved` physical budget
states, local/public large-probe candidates and unvalidated graph skeletons.
The whole three-probe capture took 4.40 s with peak RSS 310,768 KiB. Independent
reference receipts retain their separate work/time/RSS measurements. All costly
executions used one CPU and one numerical thread, 6 GiB address-space and 120 CPU
second ceilings; host preflight showed ample memory without swap I/O or memory
pressure. Free resources were not treated as an allocation.

At 1.4 Å the selected native interior skeleton has minimum clearance
1.332434868 Å, hence a negative −0.067565132 Å margin. Its native
`is_collision_validated=False` flag is preserved. A different independently
verified bent route exists; general certified navigation remains #76.

The physical-boundary targets are open under
[#180](https://github.com/uibcdf/topomt/issues/180), and the independently empty
2.5 Å carrier versus local/public candidate discrepancy is `needs_review` under
[#181](https://github.com/uibcdf/topomt/issues/181). Strict expected failures in
`tests/test_tube_study.py` retain these scientific targets. They are not passing
qualification, and future fixes must reconcile current finding cards/hub and
case summaries while preserving these original bytes.

Ackredit sessions/capture belong to the application script/notebook. TopoMT's
completed native operation retains its own attribution, and the enclosing
capture additionally includes the actually reached NetworkX/Dijkstra skeleton
operations. No external provider is credited as if it had run.

`native_observations.json` is development evidence, not a versioned public
Topography interchange format. The source checkout's human `_version.py`
display edit was preserved during work; it is not an installed/release identity.
The delivery verifies committed-source imports separately. Earlier three-case
inputs/notebooks/archives are untouched.
