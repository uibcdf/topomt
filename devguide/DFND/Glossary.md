# Delaunay Flow Network Decomposition (DFND): Glossary

Historical note: the preferred method name is now `DFND`; older mentions of
`DFND` in this subdirectory should be read as the previous provisional label.

A quick reference for the terminology used in the DFND module.

## Graph Elements

*   **Node (Tetrahedron):** The elementary volumetric unit of the mesh, defined by 4 atoms.
*   **Edge (Face/Valve):** The connection between two nodes, defined by 3 atoms.
*   **Root (-1):** A virtual node representing the "Infinite" or "Outside". All `OCEAN` nodes are collapsed into this single node.

## Topological States (Nodes)

*   **SOLID:**
    *   A tetrahedron that is physically occupied by the protein structure.
    *   Condition: $R_{insphere} < R_{probe}$.
    *   Forms the **Dry Network**.

*   **TRANSIT:**
    *   A tetrahedron that represents habitable empty space.
    *   Condition: $R_{probe} \le R_{insphere} < R_{sea\_level}$.
    *   Forms the **Wet Network** (the core of Pockets/Channels).

*   **COAST:**
    *   A tetrahedron that is geometrically open ($R_{\alpha} > R_{probe}$) but physically effectively closed or "flat" ($R_{insphere} < R_{probe}$), or simply a dead-end branch of the flow.
    *   Acts as the "surface layer" or "beach" of a pocket. It contributes to volume but not to flow throughput.

*   **OCEAN:**
    *   A tetrahedron representing the bulk solvent far from the protein.
    *   Condition: $R_{insphere} \ge R_{sea\_level}$.
    *   Merged into the **Root** node.

## Geometric Metrics

*   **$R_{probe}$:** The radius of the solvent probe (e.g., 1.4 Å for water). User-defined parameter.
*   **$R_{sea\_level}$:** The radius defining the "Macro-Surface" or bulk solvent boundary (e.g., 10 Å). Used to distinguish Pockets from the Ocean.
*   **$R_{gate}$ (Face Permeability):** The radius of the largest sphere that can pass through a triangular face.
*   **$R_{insphere}$ (Tetrahedron Habitability):** The radius of the largest sphere that fits inside a tetrahedron without overlapping atoms.
*   **$R_{\alpha}$ (Alpha Radius):** The radius of the orthogonal sphere of a tetrahedron (standard Alpha Shape metric).

## Structural Features

*   **Pocket:** A connected component of `TRANSIT` + `COAST` nodes reachable from the Root.
*   **Void:** A connected component of `TRANSIT` + `COAST` nodes **NOT** reachable from the Root (buried).
*   **Mouth:** A set of faces connecting a Pocket to the Root (Ocean).
*   **Channel:** A path in the Wet Network connecting two distinct Mouths (a topological cycle through the Root).
*   **Core:** The largest connected component of the `SOLID` (Dry) Network.
*   **Protrusion:** A branch of the `SOLID` Network extending into the Ocean.
