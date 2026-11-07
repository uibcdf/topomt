# DFND development plan after the repository review

Date: 2026-11-06, America/Mexico_City. Status: **proposed development sequence**.
Reviewed source: `3f89ae3bb44f38c5bb56966e8f45a931d4a9215b`.
GitHub state was checked on 2026-11-07 UTC, including later issue comments.

DFND has a substantial working implementation. The next investment should make
its numerical claims defensible, repair specific public-contract defects, and
complete the shared Topography model without rebuilding delivered foundations.
Rust and bounded-memory execution belong in this sequence; their success needs
measurements against stable numerical contracts.

This plan consolidates the existing [joint audit](audit_topography_2026_10_01.md),
[Topography implementation route](../topography_implementation_route.md),
[reference gate](../pending_proposals/dfnd_reference_validation_panel.md) and
[volume defect](../pending_bugs/dfnd_volume_precision_claims.md).
It proposes work; it does not accept a new scientific definition, change defaults,
resume the paused notebook laboratory or close an issue. The accompanying
[review evidence](review_2026_11_06.md) records scope, reproductions and limits.

Conceptual follow-up: the [core theoretical reconstruction](core_theory_review_2026_11_06.md)
adds a prerequisite before scientific kernel changes: reconcile existential
residence, local gate observations and physical transit, and choose the intended
relationship to all-atom free space. It also makes convexity/boundary development
an explicit workstream below. The small API fixes remain independently useful;
their success does not resolve that theoretical question.

## Delivered foundations

| Layer | Present implementation | Remaining qualification or adoption |
| --- | --- | --- |
| Input | One selected frame, hydrogen/radius policies, source atom maps and nm-normalized geometry; array-only coordinates/radii. | State/radius provenance and molecular receiving under #97/#100; map admission before coercion. |
| Geometry | Ordinary unweighted SciPy Delaunay, constrained local residence/gate solvers, unique shared faces solved once. | Conditioning/scale policy, independent unequal-radius references, nonlocal obstruction and continuous-connectivity scope. Weighted triangulation is separate. |
| Query | Frozen mesh/query configurations, inclusive thresholds, marginality, resident/transit separation, nonresident connectors, exterior links and wet/dry components. | Override normalization and consistent side/capability vocabulary. |
| Ownership | Protected numeric snapshots/mesh, shared geometry across reprobes/deepcopy/pickle, selected-frame InputContext recovery and source-rebinding rejection. | Neutral support/provenance and remaining raw/component/feature/registry mutation paths. |
| Results | Integrated Topography, promoted concavities and Mouths, `.dfnd` raw/mesh/network access, typed registries/selectors. | Discoverable maturity/availability, coherent advanced access and source-aware addon adoption. |
| Descriptors | Morphology, motifs, shortest-distance skeletons and lineage/track helpers. | Policy calibration, branch robustness, correspondence/trajectory ownership and biological usefulness. |

The ordinary public entry is `get_topography(..., method='dfnd')`; the global
method default remains Pocketeer. The lower-level `dfnd(...)` dictionary route
and `DFNDData.at_probe(...)` have different return contracts: `at_probe` returns
DFNDData, rather than a newly promoted Topography. Examples should explain this
progression instead of introducing competing facade types.

The #74 shallow-registry-copy correction, #60 numeric snapshot/InputContext
slices and #95 profiling-resource fix are delivered. Preserve their guards.

## Scientific claims to keep separate

DFND currently defines a **local-clearance discrete graph model**. Residence
maximizes minimum clearance to four vertex balls with the centre constrained to
a closed tetrahedron; a gate uses three face balls and a closed triangle. This
does not alone prove accessibility against every atom or continuous passage
through a cell or sequence of cells.

