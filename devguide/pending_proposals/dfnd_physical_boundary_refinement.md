---
summary: Refine physical boundary patches beyond native whole-face exterior clusters.
issue: uibcdf/topomt#151
status: open
opened: 2026-11-08
closed:
severity: medium
verification: reproduced
area: [dfnd, classification]
guard:
normative:
blocked_by: []
supersedes: []
---

# Physical connectivity beyond admitted carrier faces

## What

The independent #150 certificate finds four disconnected free probe-center
patches on the unchanged tetrahedron hull at 1.2 Å. Native face grouping yields
one exterior link; the zero-wall-face classifier gives Percolating, and the
public bridge promotes no Mouth children. These are reproducible discrete
semantics, but cannot be interpreted as one connected physical boundary opening
or a completely collision-free hull boundary.

## How

`DelaunayFlowNetwork._cluster_external_faces` groups admitted whole faces by shared atomic
edges. It never asks whether a free patch can cross that edge. On the frozen
tetrahedron all six edges are covered with a 0.25 Å margin, while each face has
one free patch connected by an all-atom ray to the centroid. The local face
admission predicate and `n_wall_faces==0` do not establish that every point of
those faces is free. `tests/test_tetrahedron_boundary_certificate.py` protects
the reference and current receiving contrast without declaring refinement done.

Decide the relation among native contacts, physical patches, public Mouth and
Percolating. Start with a failing physical-connectivity regression; use the
four-patch tetrahedron, one-patch opened shell and sealed shell controls. Keep
mapping, units, explicit unavailable-versus-zero state and support/provenance.
Patch components within a face may also need refinement; checking edge openness
alone is not a general solution. Test the actual raw/public route and filtering.

## Why

Mouth counts and classification must express their actual geometric observable.
Public/source prose currently calling this fully solvent-permeable overstates
the predicate. The issue remains open until the accepted bounded runtime and
contract changes are implemented and verified.

## What was refuted

No native contract regression or bridge identity mismatch is established here.
Simply renaming this case Channel, changing expectations to match a comparator,
or treating triangle area/local gate as free aperture area/global bottleneck
would not resolve the geometric limitation.

## Scope and exclusions

Same three adopted controls first. General public support belongs to #60,
independent panel to #76 and volume precision to #75. No new geometry, proteins,
providers or installed/matrix claim. Historical artifacts retain their bytes.

## Acceptance criteria

Publish the observable and compatibility decision, implement the selected bounded
refinement, correct scientific descriptions and demonstrate independent and live
receiving guards with explicit units, source correspondence and rigid motion.
Documentation/tracking alone does not satisfy runtime acceptance.

## Acceptance proposal and red regression — 2026-11-09

The [bounded contract proposal](../DFND/boundary_connectivity_contract.md)
separates carrier-face links, physical hull patches, path-supported component
contacts and public Mouth promotion. Its proposed first increment adds an
inspectable physical-contact observation while preserving the current catalog;
it does not settle final Mouth promotion or reclassify the tetrahedron.

`tests/test_dfnd_physical_boundary_contract.py` replays the three independent
certificates and reconstructs five actual public controls. Before marking the
pending candidate views, it produced **2 passed / 7 failed**, all failures due
to absent physical observations. Only that custom missing-view exception is
now a strict expected failure; other errors or present but wrong results fail
normally. These are implementation acceptance targets, not a delivered fix.

See the [source checkpoint](../DFND/boundary_contract_checkpoint.md) for bounded
execution, scope and deferred gates. #151 and its comparative finding remain
open/current; runtime patch decomposition, component paths, supports and public
receiving still require implementation and verification.

## Comparative finding navigation — 2026-11-08

The public [method explanation](../../docs/content/dfnd/exterior_and_boundaries.md)
and [worked example](../../docs/content/dfnd/worked_tetrahedron.md) now teach the
distinct observations and preserve this issue's pending runtime scope. #170's
documentation delivery does not implement physical boundary refinement.

The [maintained finding card](https://github.com/uibcdf/topomt/discussions/154#discussioncomment-19482186) carries the current
scoped conclusion and dated correction/review history. This report retains its
technical evidence; before manuscript reuse follow the
[comparative-finding lifecycle](../comparative_findings.md) and review the actual
target profile. Historical observations and source fixes do not automatically
describe every current release.
