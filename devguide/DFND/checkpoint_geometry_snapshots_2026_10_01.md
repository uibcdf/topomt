# Native geometry snapshot checkpoint

Date: 2026-10-01. Owner: [#60](https://github.com/uibcdf/topomt/issues/60).
Baseline source: `c415b8549478ad584ba6df8677e066c7b980107c`.
Status: **native numeric snapshot slice implemented; public gate partial**.

## Decision and implementation

Completed native geometry retains its selected coordinate/radius arrays in nm
and its resolved atom map. Mutable external buffers are copied into owned
immutable bytes storage. Protected accesses return inexpensive array views
with independent shape metadata. Writing, reactivating the write flag or
replacing public input/cache attributes is rejected.

`topomt.tools.geometry.immutable_array` owns the reusable array operation.
`DelaunayMesh.freeze()` is an explicit supported operation in the existing mesh
owner; DFND calls it, while other mesh consumers keep their mutable default.
The network and its `mesh.atoms` views reuse that supported storage machinery.
Private helpers remain behind those operations; no new public context classes,
serialized fields, dependencies or sibling workarounds are introduced.

New coordinates/radii/maps require a new network and geometry context. New
probes reuse the network and its frozen mesh but create separate query results.
Deep copies preserve protection and share immutable numeric buffers safely;
mutable result metadata remains independent. This keeps the #74 registry-copy
boundary intact without multiplying coordinate storage per query.

## Regression evidence

Before implementation, the focused snapshot/mesh panel reported **30 failures
and 10 passes**. Failures demonstrated external coordinate/radius/map aliasing,
public writes/replacements, canonical shape mutation and the missing mesh freeze
operation. After implementation, the snapshot/mesh/array panel passes **46
tests**. Nested NumPy outputs are compared with NumPy's recursive assertion.

Guards in `tests/test_dfnd_geometry_snapshot.py` cover nm-valued quantity inputs,
nontrivial source maps, protected input and cached arrays, write-flag reactivation,
attribute replacement, independent view metadata, rebuild identity and a live
MolSysMT coordinate edit. A regular sealed tetrahedron becomes non-resident
after shrinking its coordinates or expanding its atom radii, while its original
result remains unchanged. Probe queries share both input and mesh buffers;
deep-copy tests retain protected geometry and independent result records.

A later pickle round-trip guard reproduced NumPy's writable-array restoration
and passed after snapshot owners were made to reapply protection on restore.
Pickle may allocate fresh numerical buffers; this slice does not define a
canonical serialized Topography schema or claim buffer deduplication on disk.

The expanded DFND/Topography/mesh/tessellation/array selector passes **381 tests,
7 existing skips, 61.83 s**, Python 3.13.14 on Linux. Five skips are deferred DFND
tessellation helpers; two are the existing nonresident-passage/experimental-motif
fixture gaps. This is development-source evidence, not the complete installed
Python/OS matrix or biological validation.

Final selection after the restoration guard also includes reporting checks and
both new executable docstring examples: **385 passed, 7 existing skips, 62.26 s**.

## Memory measurements

Repeat from the repository root:

```bash
python devtools/dfnd/profile_memory.py --output /tmp/dfnd-memory.json
```

The tool retains two probes (1.4 and 2.2 angstroms), verifies shared geometry,
deduplicates network/mesh ndarray backing allocations and reports traced live
and peak allocations. Baseline and changed runs use the same fixtures and
Python 3.13.14. Values below are bytes; KB/MB in interpretation use decimal units.

| Fixture | Atoms | Input arrays | Unique network/mesh array bytes, before and after | Build traced live bytes: before → after | Second retained query added bytes: before → after |
| --- | ---: | ---: | ---: | ---: | ---: |
| Regular tetrahedron | 4 | 160 | 733 | 131297 → 136589 | 26149 → 27327 |
| Hollow sphere | 103 | 4120 | 175347 | 518473 → 524539 | 2843071 → 2844024 |
| Helical tube | 384 | 15360 | 1452273 | 4034751 → 4037859 | 24292919 → 24293572 |
| Crambin, CASTpFold `1crn` input | 327 | 13080 | 1216046 | 296286229 → 296288918 | 19280332 → 19281110 |

Input buffers use 40 bytes per atom on this 64-bit platform. Unique retained
network/mesh numerical storage is unchanged in these fixtures; build traced
live differences are approximately 2.7–6.1 KB. Sharing immutable storage avoids
duplicating those buffers in a new probe view. When a caller previously shared
live nm input arrays and retains them, owning a snapshot also retains a separate
input buffer: budget up to 40*N bytes for that boundary rather than assuming
the measured native-buffer inventory equals whole-process overhead.

The retained query allocations (about 0.026–24.3 MB here) include result records,
projected views, graphs and components. They are present in the baseline too.
These single-run traced allocations are not process RSS, a worst-case scaling
bound or a performance certification. Lazy imports/JIT/setup affect the crambin
build measurement; its large traced value cannot be attributed to atom snapshots.
Build/reprobe timings are recorded by the tool but require controlled repeated
benchmarks before inferring a performance regression or equivalence.

## Publication checks

Publication checks: full Ruff lint/format and generated report-index checks
pass. Nine authored developer-guide pages render with warnings treated as
errors and valid local Markdown targets. Public incremental HTML succeeds with
eight existing warnings under #64. The epsilon-only identity regression now
wraps internal arrays with explicit nm units and asserts unchanged coordinates
and radii, so its key difference is not accidentally produced by a tenfold
input-unit change.

## Remaining #60 work

This slice does not close the public analysis-context/spatial-support contract.
Source topology/frame recoverability, public feature/raw/support mutation paths,
the populated Topography molecular-system setter, neutral support capabilities
and an incomplete-provider example remain open. Private attribute manipulation
is outside the supported protection boundary. Geometric snapshot protection
does not establish exact physical volume or global continuous navigability.

Scientific reference validation and numerical precision remain #76/#75.
The new array utility passes its bounded mypy check. Checking the touched legacy
mesh/DFND modules also reports eight pre-existing diagnostics, reproduced using
the exact baseline files with `--shadow-file`; evidence is linked in #77.
