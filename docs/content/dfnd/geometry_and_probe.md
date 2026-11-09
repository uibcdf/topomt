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
valid three-dimensional input. They do not tile all unbounded space. Internal
faces connect neighboring cells; hull faces have no finite neighbor. The dual
Voronoi construction helps explain the geometric family, but DFND uses its own
radius-aware capacities rather than identifying every center with a Voronoi
vertex or power center.

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
