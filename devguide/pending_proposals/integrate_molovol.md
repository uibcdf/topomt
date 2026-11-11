---
summary: Integrate original local MoloVol with source-bound cavity and volume results.
issue: uibcdf/topomt#190
status: active
opened: 2026-11-11
closed:
severity: medium
verification: tested
area: [third-party, api, attribution]
guard:
normative:
blocked_by: []
supersedes: []
---

# Original local MoloVol integration

## What

The maintainer selects MoloVol after the assessment proposal under #159. Add an
optional original CLI/files route, keeping the #187 native joint review separate.
Preserve original region/volume definitions and software identity; do not alter
the scientific engine or imply native DFND classification.

## How

The original checkout is `~/repos@others/MoloVol`. Initial master/tag v1.2.0.2
is `7b2e508a2b1e06e0b06d56f89fc24e8f849db38c`; inspection finds an unconditional
Windows-console change in `base_init.cpp`. For Linux, pin its original preceding
commit `76693ae9c2b44270ae0875cefd96f8c0e9c61246`, without
patching source. It retains the newer wxWidgets compatibility changes and
reports the original 1.2.0 version independently of Git identity.

Build with the original CMake project, renderer disabled and one worker. The
maintainer installs CMake, wxWidgets and Xvfb in the shared working environment;
TopoMT does not install packages. An isolated virtual display must use its own
allocated display, never the upstream launcher’s fixed shared `:1`.

Start with a small explicitly frozen PDB/element-radius input. Its submitted
decimal coordinates are the reference model; it does not qualify an unchanged
full-precision BenchLab JSON model by name alone. Retain exact coordinates,
effective element radii, probe/grid/depth, original report and executable/data
fingerprints. Check core versus occupied measures independently of DFND names.

## Why

MoloVol adds explicit probe-core/occupied/excluded volume and surface semantics.
Its one-probe Outside region is not an internal cavity; two-probe region types
depend on the large-probe exterior. Preserve unavailable measures rather than
inventing finite exterior volumes, and preserve original table precision.

## What was refuted

An optional adapter, mock report or source checkout does not establish original
execution. A region center is not a complete region support; equal labels do
not establish equality with DFND objects. No original-server submission is used.

## Scope and exclusions

Original isolated-structure CLI, report/region fields, optional surfaces, explicit
radii, source-bound persistence and real optional attribution. Periodic analysis,
native reproduction, scientific BenchLab comparison, exhaustive OpenDX consumer
interpretation and installed/platform qualification retain separate ownership.
#159 remains open for the broader candidate review; #19/#101/#16 retain fidelity
and public qualification.

## Acceptance criteria

Write argument/parser/recovery regressions first. Execute a bounded original
pilot and direct-versus-adapter checks with exact source/model/resource receipts.
Retain valid empty and failed results, original units, source/selection/frame and
effective-radius provenance. Saved reading must require neither engine/display
nor new calculation credit. Test real Ackredit selection/reuse/enclosing capture,
absence/failure and producer-blocked saved reading. Update user/developer guides,
catalogue/resource/action routing and generated report indexes before closeout.

## Source receiving — 2026-11-11

The unchanged original CLI built and ran. Four public/direct controls passed:
isolated, completed empty, two probes and original table radii. The final scoped
run passed 294 tests in 60.36 seconds (340564 KiB parent peak RSS), one CPU and
bounded memory/time. This includes original execution, engine-free nm/pm reading,
source/query/resource rejection, private display cleanup, optional recorder
failure/absence, saved producer references and earlier provider regressions.
Repository Ruff checks and 620-file formatting pass; scoped mypy passes the 13
affected source files for 3.11/3.14 targets. Static targets do not mean execution
on every Python minor. Detailed source/build/model evidence and exclusions are
in [the overview](../molovol/overview.md); committed captures are in
`tests/data/original_local/molovol/`. Resource #191 and catalogue #68 route
remaining assessment to #159, fidelity to #19 and public qualification to #101/#16.

Full suite, coverage, remote CI, installed distributions, other platforms and
scientific BenchLab comparisons are deferred under their existing owners. The
shared editable workspace preserves the human version edit. The documentation
candidate and delivery/readback are recorded at closeout before resolving #190.
