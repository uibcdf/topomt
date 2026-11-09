# Probe scale, persistence and changing structures

Changing the probe and moving the atoms are different experiments. DFND's data
model separates the retained geometry from query-dependent states so that each
experiment can be described without confusing their identities.

## One geometry, several probes

For fixed coordinates, radii and mesh configuration, residence and gate
capacities are cached. A new probe query recomputes states, transit edges,
components, boundaries and derived records. It does not need to rebuild the
Delaunay mesh.

For the physical reference, if $p_2\ge p_1$, then $F_{p_2}\subseteq F_{p_1}$.
With fixed threshold policies, the discrete resident/admitted-contact and finite
transit availability are also nested as the probe grows. Components can split
or disappear, so their **count** need not decrease monotonically. A split can
increase the count even as the admitted set shrinks.

This statement fixes geometry and policies. Changing atom radii, coordinates,
intrusion policy or tolerances at the same time is not the same nesting test.

## Query reuse in the public result

Given a promoted result `topography`, use an explicit quantity:

```python
from topomt import pyunitwizard as puw

larger = topography.dfnd.at_probe(puw.quantity(1.7, 'angstroms'))
assert larger.network is topography.dfnd.network
```

`larger` is a new **DFNDData** result sharing protected geometry. It is not a new
promoted Topography, and it does not mutate the old Topography's features. Use a
new public analysis when separately promoted feature sets are required. The
[worked example](worked_tetrahedron.md) demonstrates both operations.

Sharing geometry still leaves per-query records and components in memory.
Retain only the queries needed by the analysis.

## Three persistence axes

| Axis | What is varied | What it describes |
| --- | --- | --- |
| Capacity hierarchy | Internal capacities within the current component/query | Ranked chamber/throat structure. |
| Probe scale | Probe radius on fixed geometry | Robustness, splitting, loss of residence and changes of access/name. |
| Time or structural ensemble | Coordinates, and possibly Delaunay support | Correspondence, lifetimes and structural events. |

A merge tree from one query is not the complete future event history of a probe
sweep. Component membership, contact clusters and residence can change. Cached
capacities provide the ingredients for new queries, not every catalog transition
without recomputing those relationships.

## Existing matching and tracks

`topomt.dfnd.lineage.match_results` compares components through exact
`support_key` equality and, when support differs, lining-atom Jaccard overlap.
`assign_tracks` chains pairwise correspondences into one-to-one tracks and
birth/death/split/merge events. These are implemented post-processing helpers.

An exact support match is strong evidence of equal tetrahedral support on the
same atom-index substrate. It is not equality of coordinates or proof of an
unchanged physical shape. Lining overlap is an explicit correspondence heuristic
and can be ambiguous when adjacent regions share many atoms.

## When atoms move

Delaunay cells can flip under coordinate changes, especially near cospherical
arrangements. A changed support digest does not necessarily mean a biological
site died. Conversely, reusing `WET-1` across frames does not prove continuity:
it is a size-ranked local label.

Frame-by-frame analysis needs consistent atom correspondence, explicit sampling
times and an event/matching policy. Flicker near numerical thresholds must be
distinguished from a physical opening. Optional temporal smoothing would be a
declared downstream operation, not a hidden modification of the static detector.

The helpers do not by themselves qualify a complete molecular-dynamics pipeline,
periodic transport or a kinetic interpretation. Temporal geometry can motivate
a gating hypothesis; rates, occupancy probabilities and biological function
require additional models and evidence.
