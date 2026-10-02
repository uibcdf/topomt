# 1STP: exported sphere regions and atom attribution

Recorded: 2026-10-02. Owning residual: [#88](https://github.com/uibcdf/topomt/issues/88).
Production scientific source remains `3a48ab1`; no default geometry or export
policy changes in this diagnostic slice. Python 3.11/3.12 CI work is explicitly
deferred by the user.

## What 1STP establishes

The corrected forty-system atom comparison exposed one 1STP pocket missing
PDB serial 592, the backbone N of SER A93. The archived pocket 3 contains
`{574, 576, 592, 596, 694, 701, 719, 720}`. Its source N has base radius
1.64 angstrom and expanded radius 3.04 angstrom with the 1.4 angstrom probe.

The archive provides five orthospheres for this pocket. All five match native
weighted tetrahedra under the prepared `castp3_protor` input, with verified
four-atom contacts and no atom penetrating the sphere. Printed coordinates
and radius use their four-decimal rounding intervals; these intervals are
comparison evidence, not a runtime geometry epsilon.

| Supporting tetrahedron, original PDB serials | Present in current region |
|---|---|
| 576, 596, 719, 720 | Yes |
| 574, 576, 596, 719 | Yes |
| 574, 592, 596, 694 | No |
| 574, 596, 694, 701 | No |
| 574, 596, 701, 719 | Yes |

Thus the absent nitrogen participates in an exported sphere whose supporting
tetrahedron exists locally but is assigned to the exterior. This is stronger
evidence than a lining-set mismatch alone. The sphere export does not reveal
every detail of the server's internal triangulation or algorithm.

The connector tetrahedron `{574, 596, 694, 701}` has two outgoing hidden-face
links. One reaches finite sink `{574, 596, 701, 719}`; the other reaches the
exterior through `{596, 694, 701, 719}`. Our existing maximum-reachable-depth
rule selects the exterior. The missing-N tetrahedron inherits that decision.
These links use the existing exact attachment predicates and rank table;
no fitted radius, rank threshold or oracle-contained neighbor expansion is
needed to expose the bifurcation. Probe-limited depth with the current full
upper rank leaves the result unchanged.

## Independent diagnostic alternative

The historical algorithmic reference contains both maximum-depth and
minimum-depth constructions. The exploratory alternative chooses the
lowest-rho terminal reachable through the same hidden-face graph, preferring
a finite terminal over the exterior whenever one exists. It derives depths
solely from native geometry, before reading any oracle component memberships.
Unresolved directed cycles raise an error rather than receive an invented
tie correction. No historical executable or copied source is used.

The diagnostic reproduces all nine 1STP regions represented by the exported
orthospheres, including the target's five tetrahedra. The union of component
vertices also reproduces all five pocket lining sets, the channel set and
three void sets. The remaining final-output discrepancy is identifiable:
the current attached-mouth reporting helper adds atoms 641 and 897 to
another pocket. The same helper was developed for the current maximum-depth
regions and cannot be assumed correct after changing the regions.

Aggregated mouth memberships independently differ in three regions: missing
255 in pocket 1, missing 656/896 and extra 641/897 in pocket 2, and missing
694 in pocket 3. Consequently, a blind depth switch would leave final pocket
agreement at 4/5 and reduce aggregate mouth agreement from 6/6 to 3/6.
Combining minimum-depth lining with maximum-depth mouths merely to obtain a
match has no independently justified rule yet and is not implemented.

The papers describe alpha shapes and discrete flow as the method's basis:
[pocket construction (1998)](https://research-explorer.ista.ac.at/record/4013)
and [CASTp 3.0 (2018)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6031066/).
The measured modern-export agreement below is an inference from fixed
archives; it does not establish which depth implementation the server runs.

## Six prior controls

We repeated both policies on 1CRN, 1ROP, 2PK4, 3PHV, 1IFB and 1HEW. These
already match final atom memberships in the current native route. 1CRN has
one void and no open features; its empty open populations remain explicit.

| Case | Exported sphere regions | Exact current regions | Exact minimum-depth regions | Minimum-depth component-vertex lining sets |
|---|---:|---:|---:|---:|
| 1STP | 9 | 6 | 9 | 9/9 |
| 1CRN | 1 | 1 | 1 | 1/1 |
| 1ROP | 3 | 3 | 3 | 3/3 |
| 2PK4 | 7 | 5 | 7 | 7/7 |
| 3PHV | 13 | 11 | 13 | 13/13 |
| 1IFB | 10 | 8 | 10 | 10/10 |
| 1HEW | 7 | 6 | 7 | 7/7 |
| Total | 50 | 40 | 50 | 50/50 |

All exported spheres in this panel have compatible native supports. Exact
region comparison means equality of supporting-tetrahedron sets with
multiset multiplicity, not matching region counts or approximate atom overlap.
The minimum-depth vertex unions match 29 pocket, 17 void, three channel and
one branched-channel lining sets.

However, keeping the existing final reporting rules after changing depth
reduces final pocket agreement from 28/29 to 25/29 and aggregate mouth
agreement from 33/33 to 23/33. This explains why earlier experiments judged
the depth alternative worse from final atom output alone. The new evidence
separates the geometry layer from that reporting regression; it does not
erase the regression. No open SA/MS metric is compared here.

## Reproduction and verification

```bash
python -m devtools.castp.audit_castp3_flow \
  --ids 1stp 1crn 1rop 2pk4 3phv 1ifb 1hew \
  --output-json /tmp/castp_flow_controls.json
```

The [source-identified artifact](artifacts/flow_audit_2026_10_02_1stp_controls.json)
retains exact ZIP/PDB hashes, executed audit-script and scientific source
hashes, Python version, sphere/contact matches, both region comparisons,
component-vertex versus final atom comparisons and local flow traces.
Tetrahedron indices are local diagnostics tied to those hashes; original
PDB serials identify the supports. A nearest overlapping component is only
a trace association; exact counts use complete multisets. Failed calculations
remain error records and incomplete geometry witnesses cannot count as passes.

The tool is deliberately isolated in `devtools/castp/`. Its temporary depth
substitution restores the original function even on failure; it is intended
for standalone audit processes, not concurrent application threads. Synthetic
tests protect finite/exterior branch choice, terminal-rank selection, cycle
rejection and rejection of penetrated spheres or ambiguous five-atom supports. A molecular 1STP
test protects the distinction between matching sphere regions/vertex lining
and still-discrepant final export, and verifies restoration of the runtime
depth function. A pinned-panel test checks input identity and panel totals.
All seven diagnostic tests and two reporting-protocol tests pass through
pytest-receptor; Ruff, the bounded tool type check and index validation pass.

## Next decision

Keep #88 open. First widen the independent sphere-region and vertex-lining
comparison to the forty-system panel. Then derive mouth boundaries and atom
contributions for the reconstructed regions from their surface geometry,
starting with the three 1STP mouth residuals above. Promote a general depth
and reporting correction only with molecular regression guards, all affected
forty-system classes checked, and preserved closed-void/analytical evidence.
DFND, public Topography and the original server-output contract are unchanged.
