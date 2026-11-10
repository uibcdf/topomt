# Temporary BenchLab improvement workplan

Created: **2026-11-10**. Status: **active coordination plan; implementation
pending**. Scope: `regular_tetrahedron`, `closed_shell`, `shell_with_opening`
and publication of the actual TopoMT documentation.

This is the requested temporary execution checklist. It coordinates existing
issues, not a new umbrella issue or a replacement scientific contract. The
[completed review](../pending_proposals/benchlab_three_case_reader_route.md)
contains the diagnosis and measurements. The
[laboratory checkpoint](notebook_laboratory_checkpoint.md),
[three-case direction](three_case_deepening.md) and
[physical-boundary proposal](boundary_connectivity_contract.md) retain authority
for scientific scope. The DFND method-book audit under #173 remains resolved.

Update a checkbox only with its delivered commit and verification, or record an
explicit scoped disposition in the owning issue. Reading a proposal, writing
this plan, passing a cached check or closing another issue does not complete a
task. Keep unresolved work visible on the issue board.

## Starting point and intended order

- [x] **REVIEW:** source review published in `8264d64`: seven fresh-kernel
  notebooks / 43 cells pass; 95 focused tests pass; seven #151 candidate views
  remain expected failures. All 199 existing BenchLab files were preserved.
  Fresh HTML has 24 BenchLab pages and 2,273 valid local links/assets/anchors.
  No BenchLab warning; eleven pre-existing whole-site warnings remain #64.
- Last observed public state, 2026-11-10: the home returns HTTP 200 with title
  `PocketMT 1.0.0`; the synthetic BenchLab index returns 404. This is #18,
  independently of the successful local source build.
- The initial independent controls, later wall/boundary certificates and public
  receiving are delivered. Physical refinement, general path validity, volume
  precision and broader public support are separate pending work.

Work in this order: **publish the reviewed baseline → improve the reader route
and republish → physical boundaries and paths → volumes → remaining public/dry
and robustness checks → eligible comparisons and case disposition**. Add the
regressions needed by each scientific change in that change, rather than
postponing all robustness work to the end. Publication and reader work need
not wait for the scientific implementation to finish.

