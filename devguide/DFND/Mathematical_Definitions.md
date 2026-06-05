# Delaunay Flow Network Decomposition (DFND): Mathematical Definitions

This document provides the formal mathematical specifications for the geometric primitives used in DFND. It serves as the definitive reference for implementation, ensuring that concepts like "permeability" and "habitability" are calculated consistently.

## 1. Preliminaries

Let the molecular system be represented by a set of $N$ atoms, where the $i$-th atom $A_i$ is defined by its center coordinates $\mathbf{c}_i \in \mathbb{R}^3$ and its van der Waals radius $r_i \in \mathbb{R}^+$.

DFND constructs the standard Delaunay triangulation of atomic centers. Atomic radii are not used as tessellation weights in the baseline method; they enter explicitly through tetrahedron habitability and face permeability.
Let $T$ be a tetrahedron defined by four atoms {$A_1, A_2, A_3, A_4$}.
Let $F$ be a triangular face defined by three atoms {$A_1, A_2, A_3$}.

The probe is a sphere of radius $R_{probe}$.

---

## 2. Face Permeability (`R_gate`)

**Objective:** determine the maximum probe radius whose center can cross a
Delaunay face under the adopted local face model.

`R_gate` is a clearance primitive, not a raw tangency root. The implementation
builds candidate centers from active constraints and then validates each
candidate against the closed triangular face before selecting the largest actual
clearance.

### 2.1. Face Plane Model

For a face `F = (A1, A2, A3)`, DFND works in the plane of the three atom centers.
The three atoms are represented by disks with the assigned atomic radii. Under
this v1 local model:

```text
R_gate(F) = max clearance(x)
            over probe-center positions x in the closed triangular face
```

where:

```text
clearance(x) = min_i(||x - c_i|| - r_i), for i in the three face atoms
```

A face is permeable to a probe of radius `R_probe` when:

```text
R_gate(F) >= R_probe
```

### 2.2. Active-Set Candidates

The candidate set includes:

- `face3`: three-atom tangent candidates generated from the 2D tangency
  construction;
- `pair2`: two-atom-limited candidates on face edges or boundary strata;
- explicit validation that the candidate center lies in the face component;
- actual-clearance recomputation against the three face atoms.

The tangency construction is therefore an internal candidate generator. It is
not the public DFND gate contract by itself.

### 2.3. Scope and Diagnostics

`R_gate` is a local face-gate radius. It does not prove global continuous-space
reachability, and it does not automatically include atoms outside the three face
atoms. Contextual intrusion flags and path-level analysis must be reported
separately when needed.

---

## 3. Tetrahedron Residence (`R_residence`)

**Objective:** determine the maximum probe radius whose center can reside in the
closed Delaunay tetrahedron under the adopted local cell model.

`R_residence` is the residence clearance primitive. It should not be equated
with a single four-atom tangent sphere unless that candidate is admissible and
optimal.

### 3.1. Formal Definition

For a tetrahedron `T = (A1, A2, A3, A4)`:

```text
R_residence(T) = max clearance(x)
                 over probe-center positions x in the closed tetrahedron
```

where:

```text
clearance(x) = min_i(||x - c_i|| - r_i), for i in the four tetrahedron atoms
```

A tetrahedron is resident for a probe of radius `R_probe` when:

```text
R_residence(T) >= R_probe
```

### 3.2. Active-Set Candidates

The candidate set includes:

- `interior4`: four-atom tangent candidates generated from the 3D tangency
  construction;
- `face3`: three-atom tangent candidates constrained to tetrahedron faces;
- `edge2`: two-atom tangent candidates constrained to tetrahedron edges;
- explicit validation that the candidate center lies in the tetrahedron;
- actual-clearance recomputation against the four tetrahedron atoms.

The four-atom tangency value is retained as `R_apollonius4` for diagnostics,
but the DFND residence primitive is `R_residence`.

### 3.3. Difference from Orthogonal Radius (`R_alpha`)

Standard alpha-shape machinery uses an orthogonal or power-distance radius. DFND
uses standard Delaunay as the neutral substrate and applies atomic radii through
`R_residence` and `R_gate` afterward.

`R_residence` can be compared with `R_alpha` diagnostically, but it is not an
alpha-shape radius and should not be described as equivalent to one.

## 3.4. Room-Window Asymmetry

`R_residence` and `R_gate` do not have a universal ordering. Compact
tetrahedra can have resident capacity larger than any face gate, while
sliver-like tetrahedra can have small resident capacity but large permeable
faces.

This motivates the separation:

```text
residence = controlled by R_residence
transit   = controlled by permeable contacts from R_gate
contact   = one-sided access without through-transit
```

A resident sealed tetrahedron is physically interpretable: the probe can reside
inside the local cell but cannot exit through any face at the selected probe
radius. A non-resident open tetrahedron is also physically interpretable: the
probe cannot reside there, but it may pass through if at least two contacts are
permeable.

---

## 4. Geometric Classifications

### 4.1. Local Permeability Class
DFND separates volumetric habitability from face permeability. A tetrahedron is
classified as wet or dry from its habitability radius, while each face is
classified as permeable or non-permeable from its gate radius.

