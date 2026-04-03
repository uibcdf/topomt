# Delaunay Flow Network Decomposition (DFND): Possible Points of Failure

Historical note: the preferred method name is now `DFND`; older mentions of
`DFND` in this subdirectory should be read as the previous provisional label.

An honest engineering approach requires anticipating failure modes. Here we analyze the potential weaknesses of DFND and propose mitigation strategies.

## 1. Geometric & Numerical Risks

### 1.1. The "Sliver" Problem (Degenerate Geometry)
*   **Risk:** Delaunay triangulation often produces "slivers" (nearly flat tetrahedra formed by 4 almost coplanar atoms). These have a near-zero volume but can have a huge circumradius ($R_{\alpha} \to \infty$).
*   **Failure Mode:** A naive algorithm might classify a sliver as `OCEAN` or `TRANSIT` (huge radius), creating a false "wormhole" tunnel through the protein surface where no physical space exists.
*   **Mitigation (Implemented):**
    *   The **`COAST`** classification logic.
    *   Strict check of **$R_{insphere}$** (inscribed sphere) vs. $R_{probe}$. A sliver has a tiny $R_{insphere}$ even if $R_{\alpha}$ is huge. By requiring `TRANSIT` nodes to have $R_{insphere} \ge R_{probe}$, we physically filter out slivers from the flow path.

### 1.2. The "Apollonius" Numerical Instability
*   **Risk:** Calculating $R_{gate}$ (the gap between 3 circles) involves solving a quadratic equation (Apollonius Problem). In degenerate cases (tangent atoms, collinear centers), floating-point errors can occur.
*   **Failure Mode:** False positives (gate opens when it should be closed) or crashes.
*   **Mitigation:**
    *   **Pre-filtering:** Check pairwise gaps ($d_{ij} - r_i - r_j$) first. If any pair is too close, the triplet cannot be permeable.
    *   **Robust Math:** Use a stable implementation of the Apollonius solver, handling edge cases (e.g., negative roots) gracefully.
    *   **Tolerance:** Apply a small $\epsilon$ tolerance (e.g., $10^{-5}$ Å) for tangency checks.

## 2. Topological & Algorithmic Risks

### 2.1. The "Infinite Roughness" (Noise Explosion)
*   **Risk:** Molecular surfaces are fractal. Every tiny cleft between two side-chains is topologically a "pocket."
*   **Failure Mode:** The algorithm detects 5,000 pockets, 4,990 of which are just 1-tetrahedron noise on the surface.
*   **Mitigation:**
    *   **Volume Pruning:** Discard pockets with Volume < $V_{min}$ (e.g., 50 Å³).
    *   **Depth Pruning:** Discard pockets that are "shallow" (geodesic depth from Root < $D_{min}$).
    *   **Sea Level Tuning:** Allow the user to adjust the `OCEAN` definition radius.

### 2.2. The "Mega-Cluster" (Percolation Threshold)
*   **Risk:** At a certain probe radius, the internal void network might percolate.
*   **Failure Mode:** All internal voids merge into one giant "Swiss Cheese" component, losing the distinction between specific sites.
*   **Mitigation:**
    *   This is physically real (if the protein is porous).
    *   **Graph Partitioning:** If a giant component is detected, apply "bottleneck cutting" (e.g., community detection algorithms or max-flow min-cut) to sub-segment the mega-cluster into logical domains based on the narrowest constrictions.

## 3. Computational Performance

### 3.1. Combinatorial Explosion
*   **Risk:** A large protein complex (e.g., viral capsid) has hundreds of thousands of atoms. Delaunay triangulation is $O(N \log N)$, which is fine, but the graph analysis could be slow if not optimized.
*   **Failure Mode:** Python loops over 200,000 tetrahedra taking minutes instead of seconds.
*   **Mitigation:**
    *   **Vectorization:** Use NumPy for all geometric checks (batch processing of tetrahedra metrics).
    *   **JIT Compilation:** Use `numba` for the critical inner loops (like the `check_permeability` math).
    *   **Dual Graph:** The number of tetrahedra is roughly $6 \times N_{atoms}$. For 10k atoms, ~60k nodes. Standard BFS/DFS is extremely fast on this scale ($< 0.1s$). The bottleneck will be the geometry, not the graph traversal.

## 4. Biological Validity

### 4.1. Static vs. Dynamic
*   **Risk:** DFND (like CASTp) analyzes a static PDB snapshot. Proteins breathe. A "closed" gate ($R_{gate} = 1.3 Å$) might open to 1.5 Å frequently.
*   **Failure Mode:** False negatives (missing a cryptic pocket).
*   **Mitigation:**
    *   **Soft Gates:** Instead of binary Open/Closed, report the $R_{gate}$ value.
    *   **Ensemble Analysis:** Design the tool to easily run on MD trajectories and aggregate statistics ("Gate open 40% of time").

### 4.2. Chemical Blindness
*   **Risk:** The current definition is purely steric (geometry). A pocket might be geometrically open but electrostatically repulsive to the ligand.
*   **Failure Mode:** Predicting a binding site that is physically accessible but chemically impossible.
*   **Mitigation:**
    *   **Property Overlay:** Map physicochemical properties (charge, hydrophobicity) onto the graph nodes (see `Future_Ideas.md`).
    *   **Hybrid Score:** Rank pockets by $Volume \times Hydrophobicity$ rather than Volume alone.
