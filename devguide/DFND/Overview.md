# Delaunay Flow Network Decomposition (DFND): Overview

## 1. Introduction

Delaunay Flow Network Decomposition (DFND) represents a paradigm shift in the
computational analysis of molecular topography. Traditionally, the
characterization of molecular surfaces identifying pockets, channels, and
protrusions has been approached through either purely geometric methods (like
Alpha Shapes in CASTp) or heuristic scanning methods (like grid-based probes
in LIGSITE or Fpocket). While successful, these methods often struggle to
decouple the *existence* of a volume from its *accessibility*, leading to
ambiguities in defining what constitutes a distinct functional cavity versus a
mere geometric void.

DFND introduces a hybrid framework that fuses **rigorous computational
geometry** (Delaunay/Voronoi tessellation) with **topological flow logic**
(network analysis). Instead of asking "Where is the empty space?", DFND asks
"How does a probe flow through the empty space?".

By modeling the molecular volume as a **hydraulic network of discrete cells
(tetrahedra)** connected by **valves (triangular faces)**, DFND provides a
unified, multi-scale description of both the concave (pockets/channels) and
convex (core/protrusions) features of a molecule within a single mathematical
object: the **Delaunay Flow Network**.

## 2. Core Philosophy: Topological Hydraulics

The central metaphor of DFND is "Topological Hydraulics". We treat the
molecular structure not as a static sculpture, but as a porous medium defined
by a continuous mesh of tetrahedral cells derived from the Delaunay
triangulation of atomic centers.

In this framework:
*   **The Mesh:** The Delaunay triangulation partitions the entire 3D space (both inside and outside the protein) into elementary volumetric units (tetrahedra).
*   **The Flow:** We simulate the potential movement of a spherical probe of radius $R_{probe}$ through this mesh.
*   **The Dual Network:** We construct a graph where nodes are tetrahedra and edges are the shared faces between them. Connectivity is not binary; it is determined by the physical permeability of the face ($R_{gate}$) relative to the probe size.

This approach allows DFND to naturally handle complex topological features that
confuse other algorithms, such as:
*   **Bottlenecks:** Large cavities connected by narrow passages are recognized as distinct topological clusters rather than arbitrarily merged or separated.
*   **Buried Voids vs. Pockets:** Internal cavities (Voids) are naturally identified as subgraphs disconnected from the external solvent ("The Ocean").
*   **Channels:** Tunnels passing through the protein are identified as cycles in the flow network connecting two distinct surface mouths.

## 3. The Unified Dual View (Wet & Dry)

A key innovation of DFND is its ability to characterize the "Negative Space"
(Solvent) and the "Positive Space" (Protein Structure) using symmetric logic.

*   **The Wet Network (Concavity):** Analyzes the flow of solvent through the empty spaces. It characterizes pockets, tunnels, and clefts.
*   **The Dry Network (Convexity):** Analyzes the "flow of structure" or structural continuity. It characterizes the protein core, domain interfaces, and protruding loops.

By inverting the condition of "habitability" (where the probe fits vs. where
it doesn't), DFND seamlessly transitions from identifying a drug-binding
pocket to analyzing the stability of the hydrophobic core surrounding it.

## 3.1. Primary representation versus derived view

DFND should be understood primarily as a **tetrahedron-centered** method, not
as an alpha-sphere-centered one.

- the primary representation is a Delaunay mesh of tetrahedra and shared faces;
- physical meaning enters through tetrahedron habitability and face
  permeability;
- alpha-spheres remain useful as a derived or visualization-friendly view, but
  they are not the core structural ontology of the method.

## 3.2. Tetrahedron-network view versus alpha-sphere-network view

The same local empty space can often be described either as a graph of
tetrahedra or as a graph of alpha-spheres derived from those tetrahedra.

| Aspect | Tetrahedron network | Alpha-sphere network |
|---|---|---|
| Node meaning | Volumetric cell of the Delaunay tessellation | Derived local empty-space sphere |
| Edge meaning | Shared triangular face / geometric gate | Adjacency inherited from neighboring tetrahedra |
| Natural quantities | Volume, boundary faces, gates, mouths, connectivity | Centers, radii, sphere clustering, visual intuitiveness |
| Best suited for | Flow logic, permeability, wet/dry decomposition, exact topology | Sphere-centric heuristics, visualization, some clustering workflows |
| Role in DFND | Primary representation | Useful derived view |

Practical reading:

- many methods can be described in either representation;
- connectivity can be close to isomorphic in simple cases;
- but DFND is physically and conceptually cleaner when formulated on the
  tetrahedral network and only later exposing alpha-sphere-derived views when
  useful.

## 4. Objectives

The primary objectives of the DFND implementation in `topomt` are:

1.  **Interpretability:** To provide results that map directly to physical intuition (e.g., "This pocket is a chamber of volume V connected to the surface by a gate of radius R").
2.  **Robustness:** To mitigate common artifacts of geometric methods, such as "sliver tetrahedra" (flat, non-physical volumes), through explicit topological classification (e.g., the COAST concept).
3.  **Persistency:** To allow efficient querying of the topography at different probe radii without re-computing the underlying geometry, by storing permeability thresholds in the network edges.
4.  **Universality:** To serve as a general-purpose engine for analyzing
    monomers, protein-protein interfaces (PPIs), and dynamic trajectories.
