# Alpha-Flow Network Decomposition (AFND): Overview

## 1. Introduction

Alpha-Flow Network Decomposition (AFND) represents a paradigm shift in the computational analysis of molecular topography. Traditionally, the characterization of molecular surfaces—identifying pockets, channels, and protrusions—has been approached through either purely geometric methods (like Alpha Shapes in CASTp) or heuristic scanning methods (like grid-based probes in LIGSITE or Fpocket). While successful, these methods often struggle to decouple the *existence* of a volume from its *accessibility*, leading to ambiguities in defining what constitutes a distinct functional cavity versus a mere geometric void.

AFND introduces a novel, hybrid framework that fuses **Rigorous Computational Geometry** (Delaunay/Voronoi tessellation) with **Topological Flow Logic** (Network Analysis). Instead of asking "Where is the empty space?", AFND asks "How does a probe flow through the empty space?".

By modeling the molecular volume as a **hydraulic network of discrete cells (tetrahedra)** connected by **valves (triangular faces)**, AFND provides a unified, multi-scale description of both the concave (pockets/channels) and convex (core/protrusions) features of a molecule within a single mathematical object: the **Alpha-Flow Network**.

## 2. Core Philosophy: Topological Hydraulics

The central metaphor of AFND is "Topological Hydraulics". We treat the molecular structure not as a static sculpture, but as a porous medium defined by a continuous mesh of tetrahedral cells derived from the Delaunay triangulation of atomic centers.

In this framework:
*   **The Mesh:** The Delaunay triangulation partitions the entire 3D space (both inside and outside the protein) into elementary volumetric units (tetrahedra).
*   **The Flow:** We simulate the potential movement of a spherical probe of radius $R_{probe}$ through this mesh.
*   **The Dual Network:** We construct a graph where nodes are tetrahedra and edges are the shared faces between them. Connectivity is not binary; it is determined by the physical permeability of the face ($R_{gate}$) relative to the probe size.

This approach allows AFND to naturally handle complex topological features that confuse other algorithms, such as:
*   **Bottlenecks:** Large cavities connected by narrow passages are recognized as distinct topological clusters rather than arbitrarily merged or separated.
*   **Buried Voids vs. Pockets:** Internal cavities (Voids) are naturally identified as subgraphs disconnected from the external solvent ("The Ocean").
*   **Channels:** Tunnels passing through the protein are identified as cycles in the flow network connecting two distinct surface mouths.

## 3. The Unified Dual View (Wet & Dry)

A key innovation of AFND is its ability to characterize the "Negative Space" (Solvent) and the "Positive Space" (Protein Structure) using symmetric logic.

*   **The Wet Network (Concavity):** Analyzes the flow of solvent through the empty spaces. It characterizes pockets, tunnels, and clefts.
*   **The Dry Network (Convexity):** Analyzes the "flow of structure" or structural continuity. It characterizes the protein core, domain interfaces, and protruding loops.

By inverting the condition of "habitability" (where the probe fits vs. where it doesn't), AFND seamlessly transitions from identifying a drug-binding pocket to analyzing the stability of the hydrophobic core surrounding it.

## 4. Objectives

The primary objectives of the AFND implementation in `topomt` are:

1.  **Interpretability:** To provide results that map directly to physical intuition (e.g., "This pocket is a chamber of volume V connected to the surface by a gate of radius R").
2.  **Robustness:** To mitigate common artifacts of geometric methods, such as "sliver tetrahedra" (flat, non-physical volumes), through explicit topological classification (e.g., the COAST concept).
3.  **Persistency:** To allow efficient querying of the topography at different probe radii without re-computing the underlying geometry, by storing permeability thresholds in the network edges.
4.  **Universality:** To serve as a general-purpose engine for analyzing monomers, protein-protein interfaces (PPIs), and dynamic trajectories.
