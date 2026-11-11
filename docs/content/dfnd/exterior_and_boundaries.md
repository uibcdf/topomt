# Exterior contacts, physical patches and mouths

An opening has both a geometric location and a connectivity meaning. DFND's
current exterior links group carrier faces; a physical aperture is a subset of
those faces left free after exclusion. Keeping them distinct makes counts and
areas interpretable.

## Native exterior links

For each finite component, DFND collects admitted hull contacts. Two such faces
are adjacent for clustering when their defining atom triples share an atomic
edge. Connected clusters become `external_links`.

Each link retains face/tetrahedron identifiers, source atom indices, support
keys and gate summaries. Its `area_geometric` is the sum of the complete carrier
triangle areas. This is an exact description of the selected triangle support;
it is not the area remaining after probe-expanded balls are removed.

## A physical boundary observable

Choose an explicit surface $S$, here the boundary of the atomic-center hull.
For a strict probe-center convention, define

$$P(S,p)=\{x\in S:c_{\rm all}(x)>p\}.$$

The connected components of $P$ are free boundary patches on that surface.
Their definition uses every selected atom, not only each face's three vertices.
The chosen surface is part of the context: a different envelope gives a
different boundary observation.

One admitted face can contain more than one free patch. Two admitted faces
sharing an edge need not have a free crossing along that edge. Scalar face
maxima and triangle adjacency therefore do not count physical patches in general.

## The tetrahedron makes the distinction visible

At probe 1.2 Å, the independently certified tetrahedron has four free patches on
its hull. All six shared atomic edges are covered by expanded balls, separating
the face interiors. Four all-atom-free rays connect those patches to the same
free central region and to infinity.

Current native clustering joins all four admitted faces into **one exterior
link**. Its resident component has zero native wall faces, so the catalog gives
Percolating. The current public bridge promotes **no Mouth children** for that
family. Four patches, one link and zero public Mouth objects are different
observations, not three estimates of one quantity.

```{figure} ../benchlab/synthetic/regular_tetrahedron/artifacts/boundary_connectivity_v1/boundary_patches.png
:alt: Retained tetrahedron boundary certificate illustration showing four free face patches separated by covered edges.

Canonical BenchLab figure. The [certificate and its scope](../benchlab/synthetic/regular_tetrahedron/boundary_connectivity.md)
provide the independent evidence; this chapter reuses its interpretation.
```

The opened shell at 1.4 Å supplies a one-patch control. The closed shell at
0.2 Å supplies a complete-cover, zero-patch control. Agreement of native and
physical counts on either control does not establish general equivalence.

## Contact with a region and promotion to Mouth

A global free hull patch is not automatically attached to every nearby native
component. Attachment needs a compatible path and support context. An all-atom
free point on a convex-hull face does have an outward-normal route to infinity,
but reaching that point from a particular region is another requirement.

Current Mouth promotion is a compatibility interpretation of native exterior
links on pocket/channel families. It preserves their source support and parent
relation. A Mouth is a legacy 1D boundary feature in the public hierarchy even
though a possible aperture realization is a two-dimensional patch; that class
dimension does not define the mathematical dimension of every support.

