# Delaunay Flow Network Decomposition (DFND): Mathematical Definitions

Historical note: the preferred method name is now `DFND`; older mentions of
`DFND` in this subdirectory should be read as the previous provisional label.

This document provides the formal mathematical specifications for the geometric primitives used in DFND. It serves as the definitive reference for implementation, ensuring that concepts like "permeability" and "habitability" are calculated consistently.

## 1. Preliminaries

Let the molecular system be represented by a set of $N$ atoms, where the $i$-th atom $A_i$ is defined by its center coordinates $\mathbf{c}_i \in \mathbb{R}^3$ and its van der Waals radius $r_i \in \mathbb{R}^+$.

We construct the weighted Delaunay triangulation (or regular triangulation) of these atoms.
Let $T$ be a tetrahedron defined by four atoms {$A_1, A_2, A_3, A_4$}.
Let $F$ be a triangular face defined by three atoms {$A_1, A_2, A_3$}.

The probe is a sphere of radius $R_{probe}$.

---

## 2. Face Permeability ($R_{gate}$)

**Objective:** Determine the radius of the largest probe that can pass through the face $F$.

This is equivalent to finding the radius $R_{gate}$ of the largest circle that can be placed in the plane of the face such that it is tangent to (or disjoint from) the three circular cross-sections of the atoms, without overlapping them.

### 2.1. Projection to 2D
First, we define the plane $\mathcal{P}$ passing through the centers $\mathbf{c}_1, \mathbf{c}_2, \mathbf{c}_3$.
Since the probe passes *through* the face, the critical constriction is in this plane. However, the atoms are spheres, so their intersection with the plane are circles.
*   The center of the atom circle $i$ in the plane is simply $\mathbf{c}_i$ (since the plane passes through the centers).
*   The radius of the atom circle $i$ in the plane is the full van der Waals radius $r_i$.

Thus, the problem reduces to the **Problem of Apollonius** in 2D: Find a circle of radius $R$ and center $\mathbf{p}$ that is externally tangent to three given circles $C_1(\mathbf{c}_1, r_1)$, $C_2(\mathbf{c}_2, r_2)$, $C_3(\mathbf{c}_3, r_3)$.

### 2.2. The Apollonius Equation
Let the solution circle have center $(x, y)$ and radius $R$. The condition of external tangency to circle $i$ is:
$$ (x - x_i)^2 + (y - y_i)^2 = (r_i + R)^2 $$

For 3 circles, we have a system of 3 quadratic equations.
Subtracting equations pairwise (e.g., Eq 1 - Eq 2) eliminates the quadratic terms $x^2, y^2, R^2$, resulting in linear equations describing the "radical axes".

However, we specifically seek the **Smallest Enclosing Circle of the Void** (which corresponds to one of the 8 Apollonius solutions: the one that touches all 3 circles externally, often called the inner Soddy circle if the atoms were touching).

**Constraint:** The probe must pass *between* the atoms.
Therefore, the valid solution must have $R > 0$ and the center $\mathbf{p}$ must lie within the triangle (or reasonably close to the gap, not enclosing the atoms).

### 2.3. Pre-Checks (The Gaps)
Before solving the quadratic system, we define the pairwise gaps:
$$ g_{ij} = ||\mathbf{c}_i - \mathbf{c}_j|| - (r_i + r_j) $$
*   If any $g_{ij} < 0$, the atoms overlap. The "gate" might still exist if the overlap is small, but if the atoms block the path, $R_{gate} = 0$.
*   **Upper Bound:** $R_{gate} \le \min(g_{12}, g_{23}, g_{13})$. Actually, this is loose. A tighter bound is related to the incircle of the triangle formed by the centers.

---

## 3. Tetrahedron Habitability ($R_{insphere}$)

**Objective:** Determine the radius of the largest probe that can fit inside the tetrahedron $T$.

This is the 3D generalization of the face permeability problem. It is the **Problem of Apollonius in 3D** (finding a sphere tangent to 4 spheres).

### 3.1. Formal Definition
We seek a sphere with center $\mathbf{p} \in \mathbb{R}^3$ and radius $R$ such that:
$$ ||\mathbf{p} - \mathbf{c}_i|| = r_i + R \quad \forall i \in \{1, 2, 3, 4\} $$