| Output | Defensible interpretation | Separate gate |
| --- | --- | --- |
| Topological volume | Sum of resident carrier-cell volumes. | Includes atom-occupied space; not solvent or participant occupancy. |
| Default solvent estimate | Finite lattice excluding four local balls; resolution 8 has 165 points/cell. | Nonlocal atoms, discretization and convergence. Not a proved bound. |
| On-demand solvent volume | Empty carrier volume excluding all gathered reaching reference balls. | Sampling intervals/numerical convergence under #75. Bare vdW exclusion differs from probe-inflated centre space. |
| `exact` volume | Current deterministic finite quadrature. | Compatibility decision and numerical-error metadata; `None` statistical error does not mean zero numerical error. |
| Channel skeleton | Shortest-distance graph skeleton, marked `is_collision_validated=False`. | All-atom witnesses and continuous-space checks before navigation claims. |
| Morphology/confidence | Name and threshold margin under a declared policy. | Robustness, calibration and biological utility; not a probability. |
| Dry bank | Geometric network incidence. | Molecular identity, chemical interpretation or localized interface. |
| `percolating` | Finite local descriptor with no counted enclosing wall faces. | A new periodic topology contract; current DFND is nonperiodic Cartesian geometry. |

This review established neither a global counterexample nor a theorem equating
the graph to continuous free space. The research outcome may be a useful bounded
local descriptor, a stronger accessibility method, or separately named outputs
for both. Tuning synthetic labels cannot settle that decision.

## A. First implementation tranche: observable contracts

Use separate, test-first changes with the following acceptance criteria.

| Item | Evidence | Acceptance |
| --- | --- | --- |
| A1: `at_probe` override units | Reproduced: bare `0.1` becomes 0.1 nm here and 0.01 nm through the facade. | Both tolerance fields, quantities, inherited values and warning policy agree across public routes. Equivalent physical inputs retain equivalent thresholds. |
| A2: empty versus unavailable side | Reproduced: complete raw dry selection returns `[]`; typed selection raises. | Raw/typed/Topography agree for empty wet/dry/both; genuinely absent capabilities remain explicit. |
| A3: secondary skeleton branches | Reproduced `KeyError(2)` on a five-node/four-mouth graph. | Virtual mouths cannot leak between paths. Every consecutive real station pair has a real edge, independently of mouth order/previous branches. |
| A4: source-map admission | Static finding: integer conversion precedes validation and can truncate fractional labels. | Reject fractional/boolean/duplicate/negative labels before coercion; preserve nonconsecutive valid maps. |
| A5: wet/dry-neighbor vocabulary | Neighbor filters use residence/nonresidence; components use transit and its complement. | A connector fixture covers both sides and establishes the distinction; an explicit compatibility policy precedes any changed public meaning. |

In parallel, compare the four failing raw-characterization cases field by field.
Explain semantics, ordering, dependency/floating-point or provenance differences
before changing hashes. A changed SHA is neither a scientific regression by
itself nor permission to bless new output.

Replace the maturity test's vacuous experimental-motif skip with meaningful
coverage of provisional motifs and experimental features. Correct stale comments
claiming morphology does not choose feature classes: promotion already uses
Groove/Cleft refinements.

**Exit:** focused red/green evidence, explained baseline, applicable lint/types
and updated examples. These fixes need no new protein study or package rebuild.

## B. Numerical accuracy and independent references

### B1. Dimensionally consistent primitive solvers

The scale probe reproduces disagreement between scalar residence, batched
residence and gates. A length epsilon also thresholds determinants and
differently dimensioned terms. The tiny reproduced scales diagnose the admitted
numerical domain, rather than failure frequency on proteins.

Separate physical margins from dimensionless conditioning/barycentric/root
tolerances. Evaluate local coordinate normalization and explicit singular or
ambiguous diagnostics. Preserve inclusive query semantics during this repair.

**Exit:** independent analytic values/bounds for symmetric and unequal-radius
cases, slivers, near-double roots, admitted scales, rigid transforms and
permutations. Compare radii, witnesses, flags and ties; nonunique maxima need an
equivalence policy. Scalar/batch agreement and finite samples are supporting
checks, not proof of active-set completeness.

### B2. Honest volume accuracy (#75)

Replace MC uncertainty that collapses to zero at all-hit/no-hit samples with a
declared boundary-safe interval policy. Test repeated-seed coverage and small
samples. Choose the confidence interpretation explicitly; a nominal two-sigma
width is not automatically a rigorous coverage guarantee.

