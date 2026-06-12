# DFND Metrics Contract

This document defines the first working contract for DFND volumes, areas, and
related metrics.

The key lesson from CASTp, fpocket, AlphaSpace2, and related work is that the
same word can mean different quantities in different algorithms. DFND must name
its metrics explicitly rather than pretending that all pocket volumes and mouth
areas are interchangeable.

## 1. Lessons From Existing Methods

### 1.1. CASTp

CASTp taught us that feature membership and physical metrics are separable.
CASTp can agree on pocket, void, channel, and atom composition while still
requiring a specialized metric layer to reproduce areas and volumes.

Important lessons:

- external links are explicit lower-dimensional boundary objects;
- external-link or derived mouth area is not the same thing as pocket surface area;
- feature volume can require subtracting atom-occupied pieces from Delaunay
  tetrahedra;
- tiny or near-threshold features can have almost zero solvent-accessible
  volume but non-zero molecular-surface metrics;
- metric parity can be harder than topological parity.

### 1.2. fpocket

fpocket taught us that alpha-sphere-derived scores and volumes are method
specific.

Important lessons:

- alpha-sphere counts and properties are useful descriptors, but they are not a
  physical solvent volume by themselves;
- build and binary drift can affect final pocket sets;
- descriptor values should be labeled as method-specific scores when they are
  not direct geometric measurements.

### 1.3. AlphaSpace2

AlphaSpace2 taught us to distinguish tetrahedral/alpha-space volume, grid or
overlap volume, beta grouping, and scoring layers.

Important lessons:

- volume can be computed from tessellation primitives or from grid/overlap
  approximations;
- pocket grouping and volume aggregation are separate layers;
- contact and scoring information should be overlaid after the geometric state
  is clear.

## 2. DFND Metric Families

DFND should report metric families explicitly.

### 2.1. Topological volume

Definition:

- sum of Euclidean volumes of tetrahedra in a feature.

Purpose:

- fast;
- deterministic;
- useful for comparing component size and dynamic trends;
- tied directly to the DFND graph.

Limitations:

- includes portions geometrically occupied by atomic vdW spheres;
- not equivalent to solvent-accessible volume.

### 2.2. Net geometric volume

Definition:

- topological tetrahedron volume minus atom-occupied portions inside the feature.

Purpose:

- closer to physical empty-space volume;
- comparable in spirit to CASTp-like physical volume calculations.

Status:

- not first implementation priority;
- should be a later high-precision mode.

### 2.3. Solvent-volume estimate

Definition:

- deterministic local estimate of empty volume inside resident tetrahedra after
  excluding the four local atomic spheres of each tetrahedron.

Purpose:

- first physically honest alternative to topological volume;
- useful for early comparisons and dynamic trends;
- explicitly not an analytic sphere-tetrahedron intersection formula.

Current v1 policy:

- compute `volume_solvent_estimate` per tetrahedron by deterministic barycentric
  sampling;
- aggregate component `volume_solvent_estimate` over resident tetrahedra only;
- do not include transit connectors as resident solvent volume;
- do not include non-local atom intrusions yet.

Open discussion:

- whether a later high-precision mode should use analytic sphere-tetrahedron
  intersections, deterministic adaptive integration, or another validated route;
- whether accessible volume should be approximated by transit tetrahedra only;
- whether COAST candidates contribute;
- whether marginal gates should be included, excluded, or reported separately.

#### High-precision physical-volume evaluation plan

The current estimator is deterministic barycentric sampling, not Monte Carlo. A
higher-precision implementation must therefore be justified by accuracy, physical
meaning, and measured performance rather than by reproducibility alone.

Before selecting an algorithm, define the target quantity precisely. At minimum,
distinguish local empty volume inside resident tetrahedra from the physically
accessible union of empty space for the complete component. A robust method must
consider:

- the **union** of atom-excluded regions, avoiding double subtraction where atomic
  spheres overlap inside a tetrahedron;
- unequal atomic radii, tolerances, degenerate intersections, and sliver
  tetrahedra;
- possible intrusion by atoms that are not vertices of the local tetrahedron;
- whether the quantity is local empty volume, probe-center-accessible volume, or
  a CASTp-like solvent/molecular-surface metric;
- uncertainty or error bounds for any approximate integration route.