This represents a sphere "kissing" the 4 atomic spheres from the outside (empty space).

### 3.2. Solution Strategy
This system can be linearized. By squaring the distances:
$$ ||\mathbf{p}||^2 - 2\mathbf{p}\cdot\mathbf{c}_i + ||\mathbf{c}_i||^2 = r_i^2 + 2r_iR + R^2 $$
Subtracting equation $j$ from equation $i$:
$$ 2\mathbf{p}\cdot(\mathbf{c}_j - \mathbf{c}_i) + 2R(r_i - r_j) = ||\mathbf{c}_j||^2 - ||\mathbf{c}_i||^2 - r_j^2 + r_i^2 $$
This gives 3 linear equations relating $\mathbf{p}$ and $R$.
We can express $\mathbf{p}$ as a linear function of $R$: $\mathbf{p}(R) = \mathbf{A} + \mathbf{B}R$.
Substituting back into the first sphere equation yields a quadratic equation for $R$:
$$ aR^2 + bR + c = 0 $$
We solve for $R$.
*   The **Habitability Radius** $R_{insphere}$ is the largest positive real root of this equation.
*   If no positive real root exists, the void is virtual or blocked.

### 3.3. Difference from Orthogonal Radius ($R_{\alpha}$)
Standard Alpha Shapes use the **Orthogonal Center**, which is the point equidistant to the surface of the atoms in terms of *power distance* ($d^2 - r^2$).
$$ ||\mathbf{p}_{\alpha} - \mathbf{c}_i||^2 - r_i^2 = R_{\alpha}^2 $$
This is a linear system (simpler to solve).
*   **Relationship:** $R_{insphere}$ is the "true" physical limit. $R_{\alpha}$ is the "topological" limit used by Delaunay.
*   **Approximation:** For atoms of similar size ($r_i \approx r_j$), $R_{insphere} \approx R_{\alpha}$.
*   **DFND Policy:** We prefer $R_{insphere}$ for physical correctness (Habitability), but we may use $R_{\alpha}$ for topological indexing since it is native to the Delaunay dual.

---

## 4. Geometric Classifications

### 4.1. Coast Condition (The Sliver)
A tetrahedron is classified as `COAST` (Sliver) if it is topologically open but physically flat.
Metric: **Aspect Ratio ($\rho$)**
$$ \rho = \frac{R_{insphere}}{R_{circum}} $$
Or more specifically for our purpose:
$$ \rho_{flatness} = \frac{R_{insphere}}{\max(L_{edges})} $$
If $R_{\alpha} > R_{probe}$ (Topologically Open) **BUT** $R_{insphere} < R_{probe}$ (Physically Closed), it is a **COAST** node.

### 4.2. Sea Level
Let $\mathcal{K}_{\infty}$ be the Alpha Complex for $\alpha = \infty$ (The Convex Hull).
Let $\mathcal{K}_{sea}$ be the Alpha Complex for $\alpha = R_{sea\_level}$.
A tetrahedron $T$ belongs to `OCEAN` if $T 
otin \mathcal{K}_{sea}$.
Ideally, $R_{sea\_level} \approx 10$ Å.

---

## 5. Flow Logic

### 5.1. Adjacency Matrix
Let $\mathbf{A}$ be the adjacency matrix of the dual graph.
$$ A_{ij} = 1 \iff (T_i \cap T_j \neq \emptyset) \land (R_{gate}(T_i \cap T_j) \ge R_{probe}) $$

### 5.2. Component Volume
The volume of a pocket $P$ is the sum of the volumes of its constituent tetrahedra.
$$ Vol(P) = \sum_{T \in P} Vol(T) $$
*   *Note:* This is the volume of the Delaunay tetrahedra (Topological Volume).
*   *Correction:* To get the "True Solvent Accessible Volume", one would subtract the volume of the atomic caps inside each tetrahedron.
    $$ Vol_{net}(P) = Vol(P) - \sum_{i \in Atoms(P)} Vol(Sphere_i \cap P) $$
    DFND focuses on $Vol(P)$ for speed and topological robustness, unless "high precision" mode is requested.
