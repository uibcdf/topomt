# Delaunay Flow Network Decomposition (DFND): Glossary

A quick reference for the terminology used in the DFND module.

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
*   **Transit domain:** A connected component obtained after removing `OCEAN` and its incident edges from the DFN. This is the mathematical graph object.
*   **Concavity domain:** A transit domain interpreted as one spatial concavity domain after adding residence regions, external links, and metadata. This is the canonical DFND decomposition object.
*   **Concavity feature:** A Topography object derived from a concavity domain after adding metrics, atoms, residues, derived mouth geometry, morphology, dynamics, and annotations.
*   **Void domain:** A transit domain with zero `external_links` and at least one resident node.
*   **Surface concavity domain:** A transit domain with exactly one `external_link` and no resident nodes. It is a one-mouth non-resident contact or dent, not simply a shallow pocket.
*   **Pocket domain:** A transit domain with exactly one `external_link` and at least one resident node.
*   **Multi-external-link domain / channel domain:** A transit domain with two or more `external_links` and at least one resident node. `Channel` is a public shorthand; tunnel or pore interpretation requires additional path or morphology evidence.
*   **Nonresident passage domain:** A transit domain with two or more `external_links` and no resident nodes; provisional raw label, not a biological channel by default.
*   **Degenerate subprobe domain:** A transit domain with zero `external_links` and no resident nodes; raw/filter label, not a void.
*   **Has open interior:** Domain descriptor indicating that at least one resident node is `wet_open`; not a family discriminator.
*   **Dry component:** A connected component of dry tetrahedra connected through non-permeable faces. It is a raw dry-graph object, not automatically a public feature.
*   **Dry interface:** A contact record between a dry component and wet domains, external links, `OCEAN`, or the hull/exterior context.
*   **Dry depth:** Unweighted graph distance from dry-interface boundary nodes into a dry component. It describes topographic dry burial, not Euclidean depth or mechanical rigidity.
*   **Dry motif:** A candidate descriptor derived from dry components and dry interfaces, such as a dry core, protrusion, ridge, rim, wall, separator, or lining region.
*   **Rim:** A dry/interface motif around or bordering an exterior opening. It is distinct from a mouth, which is derived from an `external_link`.
*   **Core:** A future convexity feature or dry motif associated with deeply buried dry topology. It should not be assumed to be simply the largest dry component.
*   **Protrusion:** A future convexity feature or dry motif associated with dry topology exposed to `OCEAN` and projecting into accessible exterior space.

*   **Transit connector:** A non-resident tetrahedron with at least two permeable contacts. It connects movement domains but does not contribute resident volume.
*   **Terminal contact:** A non-resident tetrahedron with exactly one permeable contact. It can be touched from one side but does not provide through-transit.
*   **Residence region:** Resident-node content inside one transit domain.
