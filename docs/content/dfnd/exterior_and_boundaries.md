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

Physical patch decomposition and the relation to Mouth/Percolating remain
tracked in [#151](https://github.com/uibcdf/topomt/issues/151). Candidate physical
contact views are not an implemented public API. No code example here invents
their counts or substitutes native links for missing physical observations.

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
