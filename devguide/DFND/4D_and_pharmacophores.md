# Delaunay Flow Network Decomposition (DFND): 4D Topography and Dynamic Pharmacophores

Historical note: the preferred method name is now `DFND`; older mentions of
`DFND` in this subdirectory should be read as the previous provisional label.

This document details the vision for extending DFND to the temporal dimension (Molecular Dynamics) and integrating it with pharmacophore modeling. This represents the high-end strategic potential of the DFND architecture.

## 1. 4D Topography: Explicit Topological Tracking

Conventional dynamic pocket analysis often relies on grid occupancy (voxel frequency), which loses topological identity, requires structural alignment, and depends on arbitrary grid spacing.

DFND enables **Explicit Topological Tracking** because the fundamental units—tetrahedra defined by atomic quadruplets—are intrinsic to the molecular graph and persistent across time.

### 1.1. Persistent vs. Instantaneous Graph
*   **Tetrahedron Identity:** A tetrahedron is uniquely defined by 4 atom indices $(A_1, A_2, A_3, A_4)$. These indices are constant throughout the trajectory (assuming covalent topology is preserved).
*   **Face Identity:** A face is uniquely defined by 3 atom indices $(A_1, A_2, A_3)$.
*   **Result:** The **Base Topology** (Potential Nodes and Edges) is invariant. What changes frame-to-frame are the **Numerical Properties** of these elements:
    *   $R_{insphere}(t)$ (Habitability over time)
    *   $R_{gate}(t)$ (Permeability over time)

This allows us to track features by their *atomic definition* rather than their spatial position.

### 1.2. The Topological Tensor (Implementation Strategy)
Since the number of tetrahedra $N_{tet}$ is constant (relative to the reference triangulation), we can load the entire dynamic topography into memory as a **Tensor**:

$$ \mathcal{T} \in \mathbb{R}^{F \times N_{tet} \times P} $$

Where:
*   $F$ is the number of frames.
*   $N_{tet}$ is the number of tetrahedra.
*   $P$ are the properties ($R_{insphere}$, $R_{gate}$ of max face, etc.).

**Computational Advantage:** Queries like "Calculate the average volume" or "Find when the gate opens" become instantaneous matrix operations (e.g., `numpy.mean(axis=0)`, `numpy.where(...)`), avoiding the need to re-loop over geometry for every frame.

*Note on Triangulation Stability:* While large deformations might theoretically flip Delaunay edges, for equilibrium fluctuations, the reference triangulation is often robust enough. If re-triangulation is strictly necessary, mapping can still be achieved via the invariant "Lining Atoms" sets.

---

## 2. Temporal Tracking and Event Detection

Using this tensor framework, we can detect discrete topological events that are invisible to static analysis.

### 2.1. Pocket Breathing (Integrity Profile)
Instead of re-clustering pockets every frame and solving the "Correspondence Problem" (Is this pocket A or B?), we simply monitor the state of the constituent tetrahedra of a reference pocket.

1.  **Definition:** Define Pocket $P_0$ in the reference frame (e.g., crystal structure). Get its list of `TRANSIT` tetrahedra.
2.  **Monitoring:** For each frame $t$, check the state of *these specific tetrahedra*.
    *   **Collapse:** How many have become `SOLID`? (Volume contraction).
    *   **Breach:** Have any boundary faces become `MOUTH`s? (Opening to solvent).
3.  **Result:** A time-series profile of "Pocket Integrity." This unambiguously tracks the *same* physical cavity, regardless of how much it moves or deforms.

### 2.2. Gating Events (Allosteric Detection)
We can monitor the time-series $R_{gate}(t)$ for all internal faces.
*   **Variance Analysis:** Identify faces with high variance in $R_{gate}$ that frequently cross the critical threshold $R_{probe}$. These are the **Molecular Gates**.
*   **Allostery:** Correlate the $R_{gate}(t)$ of a distal gate with the Volume$(t)$ of the active site. High correlation implies a topological allosteric pathway.

### 2.3. Temporal Connectivity Matrix
We can construct a matrix $\mathbf{M}$ where $M_{ij}$ represents the **probability** that tetrahedron $i$ and tetrahedron $j$ belong to the *same connected component* over the trajectory.

