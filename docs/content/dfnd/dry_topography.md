# Dry banks, relief and solid-side structure

Looking only at empty regions loses information about what separates and lines
them. The bank view records complementary structure on the same mesh, supplying
incidence, exposure and depth from which richer relief descriptors can develop.

## Two different meanings of dry

A locally nonresident cell fails the residence threshold. The implemented bank
node set is instead

$$D_p=\{T:T\notin\text{finite transit nodes at }p\}.$$

With connectors enabled, a nonresident connector belongs to the transit graph
and is excluded from $D_p$. With resident-only transit, the complement agrees
with nonresidence under the same numerical policy.

These are discrete graph roles. A bank tetrahedron spans space between atom
centers; it is not literally a piece of atomic material. Likewise, a wet carrier
tetrahedron is not entirely solvent. Their complementary node sets do not prove
a physical partition into molecular solid and accessible liquid.

## Bank connectivity

Under the default `dry_adjacency='face'`, two bank nodes connect only when
**both owner incidences** of their shared face are nonpermeable. Incidence
states can differ under `block_suspect`; a mixed pair therefore supplies neither
a wet edge nor a face-adjacent dry edge. The dry edge set is not the logical
complement of the wet edge set. Alternative edge/vertex adjacency groups nodes through shared
atom pairs or individual atoms and does not apply that face-permeability filter.
Those alternatives answer different grouping questions. The
[neighbor selectors](network_and_decomposition.md#advanced-inspection-residence-and-component-side-neighbors)
also distinguish residence-state filtering from actual wet-carrier/bank membership;
nonresident connectors belong to the former nonresident set and the latter wet set.

Connected bank components retain atom-defined tetrahedral support. Their
interfaces record hull exposure and contacts with resident/transit cells or
other banks. Unweighted face-depth propagation measures distance from selected
boundary nodes into the bank graph; it is not a physical burial distance.
A wet component without exterior-link roots retains zero depth by compatibility
convention. It has no measured exterior-distance reference at that value.

## What is implemented

Native records include bank components, interface faces, boundary/exposed shells,
lining-related supports and depth/core candidates. Wet and dry typed components
can inspect complementary lining relationships. These are useful observations
without requiring a public protrusion class.

A single bank can carry several lobes, ridges, rims and buried regions. Its
connected-component count therefore cannot be used as a protrusion count.

## From bank support to relief

A reproducible relief operator needs more than a bank label:

| Intended entity | Additional definition required |
| --- | --- |
| Convex patch or protrusion | A surface support, reference neighborhood/envelope, outward prominence and a base/boundary. |
| Ridge or apex | A ridge/maximum criterion, localized support and scale/stability policy. |
| Rim | Boundary extraction and ordering around a declared contact, distinct from the aperture itself. |
| Buried core | A stated depth/material criterion; an interior region is not outward convexity. |
| Solid septum | A localized bank separating specified regions, with both side roles. |

General public promotion of these entities remains unfinished. The intended
operators are part of DFND's broader topographic program; current bank/depth
records provide grounding rather than a completed segmentation of all relief.

## Interpreting wall evidence

A nonpermeable face between wet components is an empty-space constriction
descriptor. A solid divider is a bank with walls on its sides. These structures
must not be interchanged merely because both are colloquially called a septum.
Some compatibility field names retain older terminology; use their support and
definition when interpreting a record.

The distinction also matters for interfaces: a bank is a geometric object, while
a molecular participant is supplied by molecular identity/selection. Their
relationship is developed in the [next chapter](interfaces.md).

**Reading check:** if two molecular chains form one dry bank, has the molecular
interface disappeared, or has the chosen geometric grouping fused its banks?

```{dropdown} Check your reasoning
The grouping has fused the bank support. It says nothing by itself about whether
a participant-to-participant interface exists. Participant identity and the
localized contact/patch criterion are additional observations, as the
[interface chapter](interfaces.md) explains.
```
