# TopoMT: Formal Topological Feature Model (Detailed)

> **⚠️ Superseded (2026-06, kernel/catalog refactor).** This feature-type taxonomy
> predates the kernel/catalog refactor and is kept for historical context (it still
> informs the *formal intent*: minimal topological concavity/boundary/convexity +
> necks + hierarchies). The **authoritative, current sheet** is
> [`feature_catalog.md`](../../DFND/feature_catalog.md) (features by shape-type +
> generics + refined leaves + component correspondence + motifs); the naming rule is
> [`taxonomy_architecture_decision.md`](../../DFND/taxonomy_architecture_decision.md).
> Do not treat the taxonomy below as current.

## 1. Mathematical Space

Let:
- A = set of atoms (balls with centers c_i and radii r_i)
- U = union of balls
- E = set of empty tetrahedra (from regular triangulation)

Define a graph G = (E, adjacency)

---

## 2. Feature Definition

A Feature F ⊂ E satisfies:
- Connectivity: ∀ T_i, T_j ∈ F, path exists in G
- Maximality: cannot be extended without breaking definition

---

## 3. Shape Types

### 3.1 Concavity
F is concavity if:
- F ⊂ E
- boundary(F) intersects molecular surface
- F is not globally exterior

Subtypes:
- Pocket: connected to exterior by exactly one boundary component
- Channel: connected by ≥2
- Cavity: no connection

### 3.2 Boundary
B is boundary if:
- B is composed of faces between regions
- dim(B) < dim(F)

Subtypes:
- Mouth: interface between concavity and exterior
- Neck: narrow connection between regions

### 3.3 Convexity
Defined on surface patches:
- local outward curvature
- complementary to concavities

---

## 4. Boundary Operator

boundary(F) = {faces shared with non-F tetrahedra}

---

## 5. Exterior Definition

Exterior region = connected component of E touching infinity

---

## 6. Graph Relations

adjacent(F_i, F_j) if boundary intersection ≠ ∅

---

## 7. Implementation Mapping

Feature:
- cells
- boundary_faces
- neighbors

---

## 8. Key Insight

TopoMT = decomposition of empty space into connected, typed regions with explicit boundaries
