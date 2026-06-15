# Delaunay Flow Network Decomposition (DFND): Technical Design

This document bridges the gap between the mathematical definitions and the actual Python code. It defines the data structures, algorithms, and architectural choices to ensure performance and maintainability.

## 1. Data Structures: "Structure of Arrays"

To avoid the overhead of Python objects for millions of tetrahedra, we will use a **Structure of Arrays (SoA)** approach powered by NumPy.

### 1.1. The Mesh Object (`DelaunayMesh`)
This internal class holds the static geometry derived from Delaunay. It does
**not** depend on $R_{probe}$.

*   **`vertices`**: `ndarray (N_atoms, 3) float32` - Atom coordinates.
*   **`atom_radii`**: `ndarray (N_atoms,) float32` - vdW radii.
*   **`simplices`**: `ndarray (N_tet, 4) int32` - Indices of atoms forming each tetrahedron (from `scipy.spatial.Delaunay`).
*   **`neighbors`**: `ndarray (N_tet, 4) int32` - Indices of neighboring tetrahedra (-1 for boundary).

This object should also be the place where alpha-sphere-derived data is
materialized when needed. In DFND, alpha-spheres are no longer treated as a
separate architectural center. They are a derived view of the Delaunay mesh.

That means `DelaunayMesh` may also expose or cache:

*   alpha-sphere centers;
*   alpha-sphere radii;
*   tetrahedron-to-alpha-sphere mappings;
*   face-adjacency-derived alpha-sphere neighbor relations.

This keeps the representation hierarchy explicit:

*   **primary representation:** tetrahedra and shared faces;
*   **derived view:** alpha-sphere-centered arrays for methods that find that
    representation convenient.

### 1.2. The Persistent Graph Attributes
We pre-calculate and store the limiting radii. This allows the "Master Graph" functionality (querying different probes instantly).

*   **`node_habitability`**: `ndarray (N_tet,) float32`
    *   Stores $R_{residence}$ for each tetrahedron.
    *   *Usage:* To check if node $i$ is `wet` or `dry` for a given probe, we just check `node_habitability[i] >= R_probe`.

*   **`edge_permeability`**: `scipy.sparse.dok_matrix` or distinct arrays.
    *   Stores $R_{gate}$ for the interface between tetrahedra.
    *   Since the graph is structurally static (Delaunay topology), we can store this efficiently.
    *   *Optimization:* We might use two arrays: `edge_indices (N_edges, 2)` and `edge_values (N_edges,)` to store $R_{gate}$. This allows vectorized filtering.

---

## 2. Dependencies and Libraries

### 2.1. Triangulation: `scipy.spatial.Delaunay`
*   **Choice:** Use standard Delaunay triangulation initially.
*   **Justification:** DFND is conceptually cleaner when the tessellation is a
    neutral geometric partition of atomic centers and the atomic radii enter
    later through `R_residence` and `R_gate`. This keeps the physical discourse
    of "habitability" and "permeability" explicit rather than embedding too
    much of it into the tessellation itself.
*   **Weighted-Delaunay note:** Weighted or regular triangulation is not part of the baseline DFND method. It should only be reconsidered if standard Delaunay plus explicit habitability and permeability cannot explain a concrete validated failure mode.

### 2.2. Graph Algorithms: `scipy.sparse.csgraph`
*   **Choice:** We will use `scipy.sparse.csgraph` instead of `networkx` for the core traversal.
*   **Justification:** `csgraph` operates directly on sparse matrices/arrays and is implemented in C. It is orders of magnitude faster for Connected Components and Shortest Paths on large graphs (100k+ nodes).
*   **Usage:**
    *   Construct a sparse adjacency matrix $M$ where $M_{ij} = 1$ if $R_{gate} \ge R_{probe}$.
    *   Use `csgraph.connected_components(M)` to find pockets.
    *   `networkx` may be used *only* for high-level topological analysis of the simplified "Pockets Graph" (where nodes are pockets, not tetrahedra), if needed for visualization.

---

## 3. Class Architecture (API)

The module will expose a main class that encapsulates the state.

```python
class DelaunayFlowNetwork:
    """
    The main container for the DFND analysis.
    Built once per structure; queried multiple times for different probes.
    """
    
    def __init__(self, molecular_system, selection='all', ...):
        # 1. Extract coords
        # 2. Run Delaunay
        # 3. Pre-calculate R_residence for all tets (Vectorized)
        # 4. Pre-calculate R_gate for all internal faces (Vectorized/Parallel)
        pass

    def get_pockets(self, probe_radius=1.4, min_volume=50.0):
        """
        Returns raw DFND pocket/component records or converted Pocket objects, depending on the output layer.
        This method is fast because it only filters pre-calculated arrays.
        """
        # 1. Define Node States (Boolean masks based on R_residence vs probe_radius)
        # 2. Build Adjacency Matrix (Filter edges by R_gate >= probe_radius)
        # 3. Run csgraph.connected_components on finite wet nodes
        # 4. Aggregate volumes and identifying surface atoms
        # 5. Return structured data
        pass
        
    def get_dry_network(self, probe_radius=1.4):
        """
        Returns the complementary dry graph records and candidate dry descriptors.
        """
        pass
```

Conceptually, the layering should be read as:

- `DelaunayMesh`: persistent geometric substrate;
- `DelaunayFlowNetwork`: probe-dependent flow interpretation built on that
  substrate.

Methods such as `fpocket4`, `pocketeer`, and `alphaspace2` should be able to
reuse the same `DelaunayMesh` while consuming its alpha-sphere-derived view.

## 4. Algorithmic Optimization Strategy

### 4.1. The Bottleneck: $R_{gate}$ Calculation
Calculating face-gate clearance for $N_{tet} \times 4$ faces (~200k faces) is the heavy
step.

*   **Strategy:**
    1.  **Broad Phase:** Calculate the gap between atom pairs in the face. If $Gap_{ij} < -0.5$ Å (deep overlap), $R_{gate} \approx 0$. If $Gap_{ij} > 10$ Å, it's open.
    2.  **Vectorization:** Implement `check_face_permeability` to accept `(N, 3, 3)` arrays of coordinates and radii, returning `(N,)` radii.
    3.  **Parallelism:** This step is "embarrassingly parallel". If vectorization isn't enough, we can use `joblib` or `numba.prange`.

### 4.2. Memory Management
*   Storing the full graph for 100k atoms is fine (MBs, not GBs).
*   We must avoid storing Python lists of lists for neighbors. Use ragged arrays or flattened adjacency arrays (CSR format).

## 5. Output Data Format

The `get_pockets` method should return a clean, JSON-serializable structure (similar to `castp.py`), but with added topological metadata.

```python
{
    'id': 1,
    'type': 'Pocket', # or 'Void', 'SurfaceConcavity', 'Channel'
    'volume': 150.4,
    'external_link_area': 25.2,
    'transit_tetrahedra': [10, 11, 12...], # Indices into the mesh
    'coast_tetrahedra': [101, 102...],
    'lining_atoms': [5, 6, 20...],
    'bottleneck_radius': 1.8, # Min R_gate in the component (if applicable)
}
```

This design keeps the intended layering explicit:

- `DelaunayMesh` as the geometric base;
- `DelaunayFlowNetwork` as the flow-analysis structure built on that mesh;
- feature objects (`Void`, `SurfaceConcavity`, `Pocket`, `Channel`, etc.) as the semantic
  outputs of a specific query over that persistent network, with `ExternalLink`
  and derived `Mouth` descriptors attached when requested.

This design ensures that `topomt` remains a high-performance library suitable
for high-throughput screening, not just single-structure analysis.

```
