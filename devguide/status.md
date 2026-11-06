# TopoMT development status

Reviewed for machine migration on **2026-11-06**. This describes the local
handoff baseline `87fd192b03f36b0e24a279450fab3c60620244bd` and its committed
evidence. Read [the index](index.md) first, then use this page to choose the
relevant contract, checkpoint and owning issue. Dated checkpoints retain their
original producer, inputs and limits; documentation edits do not requalify them.

## Current work and delivery boundary

The documentation review is committed at `f3ffa90`; the current user-authorized
task publishes the development history and preserves local files in a separate
verified ZIP before cleaning the checkout. The previous automated long-term
implementation goal was stopped and cleared. The accepted
[original-provider programme](provider_handoff_plan.md) remains a technical
continuation plan, rather than an instruction to restart scientific work during
migration.

At the pre-publication snapshot on 2026-11-06, GitHub had 62 open issues and no
open pull requests; remote `main` was `0f82d5a`. The local scientific baseline
`87fd192` was 35 commits ahead, and the later documentation commit `f3ffa90`
made that 36. These dated observations explain the original bundle-first
handoff, not the final published state.

The authorized publication preserves the complete fast-forward history on
`main` and `work/fpocket-handoff-101`, with remote tracking configured. The local
version edit and all ignored generated files were verified in
`topomt-local-files.zip` outside the repository before the tracked file was
restored and the generated copies removed. The [migration handoff](migration_handoff.md)
now starts with a public clone. Its separate ZIP instructions preserve the old
local state without making it a required runtime or committing an obsolete
generated version. The ZIP publication receipt records the exact final SHA,
remote identities, clean-tree check and CI state. Publishing source does not
clear scientific-CI, full-matrix or installed-candidate debt.

## Implemented foundations

TopoMT contains two complementary result paths:

- `get_provider_output()` executes or recovers an explicitly selected original
  provider. Provisional version-1 records preserve pocket IDs, source indices and
  membership roles, declared geometry, attributed measurements and original
  `ProviderRun` artifacts. See the
  [provider output checkpoint](provider_pocket_output_checkpoint.md).
- `get_topography()` supplies the common `Topography`/`Feature` hierarchy.
  DFND is TopoMT's native scientific method; its raw mesh, graph and component
  evidence lives in `topography.dfnd`. Shared geometry and tessellation tools
  live under `topomt.tools` and `DelaunayMesh`. See
  [architecture](architecture.md), [API surface](api_surface.md) and
  [DFND implementation status](DFND/implementation_status.md).

