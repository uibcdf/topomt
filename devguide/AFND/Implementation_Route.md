# Alpha-Flow Network Decomposition (AFND): Implementation Route

This document outlines the step-by-step roadmap to build the AFND module in `topomt`.

## Phase 1: The Physics Engine (The Valve)

**Goal:** Implement the math to decide if a probe passes through a triangle of atoms.

*   [ ] **Task 1.1:** Create `sandbox/geometry_playground.py`.
*   [ ] **Task 1.2:** Implement `check_face_permeability(A, B, C, rA, rB, rC, r_probe)`.
    *   Sub-task: Implement the 2D Apollonius solver (find radius of tangent circle).
    *   Sub-task: Implement robust pre-checks (pairwise gaps).
*   [ ] **Task 1.3:** Verify against edge cases (tangent atoms, disjoint atoms, sliver triangles).
*   [ ] **Task 1.4:** Optimize/Vectorize. Ensure it can handle arrays of coordinates for batch processing.

## Phase 2: The Graph Architect (The Mesh)

**Goal:** Build the dual graph from atomic coordinates.

*   [ ] **Task 2.1:** Create `topomt/methods/afnd/graph_builder.py`.
*   [ ] **Task 2.2:** Implement Delaunay triangulation wrapper (`scipy.spatial`).
*   [ ] **Task 2.3:** Calculate Tetrahedron Metrics ($R_{insphere}$, $R_{\alpha}$).
    *   Classify nodes: `SOLID`, `TRANSIT`, `COAST`, `OCEAN` (based on initial thresholds).
*   [ ] **Task 2.4:** Calculate Face Permeability ($R_{gate}$).
    *   Build the Adjacency List (Dual Graph). Only add edges where $R_{gate} \ge R_{probe_{min}}$.

## Phase 3: The Flow Engine (The Logic)

**Goal:** Traverse the graph to identify features.

*   [ ] **Task 3.1:** Create `topomt/methods/afnd/traversal.py`.
*   [ ] **Task 3.2:** Implement `identify_components(graph, root_nodes)`.
    *   BFS/DFS implementation.
    *   Separate Pockets (connected to Root) from Voids (isolated).
*   [ ] **Task 3.3:** Implement `pruning_filter(components)`.
    *   Remove small noise components.
*   [ ] **Task 3.4:** Implement `DryNetwork` traversal (inverse logic for protrusions).

## Phase 4: Integration & API

**Goal:** Expose AFND as a user-friendly tool in `topomt`.

*   [ ] **Task 4.1:** Create `topomt/methods/afnd/__init__.py`.
*   [ ] **Task 4.2:** Define the main function `afnd(molecular_system, probe_radius, ...)`.
*   [ ] **Task 4.3:** Output formatting. Return structured dictionaries (like `castp.py` does) but with richer graph data.
*   [ ] **Task 4.4:** Visualization helper (`view_afnd_network`) to draw the tetrahedra/edges in NGLView/Py3Dmol.

## Phase 5: Validation & Testing

**Goal:** Ensure scientific correctness.

*   [ ] **Task 5.1:** Unit Tests (`tests/test_afnd_math.py`) for geometry.
*   [ ] **Task 5.2:** Integration Test (`tests/test_afnd_pockets.py`) on a standard protein (e.g., T4 Lysozyme or HIV Protease).
*   [ ] **Task 5.3:** Comparison Benchmark. Compare results with `fpocket` and `castp` on the same PDB. Do we find the same active site?
*   [ ] **Task 5.4:** Write tutorial notebook in `sandbox/AFND_tutorial.ipynb`.

## Milestones

*   **M1 (Prototype):** Phase 1 complete. Can calculate permeability of a single face.
*   **M2 (Alpha):** Phase 2 & 3 complete. Can find a pocket in a simple PDB.
*   **M3 (Beta):** Phase 4 & 5 complete. Usable tool with documentation and visualizer.
