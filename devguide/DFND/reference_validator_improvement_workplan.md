# Reference validator: implementation workplan after the tube families

Date: 2026-11-14. Owner: [TopoMT #76](https://github.com/uibcdf/topomt/issues/76).
First native consumer: [#181](https://github.com/uibcdf/topomt/issues/181).
Reviewed source/evidence baseline: `242f756712c3ee12b50c565459e75744542af6a9`.

**Status: A/B/C delivered; D/E delivered for complete topology and original
k=24 total/per-region precision on the selected nineteen-profile synthetic
panel; F delivered for two explicitly mapped native-input Models. Broader
native receiving and public qualification remain open.** Correctness,
exhaustive justified topology and certified volume error take priority over
runtime. The serial exact construction and independent reader remain the baseline.

The [analytic edge receiving](../evidence/reference_validator_edge_volume_v1/README.md)
passes all nineteen unchanged requests: thirteen positive profiles/sixteen
regions and six exact zeros. All sixteen clipped-boundary ladder controls and
nine earlier region controls pass. Historical box/range bounds remain valid at
their original, sometimes unresolved, precision. No native behavior changes.

| Package | Current disposition |
| --- | --- |
| A | Bounded proof/trust review and falsification controls delivered. |
| B | Checked source-cell progress, same-kernel resume and final exhaustive assembly delivered. |
| C | Original topology coverage is 19/19. |
| D | Complete conservative accounting and exact-cut analytic edge integration delivered, including signed faces, tiny/asymmetric regions and independently checked region assignment. |
| E | All original k=24 total AND per-region requests pass; selected serial precision receiving delivered. Full public/native P5/P6 admission remains separate. |
| F | Four whole-carrier exclusions checked on two fresh exactly matched actual-vdW Models. Common canonical-unit receiving across the original panel remains #76/#60. |

The subsequent [resumable source route](reference_validator_parallel_resume.md)
qualifies S6's controlled task/failure/recovery contract on three original
one/two-worker Models. It preserves original canonical topology proofs and serial
volume results. The later [canonical analytic checker](reference_validator_parallel_edge.md)
qualifies selected S7 serial/two-worker arithmetic with checked recovery. Full
parallel-panel and broader S8 admission remain separate.

The later [storage repair](reference_validator_storage.md) closes paired-size and
preflight-before-publication follow-up across all six saved routes. Broader
scientific/parallel receiving and native/public qualification remain separate.

### Next executable work under #76

1. Qualify common native receiving in canonical units under #76/#60 before
   asserting equality across all nineteen native/reference inputs. Actual
   assigned radii need a distinct captured Model and full proof when their
   bits differ from supplied-radius records. Preserve original public results.
2. Hand retained whole-carrier supports to #181's physical qualification/public
   reporting decision. Point checks and whole-carrier exclusions do not prove
   a positive carrier/path. Wider support and morphology retain #60/#180/#184/#188.
3. Continue the [performance stages](reference_validator_performance_plan.md)
   from the qualified serial baseline: complete cost accounting/invariant
   review, then explicit bounded process failure/resume/equivalence admission.
   The analytic edge checker now has selected fixed-frontier serial/two-worker
   qualification; the full parallel panel remains open. Rust is
   optional and requires a measured justified hotspot; no speed target replaces
   correctness. Keep the prior conservative routes as independently readable
   fallback evidence. No new geometry, protein or provider phase is selected.

This document gives the next implementation order, concrete tasks and acceptance
gates. The [implementation specification](physical_reference_validator_implementation.md)
retains the P0--P7 contracts and precision targets; the
[critical design](physical_reference_validator_plan.md) retains the scientific
model. The [source checkpoint](reference_validator_checkpoint.md) owns executed
results, while [the #76 report](../pending_proposals/dfnd_reference_validation_panel.md)
owns the issue disposition. Update these links and the active checkpoint as
work advances; a plan checkbox is not execution evidence.

## Review of the initial proposal

The five proposed improvements are appropriate, with these refinements:

- Establish a bounded mathematical/checker review before expanding receiving.
  Exact rational arithmetic prevents predicate roundoff; completeness also
  depends on the geometric argument, source coverage and implementation.
- Implement resumable **power-cell** work before longer construction or
  integration runs. Existing box/tetrahedron subdivision resume does not
  provide that capability for this newer route.
- Give volume integration its own feasibility gate. A rigorous coarse enclosure
  is useful, but does not prove the requested precision is attainable in the
  admitted resource envelope. Prototype on small controls before a large grid.
- Prove integration-to-region assignment and avoid double counting identical
  cells. A topology certificate is not a tessellation into wholly free cells.
- Advance small volume controls after the proof review; they need not wait for
  all ten outstanding topology profiles. Original receiving remains sequential,
  one synthetic family at a time, with no automatic concurrent calculations.
- Keep DFND comparison, native policy correction, public admission and scaling
  as separate gates. Neither a new reference nor a second implementation
  automatically qualifies native features or proves comparative superiority.

These refinements organize the existing #76 work rather than restart the
architecture study or select another geometry/backend.

## Historical baseline and exact scope

At the historical reviewed source, the power-cell route implemented complete regions,
free finite-domain boundary patches, their incidence, anchor assignment and
checked continuous paths on its admitted models. The retained topology coverage
is **nine of nineteen original profiles**:

| Original case | Atoms | Probes (Å) | Complete region / boundary-patch counts, in probe order |
| --- | ---: | --- | --- |
| `regular_tetrahedron` | 4 | 1.2, 1.4, 1.7 | `1/4`, `1/0`, `0/0`; retained. |
| `straight_tube_narrow_dense` | 81 | 1.2, 1.4, 2.5 | `1/2`, `1/2`, `0/0`; retained. |
| `straight_tube_wide_sparse` | 77 | 1.4, 2.5, 5 | `1/2`, `1/2`, `0/0`; retained. |
| `closed_shell` | 72 | 0.05, 0.2, 1.4, 5 | Not yet received through the complete power-cell route. |
| `shell_with_opening` | 66 | 1.4, 3, 5 | Not yet received through that route. |
| `dumbbell` | 94 | 1.4, 2.2, 6 | Not yet received through that route. |

The older nineteen-profile point/path run is a separate completed query panel,
not nineteen complete topology certificates. Nonempty per-region volume
precision remains unqualified. Analytic total-volume integration is already
qualified for its [contained singleton/pair cluster scope](reference_validator_precision_feasibility.md),
which does not cover general sphere clipping or region assignment.

The current construction has a hard maximum of 128 atoms, 48 supporting planes
per cell, 128 vertices per cell, 8192 total vertices, 32768 edges and 50000
clipping/constraint steps. These are operational admission ceilings, not
physical cutoffs. The bounded JSON reader also has a 16 MiB per-record limit.
All six original atom counts fit, but other work/record limits may still stop
a case. None of these facts qualifies general protein-scale execution.

Keep the exact received numerical model, original atom/frame maps, radii, probe,
strict contact exclusion and closed atomic-center hull. Do not substitute a
box or ideal smooth shell/tube. Experimental uncertainty, energetics, swept
probe volume, boundary area, globally optimal bottlenecks, higher homotopy and
periodic transport are separate extensions, not acceptance requirements here.

## Work order and ownership

All packages below are owned by #76 until independently scheduled themes are
split into linked issues with local reports. Native follow-up stays with its
existing issues. No new provider/server run or protein phase is selected.

| Package | Concrete delivery | Dependency / exit gate |
| --- | --- | --- |
| A — proof and trust review | Reviewed completeness-to-code map, explicit shared trusted base and additional falsification controls. | First implementation package; no unresolved claim of completeness on an admitted case. |
| B — resumable exact construction | Checked per-cell progress, interruption-safe bundles, cooperative stops and final exhaustive assembly. | A; resume/rejection tests and equivalent final proofs. Required before long new runs. |
| C — remaining topology receiving | Complete retained receiving for the shell families and dumbbell, with each unresolved outcome explicit. | A/B; all ten profiles have dispositions; only accepted exhaustive proofs count as complete. |
| D — certified region-volume construction | Verified integration partition, region assignment, bounds and a measured high-precision feasibility decision. | A for a small prototype; B for long runs; accepted topology for each per-region result. |
| E — precision qualification | Frozen total/per-region requests, verified refinement/resume and original-profile precision receiving. | D; requested levels pass or remain explicitly unresolved. Full P5 requires the required levels. |
| F — mapped DFND comparison | Recoverable spatial comparisons and scoped BenchLab interpretation. | Accepted outputs of C/D/E at the compared scope; native correction retains its own gate. |

The original dependency order starts with A/B and then the shell/dumbbell
receiving in C; those packages are delivered. Current continuation follows
the explicit next-work list above. Production receiving remains sequential.
Public admission and controlled scaling follow the later gates below.

Implementation locations below preserve the original proposed boundaries.
Use the checkpoint and linked construction records for actual delivered modules
and evidence; a path listed here alone is not an implementation:

| Package | Existing code to extend / proposed focused additions |
| --- | --- |
| A | `verify/power_cells.py`, `verify/geometry.py`, `power_contracts.py`; extend `tests/test_reference_validator_power_cells.py`, `tests/test_reference_validator_topology_controls.py` and the derivation's trust/obligation map. |
| B | Extract checked local-cell operations from `verify/power_cells.py`; add `power_runs.py`, `verify/power_progress.py` and `tests/test_reference_validator_power_resume.py`, reusing applicable `storage.py` contracts. Adapt `capture_power_cells.py` and its behavioral tests to retain progress. |
| C | Extend receiving/protocol handling in `capture_power_cells.py` as needed; add versioned evidence and saved-receiving guards patterned on the existing narrow/wide family tests. |
| D/E | Add `region_volume.py`, `verify/region_volume.py`, `tests/test_reference_validator_region_volume.py` and focused volume-resume controls. Reuse `volume_request.py`, admitted primitive/interval contracts and storage rather than changing their scientific meanings. |
| F | Implement the already planned `compare.py` with `tests/test_reference_validator_comparison.py`; retain source/observable/support bindings and explicit unsupported cases. |

Source names in this table are relative to `devtools/reference_validator/`;
test paths are relative to the repository root. Keep developer tools outside
the production `topomt` namespace until P6 admission.

## A — review the argument and challenge the checker

Review the [power-cell derivation](reference_validator_power_cell_construction.md)
against `power_cells.py`, `power_contracts.py`, `verify/power_cells.py` and the
domain/primitive modules under [the developer implementation](../../devtools/reference_validator/README.md).
Write a compact proof-obligation map covering:

1. Exact fixed-probe affine inequalities and exhaustive coverage of the domain.
2. The convex-cap/skeleton lemma, including both directions of the claimed
   region correspondence and whole-edge strict exclusion.
3. Gluing across shared faces, edges and vertices, including empty,
   lower-dimensional, coincident and identical cells.
4. Boundary-only gluing and unique incident global region for each patch.
5. Supporting-root anchor assignment and complete all-atom path verification.

Identify which routines independently reconstruct a conclusion and which
share trusted model decoding, domain halfspaces, canonicalization or primitive
predicates. The existing independent clipping/vertex/edge and graph routines
must remain distinct. Standalone import tests do not prove the shared
mathematical primitives correct; record that boundary explicitly.

Version new record kinds or incompatible conventions explicitly; never change
the interpretation of a frozen certificate in place. Preserve source-pinned
old reading and test unaffected earlier proof kinds. If the review finds a
defect in a previously accepted proof, retain its bytes and historical receipt,
mark the affected current guarantee for review, and record the bounded
correction/requalification work in #76 before reusing that claim.

Existing controls already include exact contact, `2^-80` gaps, unequal radii,
coincident/dominated and lower-dimensional cells, transformed models and
corrupted certificates. Preserve them. Extend tests to combinations that can
expose false joins, omitted pieces and false boundary associations: several
adjacent degenerate cells, asymmetric multiple regions, source permutations,
redundant obstacles and contacts on hull edges/vertices. Test nested free sets
at increasing probes without imposing monotone component counts. Cross-probe
cell geometry can be reused only after the current exact inequality test.

Create finite deterministic analytic fixtures with independently justified
expectations before their retained receiving. Generated rational examples may
supplement these controls, with seeds and limits recorded; agreement between
two programs is not their independent reference. Mutate proof content, not
just hashes: remove a real edge/cell, falsify a free predicate, merge/split a
region, change a domain face or forge a patch-to-region association.

**Acceptance:** the argument has an explicit mapping to checked obligations;
new meaningful controls pass test-first; invalid proofs are rejected; saved
checking still works without DFND, producer, NumPy or quantity packages. An
unresolved mathematical obligation stops the corresponding completeness claim
and gets evidence in #76 before further receiving; it is not hidden by tests.

## B — make complete construction recoverable

Reuse the existing record/manifest conventions in `storage.py`, `runs.py` and
`verify/records.py` where their contracts apply. Add a distinct power-cell
progress record and checker rather than treating it as an old subdivision
checkpoint. Refactor local cell verification from `verify/power_cells.py`
without importing producer clipping/search into the checker. Bind exact source
file fingerprints and numerical/record versions, not only friendly backend
names or a mutable branch name.

- A progress record binds the exact Model, construction/record versions,
  arithmetic convention, producer/checker source identities, runtime, fixed
  work configuration, verified completed cells and the exact remaining source
  atom IDs. Include zero-atom and dominated/empty-cell conventions.
- Retained cells are independently rechecked before reuse. A saved summary,
  hash or source ID alone is not a cell proof. Complete global topology remains
  unavailable until all source cells and the final gluing are checked.
- Commit progress after completed cells. A stop inside a cell may discard that
  cell's partial work while preserving earlier committed progress. Add bounded
  cooperative stop checks inside costly clipping and verification loops; a
  hard process kill cannot be assumed to run cleanup.
- Write immutable checkpoint bundles with the manifest published last; a torn
  final bundle is unusable while an earlier complete bundle remains loadable.
  Do not overwrite old receiving or assume filesystem crash durability beyond
  the documented protocol. Bound disk use, rational operand size, parsing and
  record size as well as RAM/CPU; chunk records if necessary through a checked
  manifest, without silently raising current limits.
- Keep same-run resume strict. Changes to probe, model/domain, source/runtime
  or scientific configuration require an explicit new identity and checked
  reuse path. A longer external time allowance is recorded separately from
  the unchanged mathematical configuration and prior execution segment.

Test cancellation before/after a cell and during writing, missing/duplicated
completed or remaining IDs, corrupted geometry, missing manifests and changed
model/source/configuration. A resumed run must recover the same complete
certificate as an uninterrupted deterministic control, with identical checked
region/patch/path semantics. Rechecking overhead belongs in measured costs.

**Acceptance:** a bounded interrupted original or small representative case
resumes from the last valid bundle; malformed state is rejected; all earlier
unaffected frozen proofs still check. Partial work never supplies a fabricated
global count. Add integration-frontier resume only after D defines its own obligations.

## C — receive the remaining original topology

Use the exact saved Models from the original
[nineteen-profile panel](../../docs/content/benchlab/synthetic/artifacts/reference_validator_panel_v1/receiving.zip),
retaining their numerical identities and the original source records. Freeze
new protocols before retained execution, leaving unknown global counts unset.

| Family order | Prior independent questions to preserve | New required result |
| --- | --- | --- |
| `closed_shell`: initialize at 0.2 Å; receive 0.05/0.2/1.4/5 Å | At 0.05 Å the original origin/access witnesses and thirteen boundary patches have their existing scope; at 0.2 Å the covered hull boundary and free origin establish enclosure; retain the existing larger-probe exclusion evidence. | Enumerate **every** free region and patch and recover incidence; do not turn thirteen patches into thirteen 3D regions or an enclosed origin into a one-region theorem. |
| `shell_with_opening`: 1.4/3/5 Å | Preserve the original opening/origin-to-exterior, enclosure and exclusion controls at their recorded probes. | Complete region/patch inventories with compatible anchor assignments and continuous witnesses or separations. |
| `dumbbell`: 1.4/2.2/6 Å | The named chamber anchors are connected, then separated, then excluded under their original proofs. | Enumerate extra regions independently; two separated anchors alone do not prove exactly two global regions. |

First measure representative cell construction and verification under a finite
envelope. Geometry reuse across a family's probes is conditional on identical
full power inequalities and a checked source proof; unequal radii generally
require fresh geometry. Never reuse another model's free labels or ordinal IDs.
Replay prior references against the admitted numerical model before treating
their bounds as new exact evidence; preserve their historical qualifications.

For each profile retain Model/protocol, complete certificate, independent saved
verification, anchors/paths, source identities, per-phase CPU/wall/RSS, disk/
certificate sizes, stop reasons and host observations. Distinguish fresh
construction, checked reprobe and unchanged saved reading. Summaries must link
the raw artifacts and preserve all earlier case inputs, notebooks and downloads.

**Acceptance:** all ten profiles have explicit dispositions and the nine
already accepted profiles remain protected. Count a profile as topology-complete
only after exhaustive checking. Nineteen populated rows with some unresolved
proofs do not pass full topology qualification or P5.

## D — construct certified volumes tied to complete regions

The first implemented conservative baseline is documented in the
[region-volume construction](reference_validator_region_volume_construction.md).
It uses a complete box cover of the same verified domain, scanning every
atomic ball and retaining boundary uncertainty, with labels from the checked
power partition. This avoids a second unqualified triangulator and integrates
coincident geometry once. The individual-power-cell candidate below remains
the higher-precision option; valid baseline bounds do not pass its precision
gate or the original k=24 target by themselves.

The initial implementation candidate integrates within the **checked** power
partition. On each cell the minimum-power owner determines exclusion; this
reduces the local geometry to a convex polytope minus one expanded ball.
Retain the all-atom proof of that reduction. The topology skeleton supplies
labels and paths, not volume elements or proof that whole cells are free.

### Partition and label obligations

Develop an independently checked rational tetrahedral decomposition or another
complete integration partition of each full-dimensional cell. Prove coverage,
containment and nonoverlapping interiors; equal total volume alone is
insufficient. Shared lower-dimensional faces have zero 3D measure but keep
their topological roles. Identical positive-volume cells from coincident equal
balls need a checked canonical single integration owner; source cells must
remain represented in the topology proof. Otherwise their volume is counted
more than once. Empty/dominated/lower-dimensional cells are accounted for.

For an initial adaptive rational baseline, each integration leaf is:

- **Wholly free:** prove all its points free. Its connected convex geometry
  and a checked anchor/root association assign its exact volume to one region.
  A free centroid alone does not certify a wholly free leaf.
- **Wholly blocked:** prove whole-leaf coverage and contribute zero free volume.
- **Unresolved:** retain its entire exact geometric volume as uncertainty,
  with a conservative set of every region that could occupy part of it.

The initial candidate set may include every checked region supported in the
parent power cell. Pruning a candidate needs a proof; nearest representatives
or a sample label do not suffice. If labels cannot be proved complete, retain
unresolved assignment instead of reporting per-region precision. Define and
check the seam/ownership conventions before implementing region summation.

### Bounds and consistent accounting

For region i, let L_i be the sum of wholly free volume assigned to it. A safe
U_i adds the volumes of unresolved leaves that might contain it. Compute total
L/U separately, counting each unresolved leaf **once**. Marginal per-region
upper bounds may overlap when one unresolved leaf has several candidates;
their sum need not equal the total upper bound. Preserve that shared uncertainty
in the certificate. All true region volumes must jointly satisfy the total
and per-region enclosures; reject double-counted lower volume and omitted mass.
Verified refinement must keep every lower bound nondecreasing and upper bound
nonincreasing for the same model, region identity and request.

### Feasibility before high-resolution production

Use existing no-atom, whole-cover and contained-ball controls first; compare
with independently bounded formulas already admitted by the analytic route.
Then qualify a clipped one-ball case with several known regions, deriving its
independent volume enclosure before receiving. Symmetric corner regions must
share the total volume equally, but symmetry alone is not a numeric reference.
Add an asymmetric multi-region control with its separately justified enclosure,
a tiny nonempty region and coincident-ball controls to challenge assignment
and double counting. These are small internal controls, not new BenchLab units.

Measure error width versus leaf count, verification cost, rational sizes and
storage. Establish the baseline's convergence assumptions and fair refinement
policy. A huge uniform grid is not the default route to high precision. If
boundary uncertainty converges too slowly, prototype a rigorously bounded
sphere/polytope boundary integration route on these same controls, with explicit
coverage and truncation/rounding error. Select only after the independent
checker can validate its enclosures. No dependency or foreign geometry engine
is selected merely by writing this option.

**Acceptance:** complete geometry/region assignment and conservative nested
bounds pass corruption and accounting tests; the small measured precision pilot
has a documented accepted scope or an explicit unresolved feasibility result.
A tight total interval cannot substitute for per-region integration, and a
coarse certified interval cannot be presented as meeting a requested target.

## E — qualify requested precision and resumable refinement

Reuse `VolumeRequest`: absolute tolerance has explicit volume units, relative
tolerance is dimensionless, and every enabled constraint must pass. For
`0 <= L <= U`, require `U-L <= absolute_tolerance` and, when requested with
`L>0`, `U-L <= relative_tolerance * L`. Handle proved `[0,0]` explicitly;
`L=0<U` cannot pass relative precision. A literal zero-error request needs an
exact-value certificate. Tiny components have no minimum-size cutoff.

Freeze the existing ladder `k=8,16,24,32`, with absolute tolerance
`V(D)*2**(-k)` and relative tolerance `2**(-k)`, for total and every requested
region separately. The initial P5 target remains **k=24**; k=32 is a further
stress study. This workplan does not lower the target because a pilot is slow.
Start with analytic controls and an original tetrahedron profile, then extend
to each qualified original family using measured finite envelopes.

Checkpoint the complete integration partition/frontier, ownership, candidate
labels, retained exact bounds, request, topology certificate and source/kernel
identity. Independently recheck state and transitions before resume. A resumed
run must enclose the same volumes as an uninterrupted control; request changes
start a new explicit run rather than relabel earlier precision evidence.

Test literal zero tolerance, exact-zero controls, tiny positive lower bounds,
relative-only and mixed requests, changed units, corrupt labels, overlapping
lower allocations, omitted unresolved mass and broken lineage. Unsupported
geometry and rejected input/proofs are errors, not physical empty results.

**Acceptance:** retain verified bounds and requested/achieved precision per
observable even on a resource stop. Report an unresolved target with its reason
and #76 ownership. Full precision qualification requires all required total/
region targets to pass; printing more decimal places or passing topology does
not meet this gate.

## F — compare spatial claims with DFND

Implement the planned developer comparison route only after its input/observable
contract is fixed. Reuse the actual saved native/public receiving and atom/frame
maps when they still match, recording that reuse; changed source receiving is
a separate execution. Keep local DFND capacities, native candidates, public
morphology and all-atom physical regions distinct.

Comparison should retain source-bound supports for: reference occupancy at
anchors, whole-segment path validity, exact reference region assignment,
boundary-patch incidence, proved exclusions and unresolved portions. A path in
the full hull does not prove a path inside a particular nonconvex native
carrier. Such a restriction needs its own coverage proof/admitted support
contract; an anchor test does not qualify an entire feature or carrier.

Use explicit mappings rather than ordinal component/patch/face identity. A
valid native local value may coexist with nonlocal collision; diagnose its
declared claim before naming an error. Report spatially supported agreements,
disagreements and unqualified comparisons without treating sample agreement
as an exhaustive physical proof.

The whole-hull negative controls are the first #181 consumer. Native corrections
still require an explicit local-candidate versus physical-guarantee policy,
test-first implementation, public support review with #60 and matching DFND
book changes. #180/#184 numerical/budget availability and #188 morphology retain
their owning issues. Follow [comparative-finding reconciliation](../comparative_findings.md)
before changing any finding's current interpretation; reference receiving alone
resolves none of these native issues.

**Acceptance:** every compared statement has the same model/domain/probe,
identified observable and recoverable support; unsupported mappings remain
explicit. Add additive, source-scoped BenchLab results, retaining the original
notebooks/downloads and linking stronger later evidence.

## Later admission and controlled scaling

The [performance implementation plan](reference_validator_performance_plan.md)
gives the subsequent S1--S8 sequence: measured cost breakdown, checked-state
reuse, exact incremental work, the existing general precision gate, optional
compiled kernels, bounded parallel cells/integration and full receiving.
Its [first receiving](../evidence/reference_validator_performance_v1/README.md)
delivers bounded serial reuse and experimental face/process routes; most stages
remain partial and original precision is still unmet. Bounded serial
profiling/reuse may precede completion of D/E; P7 scaling retains the scientific
gates below and does not replace the next clipped-cell integration task.

After the required synthetic scientific gates, review P6: intuitive supported
API/report, advanced certificate inspection, explicit quantities/maps, offline
saved checking, attribution, diagnostics, optional dependencies and installed
Python/platform qualification under #16. A report must separately state
topology completeness, boundary availability, valid volume enclosure and
requested precision; a single success flag cannot stand for all four.

Raise the current 128-atom/record/work envelope only with specific measured
receiving and checker qualification. Protein/model uncertainty, molecular
input admission and any outer-box exterior collar get their own selection
after the synthetic phase. Finite hull patches are not automatically mouths
to infinity, and physical regions are not automatic Topography catalog names.

Rust, exact-arithmetic acceleration, spatial pruning, bounded parallel CPUs or
GPU proposals follow measured bottlenecks and preserve the proof contract.
Retain the simple independently runnable checker and original proofs. Qualify
every proposed pruning bound and arithmetic mode; larger budgets or a faster
backend do not authorize dropping atoms, narrowing supports or changing contact.
The complementary ordinary-Delaunay/tetrahedral validator remains a later
bounded cross-check proposal: prove all-atom whole-link/subcell coverage and
matching seams before making completeness claims. Building a second full
engine is not a prerequisite for the current synthetic delivery.

## Resource and delivery protocol

- Use local sequential execution without Slurm for this phase, one CPU/thread
  by default. Inspect CPU load, available RAM, swap activity and memory pressure
  before costly work. Free resources are not reserved resources.
- Keep at least 20% physical RAM available and an adequate minimum reserve
  (initially 4 GiB); account for the planned worker ceiling before launch.
  Start with the existing 2 GiB address-space cap and measured finite CPU/wall
  budgets, not an unlimited inheritance. Larger envelopes require measured
  justification and a current host check; reserve responsiveness for others.
- Measure producer, verifier, queries, resume checks and integration separately.
  Record CPU/wall/RSS, counts, exact-operand sizes, certificate/disk bytes,
  source/build identities, host samples and stops. Samples normally remain
  five seconds apart. Summed workers exclude interstage development time.
- Stop cooperatively on pressure or budget exhaustion, keeping the last valid
  checkpoint. A hard-stop partial directory is not a certificate; absence of
  a completed result is never empty, disconnected or precise by default.
- Add behavioral tests before executable changes. Use the applicable bounded
  test selection, Ruff/format, local typing, report-index/finding checks and
  documentation checks. Do not add tests that merely assert plan headings.
- Preserve all 355 original frozen files and the later accepted family
  evidence. New results get versioned additive protocols/bundles with source
  fingerprints. Changes to code/checker/contracts require relevant rechecks;
  unchanged artifacts may be reused with an explicit identity and reason.
- Publish coherent increments with `[skip ci]`, update #76 and the checkpoint,
  and retain deferred full-suite/installed/matrix evidence under its owners.
  Completing one package does not close #76 or a linked native finding.

## Original first tranche and completion rule

The original first tranche, now delivered, was A's proof/trust map and focused
falsification controls, B's checked per-cell resume and a bounded closed-shell
pilot. C subsequently completes every original topology profile. D/E use the
frozen integration controls and original requests, with the general requested
precision gate kept separate from valid bounds and small analytic controls.

For every package retain: test-first failure where applicable, source/checker
identity, executed controls/limits, saved proof readback, achieved guarantees,
remaining obligations and next owning action. Progress is measured by accepted
scientific outputs, not code volume or the number of completed commands.

The selected scientific delivery is complete only with exhaustive accepted
topology/boundary incidence and required certified total/per-region precision
for the declared original scope, reproducible saved checking and coherent
BenchLab reporting. Any unresolved required item remains an explicit open
gate; public/molecular/scaling qualification retains its separate boundary.
