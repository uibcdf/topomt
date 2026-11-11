---
summary: Establish the straight-tube BenchLab unit with independent passage and wall references.
issue: uibcdf/topomt#178
status: active
opened: 2026-11-10
closed:
severity: medium
verification: inspected
area: [dfnd, validation, docs]
guard:
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
