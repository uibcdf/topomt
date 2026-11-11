# Numerical policy and reproducibility

Reproducing a result requires both a physical model and a numerical contract.
Changing one while calling the change "resolution" can conceal a different
scientific question.

## Parameter roles

| Role | Inputs/settings | What changes |
| --- | --- | --- |
| Molecular model | Coordinates, selection, frame, atom radii, hydrogen/chemical composition | The represented atomic-ball system. |
| Probe scale | `probe_radius` | The steric center-placement question. |
| Discrete policy | `transit_policy`, `gate_intrusion_policy`, `dry_adjacency` | The graph construction or bank grouping. |
| Decision band | `epsilon`, residence/permeability tolerances | Candidate/threshold numerical decisions and marginality. |
| Metric resolution | Sample count/seed, quadrature order, grid spacing | Numerical evaluation of a declared quantity. |
| Reporting | `min_size` | Suppressed/reported views while raw decomposition remains available. |

Extra tolerance may be useful in a declared sensitivity study. It is not an
experimentally determined model of flexibility, a free-energy barrier or an
uncertainty interval for atomic positions.

## Units at the boundaries

Use quantities for public physical arguments:

```python
from topomt import get_topography
from topomt import pyunitwizard as puw

result = get_topography(
    molecular_system,
    method='dfnd',
    probe_radius=puw.quantity(1.4, 'angstroms'),
    epsilon=puw.quantity(1e-6, 'angstroms'),
)
```

Legacy bare public query lengths are interpreted as angstroms with a warning.
Direct typed `DFNDQuery`/`DFNDMeshConfig` numeric fields store normalized nm;
their bare numbers must not be confused with that public compatibility rule.
The advanced array constructor has its separately documented angstrom
compatibility convention. Explicit quantities avoid the ambiguity.

Advanced settings such as physical-boundary tolerance belong to the typed
query. This example uses its **canonical nm fields** explicitly:

```python
from topomt.dfnd.config import DFNDQuery

query = DFNDQuery(probe_radius=0.14, boundary_tolerance=1e-7)
configured_result = get_topography(molecular_system, method='dfnd', query=query)
assert configured_result.dfnd.dfn.query == query
```

The shared gateway accepts an existing `DFNDQuery` or `None`, preserving its
identity and the native checks for conflicting explicit arguments. Supply
`boundary_tolerance` through this object; it is not a separate dispatcher
keyword. The immutable query validates its physical/numerical policies when
constructed, while the gateway rejects an unrelated object before execution.

The typical public epsilon of $10^{-6}$ Å is $10^{-7}$ nm. Epsilon also enters
geometric computations; one parameter name does not prove that every internal
predicate has a rigorous dimensionally uniform error analysis. Near-degenerate
behavior needs targeted inspection and margins, not a blanket precision claim.

## Degeneracy and invariance

Coincident/collinear/coplanar input, slivers and nearly singular tangency systems
can challenge triangulation and candidate validation. DFND checks input shape,
finite coordinates, positive radii and sufficient atoms, but satisfying those
checks does not guarantee a well-conditioned three-dimensional triangulation.

Cospherical centers can have nonunique Delaunay triangulations. Tiny coordinate
changes can therefore alter carrier identities and downstream observations.
SciPy's Delaunay interface documents its Qhull backend, precision-related omitted
points and neighbor convention in the [official reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html).

Rigid transformations and consistent unit conversion preserve the intended
geometry. Numerical verification still needs explicit atom correspondence,
tolerance and an appropriate comparison of supports or observables. Reindexing
atoms without preserving their source map is not an identity-preserving test.

## Record enough to repeat the question

Retain exact input coordinates/radii and selection maps, the chosen frame,
method/source version, mesh and query policies, thresholds/margins, reporting
settings and metric parameters. A rounded PDB alone can be insufficient near
a transition; the worked example restores its full-precision quantity records.

Seeded sampling is repeatable for the stated implementation; this is distinct
from an error bound or cross-version bitwise identity. Sharing immutable geometry
does not make every feature/dictionary immutable or make pickle a cross-version
scientific interchange standard.

## Computational cost and responsible execution

Let $N$ be atoms, $T$ tetrahedra and $F$ unique faces. Mesh storage and cached
local records depend on $T$ and $F$, not only $N$. A probe query adds state,
graph/component and descriptor work. On-demand volume/grid calculations can
dominate a small selected analysis and have different accuracy/cost controls.

There is no single measured speed claim for all systems and outputs. Benchmark
specific operations with pinned inputs, backend, warm/cold compilation state,
workers and memory. On shared machines, use bounded sequential/small-worker
runs, preserve resources for others and inspect current pressure before expensive
work. A documentation build displays stored results without submitting jobs or
executing every study notebook.
