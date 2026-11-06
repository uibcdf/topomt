# Original Pocketeer argument and structural checkpoint

Date: 2026-11-05. Owners: [#101](https://github.com/uibcdf/topomt/issues/101)
and the separate fidelity program [#19](https://github.com/uibcdf/topomt/issues/19).
TopoMT producer: `cac8cbb21f79b685a669e7ede06639d3d7432b79`.

## Delivered boundary

Original `get_output` and library calls now have inspectable ArgDigest contracts.
The library admits its adapter options and nine original detector parameters;
unknown names and invalid values fail before dependency/input work. Scalar
length/area quantities become explicit angstrom/angstrom-squared protocol values.
Finite positive radii/probe/SASA, the physical radius interval, positive integer
sphere counts and literal filter booleans are checked. Zero merge distance remains
supported. Unspecified options still belong to the original engine's defaults
and do not appear as invented explicit entries in `run.metadata['parameters']`.

The provider gateways admit case-insensitive native/library/wrapper routing and
consume the boolean bypass once. Their historical native default is preserved;
the original-output default remains library. This does not qualify native value
contracts or the legacy high-level `topomt.get_topography` preprocessing.

Source/index/syntax/bypass validation and actual single-frame PDB admission reuse
shared TopoMT tools extracted from fpocket. Its existing tests remain applicable.
Pocketeer rejects a multiframe export before loading the original engine and
checks imported atom counts before detection. Selection arrays retain their
input identity; submitted rows/maps follow source order.

## Original provider and real controls

The public Pocketeer 0.4.0 wheel was installed with its complete dependency
closure, including Biotite 2.0.0. All 14 Python runtime files match upstream
tag `v0.4.0`, commit `f59cd12fbe175ebf4c34d70405c4c41476d4cc03`.
The module reports `0.3.0`: TopoMT preserves that field and additionally records
`distribution_version=0.4.0` when module/metadata origins agree. A source override
does not inherit unrelated installed metadata. The
[upstream feedback draft](version_identity_issue_draft.md) remains unpublished.

The installed original detects **two pockets** from 744 selected atoms in the
745-atom bundled 2pk4 system, after an explicit partial selection with a gap and
a translated frame 1. Direct original execution on the captured submitted PDB
agrees on ordered IDs, residue masks, defining-atom source maps, sphere geometry
and reported volume. This is a structural control, not a prepared receptor.

Both nm/ps/radian and pm/fs/radian application policies preserve scientific PDB
rows, canonical parameters and original output bytes. MolSysMT's wall-clock
HEADER/creation remark is excluded only from the comparison; original artifacts
and content-derived IDs are unchanged. Run bundles recover exact bytes after
temporary files disappear, and output coordinates survive source mutation.
This recovers ProviderRun evidence, not a saved PocketeerOutput reader.

## Executed evidence

The test-first argument run failed 63 cases and passed four compatibility cases.
The corrected identity control reproduced the missing distribution-version field
in both unit policies. Preliminary fixture iterations were corrected to use
MolSysMT's public frame append, an angular standard for the seed's box and
scientific artifact comparison rather than equality of timestamped run IDs.

The wider source invocation executed 313 cases: 310 passed, two optional-engine
cases skipped and one administrative test failed because the independent runtime
prefix contains no setuptools. Its runtime/test selection is 293 passed and two
skipped; the 18-case distribution suite separately passed in the development
tool environment. The original failed invocation is retained, not relabelled.
The focused correction battery passed 96 cases. Ruff lint/format passes across
433 files; scoped mypy 2.3.1 passes nine modules with imported bodies skipped.
Sphinx 9.1.0 succeeds: the fresh build reports 12 diagnostics in other pages and
the final incremental build eight, including the unavailable PlantUML command.
No diagnostic points to the edited third-party guide.

The exact new TopoMT wheel passes **218 installed cases, zero failures/skips,
46.02 s**: 74 Pocketeer contract/structural controls and the existing 144-case
fpocket/dispatch battery. All 621 required resources are present. All 161
distributions pass before/after RECORD checks, runtime origins are checked before
and after execution, and `pip check` passes.

The unchanged shared SDK rejects fileless Biotite PyO3 modules. The first
218-pass invocation therefore failed its final origin guard and is retained as
incomplete qualification. The successful receiving control keeps the shared
checker for regular modules and separately checks seven enumerated module-to-
parent bindings to the installed, RECORD-verified Rust extension. No module is
deleted or assigned an invented origin. The existing PyUnitWizard generated-alias
check also remains. The [SDK feedback draft](installed_origin_feedback_draft.md)
describes these additional controls and their removal condition.

## Retention and remaining work

The [archive](evidence/pocketeer_arguments_20261105.zip) and
[sidecar](evidence/pocketeer_arguments_20261105.json) retain commands, copied
tests/helpers, all outcomes, origin/file receipts, original run bundles and
artifact digests. Original wheel bytes remain in the task-owned temporary
namespace. A first clean-snapshot build reproduced #78's metadata/filename
version mismatch; the retained successful development wheel is
`0.5.0+347.gcac8cbb.dirty`. Its producer and bytes are bound separately; the live
user version edit was preserved.

No general release, full hosted suite, other platform/minor, periodic calculation,
native equivalence or biological/affinity claim follows. #16/#58 and coverage
#81 retain their backlog. Explicit chemical-state admission/binding, a source
snapshot and PharmacophoreMT receiving are the next Pocketeer slice. AlphaSpace2
and pyCASTA follow after that boundary is qualified; #19's engineering progress
and #30's independent SASA work are unchanged.