Expose quadrature order/convergence and unavailable error information honestly.
Decide migration for the public `exact` spelling before renaming it or changing
return contracts. Separate model, discretization, sampling and numerical error:
more samples do not repair a different spatial definition.

**Exit:** contained/covering balls, overlap lenses, near tangency and sliver
carriers with independent values or certified bounds; boundary-safe intervals
and convergence evidence. Validate counts/orders/spacing before allocation.
Keep the bulk four-ball estimate distinct from all-reaching-ball volume.

### B3. Independent reference panel (#76)

Retain the two adopted references: regular tetrahedron and probe-tight closed
shell with a free origin. The latter certifies at least one bounded
origin-containing probe-centre region, not an exact global count or empty
volume. No third notebook was executed here; the laboratory remains paused.

Propose the next bounded tranche before running it:

1. An opening with independently bounded access for the actual finite ball
   assembly, including negative and marginal controls.
2. A tube with a collision-free witness checked against all relevant inflated
   balls; route existence differs from validity of the returned skeleton.
3. Free regions separated by a certified barrier/neck transition. Do not claim
   exactly two global regions without a completeness certificate.

Freeze coordinates, radii, probe, atom population, carrier, observable, reference
method and tolerances before observing DFND. Obtain primary method sources and
independent local optimization/bounds where analytic oracles are unavailable.
Record disagreement before tuning segmentation or morphology.

The synthetic catalog (currently 69 entries) remains useful engineering
characterization. Density/radius changes alter the obstacle union; larger probes
can split components, so their
counts need not decrease. Peer methods retain their own regions/radii/measures.
A failed provider run is not a successful zero-feature result.

**Exit:** an acceptance ledger separating local accuracy, all-ball obstruction,
continuous connectivity and biological naming. B1/B2/B3 can progress as bounded
workstreams; one analytic fixture does not qualify the whole method.

## C. Finish the narrow public support/ownership boundary (#60)

Keep the accepted [conceptual contract](../topography_conceptual_contract.md).
Start with one native concavity plus its Mouth and one provider result with
incomplete geometry, rather than a speculative new class hierarchy.

- Separate spatial support from lining atoms: kind, completeness, recovery and
  explicit available/empty/unsupported/failed states.
- Retain occurrence, selected frame, source/local map, radii, geometry/query
  identity and algorithm/software provenance. Equal lining can describe unequal
  support; reproducible recovery does not certify volume accuracy.
- Decide ownership for raw/component/feature writes and registry dictionaries.
  Supported edits preserve indexes/relations and historical meaning.
- Expose definitions, maturity, thresholds and uncertainty through a concise
  inspection path, with full declared evidence accessible to advanced users.
- Adopt captured selected-frame context in addon `new_view`; render Cleft or
  report unsupported rendering. Native `Topography.show()` already recovers
  historical input and should retain that guard.

Receive MolSysMT #97/#100 under upstream source
`00abb958fb93649131d5ce5fe5e12e90cf4900e9`. Copy and ChemicalStates support have
arrived upstream; older issue-body notices are stale. This does not qualify
DFND receiving automatically. Test state/frame association, selected-state radii,
absent/ambiguous chemistry, nonconsecutive maps, edits in both copy directions
and projected persistence. MolSysMT owns representation/chemistry; PyUnitWizard
owns quantities. Explicit coordinates/radii do not require chemical preparation.

**Exit:** stable historical results and inspectable support/capability for both
native and incomplete-provider cases, without invented geometry. Versioned DFND
persistence is a later bounded decision; pickle is not a cross-version format.

## D. Measured performance and Rust (#93)

The requested outcome is to replace five active Numba volume kernels and remove
Numba from TopoMT, rather than make it optional. Preserve the Python API and a
narrow validated numeric buffer boundary. No GPU backend is a prerequisite.

Establish cold/warm measurements for mesh, residence/gates, volume, query,
promotion/motifs and repeated probes. Record actual atoms/tetrahedra/faces,
threads, accuracy, peak RSS/native and Python-traced allocations, input hashes
and exact source/environment. Use a size ladder and retained-query workloads.

