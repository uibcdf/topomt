# Alpha-Flow Network Decomposition (AFND): Future Ideas

Once the core geometric engine is stable, AFND offers a fertile ground for advanced extensions. Here are the strategic directions for future development.

## 1. Physicochemical Graph Overlay (Chemo-Topology)

Currently, the graph nodes carry geometric data ($Volume, R_{insphere}$). We should augment them with chemical data.

*   **Node Coloring:** Assign properties to `TRANSIT` and `COAST` nodes based on the atoms defining them.
    *   **Hydrophobicity Score:** Average Kyte-Doolittle index of the 4 defining atoms.
    *   **Electrostatic Potential:** Poisson-Boltzmann potential at the circumcenter.
    *   **Evolutionary Conservation:** Map conservation scores (e.g., ConSurf) to the graph.
*   **Application:**
    *   "Find me a pocket that is *accessible* ($R > 1.4$) AND *hydrophobic*."
    *   "Identify the 'charged path' for an ion channel."

## 2. Dynamic Trajectory Analysis (4D Topography)

AFND is fast enough to run on MD frames.

*   **The "Breathing" Graph:**
    *   Track a specific pocket ID across time.
    *   Plot $Volume(t)$ and $Max\_Bottleneck(t)$.
*   **Gating Analysis:**
    *   Identify the specific face (triplet of atoms) that acts as the "Gatekeeper" (highest variance in permeability).
    *   Correlate gate opening with backbone dihedral angles (allostery).
*   **Water Residence Time:**
    *   Correlate `TRANSIT` volumes with explicit water occupancy from simulations.

## 3. Advanced Graph Theory Applications

Treating the protein as a formal network opens the door to network science metrics.

*   **Centrality Analysis:**
    *   **Betweenness Centrality:** Identify tetrahedra that act as crucial hubs for internal flow (structural weak points).
*   **Community Detection:**
    *   Use modularity maximization to automatically segment a large, continuous internal void into "chambers" without manual thresholds.
*   **Graph Kernels:**
    *   Fingerprint the graph topology to compare binding sites across protein families (e.g., "Is this kinase pocket topologically similar to that ATPase pocket?").

## 4. Multi-Probe Analysis (Ligand Size Profiling)

Since edge permeability is stored as a continuous value ($R_{gate}$), we can efficiently compute **Access Profiles**.

*   **The "Sieve" Plot:**
    *   Compute Total Accessible Volume vs. Probe Radius.
    *   The derivative of this curve reveals the discrete sizes of constrictions in the system.
    *   *Analogy:* Like Mercury Intrusion Porosimetry, but virtual.

## 5. Geometric Hashing for Docking

*   **Concept:** Use the `TRANSIT` node centers as a sparse cloud of "ideal ligand atom positions."
*   **Application:** Generate a pharmacophore model directly from the graph centers (e.g., "Ideally, place a hydrophobic carbon at node X and a hydrogen bond donor at node Y").

## 6. Visualization Enhancements

*   **Flow Lines:** Visualize the "streamlines" of the BFS traversal to show the path from the surface to the active site.
*   **Abstract Graph View:** A 2D "Subway Map" representation of the pockets (Nodes = Chambers, Edges = Tunnels), simplifying the complex 3D geometry for easier human comprehension.
