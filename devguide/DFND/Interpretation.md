# Delaunay Flow Network Decomposition (DFND): Interpretation and Use Cases

The power of DFND lies not just in finding "holes," but in providing a rich, semantically meaningful decomposition of molecular topography. This document outlines how to interpret the results of DFND in various biological and pharmacological contexts.

## 1. Drug Discovery and Binding Site Analysis

### 1.1. Pocket Characterization
DFND decomposes a binding site into a structured graph of sub-pockets.
*   **Wet volumes:** Represent the "habitable zones" where a ligand can reside comfortably. Large `wet` clusters indicate potential binding hotspots.
*   **Bottlenecks (Gates):** The edges between sub-pockets define the accessibility. A narrow $R_{gate}$ implies that a ligand might need conformational flexibility to pass.
    *   *Interpretation:* "The binding site consists of a main chamber A and a sub-pocket B, connected by a 2.1 Å constriction. Ligands targeting B must be able to squeeze through this gate."
*   **Coastline (Surface Contact):** `COAST` tetrahedra identify mixed-boundary cells where at least one face is permeable and at least one face is blocked.
    *   *Interpretation:* "While the ligand resides in the wet volume, affinity can be driven by atoms lining nearby `wet_coast` or `dry_coast` tetrahedra."

### 1.2. Cryptic Pockets
DFND is uniquely suited to detect cryptic pockets (sites that open only upon dynamic fluctuation).
*   **Analysis Strategy:** By analyzing the Dry Network (dry) surrounding a pocket, one can identify "weak walls" (thin layers of `dry` tetrahedra separating a `VOID` from the surface).
*   *Interpretation:* "A `VOID` of 150 Å³ exists just 1.5 Å behind the active site wall. A side-chain rotation could merge this void with the main pocket, creating a cryptic binding sub-site."

### 1.3. Channels and Tunnels
For enzymes with buried active sites (e.g., Cytochrome P450), the path to the surface is critical.
*   **Interpretation:** DFND identifies multi-opening transit components as finite transit components with two or more external links to `OCEAN`; channel, tunnel, or pore labels require later path and morphology analysis.
*   **Metrics:** The "Bottleneck Radius" of the channel is simply the minimum $R_{gate}$ along the path. The "Channel Profile" is the sequence of $R_{residence}$ and $R_{gate}$ values along paths between external-link regions.

---

## 2. Protein-Protein Interfaces (PPI)

DFND naturally handles multi-chain systems by carrying atom metadata (Chain ID) into the tetrahedra.

### 2.1. Interface Topography
*   **Mixed Tetrahedra:** Tetrahedra whose vertices belong to different chains define the **Contact Layer**.
*   **Inter-chain Pockets:** resident volumes formed between two chains.
    *   *Interpretation:* "Chain A and Chain B form a transient pocket at the interface. This is a potential site for small-molecule PPI stabilizers."

### 2.2. Shape Complementarity (Lock and Key)
The duality of Wet/Dry networks allows for a direct measurement of shape complementarity.
*   **Method:** Analyze the `dry` protrusions of Chain A and the `wet` pockets of Chain B at the interface.
*   **Interpretation:** "The 'Protrusion-X' of Chain A perfectly occupies the 'Pocket-Y' of Chain B, leaving minimal resident volume (high complementarity). Conversely, 'Loop-Z' leaves a large water-filled gap, suggesting a lower affinity region or a water-mediated interaction."

---

## 3. Structural Stability and Folding

### 3.1. Hydrophobic Core Analysis
The Dry Network provides a topological definition of the protein core.
*   **Deep Core:** `dry` nodes with a high geodesic distance from any `wet` node.
*   **Defects:** Small `VOIDS` or `wet` bubbles deep inside the `dry` core represent packing defects.
    *   *Interpretation:* "The core contains multiple small voids totaling 50 Å³, suggesting potential destabilization or sites for cavity-filling mutations to increase stability."

### 3.2. Surface Rugosity and Boundary Complexity
*   **Boundary Complexity:** The ratio of `COAST` labels to wet nodes gives a measure of partially blocked boundary complexity.
    *   *Interpretation:* "A high coast/wet ratio indicates a highly rugose, disordered surface, typical of Intrinsically Disordered Regions (IDRs) or flexible loops, whereas a low ratio indicates a smooth, globular domain."

---

## 4. Summary of Topo-Biological Descriptors

| Descriptor | DFND Component | Biological Relevance |
| :--- | :--- | :--- |
| **Pocket Volume** | `volume_solvent` or `volume_solvent_estimate`; `volume_topological` is raw/debug only | Binding capacity (Stoichiometry/Size). |
| **External-Link Area** | Area of boundary faces in an `external_link`; derived mouth area can be reported from it | Access kinetics ($k_{on}$). |
| **Bottleneck** | Min($R_{gate}$) along a path | Steric selectivity filter. |
| **Burial Depth** | Graph distance from external-link boundary nodes | Accessibility/Solvent protection. |
| **Packing Defect** | Volume of `VOIDS` | Thermodynamic stability ($\Delta G_{folding}$). |
| **Interface Gap** | resident volume at PPI interface | Interface quality/affinity. |
