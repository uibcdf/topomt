# Dumbbell: two chambers and a neck

When can a probe fit in both chambers yet fail to move between them? This
94-ball system follows communication and separation into DFND's native graph,
its provisional hierarchy and the actual public `Topography`.

**Read [the system](system.ipynb) first**, then [DFND observations](dfnd.ipynb).
Both notebooks run independently in fresh kernels. The website keeps long code
inputs expandable, with explanations, semantic tables and figures visible.

```{figure} artifacts/dumbbell_v1/system_study.png
:alt: Atomic centers, two chamber anchors and a separately certified enclosing barrier, alongside complete-axis clearance compared with three probe radii.
:width: 100%

The fixed atomic system and independent reference construction. Markers denote
atomic centers. The reference barrier is a covered polyhedron, not a smooth
physical surface or the native convex hull.
```

```{toctree}
:maxdepth: 1

system
dfnd
Evidence and replay <artifacts/dumbbell_v1/README>
```

## Three controls, with explicit reference scope

The input contains 94 argon balls of radius 1.88 Å, constructed from nominal
7 Å lobes whose centers are 12.5 Å apart. Sampling is nominally 3.5 Å, with
jitter 0.1 Å and seed zero. Full-precision coordinates define the ball model;
the original rounded PDB supplies topology only.

| Probe | Independent reference | Actual native/public result | Availability and limits |
| --- | --- | --- | --- |
| 1.4 Å | Both chamber anchors are free, enclosed and connected by a complete all-atom path. | Both reach one public Void. Its two chamber motifs and one throat have recoverable source support and reach the public parent. An extra OpenConcavity/Mouth is retained separately. | Global physical hull count is numerically unresolved, [#184](https://github.com/uibcdf/topomt/issues/184). Motifs remain provisional. |
| 2.2 Å | Both anchors remain free and enclosed, but a complete covered neck section separates them. | The anchors reach distinct public Voids, each without an internal chamber/throat hierarchy at this query. Additional surface candidates remain visible. | Global physical hull arrangement exhausts its budget, [#180](https://github.com/uibcdf/topomt/issues/180). The reference establishes at least two enclosed regions, not an exact global count. |
| 6 Å | Every point in the finite native hull is covered by expanded balls. | No native wet component or public feature remains. | Physical hull count still budget-unresolved (#180), although its independent target is zero. |

These are observations from scientific/helper source
`17a4c9a521c89a64efb12ba339161e15c85d4ce0`, with source/producer identities
retained separately for original capture and clean-source readers. No scientific
operator was retuned to obtain the transition.

## What the geometry proves

The complete connecting-axis clearance is **1.432602186 Å**, leaving a
**0.032602186 Å** margin for the 1.4 Å probe. The left and right anchors have
clearances **4.972042260 Å** and **4.886156411 Å**, respectively. They fit both
smaller probes even after their communication is excluded.

A closed nonconvex polygonal barrier has **1,984 completely covered triangular
faces** at 1.4 Å. Both anchors lie inside it. At 2.2 Å, **32 triangles** cover
the entire neck section. Those wall and section certificates exclude both an
internal connecting path and an escape around the wall. They establish the
named-region transition, without counting every possible physical region.

The barrier **P** differs from the atomic-center convex hull **H** used as the
native finite carrier. For the 6 Å control, a separate complete cover of H's
128 fan tetrahedra excludes all strict-free centers in H. Its unbounded exterior
still exists. A statement on P does not count every free patch on H.

## What reaches Topography

At 1.4 Å, source-mapped anchor cells select the same public parent, `VOI-1`.
Its `.motifs` retain the actual native chamber/throat dictionaries, parent keys,
source supports, sibling relations and `provisional` flags. They are not
standalone Chamber children in `children_of`, and their carrier supports are
not certified all-atom free-volume boundaries.

The native throat descriptor is **1.537739193 Å**. It is conditional on the
local graph/support; the independent controls do not validate it as the globally
optimal physical passage radius. At 2.2 Å the two anchored public Voids are
separate result objects. Repeated display IDs across probes do not establish
cross-query identity; compare their anchors, query context and source supports.

## Reading the count change honestly

The physical free set shrinks as the probe grows, but its connected components
can split. More components at a larger probe are therefore **not inherently a
failure**. The older two-versus-five native-domain observation at 1.4/2.0 Å needs
individual support diagnosis under [#188](https://github.com/uibcdf/topomt/issues/188),
`needs_review`. These new 1.4/2.2 Å references neither validate nor refute every
one of those five domains.

The [joint six-case review](https://github.com/uibcdf/topomt/issues/187) follows
this unit's establishment under #186. It retains the tubes' #180/#181/#184/#76
questions and the [version-scoped finding register](https://github.com/uibcdf/topomt/discussions/154).
The successful 6 Å empty native/public result here does not correct the tubes'
local/all-atom qualification discrepancy under #181.

## Download and reproduce

Download the {download}`complete dumbbell study <../../../../_static/benchlab/dumbbell_v1.zip>`,
extract it and follow `README_STUDY.md`. It includes both notebooks, input,
independent checkers, original observations, attribution, figures, environment
inputs and a per-file SHA-256 manifest. Execute each notebook from its case
directory in a fresh Python 3.14 kernel, using the pinned scientific source.
Run All does not overwrite evidence or execute an original provider/server.
Source/environment acquisition can need network access.

This is a known, retrospective development input. No original third-party
comparison has been executed here. Exact global region counts, physical volume,
optimal bottlenecks, biological accuracy, installed-release and platform-matrix
qualification do not follow. Previous study artifacts/notebooks/ZIPs remain
unchanged. The [evidence guide](artifacts/dumbbell_v1/README.md) retains the
reference/capture/reader chronology and bounded resource receipts.
