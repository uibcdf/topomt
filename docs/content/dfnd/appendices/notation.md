# Notation and terminology

Use one length unit throughout a calculation. Display in angstroms only after
conversion when the native records are in nanometers.

| Symbol | Meaning | Dimension |
| --- | --- | --- |
| $c_i,r_i$ | Selected atom center and effective radius | Length |
| $U$ | Union of original closed atomic balls | Spatial set |
| $p$ | Spherical probe radius | Length |
| $c_I(x)$ | Minimum signed clearance to the obstacle list $I$ | Length |
| $F_p,F_p^+$ | Nonpenetrating / strictly free all-atom probe-center sets | Spatial set |
| $A_p$ | Exterior-reachable subset under the same path convention | Spatial set |
| $H$ | Convex hull of selected atomic centers | Finite carrier |
| $T,f$ | Closed tetrahedral cell and triangular face | Spatial supports |
| $I_T,I_f$ | Their four-/three-atom vertex lists | Index sets |
| $R_T^*,R_f^*$ | Intended exact local clearance maxima | Length |
| $R_T,R_f$ | Reported residence/gate capacities | Length |
| $\varepsilon,\tau_r,\tau_g$ | Numerical epsilon and query tolerances | Public length parameters |
| $N_p$ | Finite transit node set | Discrete set |
| $G_p$ | Probe-specific transit graph | Graph |
| $D_p$ | Complementary bank node set | Discrete set |
| $L,W$ | Native exterior-link and wall-face counts | Counts |
| $o$ | Interior/mouth capacity ratio | Dimensionless |
| $S,P(S,p)$ | Declared boundary surface and its strictly free probe-center subset | Spatial sets |

## Terms at different levels

- A **cell** is a carrier tetrahedron, not a physical room with planar walls.
- **Residence** is existential center accommodation under its stated obstacle
  list; **permeability** is the analogous face observation.
- **Wet component** is the historical name of a finite transit component;
  connectors need not be resident. **Dry bank** uses the transit complement.
- **OCEAN** is a virtual exterior root, with no finite volume or residence test.
- An **external link** is a native cluster of admitted carrier contacts.
- A **physical boundary patch** is a connected free subset of a stated surface.
- A **component** has graph support and a spatial representation. A **motif** is
  a native substructure/descriptor. A **feature** is a public promoted finding.
- A **participant** is molecular/contextual, not a synonym for a dry bank.
- **Coast** classifies a tetrahedron's mixed face permeability. **Shore** and
  **beach** describe nonpermeable/permeable wet–bank face incidences.
- An empty-space **throat/constriction** and a solid **septum** have different
  supports, even where compatibility field names retain historical wording.

The retired term *domain* is not another rung between native components and
public features. Feature0D/1D/2D are legacy public class categories; they are
not a universal statement about the geometric dimension of every realization.

## Identity spaces

Local array index, native record ID, source molecular atom index and contextual
feature identity must be named separately. A tetrahedron's exact support is its
sorted source-atom quadruplet. A component support is a sorted collection of
those quadruplets, not just their union of atom indices.

Capacity, probe-scale and temporal persistence also retain separate contexts.
See [scale and dynamics](../scale_and_dynamics.md).
