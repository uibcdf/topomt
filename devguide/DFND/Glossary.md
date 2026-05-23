# Delaunay Flow Network Decomposition (DFND): Glossary

A quick reference for the terminology used in the DFND module.

> **Terminology authority.** The `component → domain → feature` ladder and the
> two reserved-word rules (`feature` never inside dfnd; `motif` never at the
> Topography level) are defined authoritatively in
> [`object_model.md`](object_model.md). Some entries below still use the legacy
> wording (wet "transit/concavity domain" vs "dry component"); per the object
> model these are unified as **`component`** (the graph object) with its
> **`domain`** (the atoms). When in doubt, `object_model.md` wins.

## Object Model Terms (component → domain → feature)

The current first-class vocabulary (see [`object_model.md`](object_model.md)):

*   **Component:** the **graph** object — a connected component of the DFN graph,
    i.e. a set of tetrahedron nodes (plus their faces/edges). The output of the
    DFND *decomposition*. Probe-dependent. Lives in `dfn.components` as a typed
    `WetComponent` / `DryComponent`.
*   **Domain:** that component **realized in the molecular system** — its lining
    atoms, volume, centre, spatial footprint. A facet of the component
    (`component.atom_indices`, `component.volume_solvent_estimate`, …), not a
    separate object. *"The domain of the component."*
*   **Motif:** a named sub-structure **of a domain** — throat/bottleneck, chamber,
    depth-region, mouth (`external_mouth`). Promotes to a child feature.
*   **Feature:** the **public** `Topography` object promoted from a domain
    (`Pocket`/`Void`/`Channel`/`Mouth`/…). The word *feature* is reserved for the
    public level; *motif* is reserved for dfnd.

The raw engine dictionary (`topography.dfnd.raw`) keeps its original field names
(`concavity_domains`, `transit_domains`, `residence_regions`, family strings like
`pocket_domain`, …) as the **legacy provenance layer**; the object-model layer
(`topography.dfnd` and the `Topography` features) is what speaks the ladder above.

## Graph Elements

*   **Node (Tetrahedron):** The elementary volumetric unit of the mesh, defined by 4 atoms.
*   **Edge (Face/Valve):** The connection between two nodes, defined by 3 atoms.
*   **OCEAN / Root (-1):** The virtual exterior node of the DFND graph. It
    represents the infinite solvent region outside the convex hull and is wet
    by definition. It is not a Delaunay tetrahedron, has no finite geometry,
    has no `R_residence`, has no volume, and cannot be `COAST`.

## Tetrahedron States

*   **Dry tetrahedron:**
    *   A tetrahedron where the probe cannot fit as a resident sphere.
    *   Condition: `R_residence < R_probe`.
    *   It can still be useful as contact or lining metadata if one of its faces is permeable.

*   **Wet tetrahedron:**
    *   A tetrahedron where the probe can fit.
    *   Baseline condition: `R_residence >= R_probe`.
    *   Wet tetrahedra connected through permeable faces form the primary wet-flow graph.

*   **OCEAN:**
    *   The virtual exterior/root node used as the outside reference.
    *   It is wet by definition because the probe is assumed to fit freely in the infinite exterior.
    *   A finite wet tetrahedron connects to `OCEAN` only through a boundary or hull face that is permeable to the selected probe.
    *   Boundary faces are finite faces of finite tetrahedra whose Delaunay neighbor is `-1`; the `-1` marker is a hull/exterior signal, not a real tetrahedron.

*   **OPEN:**
    *   A finite tetrahedron whose finite faces are all permeable.
    *   This is a local permeability label, independent of wet/dry habitability.

*   **COAST:**
    *   A finite tetrahedron with mixed local permeability.
    *   Working condition: the tetrahedron has at least one permeable finite face and at least one non-permeable finite face.
    *   `wet_coast` is a wet tetrahedron on a partially blocked boundary.
    *   `dry_coast` is a dry tetrahedron with at least one permeable face; it can help describe lining atoms or pharmacophore contact without creating wet connectivity.

*   **SEALED:**
    *   A finite tetrahedron whose finite faces are all non-permeable.
    *   This is a local permeability label, independent of wet/dry habitability.

*   **non-coast:**
    *   A derived complement only: `open` or `sealed`. It should not be used as a primary DFND label.

## Face States

