# The query graph and its decomposition

A mesh says which cells touch. A DFND query determines which of those contacts
are admitted for a probe, and which cells participate in the finite transit
graph. Connectivity is calculated from that graph rather than from a family name.

## Nodes and transit policy

Let $r_T$ denote the resident predicate and $k_T$ the number of locally admitted
faces of cell $T$, after the selected intrusion policy. The implemented rules are

| State | Predicate | Role |
| --- | --- | --- |
| Resident transit | $r_T$ | Participates in the transit graph and resident support. |
| Transit connector | $\neg r_T$ and $k_T\ge2$, when enabled | Participates in the graph, without resident volume. |
| Terminal contact | Nonresident, with one admitted contact | Contact information without through-connectivity. |
| Non-transit | Remaining nonresident cells | Outside the finite transit node set. |

`transit_policy='with_connectors'` enables the second row. Under
`resident_only`, finite transit nodes are the resident cells; nonresident
connector candidates are retained as terminal-contact diagnostics.

This distinction preserves the actual graph policy. It does not establish that
a physical probe passes through a cell in which its exact existential residence
capacity is insufficient. That {ref}`interpretation question <residence-and-paths>`
cannot be settled by naming the cell a connector.

## Edges and the common exterior

An internal transit edge requires both incident cells to be finite transit
nodes and their shared face to be admitted. The two sides use the same face
capacity/permeability decision. Marginality is recorded without imposing a
second, stricter edge threshold.

OCEAN is a virtual exterior node, represented natively by `-1`. It has no finite
tetrahedral geometry, residence capacity or volume. An admitted hull contact of
a finite transit cell supplies a graph connection to that root.

This is an abstract exterior connection. A locally admitted hull face is not
automatically an all-atom-free boundary patch. The
[boundary chapter](exterior_and_boundaries.md) explains the stronger condition.

## The decomposition

Remove OCEAN and its incident edges, then compute connected components of the
remaining finite transit graph. For each component retain:

- the full transit support and its atom-defined tetrahedra;
- its resident subset and connector subset;
- resident subregions and local state diagnostics;
- its hull contacts, grouped into native exterior links;
- all relevant query, support and source identities.

Removing the root prevents the surrounding exterior from merging all accessible
components through one shared node. It is a finite-region construction, not a
proof that each result is a separate connected component of the complete
physical admissible set $F_p$.

Residence regions answer another question: how resident nodes group inside one
transit component. One component can contain several resident regions joined
through the selected connector policy. Record those supports separately.

## What the result retains

The raw result includes all finite cell/face records, `wet_components`,
`residence_regions`, `external_links` and dry-side information. The historical
name `wet_components` includes finite transit components; it does not imply that
every constituent cell is locally resident. Inspect `resident_node_indices`
and `transit_connector_node_indices` in the typed view when that distinction
matters.

The bank graph uses the complement of finite transit nodes and is described in
[dry topography](dry_topography.md). Its node set differs from local nonresidence
when connectors are enabled.

## Decomposition, analysis and reporting

The component search precedes morphology and catalog naming. A reporting
threshold such as `min_size` can suppress a public/compatibility view without
removing the underlying raw component or changing its connectivity.

For the tetrahedron there is one finite cell. At 1.2 Å it is resident and all
four faces are admitted. At 1.4 Å it is still resident, with no admitted face.
At 1.7 Å neither resident nor connector conditions admit it into the finite
transit graph. Those outcomes follow before any Pocket/Void/Percolating name
is assigned.

**Reading check:** why can changing `min_size` remove a displayed finding without
changing the raw decomposition, while changing transit policy can change it?
