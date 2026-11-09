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
geometric or biological laws.

## Reconstruct the morphology record

`component.morphometrics` supplies the observations used above and additional
descriptors. Native lengths in this dictionary are in nm.

| Field | Current construction | Unavailable/edge case |
| --- | --- | --- |
| `interior_radius` | Largest `R_residence` among resident nodes. | With no resident nodes, the diagnostic fallback uses the full component node list; an empty eligible list gives 0. |
| `mouth_radius` | Largest `R_gate_max` among the component's native exterior links. | `None` without links. It is a local gate summary, not a measured free-aperture radius. |
| `occlusion`, `occlusion_gap` | Interior/mouth ratio and interior minus mouth, respectively. | Both `None` without a positive mouth radius. |
| `enclosable` | Whether the defined `occlusion_gap` is positive. | `None` when the gap is unavailable; a sealed Void does not receive an infinite ratio. |
| `per_mouth_occlusion` | Interior radius divided by each positive link gate maximum, in link order. | Zero/undefined link radii are omitted, so this list need not have one entry per link. |
| `buriedness` | Maximum stored topological depth over the component's transit nodes. | 0 when no depths exist; sealed components also use the flat zero-depth convention. |
| `elongation`, `elongation_axis` | PCA of the eligible residence-center point cloud, with equal weight per node. | Both `None` for fewer than three points or insufficient second-axis spread. |
| `funnel` | Narrowing with topological depth, described in [internal structure](hierarchy_and_paths.md#access-profiles-and-the-funnel-descriptor). | `None` with fewer than four sampled depth levels. |
| `deepest_chamber` | The deepest provisional chamber candidate and its peak/separation summary. | `None` without chamber candidates. |

For center points $x_j$, let $\bar x$ be their arithmetic mean and
$C=M^{-1}\sum_j(x_j-\bar x)(x_j-\bar x)^T$. If its eigenvalues are
$\lambda_1\le\lambda_2\le\lambda_3$, the implemented elongation is

$$e=\sqrt{\lambda_3}/\sqrt{\lambda_2}.$$

The axis is an eigenvector for $\lambda_3$, with arbitrary sign. The software
returns no elongation when $\sqrt{\lambda_2}\le10^{-9}$ in normalized nm, including
a collinear cloud. A single cell therefore has **no estimated elongation**,
rather than elongation zero or one. This point-cloud descriptor is neither a
volume-weighted inertia ratio nor the aspect ratio of a reconstructed surface.

When `occlusion` is `None`, the classifier keeps the topological family; it does
not force the region into OpenConcavity. Missing elongation skips the Groove
test, while the depth test can still select Cleft when applicable.

Names such as `enclosable` summarize the **current support and contacts**. They
do not certify the future lifetime of one unchanged region during a probe sweep:
its nodes, internal connections and contacts can split or disappear. Re-query
and establish correspondence when testing an actual Pocket-to-Void transition.
Likewise, a wide link can mask narrower internal subregions in the global ratio;
the [capacity hierarchy](hierarchy_and_paths.md) records a different observation.

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

Specifically, the current morphology confidence is $\min(1,|o-1|)$; occlusion is
marginal within 0.1 of 1. In the open branch, proximity within 1 depth step of
the Cleft threshold or 0.3 of the Groove threshold also marks marginality.
For example, $o=1.03$ retains Pocket with confidence 0.03. That number is a
distance-based policy score, not a 3% probability of being a pocket. The score
does not incorporate uncertainty in the underlying capacities or PCA fit.

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

```{dropdown} Check your reasoning
It establishes that the supplied resident/wall-count signature selects that
catalog branch without ambiguity. It does not certify all-atom connectivity,
four physical hull patches, or the accuracy of their areas. Those need their
own definitions and independent evidence.
```