| Block | Owning issues | Closure boundary |
| --- | --- | --- |
| WEB: actual TopoMT site | [#18](https://github.com/uibcdf/topomt/issues/18) | Correct site identity and independently verified published pages. |
| BUILD: whole-site defects | [#64](https://github.com/uibcdf/topomt/issues/64) | Each diagnostic fixed or explicitly scoped; no blanket warning suppression. |
| READ: coherent web/Jupyter study | [#175](https://github.com/uibcdf/topomt/issues/175) | Current conclusions and executable public receiving are reachable through both routes. |
| PHY: physical patches and paths | [#151](https://github.com/uibcdf/topomt/issues/151), [#76](https://github.com/uibcdf/topomt/issues/76) | Independently checked physical observations, not renamed native face counts. |
| VOL: volume references and precision | [#75](https://github.com/uibcdf/topomt/issues/75), #76 | Defined measured sets, suitable references and honest numerical uncertainty. |
| PUB: public/dry support and relations | [#60](https://github.com/uibcdf/topomt/issues/60), [#61](https://github.com/uibcdf/topomt/issues/61), #76 | Bounded supported observations; broader architecture retains separate gates. |
| ROB: thresholds and invariance | #76, with #151/#75/#60 as affected | Meaningful mapped-support and numerical acceptance checks. |
| CMP: original comparators | [#155](https://github.com/uibcdf/topomt/issues/155), [#156](https://github.com/uibcdf/topomt/issues/156), [#158](https://github.com/uibcdf/topomt/issues/158), [#159](https://github.com/uibcdf/topomt/issues/159), [#168](https://github.com/uibcdf/topomt/issues/168) | Applicability/diagnosis first; new original execution gets a bounded owner when selected. |

## WEB — restore a usable public reading route first

- [ ] **WEB-A: establish the publishing route.** Under #18, inspect Pages
  settings, domain/redirects, publishing branch or artifact and the last actual
  deployment. Trace `.github/workflows/sphinx_docs_to_gh_pages.yaml` and its
  called action before changing them. The current workflow is release/manual
  dispatch triggered; ordinary `[skip ci]` commits do not publish this site.
  Record the exact source and deployed identities; do not infer them from a
  successful local build or a green unrelated workflow.
- [ ] **WEB-B: prepare one reviewed documentation candidate.** Check the root
  identity, navigation, install/import examples, BenchLab and DFND links. Keep
  historical PocketMT references explicitly historical. Validate the dependency
  closure actually used by the documentation workflow: its current Python 3.13
  route is not qualified by the local Python 3.14 result. Retain reviewed source
  pins where needed; diagnose missing tools/packages before asking the
  maintainer to install anything. Use one Sphinx worker, execution off for
  stored notebooks, and a bounded workflow timeout. Replace the current
  `-j auto` invocation when preparing that controlled route.
- [ ] **WEB-C: receive build diagnostics under #64.** Fix blockers to the
  published reading route, including identity, missing navigation/downloads
  and any required diagram runtime. Keep reviewed nonblocking whole-site
  defects explicitly owned if not included in this delivery. Never describe
  a build with those diagnostics as a clean whole-site build. Do not make
  closure of every unrelated warning a prerequisite to useful BenchLab access.
- [ ] **WEB-D: publish a bounded documentation checkpoint.** Commit the candidate
  before dispatch. When executing this block, run one documentation deployment
  for that exact candidate and inspect its result with the registered
  gh-run-receptor/native fallback. Retain checkout SHA, run/attempt, build
  result and deployed identity. No package release or new scientific run is
  needed merely to publish stored reviewed content.
- [ ] **WEB-E: check the served site independently.** Verify both advertised
  host forms and redirects, TopoMT identity, BenchLab's two collection indexes,
  all three case entries, DFND, notebook pages, downloadable notebooks and
  representative JSON/PDB/figure resources. Compare downloaded evidence bytes
  with the publishing source where applicable. Check figure/math display and
  a normal desktop/narrow-window reading route in a real browser. Close #18
  only with served-site evidence; #64 keeps any separate remaining defects.

**First usable delivery:** the current reviewed baseline is
readable on the public site, with its current limits visible. Do not wait for
#151 or #75 to claim completion before providing that access. Do not publish
unimplemented physical observations as already available.

## READ — make web and Jupyter tell the same current story

- [ ] **READ-A: fix the study narrative under #175.** Give each mutable case
  overview a compact table: question, probe, independent expectation, native
  observation, public objects, current conclusion and owning open issue.
  Mark dated outputs and later follow-ups clearly. The reader should see a
  geometry/result figure and its interpretation before long code/provenance.
- [ ] **READ-B: preserve the frozen notebook contract.** Existing protocols
  hash the original `system.ipynb`, `dfnd.ipynb` and comparison notebooks at
  their current paths. Keep those bytes and paths. Add an independently
  executable **`topography.ipynb` per case**, with a dated current-reading map
  linking system → native study → public receiving → later certificates →
  eligible comparisons. Link it prominently from the case overview and the
  cross-case public page. Its opening makes the original notebooks' dated
  scope clear to a Jupyter reader; do not silently overwrite them to remove
  an earlier conclusion. Keep stages separate rather than combining the
  entire study into a large notebook.
- [ ] **READ-C: add real public inspection.** In the new stage use the actual
  public `get_topography(method='dfnd')` route, full-precision frozen input,
  verified radii and parent/source atom correspondence. Show region classes,
  grounded signature versus catalog refinement, child/parent relations,
  support recovery, reporting suppression and genuine empty results. Clearly
  separate executed receiving from loading retained reference evidence.
  Physical views that are still absent remain unavailable; do not insert
  proposed field names as if they were implemented public API.
- [ ] **READ-D: bring the later conclusions into that route.** For the
  tetrahedron, show four physical patches / one native cluster / zero current
  Mouth children, and resolve the historical comparison's radius unknowns with
  the original-reader follow-up. For the closed shell, link/replay the stronger
  0.2 Å cover and the already delivered opening unit. For the opened shell,
  expose the one-patch 1.4 Å certificate and defer the tube consistently.
  Retained historical reports keep their original dispositions and dates.
- [ ] **READ-E: make presentation portable.** Supply ordinary relative links
  alongside Sphinx-specific downloads, explicit case working directories,
  tested kernel/environment requirements and a fresh-kernel Run All route.
  Produce a new versioned presentation figure fixing the opening-contact
  legend clipping; keep the original figure. Use consistent units, matched
  view ranges where comparison needs them, and captions distinguishing atomic
  balls, carrier centroids, contact triangles and physical free patches.
- [ ] **READ-F: qualify and republish this reader checkpoint.** Execute new
  notebooks independently, verify preservation hashes, links and rendering,
  and review the actual browser/Jupyter flow. Publish a second bounded docs
  checkpoint using WEB-D/E. Close/archive #175 only after its reader acceptance
  criteria pass. Runtime refinement and its scientific issues remain separate.

New narrative/evidence belongs in a new versioned directory, for example
`artifacts/reader_route_v1/`. Its protocol identifies the earlier inputs,
references and known results before new capture. A corrected current view is
not a retroactive fresh observation or a held-out benchmark.

## PHY — settle boundary observations and compatible continuous paths

- [ ] **PHY-A: implement #151's first bounded contract.** Review and record
  the chosen contract against `tests/test_dfnd_physical_boundary_contract.py`
  and the current proposal before implementation.
  Add recoverable all-atom free patches on the declared atomic-center hull,
  within-face connectivity, seam decisions and explicit unresolved/computed
  states. Preserve native whole-face links and catalog classes in this first
  increment. Do not glue across a blocked atomic edge or treat a whole
  triangle as exact patch support.
- [ ] **PHY-B: qualify contacts through actual raw and public results.** Use
  the frozen four/one/zero panel: tetrahedron 1.2/1.4/1.7 Å, closed shell
  0.2 Å, opened shell 1.4 Å. Attach patches to regions only with compatible
  continuous all-atom paths. All seven pending acceptance targets must pass
  for their delivered scope; remove expected-failure markers as capabilities
  land. The reference verifiers remain independent of DFND.
- [ ] **PHY-C: deepen the same systems under #76.** Count the physical contacts
  on the 0.05 Å shell rather than assuming its ten native links are ten mouths.
  Examine compatible within-cell/face paths and tighten access/closure
  brackets on the fixed shell/opening. Record positive witnesses, justified
  exclusions and unresolved intervals separately. A failed ray search is not
  proof against a curved path, and a local gate is not a global bottleneck.
- [ ] **PHY-D: make the promotion decision explicitly.** After inspecting the
  supported contacts, decide under #151 how they relate to public `Mouth` and
  `Percolating`, including compatibility and classification provenance.
  Four hull patches can join the same volumetric region and exterior; they
  are not automatically four channels. Distinguish boundary dependence,
  free aperture area and transport interpretation. Reconcile the public book,
  current case narrative, issue/report and comparative record in the same
  delivery; documentation alone does not resolve the runtime limitation.

## VOL — establish what the volumes mean and how accurate they are

- [ ] **VOL-A: freeze the measurement questions under #75/#76.** Keep carrier
  volume, bare free volume, free probe-center volume and exterior-accessible
  volume separate. State domain, atomic exclusion, probe, units, required
  error and computational budget before generating a reference.
- [ ] **VOL-B: start with the tetrahedron.** Establish the analytic bare
  vertex-ball-sector reference only after checking its nonoverlap/truncation
  hypotheses. Validate carrier volume separately. Probe-expanded balls may
  overlap, so they need an appropriate different reference or justified bounds;
  do not subtract those sectors as though disjointness persisted.
- [ ] **VOL-C: correct the numerical contract.** Add meaningful failing tests
  for the known quadrature/Monte Carlo issues, then implement the chosen
  convergence/error and boundary-safe sampling rules. Preserve a documented
  compatibility path for existing `exact` callers. Compare matched quantities
  and disclose unresolved numerical error; fixed-order quadrature and an
  all-hit/no-hit sample are not zero-error proofs.
- [ ] **VOL-D: extend to the two shells.** Use independent bounds/reference
  calculations and the same declared observable. Cap deletion changes both
  the atomic union and the hull; use a common comparison domain or explicitly
  account for the domain change. Qualify only the measured scope, then update
  the new reader stage and method/metric documentation.

## PUB and ROB — exploit the remaining information without inventing features

- [ ] **PUB-A, #60/#76:** inspect resident versus connector supports, native
  dry components, wet/dry boundaries, depths and refinement provenance. Make
  recovery, units, source mappings, input/query identity and unavailable
  operations inspectable. Preserve the distinction between lining atoms and
  actual geometric support, and between catalog dimensionality and geometric
  dimension. Existing registry/relation/filter checks are a starting point.
- [ ] **PUB-B, #60/#61:** exercise relevant result ownership, reuse, copy/read
  and relation behaviour through the selected public contracts. Keep native
  banks separate from molecular participants. These three controls do not
  supply every positive interface/convexity case; record honest native-only
  outcomes and leave broader participant/interface gates open.
- [ ] **ROB-A, #76 with affected owners:** choose below/at/above-threshold
  controls with explicit physical tolerance and mesh epsilon, then extend
  missing observables under unit-policy changes, rigid motion and source
  permutation. Use explicit correspondence, not equality of mesh IDs. For
  similarity scaling, scale every relevant length and tolerance together.
  Reuse already valid guards; do not label all invariance work absent.
- [ ] **ROB-B:** require nested primitive availability only where the fixed
  model/policy justifies it. Connected-component or mouth counts need not be
  monotone with increasing probe. Retain numerical marginality rather than
  rounding it into a physical decision.

## CMP — compare original methods only on qualified questions

- [ ] **CMP-A:** resolve or explicitly scope existing investigations: CAVER
  tiny-input applicability (#155), MOLE four-atom failure (#156), grid/operator
  eligibility (#158), volume-reference candidates (#159), retained CASTpFold
  job disposition (#168). Reuse original evidence first. Retrieve an existing
  remote job only by its receipt; never replace unavailable results with a
  fresh submission or an invented empty result.
- [ ] **CMP-B:** when a new execution is selected, open/reuse a bounded owning
  issue and freeze its protocol. Audit parser/selection, effective radii,
  coordinate rounding, units, probe/operator, grid spacing/orientation,
  required origins and output domain. Start with the same question, not merely
  the same label or PDB. Keep the no-payment scope and review licensing/access;
  inspect exact upstream revisions and local changes before using/updating a
  reference checkout. Original executions, native adaptations and evidence
  recovery remain distinct, with the appropriate Ackredit attribution.
- [ ] **CMP-C:** expose comparable observations and incompatible definitions
  side by side. Retain completed-empty/nonempty, unsupported, unavailable,
  failed and pending outcomes. Add comparisons progressively to the two shell
  units where eligible. Do not require every detector to support four dummy
  atoms or derive superiority from another program's crash.

## Verification, publication and resource discipline

For each delivered slice, record input/protocol and source identities, exact
checks, figures/results, limits and the next owning issue. Runtime changes are
test-first; prose-only maintenance uses documentation/governance checks.
Executable changes also need applicable Ruff/format and scoped type checks;
changed scientific routes need the real-provider attribution checks in
[the attribution guide](../attribution.md). Review affected
[DFND chapters](../../docs/content/dfnd/index.md) whenever operators, query
policies, metrics or public interpretation change.

| Change | Minimum relevant verification |
| --- | --- |
| Workplan/navigation only | Local links and MyST rendering, report index and comparative/reporting consistency. Reuse the earlier scientific run only within its recorded scope. |
| Reader notebooks/figures | One pilot, fresh kernels sequentially, no accidental provider/server calls, matching recorded outputs and preserved frozen hashes; visual review in web and Jupyter. |
| Physical boundaries/paths | Independent certificate replay, pending-to-passing #151 targets, all-atom path/support checks, real public receiving and relevant unit/map/invariance guards. |
| Volume implementation | Independent matching reference, declared error/coverage/convergence controls, numerical edge cases and descriptor/public receiving checks. |
| Documentation publication | Fresh one-worker candidate build and relevant links/downloads, exact-source remote run evidence, then independent checks of served content. |
| Comparative limitation correction | Card, hub, lifecycle metadata, current method/case summaries, issue/report and affected DFND chapters reconciled, with live readback. |

Useful repository-root commands, to run within the resource controls selected
after preflight and with the intended environment active:

```bash
python devtools/devguide_index.py --check
python devtools/comparative_findings.py --check
python -m pytest --receptor=llm tests/test_reporting_protocol.py tests/test_comparative_findings.py
python -m pytest --receptor=llm tests/test_dfnd_physical_boundary_contract.py tests/test_benchlab_public_topography.py
python -m sphinx -E -a -b html -j 1 docs .cache/benchlab-improvements/html
```

Select the relevant commands for the slice; the physical-contract command still
has seven expected failures at the starting point. Reading/replaying the old
95-test receipt does not qualify a changed runtime. A later complete target
panel and installed/support-matrix claims need their own required checks.

Before a potentially costly execution inspect Slurm/allocation, available RAM,
CPU/load, memory pressure and swap activity. Keep a conservative reserve,
including the session's 20% RAM guidance; free resources are not reserved.
Start small, one CPU/numerical thread, bounded time/memory and sequential
notebooks/tests. Monitor own intensive work and stop/reduce it if pressure
appears. Use current conditions to choose limits; do not copy the previous
resource snapshot as permission for a larger run.

Normal incremental commits retain `[skip ci]` under the maintainer's standing
instruction. Group remote validation/publication into explicit checkpoints;
a skip marker is neither a deployment nor release/full-matrix evidence.
Package installation, new remote coordinate submissions and broader scientific
qualification keep their own scope and authorization. This workplan itself
does not dispatch a workflow, start a server or execute those later stages.

## Final disposition and retirement of this temporary file

- [ ] **CLOSE-A:** each case has a concise current conclusion, qualified probe
  regimes, remaining limits, reproducible evidence and an owning issue for
  each concrete pending action. Presentation, native implementation and
  independent-reference status are distinguishable.
- [ ] **CLOSE-B:** the public site serves the verified reader checkpoint.
  #18/#175 can close for their own delivered scope even while scientific work
  continues. Broader #75/#76/#60/#61 close only against their own acceptance,
  not because three examples pass. The current three-case boundary limitation
  changes state only through the comparative-finding workflow.
- [ ] **CLOSE-C:** decide whether the necessary questions on these inputs have
  sufficient evidence to admit the next synthetic geometry. If a necessary
  question remains unresolved, retain that block or obtain an explicit scoped
  disposition; do not silently advance. These three cases cannot validate all
  DFND properties, every catalog entry, protein accuracy or a held-out benchmark.
- [ ] **CLOSE-D:** transfer decisions, regression guards and final receipts to
  their maintained contracts, issue-backed reports and case pages. Give every
  checklist item a disposition. Archive this coordination file as dated
  history and replace active checkpoint/index links with the delivered records;
  it must not remain an apparently current pending-work list after completion.

**Next executable slice:** WEB-A/B/C, followed by the reviewed baseline's
WEB-D/E. Then implement READ-A through READ-F as one coherent reader delivery.
Resume the bounded #151 physical-observation work before the volume sequence.
