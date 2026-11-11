# What the public result lets us recover

A label is useful only if we can recover the geometry and context behind it.
This continuation follows the same three frozen inputs through the actual
public dispatcher, their native wet carriers and dry banks, and the public
feature registry. It complements the [physical boundary](closed_shell/small_probe_connectivity.md)
and [volume](volume_measurements.md) studies; it adds no molecular participants.

## Supports, banks and depths

The formal capture at source `80855e5` inspects **16 queries**: ten original
controls and six analytic-threshold neighbors. Every finite tetrahedron belongs
to exactly one native wet carrier or dry bank. Source-mapped quadruples recover
the carrier; lining atoms describe its boundary context and cannot replace that
support. Coast face IDs are unique, their triangle areas agree with the captured
coordinates, and wet/dry lining incidences and areas are reciprocal.

| Case / probe | Resident + connector cells | Native dry banks | Wet/dry coast faces | Public objects | Physical hull patches |
| --- | ---: | ---: | ---: | --- | ---: |
| Tetrahedron / 1.2 Å | 1 + 0 | 0 | 0 | `Percolating` | 4 |
| Tetrahedron / 1.4 Å | 1 + 0 | 0 | 0 | `Void` | 0 |
| Tetrahedron / 1.7 Å | 0 + 0 | 1 | 0 | Empty registry | 0 |
| Closed shell / 0.05 Å | 128 + 1 | 29 | 93 | `Channel`, 10 `Mouth` children | 13 |
| Closed shell / 0.2 Å | 95 + 3 | 17 | 94 | `Void` | 0 |
| Closed shell / 1.4 Å | 33 + 0 | 1 | 42 | `Void` | 0 |
| Opened shell / 1.4 Å | 35 + 0 | 1 | 43 | `Pocket`, 1 `Mouth` child | 1 |
| Opened shell / 3 Å | 9 + 0 | 1 | 18 | `Void` | 0 |
| Either shell / 5 Å | 0 + 0 | 1 | 0 | Empty registry | 0 |

These are **native decomposition counts**, not physical cavity counts. The
physical-patch column has its own independent certificates. In particular,
13 patches, ten native exterior links and ten promoted `Mouth` children are
three different observations at the closed shell's small probe.

Depth is dimensionless graph distance from admitted exterior contacts. The
opened shell at 1.4 Å has depths 0–9 and 29 contextual depth regions. A sealed
component has no such root: its all-zero depth is the current compatibility
convention, **not a measurement of zero physical burial**. The audit reconstructs
rooted graph distances independently from the raw admitted edges and checks that
depth regions partition their parent support.

### A precise neighbor query

The closed shell at 0.2 Å makes the distinction concrete. Three cells are
nonresident but belong to the wet carrier as transit connectors:

```python
wet = next(c for c in topography.dfnd.dfn.components.wet
           if c.transit_connector_node_indices)
connector = wet.transit_connector_node_indices[0]
node = topography.dfnd.mesh.neighbors(connector)[0]
graph = topography.dfnd.dfn.graph
assert connector in graph.neighbors(node, side='dry')          # nonresident
assert connector in graph.neighbors(node, component_side='wet')
assert connector in graph.neighbors(node, side='dry', component_side='wet')
```

