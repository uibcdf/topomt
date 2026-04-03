# Delaunay Flow Network Decomposition (DFND): Interpretation and Use Cases

Historical note: the preferred method name is now `DFND`; older mentions of
`DFND` in this subdirectory should be read as the previous provisional label.

The power of DFND lies not just in finding "holes," but in providing a rich, semantically meaningful decomposition of molecular topography. This document outlines how to interpret the results of DFND in various biological and pharmacological contexts.

## 1. Drug Discovery and Binding Site Analysis

### 1.1. Pocket Characterization
DFND decomposes a binding site into a structured graph of sub-pockets.
*   **Transit Volumes:** Represent the "habitable zones" where a ligand can reside comfortably. Large `TRANSIT` clusters indicate potential binding hotspots.
*   **Bottlenecks (Gates):** The edges between sub-pockets define the accessibility. A narrow $R_{gate}$ implies that a ligand might need conformational flexibility to pass.
    *   *Interpretation:* "The binding site consists of a main chamber A and a sub-pocket B, connected by a 2.1 Å constriction. Ligands targeting B must be able to squeeze through this gate."
*   **Coastline (Surface Contact):** The `COAST` tetrahedra define the intimate contact surface.
    *   *Interpretation:* "While the ligand resides in the `TRANSIT` volume, its binding affinity is driven by interactions with the atoms lining the `COAST` tetrahedra."

### 1.2. Cryptic Pockets
DFND is uniquely suited to detect cryptic pockets (sites that open only upon dynamic fluctuation).
*   **Analysis Strategy:** By analyzing the Dry Network (SOLID) surrounding a pocket, one can identify "weak walls" (thin layers of `SOLID` tetrahedra separating a `VOID` from the surface).
*   *Interpretation:* "A `VOID` of 150 Å³ exists just 1.5 Å behind the active site wall. A side-chain rotation could merge this void with the main pocket, creating a cryptic binding sub-site."

### 1.3. Channels and Tunnels
For enzymes with buried active sites (e.g., Cytochrome P450), the path to the surface is critical.
*   **Interpretation:** DFND identifies channels as cycles in the flow graph (Root $\to$ Mouth A $\to$ Active Site $\to$ Mouth B $\to$ Root).
*   **Metrics:** The "Bottleneck Radius" of the channel is simply the minimum $R_{gate}$ along the path. The "Channel Profile" is the sequence of $R_{insphere}$ and $R_{gate}$ values from mouth to depth.

---

## 2. Protein-Protein Interfaces (PPI)

DFND naturally handles multi-chain systems by carrying atom metadata (Chain ID) into the tetrahedra.

### 2.1. Interface Topography
*   **Mixed Tetrahedra:** Tetrahedra whose vertices belong to different chains define the **Contact Layer**.
*   **Inter-chain Pockets:** `TRANSIT` volumes formed between two chains.
    *   *Interpretation:* "Chain A and Chain B form a transient pocket at the interface. This is a potential site for small-molecule PPI stabilizers."

### 2.2. Shape Complementarity (Lock and Key)
The duality of Wet/Dry networks allows for a direct measurement of shape complementarity.
*   **Method:** Analyze the `SOLID` protrusions of Chain A and the `WET` pockets of Chain B at the interface.
*   **Interpretation:** "The 'Protrusion-X' of Chain A perfectly occupies the 'Pocket-Y' of Chain B, leaving minimal `TRANSIT` volume (high complementarity). Conversely, 'Loop-Z' leaves a large water-filled gap, suggesting a lower affinity region or a water-mediated interaction."

---

## 3. Structural Stability and Folding

### 3.1. Hydrophobic Core Analysis
The Dry Network provides a topological definition of the protein core.
*   **Deep Core:** `SOLID` nodes with a high geodesic distance from any `WET` node.
*   **Defects:** Small `VOIDS` or `TRANSIT` bubbles deep inside the `SOLID` core represent packing defects.
    *   *Interpretation:* "The core contains multiple small voids totaling 50 Å³, suggesting potential destabilization or sites for cavity-filling mutations to increase stability."

### 3.2. Surface Rugosity
*   **Fractal Dimension:** The ratio of `COAST` nodes to `TRANSIT` nodes gives a measure of surface complexity.
    *   *Interpretation:* "A high Coast/Transit ratio indicates a highly rugose, disordered surface, typical of Intrinsically Disordered Regions (IDRs) or flexible loops, whereas a low ratio indicates a smooth, globular domain."

---

## 4. Summary of Topo-Biological Descriptors

| Descriptor | DFND Component | Biological Relevance |
| :--- | :--- | :--- |
| **Pocket Volume** | $\sum Vol(TRANSIT) + \sum Vol(COAST)$ | Binding capacity (Stoichiometry/Size). |
| **Mouth Area** | Area of Faces connecting to `OCEAN` | Access kinetics ($k_{on}$). |
| **Bottleneck** | Min($R_{gate}$) along a path | Steric selectivity filter. |
| **Burial Depth** | Geodesic distance from Root | Accessibility/Solvent protection. |
| **Packing Defect** | Volume of `VOIDS` | Thermodynamic stability ($\Delta G_{folding}$). |
| **Interface Gap** | `TRANSIT` volume at PPI interface | Interface quality/affinity. |