Static targets, not new measured speedups, are:

- Residence's 142 candidate slots/cell and broadcast temporaries: stream/chunk
  with a declared temporary-memory budget.
- Python per-tetrahedron initialization and the 165-point lattice: five
  quadrature ports alone will not remove these costs.
- Repeated immutable incidence/spatial-index construction, whole-edge scans and
  rich-record retention: optimize the measured stages while preserving queries.
- MC/grid sample-by-atom matrices: chunk and prune spatially without dropping
  reaching balls or changing seeds/error semantics.

Use MolSysMT's private-extension/setuptools-rust pattern as a reference, retaining
TopoMT versioning/resources. Its inspected checkout was clean at
`9e1f1b1ad8bf09446374ab6f04ca7208e2717936` and was not pulled. Its packaging
evidence, including any `abi3` behavior, does not qualify TopoMT.

Port the five bounded kernels against B2's independent tests with strict FP64.
Compare accuracy and performance; fastmath output is not an oracle. Choose
further clearance/graph ports from measured bottlenecks.

**Exit:** declared behavior/error compatibility, measured cold/warm/memory
results, actual clean binaries on Python 3.11–3.14 and supported Linux/macOS,
no JIT/toolchain for wheel users, and removal of owned Numba call sites,
declarations and environment inputs. Installed-artifact qualification belongs
at this milestone, not as the next action after this review. The initial port
need not wait for all biological references in #76.

## E. Scientific usefulness and richer public analysis

### E0. Convexities and their boundaries

Treat positive relief as a central native capability. A connected dry bank can
contain many protrusions, ridges and rims, so bank decomposition alone cannot
supply their local segmentation. Current shell/lining/core candidates provide
raw support for this work, rather than complete detectors.

Select one relief family first. Define its spatial support, the neighborhood or
reference against which it projects, its prominence/elongation criterion and
the boundary/base that separates it from the remaining bank. Keep a buried core,
a solid separator, an aperture rim and an empty-space constriction distinct.
Raw descriptor development can proceed alongside C; public promotion needs C's
support/availability contract.

**Exit:** frozen single-relief, multiple-relief-on-one-bank, smooth/flat negative
and scale controls; an independently justified support and boundary; declared
probe/radius/triangulation sensitivity. Relations to nearby concavities and
molecular interface patches enrich the result without defining it by name.

### E1. Morphology and real molecular references

Separate topology, morphology policy and biological interpretation. Calibrate
provisional elongation/depth/funnel/persistence thresholds on frozen references
and disjoint holdouts. Report radius/sampling/triangulation/probe sensitivity.

