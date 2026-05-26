# Delaunay Flow Network Decomposition (DFND): Pertinence and Integration Analysis within TopoMT

This document analyzes the strategic fit of the DFND module within the existing architecture and philosophy of the TopoMT library. It validates that DFND is not merely an add-on, but a core engine that aligns with and empowers the library's hierarchical design.

## 1. Philosophical Alignment

**TopoMT Goal:** "Hierarchical analysis of molecular surface topography."
**DFND Contribution:** DFND provides the mathematical mechanism to generate this hierarchy. By decomposing the space into a flow network, it naturally distinguishes and relates topological features (Pockets, Channels, Voids) based on physical connectivity rules, fulfilling the "hierarchical" promise of the library's name.

**Verdict:** DFND is the native algorithmic realization of TopoMT's core philosophy.

## 2. Architectural Integration

### 2.1. The "Engine" Pattern
The relationship between DFND and the existing codebase should follow a **Generator/Product** pattern.

*   **The Generator (DFND):** The `DelaunayFlowNetwork` class acts as the computational engine. It ingests atomic coordinates and builds the persistent, parameter-independent dual graph (Delaunay + Permeability Map).
*   **The Configuration:** The user supplies specific query parameters such as $R_{probe}$ and optional exterior or sea-level policy settings.
*   **The Product (`Topography`):** The result of querying the DFND engine is a populated `Topography` object containing instances of `Void`, `SurfaceConcavity`, `Pocket`, `Channel`, and derived exterior-link descriptors.

**Implication:**
DFND does not replace `topomt.topography.Topography`; it populates it. The `Topography` class becomes the container for the specific "instance" of the topography at a given resolution, derived from the underlying DFND model.

### 2.2. Mapping to Existing Feature Classes
TopoMT already defines a rich ontology in `topomt/features/`. DFND provides a direct, 1-to-1 mapping for these classes:

| DFND Concept | TopoMT Class | Mapping Logic |
| :--- | :--- | :--- |
| **Void** | `topomt.features.Void` | Transit component with zero `external_links` and at least one resident node. |
| **Surface Concavity** | New feature class or pocket-family subtype | Transit component with exactly one `external_link` and no resident nodes. |
| **Pocket** | `topomt.features.Pocket` | Transit component with exactly one `external_link` and at least one resident node. |
| **Channel** | `topomt.features.Channel` | Resident `multi_external_link`; channel remains shorthand until morphology/path analysis. |
| **External Link** | New descriptor class or `Mouth` precursor | DFN-level exterior connection. A geometric `Mouth` can be derived from it. |
| **Solid Component** | *New Feature Class* | (Proposed) `topomt.features.Protrusion` or `Core`. |

**Verdict:** High architectural compatibility. DFND will act as a factory that instantiates these existing classes, giving them rigorous geometric definitions.

## 3. Data Flow and Dependencies

### 3.1. Input: MolSysMT
DFND will strictly adhere to the `MolSysMT` ecosystem for input handling.
*   **Input:** `molsysmt.MolSys` object.
*   **Extraction:** Use `msm.get(..., coordinates=True)` to extract raw data.
*   **Benefit:** Inherits support for all molecular file formats and selection syntax supported by MolSysMT.

### 3.2. Internal Processing: NumPy/SciPy
*   **Philosophy:** "Units at boundaries, raw floats inside."
*   **Input Boundary:** `pyunitwizard` strips units (converting to Angstroms).
*   **Core:** NumPy arrays and SciPy sparse matrices process raw floats for maximum performance.
*   **Output Boundary:** `pyunitwizard` re-attaches units to volumetric/area results before returning them to the user or populating the `Topography` object.

### 3.3. Output: The `Topography` Object
The workflow for a user will be:

```python
# 1. Initialize the Master Graph (Expensive step, done once)
afn = DelaunayFlowNetwork(molecular_system)

# 2. Generate a Topography for water probe (Cheap step)
topo_water = afn.get_topography(probe_radius=1.4) 
# Returns a topomt.topography.Topography object populated with Pockets/Channels

# 3. Generate a Topography for a larger ligand (Cheap step)
topo_ligand = afn.get_topography(probe_radius=3.0)
```

## 4. Conclusion

The DFND module is highly pertinent. It resolves the current fragmentation of methods (wrappers vs. simple scripts) by providing a **unified, native Python engine**. It respects the existing class structure and elevates the `Topography` class from a passive container to the dynamic result of a rigorous topological query.