The compatibility decision under [#151](https://github.com/uibcdf/topomt/issues/151)
keeps that promotion policy. The bounded physical analysis adds a separate
observation; four contacts on a Percolating therefore do not create four Mouth
children or rename it Channel. Mouth areas retain their carrier meaning.

## Inspect the physical observation

The source implementation exposes the canonical record at
`topography.dfnd.dfn.boundary_connectivity`, also retained in
`topography.dfnd.raw['boundary_connectivity']`. Its schema is
`dfnd.physical_boundary.nm.v1`: numeric coordinates, lengths and margins are nm.
A wet feature's `boundary['physical_openings']` refers to the same patch IDs
and retains its component-path evidence. It is not a second aperture geometry.

| State | Permitted reading |
| --- | --- |
| `resolved` | A complete hull decomposition supplies `n_patches`, including a justified zero. |
| `unresolved` | The selected analysis encountered marginal geometry, incomplete evidence or a work ceiling; `n_patches` is `None`. |
| `not_computed` | Physical analysis was disabled or absent in historical data; no count is implied. |

Global patches and component attachments have separate availability. A complete
hull decomposition can coexist with an unresolved attachment search. Failure to
find a straight segment does not exclude a curved route. A zero boundary count
can also coexist with positive enclosed free volume, as at 1.4 Å in the tetrahedron.

The first independent receiving panel qualifies 4/0/0 patches for the tetrahedron
at 1.2/1.4/1.7 Å, zero for the 0.2 Å closed shell and one for the 1.4 Å opened
shell. The two positive controls include compatible continuous component paths.
This bounded source evidence is distinct from general biological qualification.

The fixed closed shell at 0.05 Å adds a more demanding control: the
[independent reference](../benchlab/synthetic/closed_shell/small_probe_connectivity.md)
establishes thirteen patches, including two disconnected regions on one face.
All thirteen have common-origin access. DFND's physical view agrees, while ten
native exterior clusters / Mouth children retain their compatibility meaning.
Independently checked [access/enclosure brackets](../benchlab/synthetic/origin_access_brackets.md)
also narrow the two shell transitions to 0.005 Å intervals. These are fixed-input
path/cover bounds, rather than exact bottlenecks or general path qualification.

## How the bounded decomposition works

On each hull triangle, all selected probe-expanded balls become plane disks.
The algorithm inventories circle extrema, circle intersections, circle/edge
intersections and triangle vertices. These critical sections delimit strips
whose analytic arc/line endpoint ordering is fixed. Their strict-free intervals
are connected across event sections and across independently checked free hull
edge intervals. Several free regions inside one face remain distinct.

Support retains triangle frames, circle constraints, analytic cell selectors,
source atom maps and seam intervals. Covered faces additionally retain a complete
positive-margin ball cover, using at most twelve subdivision levels. Thus an
empty candidate inventory alone cannot establish zero. Marginal arrangements
can use that cover to establish an empty face; they cannot guess a positive count.
The numerical margins are inspectable floating evidence, not formal interval arithmetic.

For a component contact, DFND checks the entire segment against all expanded
balls and covers its complete parameter interval with tetrahedra of that
component's carrier. The outward-normal continuation is checked as an infinite
all-atom ray. Endpoints, minimum margins, carrier intervals and support identities
are retained. These particular paths do not certify every edge of the native graph.

## Work policy and limits

`DFNDQuery` enables physical analysis by default with `physical_boundary=True`
and a separate `boundary_tolerance=1e-7` nm. This numerical margin does not widen
the strict physical set or reuse mesh epsilon. The default ceilings are 512
selected atoms, 512 hull faces, 100,000 arrangement work units, 4,096 association
records and 4,096 path attempts. The work units include tested intersections,
section/cell evaluation, joins and cover subdivision; they are not just the
number of final critical sections. Configure these limits through the query.

Exhaustion reports unresolved availability. Disabling the analysis reports
not computed. Broad hull families, numerical degeneracies and path searches
without a validated segment remain outside the qualified panel under
[#76](https://github.com/uibcdf/topomt/issues/76). Free aperture area and a globally
optimal bottleneck are not supplied by this connectivity observation.

The [new straight-tube control](../benchlab/synthetic/straight_tube_narrow_dense/index.md)
exercises that work ceiling: initial source `b07a20e` exhausts its arrangement
budget despite independently certified two-end hull patches. The count remains
unknown; [#180](https://github.com/uibcdf/topomt/issues/180) owns this bounded
extension. The earlier five-control qualification does not cover this tube.

## Other boundary roles

| Native relation | Interpretation in the discrete construction |
| --- | --- |
| Nonpermeable wet–bank face | A `shore` wall. |
| Permeable wet–bank incidence | A `beach` contact used by past-beach descriptors. |
| Nonpermeable boundary between wet components | An empty-space constriction descriptor. |
| Solid bank dividing regions | A possible solid septum, requiring its own support. |

`coast` is a local tetrahedron permeability class; it is not a synonym for every
boundary face. Wall clustering also uses carrier adjacency. Neither a whole
face nor an atom list by itself reconstructs a clipped physical free surface.
