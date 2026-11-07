# DFND Justification and Novelty

This document explains why DFND is worth implementing as a native TopoMT method
and how its claims should be framed responsibly.

Evidence update (2026-11-07): the [MOLE comparison](mole_comparison_2026_11_07.md)
identifies direct antecedents for tetrahedral accommodation, separate scales,
cavity components, depth and opening grouping. The contributions below describe
DFND's design and candidate research value; they do not establish historical
priority. MOLE also retains cavity/void regions before extracting paths.

DFND should not be presented as a formal limiting case or superset of CASTp,
fpocket, MOLE, Caver, or other tools. It shares concepts with several of them,
especially Delaunay/Voronoi geometry and probe-based accessibility, but it uses
its own graph semantics and deliberately keeps standard Delaunay as the baseline
substrate.

## 1. Current Landscape

Molecular topography tools differ in substrate, objective, and output:

- CASTp-style alpha-shape methods provide analytically grounded pockets,
  cavities, mouth areas, and volumes, with strong historical validation.
- fpocket-style alpha-sphere clustering methods are practical and efficient for
  binding-site detection and ranking, but use heuristic clustering choices.
- MOLE-style tunnel methods retain cavity/void regions and boundary information
  before extracting centreline paths and profiles. Compare their region and
  path products separately; other tunnel methods need their own source review.
- Grid and surface scanning methods are flexible but can depend on sampling,
  orientation, and resolution choices.

DFND is motivated by a different internal separation:

```text
tetrahedron habitability -> can the probe reside here?
face permeability        -> can the probe pass through this gate?
graph connectivity       -> what components and access relations result?
```

## 2. Core Contribution

DFND's central design choice is an explicit pair of local volume-habitability
and face-permeability capacities. Accommodation and passage already have MOLE
antecedents; the precise operators, solver and induced decomposition are the
candidate contributions to evaluate.

```text
R_residence: node-level resident-probe capacity
R_gate:     face-level passage capacity
```

This allows a component to keep information about chambers, gates, bottlenecks,
and access without forcing every decision into a single alpha-radius or cluster
threshold.

Another design commitment is traceability. DFND is designed so that each component,
external link, dry component, and interface can be traced back to exact atoms,
tetrahedra, faces, thresholds, and marginal decisions.

An additional goal is dynamic use. Tetrahedron and face identities
provide a natural basis for tracking topographic objects through molecular
dynamics frames without relying only on shape fitting.

## 3. Wet and Dry Views

DFND uses two complementary graph views over the same Delaunay mesh:

- the finite transit graph, including resident cells and optional connectors;
- a dry bank graph over its complement, with an explicit adjacency policy.

These are local discrete descriptors, not a certified partition of physical
solvent and molecular material. Dry-bank membership differs from nonresidence
when connectors are enabled; physical passage needs the
[theoretical reconciliation](core_theory_review_2026_11_06.md).

The wet side supports concavity components such as voids, pockets, and
multi-opening components. The dry side supports raw dry components, dry interfaces,
face depth, and future candidate motifs such as walls, rims, ridges, protrusions,
separators, and dry cores.

The dry side is not claimed as a validated public feature system yet. It is a
raw and candidate-descriptor layer in the v1 plan.

## 4. Responsible Comparison

DFND should be compared to existing tools on measurable outputs, not on broad
superiority claims.

Initial comparison dimensions:

| Dimension | CASTp-style | fpocket-style | tunnel tools | DFND target |
|---|---|---|---|---|
| Analytical geometry | strong | partial | strong for paths | strong for mesh/graph primitives |
| Binding-site ranking | not primary | strong | not primary | future |
| Mouth/exterior access | strong | indirect | path exits | explicit `ExternalLink` |
| Chamber/gate descriptors | partial/tool-dependent | heuristic | path bottlenecks | explicit graph descriptors |
| Dynamic tracking | not primary | MD variants exist | path tracking possible | atom/tetrahedron/face identity |
| Dry-side descriptors | not primary | not primary | not primary | candidate/future |

This table is a design-orientation summary, not a benchmark result. Publication
or adoption claims require quantitative validation.

## 5. Claims to Avoid

Avoid these claims unless future work proves them precisely:

- DFND contains CASTp as a formal limiting case.
- DFND contains MOLE or Caver as formal limiting cases.
- DFND is categorically more exact than existing tools.
- `volume_topological` is a physical pocket volume.
- `channel` necessarily means a biological tunnel or pore.
- dry motifs are validated public feature families.

## 6. Claims That Are Currently Defensible

Current defensible claims:

- DFND is a native TopoMT method based on standard Delaunay geometry,
  tetrahedron habitability, face permeability, and graph decomposition.
- DFND explicitly separates resident capacity (`R_residence`) from passage
  capacity (`R_gate`).
- DFND keeps `OCEAN` and `ExternalLink` as first-class graph objects for
  exterior access.
- DFND records marginal and degenerate decisions explicitly rather than hiding
  them behind silent thresholds.
- DFND provides a natural raw-record substrate for later trajectory tracking,
  dry/wet interface analysis, and feature enrichment.

## 7. Validation Requirement

DFND should not be promoted as a competitive detector until it has been tested
against real systems using explicit metrics. A first validation plan is defined
in [`validation_plan.md`](validation_plan.md).
