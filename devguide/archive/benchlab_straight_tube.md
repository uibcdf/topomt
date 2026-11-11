---
summary: Establish the straight-tube BenchLab unit with independent passage and wall references.
issue: uibcdf/topomt#178
status: resolved
opened: 2026-11-10
closed: 2026-11-10
severity: medium
verification: measured
area: [dfnd, validation, docs]
guard: tests/test_tube_notebook_delivery.py::test_downloaded_tube_references_replay_with_only_the_supplied_helper_tree
normative:
blocked_by: []
supersedes: []
---

# Straight-tube passage study

## What

The maintainer selects the next case after the finite three-case checkpoint.
Create a descriptive `cylinder_tube` study unit with independent references,
separate `system.ipynb` and `dfnd.ipynb` stages, and actual public receiving.
The broader independent-reference panel remains #76.

## How

Review the existing clean-tube catalog input and generator, freeze full-precision
coordinates/radii/maps and bounded protocols before any new DFND query, then
verify continuous passage, lateral-wall and selected blocked regimes.
Reference computations use captured coordinates and independently checked
certificates, never the detector's answer as their oracle. Selected probes and
numerical budgets precede native observation. Keep exact/global quantities
unavailable where these references do not establish them.

## Why

A finite many-cell passage tests two-end connectivity, native/public support,
physical boundary interpretation and graph-derived candidate paths. Its discrete
atomic wall is not automatically an ideal continuous cylinder.

## What was refuted

Catalog shape names, previous channel counts and a plotted centerline do not
prove a collision-free passage or exactly two physical openings. A blocked fixed
axis does not exclude a different curved path. Finite carrier volume, free-center
volume and globally accessible/swept volume remain distinct.

## Scope and exclusions

One existing generator family, retained catalog/history, independent references
and bounded original native/public observations. No automatic original-provider
execution, remote coordinate submission, protein characterization, paid/unreviewed
provider admission or installed/full-platform qualification. Comparator eligibility
and existing CAVER/MOLE investigations retain #155/#156 and later fixed protocols.

## Acceptance criteria

Commit inputs/protocols before capturing reference/native answers. Retain
independently checkable passage/wall/blocking certificates or explicit unresolved
states; meaningful corruption, unit/map and relevant source/public regression
guards; fresh independent notebook kernels; readable case navigation/figures;
applicable Ruff/scoped typing, reporting/comparative and strict documentation
checks. Record actual source identities and measured one-CPU resource use.
Preserve all earlier study bytes. A new defect gets its own owner and test-first
scope rather than a revised expected scientific answer.

## Delivery and bounded disposition — 2026-11-10

The first study unit is delivered at source 7f2e2a84ee2a1f9bcf34a5680426a888de36e0ce:
separate executed system/native notebooks, independent references and preserved
initial attempts, actual raw/typed/public receiving, two reviewed figures and
a complete source-bound ZIP. Inputs/protocols precede new queries; the native
scientific source is b07a20ed0ee1533cc16a0b6e30ace73c2ab09ac4. Both notebooks
run independently inside the checkout and from the exact final ZIP extracted
in /tmp with clean committed TopoMT imports. All 359 download files verify.

The selected checks pass 106 tests with three strict expected failures owning
unfinished scientific targets (#180 twice and #181 once). Pure reference guards
include corrupt support/units/claimed clearance, complete segments rather than
station samples, independent two-end wall inventory and rigid/source permutation.
Ruff passes globally; scoped mypy passes four changed source modules. Full tests,
installed-release/platform support and broader validation remain #16/#76.

Strict Sphinx on a clean committed source succeeds without warnings: 96 HTML
pages and 8,975 local targets checked. Exact documentation and portable receipts
are in devguide/evidence/benchlab_tube_{documentation,portable}_receiving_v1.json.
No prior three-case notebook/input/archive changed. Actual one-CPU resource
measurements and kernel/source identities are retained.

This closes establishment of the study unit, not qualification of DFND on this
tube. Stay on this input: #180 owns native physical arrangement budget, #181
owns the local-candidate/all-atom diagnosis and public policy decision, and #76
retains certified physical paths. Current cards/hub/lifecycle/method/case summaries
are reconciled. No original-provider comparison, protein characterization,
optimal bottleneck, aperture area or free-volume precision is claimed.

## Presentation correction before final publication — 2026-11-10

Actual Chrome review exposed rich Markdown tables rendered as literal pipes in
Sphinx and long plotting inputs between explanations and figures. The same #178
delivery replaces only table serialization with escaped semantic HTML and folds
web code inputs. The prior cell protocol is preserved; a new notebook-output
guard checks actual HTML tables. Source/native/reference semantics and all old
three-case bytes remain unchanged. Fresh source and extracted-download kernels
and a strict clean-source documentation build are repeated for the revised reader.
Later v2 portable/documentation receipts supersede the v1 reader receipts for
presentation only; the original b07a20e scientific observations remain retained.
The first own Pages attempt 42946451225 was cancelled before final delivery so
that the corrected reader could be published together.
