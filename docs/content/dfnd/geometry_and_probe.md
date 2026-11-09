# Geometry, probe placement and accessibility

The scientific input is a set of atom centers and effective radii, not just a
PDB identifier. Radius assignment, selection and the analyzed frame are part
of the modeled object.

## Atomic balls and clearance

Write the selected atoms as $(c_i,r_i)$ with $c_i\in\mathbb R^3$ and $r_i>0$.
Their closed-ball union is

$$U=\bigcup_i \overline B(c_i,r_i).$$

For an obstacle index set $I$, define the signed clearance field

$$c_I(x)=\min_{i\in I}(\|x-c_i\|-r_i).$$

Positive clearance measures the radius available to a probe centered at $x$.
Negative clearance places that center inside at least one atomic ball. Use
$c_{\rm all}$ when every selected atom participates in exclusion.

For probe radius $p\ge0$, distinguish

$$F_p=\{x:c_{\rm all}(x)\ge p\},\qquad
F_p^+=\{x:c_{\rm all}(x)>p\}.$$

$F_p$ permits tangency; $F_p^+$ requires strictly positive clearance beyond the
probe radius. The latter is the complement of the union of **closed** expanded
balls of radii $r_i+p$. The nonpenetrating set includes their exposed boundary.
At a tangent neck, this distinction can change connectivity.

```{figure} figures/probe_geometry.svg
:alt: Atomic disks, probe-expanded disks and a probe at an admissible center in a two-dimensional explanatory section.

An explanatory section: the probe center must avoid the expanded obstacles.
Its occupied ball and the center's allowed positions are different sets.
```

## Fitting is different from reaching

Define $A_p\subseteq F_p$ as positions connected to the unbounded exterior by a
continuous center path lying in $F_p$. With strict clearance, define the analogous
subset of $F_p^+$. Use one convention throughout a statement or certificate.

A probe can be placed mathematically in a sealed cavity even when it cannot
enter from outside. Such a position belongs to the admissible set but not the
exterior-reachable subset. Conversely, several accessible surface indentations
can communicate through the same unbounded exterior region.

Consequently, a finite pocket segmentation needs an additional support or
boundary convention. The connected components of all accessible space are not
automatically a list of binding pockets. DFND's finite carrier and OCEAN treatment
provide its discrete construction; they do not compute exact $F_p$ or $A_p$ first.

## Four sets that must keep their names

| Set | What it represents |
| --- | --- |
| Bare empty space | Positions outside the original atomic balls. |
| Admissible center space | Positions where the selected spherical probe can be placed without penetration. |
| Exterior-reachable center space | Admissible centers connected to the exterior under the same path convention. |
| Swept probe volume | The union of occupied probe balls over a declared set of centers. |

A tetrahedral carrier union is another set. Its volume includes portions inside
atomic balls unless exclusion is applied. Surface-area accessibility also has
a separate definition; probe-based molecular surface conventions have a long
history {cite:p}`DFNDLeeRichards1971`.

## Delaunay as the carrier

Ordinary Delaunay tetrahedra partition the atomic-center convex hull $H$ for a
valid three-dimensional input. A tetrahedron has four atom centers as vertices;
its four triangular faces each use three of them. Sharing a face makes two cells
neighbors. Hull faces have no finite neighbor. These finite cells do not tile
all unbounded space.

The defining **empty-circumsphere condition** says that no other input center
lies strictly inside a cell's circumsphere. "Empty" here concerns atom centers,
not atomic balls or probe clearance. Five cospherical centers can make the
triangulation nonunique. See the [CGAL definition](https://doc.cgal.org/latest/Triangulation_3/index.html).

The ordinary Voronoi cell of atom center $c_i$ is

$$V_i=\{x:\|x-c_i\|\le\|x-c_j\|\text{ for every }j\}.$$

It groups positions by nearest **center**. In a nondegenerate configuration,
four meeting Voronoi cells identify a Delaunay tetrahedron; their meeting point
is its circumcenter. Neighboring tetrahedra correspond to a Voronoi edge.
[SciPy's spatial tutorial](https://docs.scipy.org/doc/scipy/tutorial/spatial.html#voronoi-diagrams)
introduces both constructions. A circumcenter can lie outside its tetrahedron;
it is not automatically an admissible residence center on the closed support.

## Atomic radii do not make every construction equivalent

DFND uses the ordinary triangulation as its carrier, then evaluates additive
radius-aware clearance. Compare the fields:

| Field | Per-atom expression | Role |
| --- | --- | --- |
| Ordinary nearest-center distance | $\|x-c_i\|$ | Defines ordinary Voronoi/Delaunay geometry. |
| Additive clearance | $\|x-c_i\|-r_i$ | Minimum gives DFND's spherical-probe clearance. |
| Power distance with weight $r_i^2$ | $\|x-c_i\|^2-r_i^2$ | Defines power diagrams and regular triangulations. |

The [CGAL regular-triangulation definition](https://doc.cgal.org/latest/Triangulation_3/index.html)
specifies the weighted construction. For unequal radii these fields need not
choose the same limiting atom or the same candidate center. For example, atom
distances 3 and 4 Å with radii 1 and 2.5 Å give clearances 2 and 1.5 Å, but powers
8 and 9.75 Å²: the smaller value belongs to a different atom in the two fields.
Tangency for a probe of radius $R$ requires distances $r_i+R$, as derived in the
[clearance appendix](appendices/clearance_derivations.md). It cannot be replaced
by equal power to the original balls.

Thus an ordinary empty circumsphere is not a maximal physical probe sphere.
DFND computes its own constrained capacities rather than treating every Voronoi
vertex or power center as the answer.

Alpha shapes provide a related geometric framework {cite:p}`DFNDAlphaShapes1994`.
Current DFND does not construct a weighted alpha complex or inherit its pocket
theorems. Its [historical context](references.md#development-context) explains
the difference from the early alpha/discrete-flow proposal.

## Choosing the modeled system

The molecular route delegates input representation, selection and radius lookup
to MolSysMT. Current defaults exclude hydrogens and use `vdw` radii. `protor`
and supplied-radius workflows have different typing/input requirements. A
heavy-atom model with one radius convention is not interchangeable with a
different convention or a model containing explicit hydrogens.

Resolve alternate locations upstream. Include or exclude waters, ions, ligands
and cofactors intentionally: each can change the ball union. DFND analyzes one
selected frame in nonperiodic Cartesian geometry. A retained simulation box
does not make the calculation periodic or apply minimum-image distances.

Choose $p$ for the steric question. The conventional 1.4 Å default is a scale
choice, not a model of every ligand shape, flexibility or hydration state.
Changing atomic sampling, radii or selected atoms changes the physical model;
it is not automatically a numerical resolution test.

**Reading check:** which of these sets would you measure when asking for a
cavity's empty volume, and which when asking whether a probe can enter it?

```{dropdown} Check your reasoning
For empty volume, integrate bare empty space over a declared finite region.
For entry, ask whether admissible center positions connect to the exterior under
the chosen strictness. A nonzero empty volume answers neither the probe-size
test nor the path question. The [measurement chapter](measurements.md) keeps
these integrals separate.
```