The old `side` selector retains its residence meaning. `component_side` selects
native wet/bank membership; both inspect face incidence, not necessarily an
admitted transit edge. Missing captured role context raises an availability
error. Selection inspects at most four stored neighbors and adds no fresh
calculation attribution. See the [method explanation](../../dfnd/network_and_decomposition.md#advanced-inspection-residence-and-component-side-neighbors).

## Thresholds and numerical honesty

For the unchanged tetrahedron, the independent capacities are
`5.3 / sqrt(3) - 1.7` Å for a face and `sqrt(6) * 5.3 / 4 - 1.7` Å for residence.
The additional queries use an offset of **0.0001 Å**, mesh epsilon **0.000001 Å**
and physical tolerance **0.000001 Å**, frozen before receiving.

| Threshold | Below | Exactly at | Above |
| --- | --- | --- | --- |
| Face capacity | Native `Percolating`; physical four patches | Native marginal `Percolating`; physical `unresolved` | Native `Void`; physical `unresolved` |
| Residence capacity | `Void` | Marginal `Void` under native slack | Empty resident registry |

The two unresolved boundary records retain `n_patches=None` and the reason
`zero lacks a complete positive-margin cover`. They are conservative failures
of this bounded numerical certificate, not accepted positive openings or failed
native classification. The analytic strict model supplies a separate reference;
the implementation does not overwrite its unavailable numerical answer with it.
Further near-threshold certification remains in [#76](https://github.com/uibcdf/topomt/issues/76).
It is not needed for the already margin-separated controls or their next use.

The added guards also check rigid motion, source permutation, alternate
nm/ps and pm/fs unit policies, and a similarity transform of factor three.
Every active length, including epsilon, probe and physical tolerance, scales
with the model. Mapped supports and physical counts agree; analytic bare-volume
errors meet the predeclared carrier-relative target. Sampling intervals retain
their conditional meaning. Reusing a compatible shell mesh across probes agrees
with fresh support construction without changing earlier observations.

Fixed-model residence, admitted-face and finite-transit availability are nested
on the selected policies. **Component counts, mouth counts and independently
sampled volume point estimates need not be monotone.** These bounded guards are
not a proof for every remeshing degeneracy or synthetic geometry.

## Ownership and availability

The public registry preserves grounded signatures, catalog refinements, source
and component/support identities, and reciprocal parent/child relations. Its
legacy `dimensionality` remains a catalog value, not the dimension of the full
geometric carrier. The public shape declaration now includes the existing
runtime `neutral` value of `Percolating`.

Existing guards exercise live-input mutation, historical snapshots, independent
copy registries, shallow payload sharing, deep copy and native Python pickle
restoration. **No versioned public Topography interchange format is implemented.**
The JSON observations here are fixed-unit study evidence, not that API. General
neutral support/availability and registry migration remain
[#60](https://github.com/uibcdf/topomt/issues/60); supplied molecular participants
and positive interface/convexity validation remain
[#61](https://github.com/uibcdf/topomt/issues/61).

Native bank-derived interface flags are not participant assignments. Beach
candidate atom unions are not established probe contacts, and their summed local
stencils are proxies, not physical accessible or swept volumes. Characteristic
radii summarize current native support; they are not certified global bottlenecks.
Physical aperture area, exact maximum bottleneck and exact global cavity count
remain unavailable in this study. None is silently replaced with carrier areas,
local capacities or native component counts.

## Reproduce and inspect

Download the complete observations for the
{download}`tetrahedron <regular_tetrahedron/artifacts/public_contract_v1/observations.json>`,
{download}`closed shell <closed_shell/artifacts/public_contract_v1/observations.json>` and
{download}`opened shell <shell_with_opening/artifacts/public_contract_v1/observations.json>`.
They retain explicit raw nm/nm²/nm³ units, public quantity records, source atom
maps, complete wet/dry supports, query/result identities and unresolved reasons.
The source-bound capture takes 1.77 / 3.28 / 1.59 seconds per case; peak process
RSS is 291 MiB or less. These tiny sequential captures are not scaling benchmarks.

The combined public/ownership/robustness/documentation/lifecycle selector passes
161 tests (47.66 seconds; peak RSS 627 MiB), with two existing NumPy shape-setter
deprecation warnings. Nine current reader guards also pass. Ruff and six scoped
mypy files pass. Guards include `test_three_case_public_contract.py`,
`test_three_case_robustness.py`, `test_dfnd_component_neighbors.py` and the
existing input/snapshot/registry suites. Full installed/platform qualification
remains separate under [#16](https://github.com/uibcdf/topomt/issues/16).