Candidate routes include exact or semi-analytic sphere-polyhedron union formulas,
deterministic adaptive integration, and accelerated bounded approximations. No
route should be called exact or preferred until validated.

Validation must include:

1. zero-radius and fully occupied tetrahedra;
2. single-sphere intersections with known references;
3. overlapping spheres where independent subtraction would fail;
4. unequal radii, near-tangent cases, and slivers;
5. synthetic cavities with analytic empty volume;
6. comparison against trusted CASTp/VOLBL-style references where semantics match;
7. measured accuracy and runtime on representative proteins.

A future publication-grade metric should use a new explicit name and preserve the
current estimate for provenance and comparison.

### 2.4. External-link and derived mouth area

Definition:

- geometric area of the connected cluster of permeable boundary faces that form
  an `external_link`.

First working policy:

- `external_link_area_geometric`: sum of Euclidean triangle areas for the
  boundary faces in an `external_link`;
- no atom-cap subtraction in the first implementation;
- raw records must list the external-link faces used.

Later possible metrics:

- `mouth_area_geometric`: geometric mouth area derived from an `external_link`;
- `mouth_area_accessible`: mouth opening area corrected by atomic disks/spheres
  or by a more physical aperture model.

### 2.5. Surface/contact area

Definition:

- area of feature boundary faces against solid or non-throughput regions.

Status:

- decision pending;
- should not be conflated with external-link or derived mouth area;
- may require a separate surface reconstruction or atom-cap correction.

## 3. Required Metric Names

DFND should avoid ambiguous fields like just `volume` or `area` in raw records.

Preferred names:

- `volume_topological` as a raw graph/debugging metric, not physical solvent volume;
- `volume_solvent_estimate` or `volume_solvent` before publication-level comparison;
- `volume_net_geometric`;
- `volume_accessible`;
- `external_link_area_geometric`;
- `mouth_area_geometric`;
- `mouth_area_accessible`;
- `surface_area_boundary`;
- `minimum_gate_radius`;
- `maximum_gate_radius`;
- `mean_gate_radius`;
- `n_tetrahedra`;
- `n_external_link_faces`;
- `n_external_links`;
- `n_mouth_faces` when derived mouth descriptors are requested;
- `n_mouths` when derived mouth descriptors are requested.

The public `Topography` object may expose simplified aliases later, but raw
records should preserve precise metric names.

## 4. First Implementation Policy

The first DFND implementation should report:

- topological volume for void, surface-concavity, pocket, and channel components;
- deterministic local `volume_solvent_estimate` for resident tetrahedra and components;
- geometric external-link area for each external link;
- total external-link area per feature;
- derived mouth area when requested;
- gate-radius summaries;
- tetrahedron and face counts;
- atom and residue ownership;
- raw face lists for reproducibility.

It should not yet claim CASTp-like solvent-accessible metric equivalence.

## 5. Dynamic Metrics

For trajectories, DFND should report time series of the same metric family:

- `volume_topological(t)`;
- `volume_solvent_estimate(t)` when available;
- `n_external_links(t)`;
- `external_link_area_geometric(t)`;
- `minimum_gate_radius(t)`;
- accessibility state over time;
- open probability for gates and external links.

This keeps static and dynamic analyses consistent.

## 6. Pending Decisions

Decisions intentionally left open:

- whether COAST contributes to topological volume;
- whether tiny one-tetrahedron features are emitted or filtered;
- whether near-zero external-link areas remain primary links or are flagged as marginal;
- how to compute net geometric volume efficiently;
- whether high-precision area/volume should borrow CASTp/VOLBL-style formulas
  or use a new DFND-specific integration route.


## 9. Volume Credibility Boundary

`volume_topological` is the sum of Delaunay tetrahedron volumes belonging to a
record. It includes atom-occupied portions because tetrahedra extend to atom
centers. It is useful for raw graph debugging and internal monotonicity checks,
but it must not be reported as physical pocket volume.

For comparison with CASTp-like tools or publication-level pocket metrics, DFND
now exposes `volume_solvent_estimate` as a first deterministic local correction
for atom-occupied portions. This is a v1 estimate, not a final analytic
CASTp-like volume. A future `volume_solvent` metric should be reserved for a
higher-precision physical implementation.