```text
tetrahedron_wet(T) = R_residence(T) >= R_probe
tetrahedron_dry(T) = R_residence(T) < R_probe

face_permeable(F) = R_gate(F) >= R_probe
face_non_permeable(F) = R_gate(F) < R_probe
```

The local permeability class of a finite tetrahedron is:

```text
open(T) = all finite faces of T are permeable

coast(T) = at least one finite face of T is permeable
           and at least one finite face of T is non-permeable

sealed(T) = all finite faces of T are non-permeable
```

`non-coast` is only a derived complement, not a primary label:

```text
non_coast(T) = open(T) or sealed(T)
```

Combining habitability and local permeability gives:

```text
wet_open(T) = tetrahedron_wet(T) and open(T)
wet_coast(T) = tetrahedron_wet(T) and coast(T)
wet_sealed(T) = tetrahedron_wet(T) and sealed(T)

dry_open(T) = tetrahedron_dry(T) and open(T)
dry_coast(T) = tetrahedron_dry(T) and coast(T)
dry_sealed(T) = tetrahedron_dry(T) and sealed(T)
```

These labels do not create flow connectivity by themselves. Primary movement
connectivity is the transit graph: resident tetrahedra plus non-resident
transit connectors connected through permeable faces. Local class labels are
retained as boundary, lining, pharmacophore, and diagnostic metadata. Whether
any local class contributes to a reported feature volume is a metric-policy
decision, not part of the topological classification itself.

### 4.2. Sea Level and Exterior
The baseline DFND exterior is probe-dependent. A wet component contacts the
exterior when it has one or more permeable boundary or hull faces connected to
the outside root.

`OCEAN` is the virtual exterior node of the DFND graph. Geometrically, it
represents the unbounded region outside the convex hull. It is wet by
definition because the probe is assumed to fit freely in the exterior. It is
not a finite Delaunay tetrahedron, has no `R_residence`, has no volume, and
cannot be `COAST`.

The default sea-level scale is therefore tied to `R_probe`, with 1.4 Å as the
water-probe default.

Larger sea-level values may be introduced later as an optional macro-surface
mode, but they are not part of the first canonical DFND contract.

---

## 5. DFN and Concavity Components

### 5.1. Delaunay Flow Network
Let `DFN` be the probe-specific graph built over the Delaunay triangulation.
Finite transit tetrahedra are graph nodes. Resident tetrahedra are transit nodes. Non-resident tetrahedra with at least two permeable contacts are transit connectors. Two finite transit tetrahedra are connected when they share a permeable face.

Let `OCEAN` be the virtual wet exterior root. It is connected to a finite transit tetrahedron only through a permeable boundary or hull face.

### 5.2. External Links
An `external_link` of a concavity component is a connected cluster of
permeable boundary or hull contacts between that component and `OCEAN`.

A single wide exterior opening may contain many boundary faces, but it should
count as one `external_link` if those faces form one connected cluster.

`mouth` is a geometric descriptor that may be derived from an `external_link`;
it is not the primitive used to define primary DFN feature families.

### 5.3. Primary Component Families
Remove `OCEAN` and its incident edges from the transit graph. Each connected component of the remaining finite transit graph is a `Component` `D`, interpreted topographically with its residence regions and external links.

Define:

```text
L(D) = n_external_links(D)
has_residence(D) = n_resident_nodes(D) >= 1
has_open_interior(D) = exists t in D such that t is wet_open
```

Primary family classification uses access and residence:

```text
void(D) = L(D) == 0 and has_residence(D)
degenerate_subprobe(D) = L(D) == 0 and not has_residence(D)

surface_concavity(D) = L(D) == 1 and not has_residence(D)
pocket(D) = L(D) == 1 and has_residence(D)

nonresident_passage(D) = L(D) >= 2 and not has_residence(D)
channel(D) = L(D) >= 2 and has_residence(D)
```

`has_open_interior(D)` is a descriptor, not the classifier. The resident multi-mouth family is named `channel` (mapping to the public `Channel` feature), but biological channel, tunnel, or pore labels should be assigned only after additional path, depth, geometry, or morphology analysis.

`surface_concavity` remains provisional until explicit toy systems or
geometric sweeps demonstrate the realizability and utility of accessible
wet components without wet-open tetrahedra under the current `R_residence` and
`R_gate` definitions.

### 5.4. Component Volume
The topological volume of a concavity component `D` is the sum of the Euclidean
volumes of its constituent finite Delaunay tetrahedra.

$$ Vol_{topological}(D) = \sum_{T \in D} Vol(T) $$

This quantity includes portions of tetrahedra occupied by the atomic balls,
because Delaunay tetrahedra extend to atom centers. It is useful for graph
debugging and coarse internal comparisons, but it is not a physical solvent
volume and should not be compared directly with CASTp-like pocket volumes.

A physical or publication-facing volume must be represented separately, for
example as `volume_solvent` or `volume_solvent_estimate`, and should subtract or
otherwise correct atom-occupied portions according to an explicit metric policy.
