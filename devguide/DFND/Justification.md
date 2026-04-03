# Delaunay Flow Network Decomposition (DFND): Justification and Novelty

Historical note: the preferred method name is now `DFND`; older mentions of
`DFND` in this subdirectory should be read as the previous provisional label.

## 1. The Landscape of Current Methods

To justify the development of DFND, we must critically evaluate the current state-of-the-art in molecular topography analysis. The field is broadly divided into two families:

### 1.1. Pure Geometric Methods (e.g., CASTp, Alpha Shapes)
*   **Mechanism:** Construct the Delaunay triangulation and filter tetrahedra based on the radius of the associated Alpha Sphere ($R_{\alpha}$). Adjacent empty tetrahedra are merged into pockets.
*   **Limitation:** They rely on a binary "Exist/Don't Exist" classification based on a single parameter ($R_{probe}$). 
    *   *The Fusion Problem:* If two large pockets are connected by a tiny, biologically irrelevant neck (slightly larger than $R_{probe}$), they are merged into a giant, meaningless cluster.
    *   *The Separation Problem:* If the probe is slightly increased, the neck breaks, and the pockets are totally separated, losing the information that they are proximal.
    *   *Lack of Hierarchy:* They do not inherently capture the "structure" of the empty space (chambers, bottlenecks, mouths).

### 1.2. Scanning/Grid Methods (e.g., Fpocket, LIGSITE, PockDrug)
*   **Mechanism:** Use grids, rays, or Voronoi vertices (without full tessellation logic) to scan for void points and cluster them.
*   **Limitation:** 
    *   *Approximation:* Grid methods suffer from discretization errors (voxel size dependency) and orientation dependence.
    *   *Heuristic Connectivity:* The clustering of "alpha spheres" in Fpocket is based on distance heuristics ($D_{max}$), not physical connectivity. It works well for simple pockets but struggles with complex, branching tunnel systems.

### 1.3. Tunnel Finders (e.g., MOLE, Caver)
*   **Mechanism:** Construct a Voronoi diagram and find optimal paths (centerlines) from a user-defined start point to the surface.
*   **Limitation:** They reduce the 3D volume of a pocket to a 1D line. They are excellent for ion channels but poor for large, irregular binding clefts where "volume" matters more than "path."

---

## 2. The DFND Innovation: "Topological Hydraulics"

DFND is novel because it **unifies** these approaches into a single, physically consistent model. It is neither just a volume calculator (CASTp) nor just a pathfinder (MOLE).

### 2.1. Decoupling Volume from Connectivity
This is the single most significant innovation.
*   **CASTp:** $Volume \iff Connectivity$. If it fits, it connects.
*   **DFND:** $Volume \neq Connectivity$.
    *   **Volume** is defined by the tetrahedron's habitability ($R_{insphere}$). 
    *   **Connectivity** is defined by the face's permeability ($R_{gate}$). 

**Why this matters:** This allows DFND to identify a "Dumbbell Pocket" (two large volumes connected by a narrow neck) as a single topological object with two distinct sub-domains separated by a constriction. Traditional methods see either "One Blob" or "Two Blobs" depending on the probe radius. DFND sees "Two Chambers connected by a Gate."

### 2.2. The "Coast" Concept
Geometric methods often suffer from "sliver tetrahedra"—flat, unphysical artifacts of Delaunay triangulation that have large Alpha radii but zero volume.
*   **Novelty:** DFND introduces the explicit topological category **`COAST`** (accessible but not transitable). This acts as a robust filter for geometric noise, preserving the surface atoms without allowing false flow paths through non-physical slivers.

### 2.3. The "Sea Level" Reference
By introducing the `OCEAN` concept (defined by a large "Beach Ball" Alpha Shape), DFND solves the boundary condition problem.
*   **Novelty:** Instead of using the Convex Hull (too loose) or a tight probe wrap (too noisy), DFND uses a **multi-scale definition of the exterior**. The "Pocket" is rigorously defined as the volume between the "Molecular Surface" (inner limit) and the "Beach Ball Surface" (outer limit).

### 2.4. Symmetric Wet/Dry Analysis
Most tools focus 100% on the empty space. DFND treats the solid space (`SOLID` network) with the same mathematical rigor.
*   **Novelty:** This enables "Inverse Pocket Detection" (i.e., Protrusion Detection) using the exact same code, providing a holistic view of surface complementarity for PPI analysis.

## 3. Summary of Advantages

| Feature | CASTp | Fpocket | MOLE | **DFND** |
| :--- | :---: | :---: | :---: | :---: |
| **Exact Volume** | ✅ | ❌ | ❌ | ✅ |
| **Bottleneck Detection** | ❌ | ❌ | ✅ | ✅ |
| **Multi-Chamber Topology** | ❌ | ❌ | ❌ | ✅ |
| **Noise Robustness** | ⚠️ | ✅ | ✅ | ✅ (**Coast**) |
| **Wet/Dry Symmetry** | ❌ | ❌ | ❌ | ✅ |
| **Physical Interpretability** | High | Medium | High | **Very High** |

DFND is not just an incremental improvement; it is a **structural generalization** that contains CASTp and MOLE as special limit cases, offering a richer grammar for describing molecular shape.
