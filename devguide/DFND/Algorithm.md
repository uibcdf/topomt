# Delaunay Flow Network Decomposition (DFND): Algorithm Description

> **Terminology.** Connected components of the graph are `components` (wet ones in
> the raw field `wet_components`; the legacy "Transit Components" wording is now
> `components`); a component's atoms are its `component`; the public object is a
> `feature`. See [`object_model.md`](object_model.md).

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

1.  **Tetrahedron Habitability ($R_{residence}$):**
    The radius of the largest sphere that can fit inside the tetrahedron
    without intersecting the van der Waals spheres of its 4 defining atoms.
    *   *Significance:* Determines if a probe of radius $R_{probe}$ can physically "reside" inside the tetrahedron.

2.  **Face Permeability ($R_{gate}$):**
    The largest local clearance available to a probe center crossing the triangular face defined by 3 atoms. It is computed from active-set clearance candidates and validated in the face component.
    *   *Significance:* Determines if a probe of radius $R_{probe}$ can "flow" from one tetrahedron to its neighbor.

---

## 2. Topological Classification (The Ontology)

DFND first separates residence, face permeability, and transit for a selected
probe radius $R_{probe}$. Exterior contact is then detected from boundary or
hull faces. `COAST` is derived from face permeability, but the movement graph is
built from transit states.

### 2.1. Dry Tetrahedra
*   **Condition:** `R_residence < R_probe`
*   **Physical Meaning:** The probe cannot reside inside the tetrahedron. It represents excluded or blocked local volume.
*   **Role:** These nodes cannot contribute resident volume. If they have two or more permeable contacts, they can still act as transit connectors; otherwise they are terminal contacts or non-transit dry nodes.

### 2.2. Wet Tetrahedra
*   **Condition:** `R_residence >= R_probe`
*   **Physical Meaning:** The probe can reside inside the tetrahedron. This is the habitable volume of pockets, channels, or clefts.
*   **Role:** Wet tetrahedra are resident-transit nodes. They contribute resident volume and participate in the transit graph through permeable contacts.

### 2.3. COAST (The Mixed Boundary)
*   **Condition:** A tetrahedron has at least one permeable face and at least one non-permeable face.
*   **Physical Meaning:** COAST marks a local boundary between passable and blocked directions. It is a tetrahedron-level contact or lining label, not a separate flow state.
*   **Wet subtype:** `wet_coast` is habitable (`R_residence >= R_probe`) and belongs to the wet-flow graph if connected through permeable faces.
*   **Dry subtype:** `dry_coast` is not habitable (`R_residence < R_probe`) but still touches at least one permeable face, so it can help identify lining atoms, contact regions, and pharmacophore-relevant boundary geometry.
*   **Role:** COAST is attached after computing the primary wet connectivity. It must not create additional connectivity by itself. Whether it contributes to reported feature volume is left to the metrics contract.

### 2.4. OCEAN / Exterior Root
*   **Condition:** `OCEAN` is the virtual exterior node of the DFND graph. It is wet by definition and does not require an `R_residence` test.
*   **Physical Meaning:** The infinite solvent region outside the convex hull.
*   **Geometry:** `OCEAN` is not a finite Delaunay tetrahedron. It has no finite geometry, no volume, no `R_residence`, and cannot be `COAST`.
*   **Role:** A finite wet tetrahedron connects to `OCEAN` only through a boundary or hull face that is permeable to the selected probe. Connected clusters of those exterior contacts are `external_links`; geometric mouths can be derived later from them.

---

## 3. Network Construction and Flow

The Delaunay Flow Network (`DFN`) is the probe-specific movement graph built on top of the Delaunay triangulation. Finite transit nodes include resident tetrahedra and non-resident transit connectors. Permeable shared faces create transit edges, and `OCEAN` is added as a virtual exterior node.

### 3.1. Edge Permeability Rule
An edge exists between two tetrahedra $T_i$ and $T_j$ sharing face $F_{ij}$ if and only if:
1.  **Geometric Permeability:** $R_{gate}(F_{ij}) \ge R_{probe}$.
2.  **Topological Validity:** Flow is tracked between transit nodes. A non-resident tetrahedron with two or more permeable contacts can be a transit connector; a non-resident tetrahedron with one permeable contact is only a terminal contact.

### 3.2. The Flow Algorithm (DFN)

1.  **Initialization:** Add the virtual **OCEAN / Root Node (-1)** as the wet exterior reference.
2.  **Transit Backbone:** Build the finite transit graph from resident-transit nodes and non-resident transit connectors connected through permeable shared faces.
3.  **Components:** After removing `OCEAN`, each finite transit component is a `Component`.
4.  **Residence Regions:** Record resident-node subsets inside each `Component`; transit connectors contribute connectivity but not resident volume.
5.  **External Links:** For each component, group connected permeable boundary or hull contacts into `external_links` to `OCEAN`.
6.  **Component Identification:**
    *   Compute `n_external_links`, `n_resident_nodes`, `has_residence`, and `has_open_interior` for each `Component`.
    *   **Void:** zero `external_links` and at least one resident node (`void`).
    *   **Degenerate subprobe:** zero `external_links` and no resident nodes (`degenerate_subprobe`; filter/provisional component).
    *   **Pocket:** exactly one `external_link` and at least one resident node (`pocket`).
    *   **Surface concavity:** exactly one `external_link` and no resident nodes (`surface_concavity`).
    *   **Multi-external-link component:** two or more `external_links` and at least one resident node (`channel`). `Channel` is a public shorthand only after path or morphology interpretation.
    *   **Nonresident passage:** two or more `external_links` and no resident nodes (`nonresident_passage`; provisional raw label).
    *   **Local labels:** `open`, `coast`, and `sealed` remain local metadata and do not create connectivity by themselves. `wet_open` is reported as `has_open_interior`, not used as the family gate.


### 3.3. The Dry Network

The dry network is the complementary probe-blocking graph. It is not a direct
public-feature classifier in v1.

1. **Dry nodes:** finite tetrahedra with `R_residence < R_probe`.
2. **Dry edges:** connections between two dry nodes through a shared finite face
   with `R_gate < R_probe`.
3. **Dry components:** connected components of the dry graph.
4. **Dry interfaces:** records where dry components contact wet components,
   external links, `OCEAN`, or hull/exterior context.
5. **Dry depth:** unweighted graph distance from dry-interface boundary nodes
   into a dry component.

Dry motifs such as protrusions, ridges, rims, walls, separators, lining regions,
and dry cores remain candidate descriptors until validated.

---

## 4. Reporting Filters and Refinement

Core graph construction should not silently prune components. Small components,
dry singletons, marginal gates, and near-zero-volume records must first appear
in raw output with flags.

Optional reporting filters may later hide or group records using criteria such
as minimum volume, minimum depth, persistence, or confidence. These filters are
not part of the primary decomposition rule.

### 4.1. Why standard Delaunay is the preferred default

In DFND, atomic radii already enter the method in the physically meaningful
places:

- in tetrahedron habitability (`R_residence`);
- and in face permeability (`R_gate`).

That means the tessellation itself can remain a neutral Delaunay partition of
atomic centers while the physical model of excluded volume and probe flow is
applied explicitly afterward.

This separation is conceptually useful:

- geometry defines the cells and adjacencies;
- physics defines what is habitable and what is permeable.

Weighted Delaunay is not part of the baseline DFND method. The standard Delaunay route is the canonical default because atomic radii already enter explicitly through habitability and permeability.

This algorithmic structure ensures that DFND identifies features that are both
explicitly traceable and topologically significant.
