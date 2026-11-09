# From observations to topographic names

Classification interprets a component after its support and observations exist.
The public name is useful, but it cannot supply geometric evidence that was
never calculated.

## The native signature

The basic observations are the number of native exterior links $L$, the presence
of at least one resident node, and the number of native nonpermeable boundary
wall faces $W$. Current topological naming applies this rule first:

$$\text{has residence and }W=0\quad\Longrightarrow\quad\texttt{percolating}.$$

Otherwise it uses the access/residence table:

| Native exterior links | Resident content | Topological family |
| --- | --- | --- |
| 0 | Present | `void` |
| 1 | Present | `pocket` |
| 2 or more | Present | `channel` |
| 0 | Absent | `degenerate_subprobe` diagnostic |
| 1 | Absent | `surface_concavity` diagnostic |
| 2 or more | Absent | `nonresident_passage` diagnostic |

The classifier remains total over those inputs. A diagnostic branch in code
is not proof that a physically meaningful system realizes it, or that it has
been promoted as a biological feature family.

Zero wall faces means no carrier face counted as a nonpermeable boundary wall.
It does not mean that every boundary point is collision-free. This is why the
tetrahedron's current Percolating label must retain its discrete meaning.

## Morphological refinement

For a one-link resident component, the morphology layer compares the largest
resident clearance with the widest native exterior gate:

$$o=\frac{R_{\rm interior}}{R_{\rm mouth}},\qquad
\Delta R=R_{\rm interior}-R_{\rm mouth}.$$

With a defined positive mouth radius, $o>1$ retains Pocket. At $o\le1$ the
generic refined name is OpenConcavity. Current provisional refinements test
buriedness first, then elongation:

| Condition after the open-concavity decision | Refined name |
| --- | --- |
| Topological buriedness at least 10 | Cleft |
| Otherwise, resident-center PCA elongation at least 2.5 | Groove |
| Neither | OpenConcavity |

Buriedness here counts graph steps, not angstroms. Elongation is a ratio derived
from residence-center spread. The thresholds are catalog policies, not universal
geometric or biological laws. Missing/degenerate descriptors need their declared
fallback interpretation; changing them can alter a refined name.

These current values describe `classify.py` at the reviewed source. They are
included so the result can be reconstructed, not to recommend calibration on
the three teaching cases. The bridge selects the public class from the refined
name while preserving the native family and supporting observations.

## Confidence, margins and identity

For a topological name, `confidence=1.0` means the rule is determined by the
given discrete signature. It does not certify the signature's physical accuracy.
For the one-link morphology decision, confidence scales with distance from the
occlusion threshold; marginality also examines the relevant refinement bands.
Different thresholds have different units and evidence maturity.

A source/context/support identity is independent of the catalog name. Two
results sharing a display label such as `WET-1` are not thereby the same region,
and a region receiving a new name does not automatically lose its support
correspondence. See [results and provenance](results_and_provenance.md).

Interface status is an orthogonal descriptor. An interface pocket remains a
pocket under its primary geometric classification. Biological pore, tunnel,
binding-site or functional labels need additional evidence beyond an exterior
link count or a registered Python class.

**Reading check:** what does confidence 1 establish for the tetrahedron's
Percolating label, and what does it leave unproved?
