# DFND Justification and Novelty

This document explains why DFND is worth implementing as a native TopoMT method
and how its claims should be framed responsibly.

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
- MOLE/Caver-style tunnel methods focus on centerlines and transport paths,
  which is powerful for tunnels and channels but less direct for irregular
  volumetric binding regions.
- Grid and surface scanning methods are flexible but can depend on sampling,
  orientation, and resolution choices.

DFND is motivated by a different internal separation:

```text
tetrahedron habitability -> can the probe reside here?
face permeability        -> can the probe pass through this gate?
graph connectivity       -> what components and access relations result?
```

## 2. Core Contribution

The main DFND contribution is the explicit decoupling of local volume
habitability from connectivity.

```text
R_residence: node-level resident-probe capacity
R_gate:     face-level passage capacity
```

This allows a component to keep information about chambers, gates, bottlenecks,
and access without forcing every decision into a single alpha-radius or cluster
threshold.

The second contribution is traceability. DFND is designed so that every component,
external link, dry component, and interface can be traced back to exact atoms,
tetrahedra, faces, thresholds, and marginal decisions.

The third contribution is future dynamic use. Tetrahedron and face identities
provide a natural basis for tracking topographic objects through molecular
dynamics frames without relying only on shape fitting.

## 3. Wet and Dry Views

DFND uses two complementary graph views over the same Delaunay mesh:

- the wet graph, where the probe can reside and pass;
- the dry graph, where the probe cannot reside and where faces block passage.

The wet side supports concavity components such as voids, pockets, and
multi-opening components. The dry side supports raw dry components, dry interfaces,
dry depth, and future candidate motifs such as walls, rims, ridges, protrusions,
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