Initial provider delivery [#65](https://github.com/uibcdf/topomt/issues/65),
MolSysViewer adoption [#66](https://github.com/uibcdf/topomt/issues/66), and the
Topography shallow-copy correction
[#74](https://github.com/uibcdf/topomt/issues/74) are closed bounded outcomes.
The addon displays provider pocket representations separately from canonical
Topography state. These deliveries and displayed point/sphere sets do not
establish exact closed regions or complete public-model semantic admission.

## Original-provider receiving

MolSysMT owns molecular representation, loading, selections, chemistry,
coordinates and atom correspondence. TopoMT owns original topography execution,
evidence, source maps and pocket records. PharmacophoreMT owns recognition,
complementation, query placement, tolerances, essentiality, weights and native
model persistence. Missing sibling capabilities go to their owner. ArgDigest,
DepDigest, SMonitor and PyUnitWizard retain their registered responsibilities.

| Provider | Committed bounded evidence | Continuation gap |
| --- | --- | --- |
| fpocket | Original CLI/files, source/frame/reference-state guards, prepared public PharmacophoreMT receiving and source/installed receipts. See [overview](fpocket4/overview.md). | Preserve regressions; exhaustive fidelity and general qualification remain separate. |
| Pocketeer | Original 0.4.0 argument/state contracts, engine-independent saved recovery and a prepared 46-site hydrophobic control. Producer `bb34e67` has a recorded 311-case installed qualification. See [consumer checkpoint](pocketeer/pharmacophore_handoff_checkpoint.md). | Preserve artifact/evidence identities and re-establish the receiving environment. |
| AlphaSpace2 | Original 0.1.2 argument/source contracts, schema-1 recovery and prepared public receiving at `ce4708a`: 13 pockets, retained empty hydrophobic recognition and two explicitly projected donor sites from recognized acceptors. See [handoff checkpoint](alphaspace2/handoff_checkpoint.md). | Repeat and durably preserve updated exact installed qualification and dependency-origin checks; the later interrupted attempt has no committed installed receipt. |
| pyCASTA | Existing original adapter/output and retained JSON/files; [overview](pycasta/overview.md) and [contract](pycasta/contract.md). | Original argument/source/recovery and prepared consumer qualification. Native `1a6w` parity [#53](https://github.com/uibcdf/topomt/issues/53) is separate. |
| CASTp/CASTpFold | Server/files integrations and original exports; [overview](castp/overview.md). Local modern closed-void measures have their own historical validation. | Original route/source fidelity and an explicit prepared consumer; local/native parity and residual memberships remain separate. |

The AlphaSpace2 prepared-source checkpoint retains passing execution evidence
for **523 distinct affected cases**, including eight initially skipped fpocket
cases that subsequently ran with the required executable variable. Original
skips remain visible. Two complete source flows agree under pm/fs and nm/ps;
saved public consumption works without AlphaSpace2 or MDTraj installed. These
are declared analytical hypotheses on one historical prepared reference state,
with no affinity or binding-site relevance claim. They do not qualify an updated
installed package, another platform, current sibling mains or the full suite.

Source, installed candidate and public delivery are distinct evidence classes.
Historical temporary prefixes, wheels and `/tmp` or `/dev/shm` paths are not
portable installation requirements. Use the committed archives and their hashes
to recover available evidence, and [the environment guide](packaging_and_environments.md)
to establish actual imports/dependencies. Conversation-only outcomes and missing
temporary files are not acceptance evidence.

## DFND and Topography gates

The [DFND notebook laboratory](DFND/notebook_laboratory_checkpoint.md) is paused
after regular-tetrahedron and sampled closed-shell studies. Opening, tube, neck
and new kernel studies await a separately selected resume. DFND is not required
to reproduce other methods' definitions or rankings.

Delivered groundwork includes canonical residence/transit decisions, source/local
index checks, typed mesh/query configuration, static support/context identity,
protected numerical snapshots and selected-frame input recovery. Raw dry-network,
motif and dynamic matching helpers exist without completing their scientific or
public contracts. Details remain in the
[joint audit](DFND/audit_topography_2026_10_01.md),
[implementation status](DFND/implementation_status.md) and
[Topography implementation route](topography_implementation_route.md).

Distinct unfinished gates are:

- [#60](https://github.com/uibcdf/topomt/issues/60): public context/support,
  provenance and remaining mutation adoption; delivered snapshot/input guards
  cover slices rather than the whole gate.
- [#61](https://github.com/uibcdf/topomt/issues/61),
  [#62](https://github.com/uibcdf/topomt/issues/62),
  [#63](https://github.com/uibcdf/topomt/issues/63): molecular participants,
  contextual contact/occupancy and semantic provider admission.
- [#75](https://github.com/uibcdf/topomt/issues/75),
  [#76](https://github.com/uibcdf/topomt/issues/76): volume precision/uncertainty
  and independent references. Deterministic estimator output is not evidence of
  analytic or publication-grade volume precision.
- [#97](https://github.com/uibcdf/topomt/issues/97),
  [#100](https://github.com/uibcdf/topomt/issues/100): molecular ownership/copy
  and receiving MolSysMT's independent ChemicalStates/Topology contract.

CASTp3 closed-void delivery [#79](https://github.com/uibcdf/topomt/issues/79) and
bounded radius-profile study [#80](https://github.com/uibcdf/topomt/issues/80)
are closed, rather than the immediate implementation priority. Residual
lining/rim/component membership [#88](https://github.com/uibcdf/topomt/issues/88)
and terminal-oxygen policy [#84](https://github.com/uibcdf/topomt/issues/84)
remain open with their own acceptance criteria.

## Qualification and known limitations

The last committed **complete source-suite** run in the
[2026-11-05 checkpoint](fpocket4/full_suite_checkpoint.md) executed 2,245 cases:
2,156 passed, eight failed, 76 skipped and five xfailed. All eight failures also
reproduced on the pre-ArgDigest baseline with identical exception messages.
Declared optional tools resolved two environment failures in a separate control;
four DFND characterization-hash and two viewer-selection failures remain
unresolved baseline findings. Expected hashes, numerical thresholds and missing
molecular indices were not changed to obtain a pass. Later focused green
selections do not replace that full-suite result.

Python metadata and the required matrix target **3.11–3.14**, with routine work
on Python 3.14. Public support on every minor/platform is not established by
source or installed pilots. Qualification remains
[#16](https://github.com/uibcdf/topomt/issues/16), full-CI recovery
[#58](https://github.com/uibcdf/topomt/issues/58), distribution
[#78](https://github.com/uibcdf/topomt/issues/78), and coverage
[#81](https://github.com/uibcdf/topomt/issues/81). The clean-build version/metadata
mismatch belongs to #78; existing Sphinx/reference diagnostics remain
[#64](https://github.com/uibcdf/topomt/issues/64), and typing debt is #77/#86.

Further open work includes support-library adoption #56, temporary-resource
lifecycle #96, Numba-to-Rust migration #93, optional OpenCASTp transition #90 and
independent evaluation of AI-generated designs #102. Backlog presence does not
schedule these ahead of the selected programme or authorize scientific workloads
during documentation work. Local [bug](pending_bugs/README.md) and
[proposal](pending_proposals/README.md) queues hold issue-backed analyses;
[GitHub issues](https://github.com/uibcdf/topomt/issues) also contain work without
local queued reports. Use [validation and tests](validation_and_tests.md) for
commands and acceptance scope.
