# Delaunay Flow Network Decomposition (DFND): Algorithm Description

## 1. Geometric Foundations

The DFND algorithm is built upon the Delaunay triangulation of the atomic
centers of the molecular system. This tessellation provides a mathematically
rigorous partition of the 3D space into a set of non-overlapping tetrahedra.

Let $S$ be the set of atomic centers $\{a_1, a_2, ..., a_N\}$ with associated van der Waals radii $\{r_1, r_2, ..., r_N\}$.
Let $DT(S)$ be the Delaunay triangulation of $S$.

Each tetrahedron $T \in DT(S)$ is defined by 4 atoms.
Each face $F$ of a tetrahedron is defined by 3 atoms.

### 1.1. Key Geometric Metrics

To construct the flow network, we compute two critical metrics for every element in the mesh:

1.  **Tetrahedron Habitability ($R_{insphere}$):**
    The radius of the largest sphere that can fit inside the tetrahedron
    without intersecting the van der Waals spheres of its 4 defining atoms.
    *   *Significance:* Determines if a probe of radius $R_{probe}$ can physically "reside" inside the tetrahedron.

2.  **Face Permeability ($R_{gate}$):**
    The radius of the largest circle that can pass through the triangular face defined by 3 atoms, tangent to their van der Waals radii. This is the solution to a constrained Apollonius problem on the face plane.
    *   *Significance:* Determines if a probe of radius $R_{probe}$ can "flow" from one tetrahedron to its neighbor.

---

## 2. Topological Classification (The Ontology)

We classify every tetrahedron in the mesh into one of four distinct topological states relative to a given probe radius $R_{probe}$ and a reference "Sea Level" radius $R_{sea\_level}$ (typically a large value, e.g., 10-12 Å, representing the bulk solvent curvature).

### 2.1. SOLID (The Structure)
*   **Condition:** $R_{insphere} < R_{probe}$
*   **Physical Meaning:** The space is too cramped for the probe. It represents the atoms and their immediate excluded volume.
*   **Role:** These nodes act as **Walls** in the Wet Network and as **Nodes** in the Dry Network.

### 2.2. TRANSIT (The Volume)
*   **Condition:** $R_{probe} \le R_{insphere} < R_{sea\_level}$
*   **Physical Meaning:** The probe fits comfortably inside. This is the "habitable volume" of pockets, channels, or clefts.
*   **Role:** These are the **Hubs** of the Wet Network. Flow can enter and exit these nodes, forming paths.

### 2.3. COAST (The Interface/Beach)
*   **Condition:** Technically $R_{insphere} \ge R_{probe}$ (geometrically valid), but topological or heuristic criteria mark it as a "dead end" or "shallow water".
    *   *Scenario A (Slivers):* Flat tetrahedra with large $R_{\alpha}$ but negligible physical volume or height.
    *   *Scenario B (Periphery):* Tetrahedra that connect to `SOLID` walls but do not lead to other `TRANSIT` nodes via permeable faces.
*   **Physical Meaning:** The "shoreline" of the pocket. Accessible but not traversable. The probe can "poke its nose" in but cannot fully lodge or pass through.
*   **Role:** These nodes contribute to the **Volume** and **Surface Area** of a pocket but are **pruned** from the graph traversal to prevent false connectivity.

### 2.4. OCEAN (The Infinite Bulk)
*   **Condition:** $R_{insphere} \ge R_{sea\_level}$
*   **Physical Meaning:** The bulk solvent far from the protein surface.
*   **Role:** All `OCEAN` tetrahedra are collapsed into a single virtual **Root Node (-1)** or "Infinity". Any connection between `TRANSIT`/`COAST` and `OCEAN` constitutes a **Mouth**.

---

## 3. Network Construction and Flow

The Delaunay Flow Network is a dual graph $G = (V, E)$ where nodes $V$ are
tetrahedra and edges $E$ are shared faces.

### 3.1. Edge Permeability Rule
An edge exists between two tetrahedra $T_i$ and $T_j$ sharing face $F_{ij}$ if and only if:
1.  **Geometric Permeability:** $R_{gate}(F_{ij}) \ge R_{probe}$.
2.  **Topological Validity:** Both $T_i$ and $T_j$ are "compatible" for flow (e.g., typically flow is tracked between `TRANSIT` nodes, or from `OCEAN` to `TRANSIT`).

### 3.2. The Flow Algorithm (Wet Network)

1.  **Initialization:** Identify the **Root Node** (the collection of all `OCEAN` tetrahedra).
2.  **Breadth-First Search (BFS):** Start a traversal from the Root Node into the mesh.
    *   Flow can pass through faces where $R_{gate} \ge R_{probe}$.
    *   Flow enters `TRANSIT` nodes.
    *   Flow *stops* at `SOLID` nodes (walls).
    *   Flow *accumulates* at `COAST` nodes (dead ends) but does not continue through them.
3.  **Component Identification:**
    *   **Pockets:** Connected components of `TRANSIT` + `COAST` nodes that are reachable from the Root but are geometrically distinct (e.g., separated by a bottleneck).
    *   **Voids:** Connected components of `TRANSIT` + `COAST` nodes that are **NOT** reachable from the Root (no permeable path to infinity).
    *   **Channels:** Paths within a component that connect two distinct Mouths (cycles involving the Root).

### 3.3. The Structure Algorithm (Dry Network)

Symmetrically, we can analyze the `SOLID` nodes:
1.  **Core Definition:** The largest connected component of `SOLID` tetrahedra.
2.  **Protrusions:** Branches of the `SOLID` network that extend deeply into `OCEAN` territory.
3.  **Dry/Wet Interface:** `SOLID` tetrahedra that share a face with `TRANSIT` or `OCEAN` nodes are defined as the **Surface Shell**.

---

## 4. Pruning and Refinement

To ensure robustness against surface roughness (atomic noise):
1.  **Volume Pruning:** Small, isolated branches of `TRANSIT` nodes with volume $< V_{min}$ are merged into the bulk or discarded as surface roughness.
2.  **Depth Pruning:** `TRANSIT` chains that do not penetrate deeper than a threshold $D_{min}$ from the "Sea Level" (Alpha Shape boundary) are considered surface rugosity, not pockets.

### 4.1. Why standard Delaunay is the preferred default

In DFND, atomic radii already enter the method in the physically meaningful
places:

- in tetrahedron habitability (`R_insphere`);
- and in face permeability (`R_gate`).

That means the tessellation itself can remain a neutral Delaunay partition of
atomic centers while the physical model of excluded volume and probe flow is
applied explicitly afterward.

This separation is conceptually useful:

- geometry defines the cells and adjacencies;
- physics defines what is habitable and what is permeable.

Weighted Delaunay remains a valid future audit direction, but the standard
Delaunay route is the cleaner default for the DFND physical narrative.

This algorithmic structure ensures that DFND identifies features that are both
**geometrically exact** and **topologically significant**.