Select a small annotated molecular panel once its observables are defensible.
`3ptb` is an available candidate, not a complete benchmark. Freeze site/ligand
annotations, preparation, atom/radius policies, negatives and apo/holo
distinctions. Define localization/contact/overlap/ranking metrics first.
Discussion [#92](https://github.com/uibcdf/topomt/discussions/92) and the
[benchmark catalogue](../benchmark_catalog.md) guide acquisition/provenance;
dataset discovery is not qualification. Volume, rank and geometric confidence
do not establish affinity or druggability.

### E2. Participants, relations, contacts and occupancy (#61–#63)

After C, introduce molecular participants and typed relations under #61, with
overlapping roles and distinct declared/inferred/localized associations. Dry
banks are not participants.

Then implement both contacts and occupancy under #62. Its first accepted model
uses resident-cell union `T`, all reaching reference vdW balls `A`, including
nonvertex intruders, and participant-ball union `B`:
`Omega = T minus A`, occupancy = `volume(Omega intersect B) / volume(Omega)`
only for positive denominator. These are bare vdW balls, not probe-expanded
balls or contact-weighted provider volume.

**Exit:** zero/partial/full occupancy, zero denominator, overlap deduplication,
units/alignment, pose changes and B2-compatible uncertainty. Contacts require
declared delimiting atoms, cutoff and self-pair/union policy. Contacts alone do
not complete #62.

The #63 capability inventory can proceed alongside #61/#62; runtime admission
waits for the relevant contract. Preserve provider labels/measures and explicit
unsupported operations. CASTp mouth aggregates cannot become fabricated Mouths.

### E3. Dynamics and later consumers

Build public dynamic collections on existing lineage helpers after validating
source/query/correspondence. Handle Delaunay flips, changing support, ambiguity,
birth/death and split/merge. Probe reuse does not imply one triangulation for
an MD trajectory. MolSysMT owns frame/PBC transformations; periodic DFND needs
a distinct topology contract. A chemical overlay is not a pharmacophore method.

Exploratory AI-design evaluation in #102 can later consume #62 endpoints. It
does not justify inference dependencies, reward optimization or an unvalidated
universal score during this core work.

## Dependencies and recommended next step

| Workstream | Prerequisite | Completion evidence |
| --- | --- | --- |
| Core meaning | Reconcile residence/transit and define the intended all-atom correspondence. | Explicit scientific decision and independent per-implication references before kernel retuning. |
| A: small fixes/baseline | This review and individual regressions. | Focused red/green, explained characterization. |
| B1: primitives | Frozen local objective/domain. | Independent values/bounds and conditioning policy. |
| B2: volume (#75) | Region/error contract. | Coverage/convergence and analytic controls. |
| B3: references (#76) | Selection of a bounded scientific tranche. | Independent per-observable acceptance. |
| C: #60 and #97/#100 receiving | Accepted conceptual route. | Coherent native plus incomplete-provider slice. |
| D: Rust/performance (#93) | Stable contract/tests for each ported kernel. | Measured behavior, actual binaries, Numba removal. |
| E0: convexities/boundaries | A chosen relief/reference/segmentation definition; C for public promotion. | Independent support/boundary controls, including multiple reliefs on one bank. |
| E1: morphology/usefulness | Valid reference/metric for each claim. | Calibration/holdout report and visible maturity. |
| E2: #61 → #62 | C; occupancy additionally needs B2. | Molecular identity and geometric evaluations. |
| #63, dynamics, AI consumers | Relevant support/evaluation/correspondence. | Capability-specific evidence. |

Resolve the core interpretation before selecting scientific kernel changes.
A1/A2/A3, A4 and baseline triage remain independent small implementation slices.
B1/B2, C and E0's definition can progress in parallel under their stated gates.
Select B3's next case deliberately; do not automatically restart every
experiment or retune the model.

## Tracking and validation checkpoints

Live owners remain [#60](https://github.com/uibcdf/topomt/issues/60),
[#75](https://github.com/uibcdf/topomt/issues/75),
[#76](https://github.com/uibcdf/topomt/issues/76),
[#93](https://github.com/uibcdf/topomt/issues/93) and
[#61–#63](../topography_implementation_route.md).
[#97](https://github.com/uibcdf/topomt/issues/97) and
[#100](https://github.com/uibcdf/topomt/issues/100) retain consumer receiving.
[#77](https://github.com/uibcdf/topomt/issues/77) tracks bounded typing;
[#16](https://github.com/uibcdf/topomt/issues/16) and
[#58](https://github.com/uibcdf/topomt/issues/58) retain qualification/checkpoint
evidence. Reconcile #15 against current SMonitor configuration before treating
its old diagnostic observation as current behavior.

New study findings are not new issues or queue entries. When publication is
authorized, triage them into independently closable issues using the reporting
protocol, reusing existing owners where appropriate. Helper defects in mutable,
weighted or rendered geometry remain separate from ordinary frozen DFND.

Use small direct commits with `[skip ci]`, applicable local checks and docs.
Group full CI, installation and support-matrix evidence at meaningful
checkpoints; retain deferred evidence. No packages were needed for this study.
Reassess build dependencies when D begins.

Executed evidence is bounded: **75 passed, 4 raw-hash failures, 1 maturity skip**
in the controlled current-source panel; a **67-pass API panel overlaps it**
and uses public MolSysMT 0.23.0. Neither is a full scientific suite,
installed-package result or support matrix. See the [review](review_2026_11_06.md).
