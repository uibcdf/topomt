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
nodes and **both incidences** of their shared face to be admitted. An incidence
is the face as seen from one of its two neighboring cells. Its cached capacity
is identical on both sides, but intrusion policy can give different admission
states: each cell has its own opposite apex. Under `block_suspect`, one side
can be blocked while the other passes. The edge then remains absent on both
records. Marginality does not impose a second, stricter capacity threshold.

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

Resident-only connectivity answers another question: how resident nodes group
when connector nodes are excluded. A transit component can contain several such
connected subsets. The current raw `residence_regions` field instead stores
**one resident aggregate per transit component with resident content**, with
connectors listed separately. It does not export one record per resident-only
connected subset. Use the recorded supports rather than inferring that count
from the length of the field.

## Follow a multi-cell graph by hand

```{figure} figures/finite_decomposition.svg
:alt: Before removing OCEAN, its edges join the A-C-B and D-E groups through the exterior. After removal these are separate finite components, alongside the isolated resident cell S. C is a connector.

An abstract policy illustration, not a geometrically certified arrangement of
atoms. Circles are resident cells; the diamond is a nonresident connector.
Lines stand for admitted graph contacts, not center trajectories.
```

Assume only the drawn contacts are admitted, and enable connectors. The three
finite components after removing OCEAN are $\{A,C,B\}$, $\{D,E\}$ and $\{S\}$.
The first contains two resident-only connected subsets, $\{A\}$ and $\{B\}$,
joined through connector $C$. Its current raw residence record would aggregate
$\{A,B\}$, retaining $C$ separately. The sealed resident cell $S$ remains a component despite
having no exterior contact. Keeping OCEAN would join the first two groups through
the root and hide their finite separation.

Switching to `resident_only` removes $C$ from the transit node set, yielding four
finite components: $\{A\}$, $\{B\}$, $\{D,E\}$ and $\{S\}$. By contrast,
`min_size=3` under the original connector policy leaves all three raw components
intact, but includes only $\{A,C,B\}$ in the compatibility reporting view: the
current size filter counts **transit cells**, including connectors.

The diagram establishes the consequences of the stated graph rules. It supplies
no atomic geometry realizing the nonresident connector, no count of physical
boundary patches, and no physical crossing certificate. Those require the
separate [local-capacity](local_capacities.md) and
[boundary](exterior_and_boundaries.md) arguments.

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

```{dropdown} Check your reasoning
`min_size` filters an already decomposed result. Transit policy determines which
nodes enter that decomposition. In the diagram, filtering hides small groups;
removing connector C actually separates A from B. Neither operation changes
cached local capacities.
```

## Advanced inspection: one face, two owner states

The existing closed shell makes the distinction concrete. At 0.2 Å, face support
`[13, 23, 26]` has shared gate capacity 0.1198879391121351 nm. With `flag_only`
both incidences pass. Switching to `block_suspect` blocks one incidence; neither
record then has a transit edge. This describes the implemented graph policy,
without certifying a physical path through the face.

To reproduce it, save {download}`closed_shell.py <examples/closed_shell.py>` in
your working directory, and put the canonical
{download}`input.json <../benchlab/synthetic/closed_shell/artifacts/closed_shell_v1/input.json>`
and {download}`input.pdb <../benchlab/synthetic/closed_shell/artifacts/closed_shell_v1/input.pdb>`
in `shell_input/`. The script restores full-precision coordinates, checks the
frozen input hash/radii and runs the public molecular route. The PDB supplies
dummy topology; no new molecular system or external engine is downloaded.

```python
from pathlib import Path
from closed_shell import analyze_closed_shell
from topomt import pyunitwizard as puw

shell_topography = analyze_closed_shell(Path('shell_input'))
blocked = shell_topography.dfnd.at_probe(
    puw.quantity(0.2, 'angstroms'), gate_intrusion_policy='block_suspect'
)
face_pair = [f for f in blocked.raw['faces']
             if sorted(f['atom_indices']) == [13, 23, 26]]
assert len(face_pair) == 2
assert face_pair[0]['R_gate'] == face_pair[1]['R_gate']
assert {f['permeability_state'] for f in face_pair} == {'permeable', 'non_permeable'}
assert not any(f['transit_edge'] for f in face_pair)
assert any('blocked_by_intrusion_policy' in f['flags'] for f in face_pair)
baseline = [f for f in shell_topography.dfnd.raw['faces']
            if sorted(f['atom_indices']) == [13, 23, 26]]
assert all(f['permeability_state'] == 'permeable' for f in baseline)
```

The records keep their owner/neighbor IDs and source atoms. Locate the support
by its atoms rather than assuming a local face number survives another mesh
revision. [Local capacities](local_capacities.md#the-apex-intrusion-policy)
define the exact heuristic behind the flags.

## Advanced inspection: a many-cell center

On the same result, the reported Void with the most transit cells has several carrier cells. Its
public center can be recovered from their geometry:

```python
import numpy as np

shell_void = max(shell_topography.get_features(by='type', value='void'),
                 key=lambda feature: len(feature.tetrahedron_indices))
shell_component = shell_topography.dfnd.dfn.components[shell_void.component_id]
resident_aggregate = next(
    region for region in shell_topography.dfnd.raw['residence_regions']
    if region['component_key'] == shell_component.component_key
)
assert resident_aggregate['tetrahedron_ids'] == shell_component.resident_node_indices
network = shell_topography.dfnd.network
nodes = shell_component.node_indices
cell_vertices = network.atom_coords[network.tetra_atoms[nodes]]
cell_volumes = network.mesh.simplex_volumes[nodes]
centroid_nm = np.average(cell_vertices.mean(axis=1), axis=0, weights=cell_volumes)
np.testing.assert_allclose(
    puw.get_value(shell_void.center, to_unit='nm'), centroid_nm, rtol=0, atol=1e-13
)
```

This is a **carrier centroid**, distinct from the optimized residence centers
of individual cells. The [measurement definition](measurements.md#centers-and-placement)
explains why it is not a guaranteed free placement point. For a many-cell public
Mouth and its parent/support mapping, follow the existing
[three-case walkthrough](../benchlab/synthetic/public_topography.md).