$$ M_{ij} = \frac{1}{F} \sum_{t=1}^{F} \mathbb{I}(\text{Path exists between } i \text{ and } j \text{ at time } t) $$

*   $M_{ij} \approx 1.0$: **Stable Core.** These regions are always connected.
*   $M_{ij} \approx 0.5$: **Transient/Flexible Region.** Connected only during specific conformational states ("Breathing").
*   $M_{ij} \approx 0.0$: **Steric Barrier.** Permanent separation.

**Benefit:** This generates a "Topological Stability Heatmap" without needing any structural alignment. It reveals the dynamic segmentation of the protein interior.

---

## 3. Semantic 4D Analysis

By injecting chemical information (Residue ID, Polarity) into the topological graph, the analysis becomes semantic.

### 3.1. Mechanism of Closure
We can explain *why* a pocket closes:
*   *Example:* "The pocket volume drops not because the whole cavity collapses, but because the **Entry Tetrahedron** (defined by hydrophilic residues Arg/Asp) becomes `SOLID`, while the **Hydrophobic Interior** remains `TRANSIT`."
*   This distinguishes "Occlusion" (gate closure) from "Collapse" (volume loss).

### 3.2. Water Tracking Validation
We can cross-reference the theoretical `TRANSIT` volume with explicit water occupancy from the MD simulation.
*   *Discrepancy:* If a region is theoretically `TRANSIT` (geometric void) but has low water density, it indicates an **Entropic or Hydrophobic Exclusion** effect that geometry alone misses. This highlights "Dry Pockets" potentially favorable for high-affinity lipophilic ligands.

---

## 4. Dynamic Pharmacophores (Dyn-Pharmacophores)

DFND offers a unique platform for this because, unlike grid methods (which yield diffuse interaction clouds), DFND provides **discrete, semantic anchor points** via the `TRANSIT` and `COAST` nodes.

### 4.1. The Idea: Nodes as Pharmacophoric Anchors
Each node (tetrahedron) is defined by 4 atoms. We can assign a pharmacophoric label to the node based on the chemical nature of those atoms.

*   **Interaction Points (`COAST`):** If a `COAST` node touches a specific atom type:
    *   Touches Lys (Nζ) $\to$ **H-Bond Donor / Positive Charge**.
    *   Touches Backbone Carbonyl $\to$ **H-Bond Acceptor**.
*   **Volume Constraints (`TRANSIT`):**
    *   Surrounded by Leu/Val $\to$ **Hydrophobic Volume**.

### 4.2. Consensus Dynamic Pharmacophore
By aggregating the topological tensor with these labels over the trajectory ($F \times N_{tet}$):

1.  **Persistence Filter:** Identify nodes that remain Topologically Stable (`TRANSIT` or `COAST`) for $> X\%$ of the simulation time.
2.  **Feature Stability:** Among persistent nodes, select those that **Chemically Stable** (consistently present the same pharmacophoric feature, e.g., "Always Hydrophobic").
    *   *Noise Filtering:* A point that appears and disappears in 1 ns is irrelevant noise. One that persists 80% of the time is a **Pharmacophoric Hotspot**.
3.  **3D Model Generation:**
    *   Cluster centroids of stable `TRANSIT` nodes define the **Ligand Volume**.
    *   Stable `COAST` nodes define the **Interaction Points** (vectors/arrows).
    *   **Result:** A 3D pharmacophore model (spheres and vectors) directly exportable to VS tools like **RDKit**, **Pharmer**, or **LigandScout**.

### 4.3. The "Internal Frame" Advantage
This is a massive technical advantage of DFND over grid methods.
*   **Grid Methods:** Require perfect structural alignment. If the protein domain moves or rotates, the grid blurs.
*   **DFND:** Uses **Internal Definition**. The node is defined relative to atoms $A_1..A_4$. If the domain moves, the tetrahedron moves with it. The pharmacophore point travels with the protein.
*   **Implication:** **No Alignment Required.** The resulting model inherently captures the **conformational selection** of the pocket, fitting the ensemble of accessible shapes rather than a single static snapshot.
