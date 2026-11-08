---
summary: Add source-bound original MOLE execution and engine-independent recovery.
issue: uibcdf/topomt#140
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: measured
area: [third-party]
guard: tests/test_mole_evidence.py::test_original_mole_evidence_reconstructs_without_engine
normative:
blocked_by: []
supersedes: []
---

# Original MOLE provider

## What

The maintainer prioritized MOLE after the four-provider source batch. Add the
original local CLI and saved recovery using the maintained Webchemistry source,
without changing its scientific implementation or claiming native DFND admission.

## How

Pin `sb-ncbr/webchemistry@fe0e84582a6bd42bc69224fd3a3022bf5c51cec3`.
The maintainer installed .NET SDK 10.0.114/runtime 10.0.14. An isolated clean
source archive builds with serial MSBuild, disabled persistent build servers,
one CPU, a 1 GiB managed heap cap and 6 GiB address-space cap. Build wall time
was 32.66 seconds, peak RSS 218180 KiB. The distributed 1TQN example completed
in 2.18 seconds and reports 14 tunnels, 9 cavities and 6 voids. That initial checkpoint established
an original executable before the adapter implementation below.

Reuse the original-local orchestration, MolSysMT source preparation/context,
ArgDigest options, DepDigest selected-command checks, SMonitor diagnostics,
PyUnitWizard conversions and immutable ProviderRun capture. Write focused
contract/parser tests before implementing the adapter; then retain and replay
a complete original source-bound capture under two unit policies.

## Why

MOLE is a relevant Delaunay/Voronoi channel and cavity comparator. Its original
profiles and cavity decomposition should be available through the same public
execution/recovery workflow as the existing providers. Documentary algorithm
review and actual integration are separate evidence.

## What was refuted

The legacy standalone MOLE tree targets .NET Framework, but the maintained
Webchemistry tree provides a .NET 10 build. The Python MOLEonline server still
executes this external engine. A historical CLI's error behavior does not
describe the selected maintained version, which sets a nonzero error exit.
Still require consistent completion and output rather than exit zero alone.

MOLE cavity Volume sums retained tetrahedral volumes. Do not describe it as
solvent-excluded free volume, and do not infer independent ground truth from
the original Cavity/Void labels or a path's sphere representation.

## Scope and exclusions

One reviewed local protocol, bounded original executions and source-bound saved
recovery. Preserve original channel/cavity kinds, all original artifacts and
available profile/mesh/descriptor data. Hosted services, membrane orientation,
native reproduction, exhaustive fidelity (#19), installed/public qualification
(#101/#16) and full-suite/matrix recovery (#58/#81) remain separate. Molecular
smoke inputs are integration controls; native DFND remains synthetic-first.

## Acceptance criteria

The optional CLI executes the original engine and keeps source mappings,
configuration, executable/version identity, raw output and explicit units.
Success, actual empty output, malformed/partial results, missing dependencies,
custom command identity, invalid options, incompatible sources and non-default
quantity policies have focused tests. A committed original capture replays
without the engine and checks exposed geometry/measurements against its bytes.
Document the protocol, controls, scientific definitions, resource limits and
actual qualification boundary before closing this source milestone.

## Resolution — 2026-11-08

The local CLI/files provider is implemented with distinct original channel and
cavity/void records, retained profile/mesh/layer/descriptor data, explicit units,
source context, checked executable identity and bounded resources. Complete
original captures are committed for 1AKD, its real empty high-threshold control,
and the official 1TQN pore example. Direct original invocations match the public
adapter's channel and cavity data. Failure status and engine-independent
reconstruction have executed controls.

The combined source selection passed 236 tests, including all 43 new MOLE
cases, existing original providers and the actual pyKVFinder source gates.
Ruff passes repository-wide; scoped mypy passes 15 source/test files. Full
Sphinx HTML builds with the same 12 baseline warnings and no new warnings.
The durable guard reconstructs the three original captures under two physical
unit policies and checks exposed coordinates, radii, mesh vertices and volumes
against their raw original fields. See [the source checkpoint](../mole/source_checkpoint.md).

This resolves the bounded original source milestone only. Installed/public
TopoMT, exhaustive fidelity, full-suite/matrix and other scientific gates remain
with #101/#16/#19/#58/#81. Authorized direct commits use [skip ci]; these source
checks do not replace hosted CI or qualify a release.
