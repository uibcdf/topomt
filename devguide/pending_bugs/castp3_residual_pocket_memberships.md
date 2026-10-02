---
summary: Resolve residual lining, rim and component-count discrepancies in the corrected CASTp3 forty-system panel.
issue: uibcdf/topomt#88
status: open
opened: 2026-10-02
closed:
severity: medium
verification: measured
area: [castp, geometry, validation]
guard:
normative:
blocked_by: []
supersedes: []
---

# Residual CASTp3 pocket and mouth memberships

## What

The completed #87 audit matches 468/534 server pockets against 551 native
pockets. Sixty-six server sets and eighty-three native sets remain unmatched.
All 388 closed-void sets match; channels match 45/52, branched channels 8/17
and aggregated mouth records 520/603.

## How

Reproduce with `python -m devtools.castp.compare_castp3_oracles --ids 1stp
3ptb 1a6u 1bmq 1cge 1a4j --radii-model castp3_protor --workers 3
--output-json /tmp/castp_residuals.json`. The forty-system source hashes,
policies and missing/extra memberships are pinned in
`castp/artifacts/membership_audit_2026_10_02_corrected_inputs.json`.

## Why

Exact counts do not establish matching lining/rim sets. Unmatched native sets
include different atom attribution and count/component differences; they do
not automatically represent eighty-three extra physical pockets. Reliable
local pocket delivery requires independent diagnosis of these observations.

## What was refuted

The old micro-pocket counterexamples (3PTB 27 and 1BMQ 34) now match exact
pocket and mouth sets under independent molecular guards. The old preparation
and source-mapping assumptions cannot establish present impossibility. This
does not prove general equivalence or identify each remaining root cause.

## Scope and exclusions

Start with the lining atom absent in 1STP (serial 592), the lining/rim atom
absent in 3PTB (1054) and extra rim atom in 1A6U (733). Then address count
differences in 1BMQ, 1CGE and 1A4J and branched-channel membership. No fitted
epsilon, oracle-dependent expansion or molecule-specific radius rule. Terminal
variants retain #84's separate boundary; open SA/MS work stays under #41–#52.

## Acceptance criteria

Establish independently justified rules for each failure class with failing-first
molecular guards. Re-evaluate every affected class on all forty controls,
preserving exact closed-void memberships and the independent 225-void,
900-measure panel. Distinguish atom membership, component topology, individual
mouth boundaries and metric definitions. No DFND/Topography semantic change.

## 2026-10-02: 1STP flow diagnosis

The [focused checkpoint](../castp/checkpoint_2026_10_02_1stp_flow.md) now
distinguishes sphere-region reconstruction from final atom export. The missing
SER A93 nitrogen supports an archived orthosphere whose native tetrahedron is
sent to the exterior by the maximum-depth flow rule. The minimum-reachable
alternative reproduces all fifty exported sphere regions and component-vertex
lining sets in 1STP plus six prior controls. Applying existing reporting rules
to those regions nevertheless regresses final pocket and mouth memberships.
No production default changes. Extend geometry evidence to the forty-system
panel and derive atom/mouth reporting before promoting the alternative.
Python 3.11/3.12 CI work is deferred at the user's explicit request.

## 2026-10-02: explicit definitions and geometric vertices

The [new checkpoint](../castp/checkpoint_2026_10_02_pocket_definitions.md) implements
separate literature and empirical CASTp3 choices, independent of radii. Actual
component/mouth vertices remove the former reporting compensation. A completed
forty-input diagnostic matches all atom classes in 38/40 systems and 533/534
pocket sets. 1CDO's false sink is a local numeric defect tracked separately
under #89; 1HIV includes fourteen CSO HETATM atoms absent from the server
contribution list. No demonstrated server algorithm bug is asserted. Fresh
production validation and the remaining input/metric boundaries are recorded
in the checkpoint; historical diagnostic counts remain dated evidence.


The fresh explicit-compatibility production run now matches every compared atom
class in 39/40 systems: 533/534 pockets, 388/388 closed voids, 52/52 channels,
17/17 branched channels and 602/603 aggregate mouths. A 968-test run preserves
the independent 225-cavity/900-measure panel and recovers 1CDO's separate regions.
#89 is resolved. #88 remains open for generic input/individual-mouth fidelity;
1HIV is the sole current atom-set residual. Work pauses before new input-policy
or open-metric development; no general equivalence certification is claimed.