*   **Permeable face:**
    *   A face whose gate can be crossed by the probe.
    *   Condition: `R_gate >= R_probe`.

*   **Non-permeable face:**
    *   A face whose gate blocks the probe.
    *   Condition: `R_gate < R_probe`.

Faces should be called permeable or non-permeable. Wet and dry are reserved for tetrahedra and volumetric regions.

## Geometric Metrics

*   **`R_probe`:** The radius of the solvent probe, with 1.4 Å as the water-probe default.
*   **`R_sea_level`:** Exterior reference scale. In the first DFND policy, its default is tied to `R_probe`; larger values are a pending optional mode.
*   **`R_gate` (Face Permeability):** The radius of the largest sphere that can pass through a triangular face.
*   **`R_residence` (Tetrahedron Habitability):** The radius of the largest sphere that fits inside a tetrahedron without overlapping atoms.
*   **`R_alpha` (Alpha Radius):** The radius of the orthogonal sphere of a tetrahedron. It may be retained as diagnostic metadata, but it is not the primary physical habitability criterion.

## Graph and Structural Features

*   **DFN:** The Delaunay Flow Network. It is the probe-specific movement graph built from finite transit tetrahedra, permeable faces, and the virtual wet `OCEAN` root. Transit tetrahedra include resident nodes and non-resident transit connectors.
*   **External link:** A connected cluster of permeable boundary or hull contacts linking one finite transit domain to `OCEAN`. It is a DFN primitive.
*   **Mouth:** A geometric descriptor that can be derived from an `external_link`. It is not the primitive used for primary DFN feature classification.
*   **Wet component:** A connected component obtained after removing `OCEAN` and its incident edges from the DFN. The mathematical graph object (a set of tetrahedron nodes); the raw field is `wet_components`. Each carries a `family`.
*   **Domain:** A component realized in the system — its lining atoms, volume, centre. A facet of the component, not a separate object.
*   **Feature:** The public `Topography` object promoted from a domain (`Pocket`/`Void`/`Channel`/`Mouth`/…), after adding metrics, atoms, residues, mouth geometry, morphology, dynamics, and annotations.
*   **Component family** (`family`): the classification of a wet component by `n_external_links` × `has_residence`:
    *   `void` — zero `external_links`, at least one resident node.
    *   `pocket` — exactly one `external_link`, at least one resident node.
    *   `channel` (raw `multi_external_link`) — two or more `external_links`, at least one resident node. `Channel` is a public shorthand; tunnel/pore needs path/morphology evidence.
    *   `surface_concavity` — exactly one `external_link`, no resident nodes (a one-mouth non-resident contact/dent, not simply a shallow pocket).
    *   `nonresident_passage` — two or more `external_links`, no resident nodes; provisional raw label, not a biological channel by default.
    *   `degenerate_subprobe` — zero `external_links`, no resident nodes; raw/filter label, not a void.
*   **Has open interior:** Component descriptor indicating that at least one resident node is `wet_open`; not a family discriminator.
*   **Dry component:** A connected component of dry tetrahedra connected through non-permeable faces (family `dry_bank`). A raw dry-graph object, not automatically a public feature.
*   **Dry interface:** A contact record between a dry component and wet domains, external links, `OCEAN`, or the hull/exterior context.
*   **Dry depth:** Unweighted graph distance from dry-interface boundary nodes into a dry component. It describes topographic dry burial, not Euclidean depth or mechanical rigidity.
*   **Dry motif:** A candidate descriptor derived from dry components and dry interfaces, such as a dry core, protrusion, ridge, rim, wall, separator, or lining region.
*   **Rim:** A dry/interface motif around or bordering an exterior opening. It is distinct from a mouth, which is derived from an `external_link`.
*   **Core:** A future convexity feature or dry motif associated with deeply buried dry topology. It should not be assumed to be simply the largest dry component.
*   **Protrusion:** A future convexity feature or dry motif associated with dry topology exposed to `OCEAN` and projecting into accessible exterior space.

*   **Transit connector:** A non-resident tetrahedron with at least two permeable contacts. It connects movement domains but does not contribute resident volume.
*   **Terminal contact:** A non-resident tetrahedron with exactly one permeable contact. It can be touched from one side but does not provide through-transit.
*   **Residence region:** Resident-node content inside one transit domain.
