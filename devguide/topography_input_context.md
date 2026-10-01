# Input-context schema decision

Date: 2026-10-01. Owner: [#60](https://github.com/uibcdf/topomt/issues/60).
This is the bounded input-recovery slice, not completion of public spatial support.

## API and ownership

`topomt.topography.input_context.InputContext` is an engine-neutral, read-only
input record. Native DFND exposes the same instance through
`network.input_context`, `DFNDData.input_context` and `Topography.input_context`.
Other engines remain unadopted (`Topography.input_context is None`).

Required fields are an opaque `source_id` (a captured occurrence, not molecular
identity), requested `selection`, `selection_syntax`, original `structure_index`,
resolved local-to-source `atom_indices`, selected `coordinates` and `radii` as
PyUnitWizard quantities in nm, `coordinate_convention`, `coordinate_transform`, `hydrogen_policy`, and
`radii_model`. Coordinates, radii and index buffers share the native protected
storage. Selection sequences become tuples; requested order and MolSysMT's
resolved selection order are retained separately. The first supported convention is
nonperiodic Cartesian coordinates with an identity transform. Box metadata, if
present, remains recoverable input evidence; no minimum-image analysis is claimed.

Topology and single-frame structural metadata are retained as a private selected
MolSysMT MolSys. MolSysMT owns extraction, topology and copying. No duplicate
atom/residue model is introduced. `recover_molecular_system()` returns an
independent, editable selected MolSys with one frame. Its local indices are
`0..N-1`; `atom_indices` maps these back to the original input. Array inputs retain
no fabricated topology and recovery raises `ValueError`.

`local_atom_indices(source_atom_indices, *, source_id)` checks the occurrence
namespace and selected membership before mapping. Equal indices or numerical
DFND substrate keys across independently captured inputs do not establish source
correspondence. Probe queries share the same input occurrence; copied/restored
records retain that occurrence. DFND mesh/query/component keys remain under DFND,
with their existing numerical meaning. This record is not a query, classification
or universal atom-identity record.

Public getters return independent array metadata or immutable values; public
attribute replacement is rejected. Recovery cannot mutate retained topology.
Python copy/pickle are supported; this delivery defines no JSON/wire schema or
cross-version pickle promise. The Python API is additive and provisional until
the complete #60 context/support gate is validated.

## Compatibility and mutation boundaries

`Topography.molecular_system` remains the original-input compatibility reference.
It can be live; historical recovery must use `input_context`, not reinterpret this
reference as the saved frame. `BaseFeature.molecular_system` retains that behavior.
Native diagnostic labels and `Topography.show()` use the retained input when
available, translating original feature indices to local snapshot indices.
Feature construction by labels uses retained selected topology and translates
resolved local indices back to original source indices. The native MolSysViewer
addon retains its separate source/index-space boundary; this delivery does not
adopt input contexts in that integration.

Assigning `molecular_system` on a Topography containing features, provider runs,
native analysis, or an input context raises `ValueError`, including assigning
`None`. Construct a new analysis instead. Empty unanalysed objects can still bind
an input, with their configured selection/frame; conversion failure is atomic.
This does not yet protect every mutable raw/feature/registry field in #60.

DFND now accepts exactly one explicit non-negative frame index (scalar or
one-element sequence). Empty/multiple/all-frame requests are rejected instead of
silently analysing the first converted frame. A source trajectory is not copied
into the retained context; only selected atoms in the chosen frame are stored.
The original live reference may keep that trajectory alive, as before.

## Evidence and next gate

Guards belong in `tests/test_dfnd_input_context.py` and
`tests/test_topography_input_binding.py`: selected nonconsecutive source order,
multiple distinguishable source frames, later coordinate/topology edits,
independent recovery, protected buffers, explicit namespaces, shared probe
context, copy/restoration and atomic rebinding rejection.

Public neutral spatial supports, mutation migration for feature registries,
incomplete-provider admission, numerical precision (#75) and independent
scientific references (#76) remain separate work.

## Local verification and memory

Development baseline: `aef4b34105926eecc1781f07021bbe8c738b594f`.
Before implementation, the new input/binding panel failed **19 tests**. A
separate failing-first label guard resolved source atom 6 as local index 3;
the implementation now returns source index 6. The complete joint native,
Topography, geometry, reporting and executable-example panel passes **420 tests,
7 existing skips, 60.92 s**, Python 3.13.14 on Linux.

The existing global-index diagnostic guard now verifies local queries into the
saved selected MolSys and original global indices in the displayed card. Its
legacy diagnostic-only container still supports querying an original source.

`python devtools/dfnd/profile_memory.py --output /tmp/context-memory.json`
still reports the same unique native numerical buffer inventory: tetrahedron
733 B, hollow sphere 175347 B, helical tube 1452273 B and 1crn 1216046 B. Direct
guards verify that coordinates/radii/maps share backing storage with the context
and that probe results share the same context instance.

Selected molecular topology costs additional memory once per input context.
A separate local measurement prepared a network and recovered selected MolSys,
warmed `InputContext(...)` construction, then retained one further context under
`tracemalloc` in each of three repetitions. Inputs reuse native protected
quantities/maps and the recovered MolSys. Median traced live allocations were:

| Selected molecular input | Atoms | Capturing one additional context |
| --- | ---: | ---: |
| Regular tetrahedron | 4 | 62052 B |
| Hollow sphere | 103 | 72137 B |
| Crambin 1crn | 327 | 104311 B |

These measurements include MolSysMT topology/structural metadata copies and
Python/wrapper allocations. They exclude an entire trajectory copy and are not
RSS measurements or a scaling bound. Whole-pipeline traced comparisons against
earlier sessions have import/JIT differences and cannot isolate context cost.
The original-input compatibility reference still keeps its source alive;
deep-copying or pickling a complete Topography/network may copy/serialize that
live reference too. InputContext itself retains selected single-frame evidence.

Full Ruff lint/format and generated queue checks pass. Ten authored developer
pages render with warnings treated as errors; public `make html` succeeds with
eight existing warnings tracked by #64. The new module passes isolated mypy with
missing external imports ignored. Unfiltered checking reports its two missing
MolSysMT stub imports plus 17 diagnostics in touched legacy modules; all 17
reproduce with baseline shadow files. Those existing typing/stub limitations
remain under #77; this is not a clean repository-wide typing claim.

The additional feature/atom-label/provider/addon compatibility selection reports
**249 passed, 3 failed, 6 skipped, 205.70 s**. All three failures are fpocket CLI
calls to `check_dependency(kind=...)`: the active editable DepDigest reports
`0.10.1+15.g78a9106`, below TopoMT's declared `>=0.12.0`. Executing the exact
published-baseline runner reproduces the same TypeError before fpocket starts.
This input-context change does not modify that runner or claim installed-engine
validation in this environment. Updating the sibling checkout/environment is
separate from this delivery; the declared minimum is not weakened.

GH Run Receptor's terminal report for baseline CI
[36849438075](https://github.com/uibcdf/topomt/actions/runs/36849438075)
preserves failure: one cell fails installing the pinned MolSysViewer source,
five fail in tests, with bounded causes naming the existing dependency-declaration
test and funnel-motif test. This is baseline matrix evidence under #16, not a
successful cross-platform native validation claim.
