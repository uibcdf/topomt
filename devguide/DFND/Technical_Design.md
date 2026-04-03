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

### 1.2. The Persistent Graph Attributes
We pre-calculate and store the limiting radii. This allows the "Master Graph" functionality (querying different probes instantly).

*   **`node_habitability`**: `ndarray (N_tet,) float32`
    *   Stores $R_{insphere}$ for each tetrahedron.
    *   *Usage:* To check if node $i$ is `TRANSIT` or `SOLID` for a given probe, we just check `node_habitability[i] >= R_probe`.

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
    later through `R_insphere` and `R_gate`. This keeps the physical discourse
    of "habitability" and "permeability" explicit rather than embedding too
    much of it into the tessellation itself.
*   **Weighted-Delaunay note:** Regular/weighted triangulation remains a valid
    future audit path, but in DFND it should be treated as an optional
    alternative tessellation, not as the default conceptual model.

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
        # 3. Pre-calculate R_insphere for all tets (Vectorized)
        # 4. Pre-calculate R_gate for all internal faces (Vectorized/Parallel)
        pass

    def get_pockets(self, probe_radius=1.4, min_volume=50.0, sea_level=10.0):
        """
        Returns a list of Pocket dictionaries.
        This method is fast because it only filters pre-calculated arrays.
        """
        # 1. Define Node States (Boolean masks based on R_insphere vs probe_radius)
        # 2. Build Adjacency Matrix (Filter edges by R_gate >= probe_radius)
        # 3. Run csgraph.connected_components on TRANSIT nodes
        # 4. Aggregate volumes and identifying surface atoms
        # 5. Return structured data
        pass
        
    def get_dry_network(self, probe_radius=1.4):
        """
        Returns the complementary Solid/Protrusion network.
        """
        pass
```

## 4. Algorithmic Optimization Strategy

### 4.1. The Bottleneck: $R_{gate}$ Calculation
Calculating Apollonius for $N_{tet} \times 4$ faces (~200k faces) is the heavy
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
    'type': 'Pocket', # or 'Void', 'Channel'
    'volume': 150.4,
    'mouth_area': 25.2,
    'transit_tetrahedra': [10, 11, 12...], # Indices into the mesh
    'coast_tetrahedra': [101, 102...],
    'lining_atoms': [5, 6, 20...],
    'bottleneck_radius': 1.8, # Min R_gate in the component (if applicable)
}
```

This design keeps the intended layering explicit:

- `DelaunayMesh` as the geometric base;
- `DelaunayFlowNetwork` as the flow-analysis structure built on that mesh;
- feature objects (`Pocket`, `Void`, `Channel`, `Mouth`, etc.) as the semantic
  outputs of a specific query over that persistent network.

This design ensures that `topomt` remains a high-performance library suitable
for high-throughput screening, not just single-structure analysis.

```
