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

#### Implemented high-precision methods (on-demand)

The plan above is now realized. The publication-grade metric uses new explicit
names (`volume_solvent_resident`, `volume_solvent_transit`, both `canonical`);
the old `volume_solvent_estimate` is preserved as a `provisional` fast bulk
field for provenance. The precise quantity is computed **on demand** (never in
the bulk pass) and lives in `topomt/dfnd/core/solvent_volume.py`, wired through
`DFNDData.solvent_volume(component_id, *, region, method)` and
`DFNDData.occupancy_grid(component_id, *, region, spacing)`.

Target quantity (all three methods agree on it):

> empty (solvent) volume of a component region = `vol(region)` −
> `vol(region ∩ union(atom vdW balls))`,

over the **union** of the excluding spheres, so overlapping atoms are never
double-subtracted. Overlaps are pervasive in proteins (a covalent bond places
each atom's centre well inside its neighbour's vdW sphere), so this is the
common, not the corner, case. Atom gathering uses a KD-tree, so non-vertex
intruder atoms are subtracted too. `region` is `'resident'` (resident tetrahedra
only) or `'transit'` (resident + transit connectors); volumes are nm³ quantities.

Three methods, offered for richness — each honest about its own error mode:

- **Monte Carlo** (`method='mc'`, the production default). Seeded
  stratified-barycentric sampling per tetrahedron; returns the volume **and a
  rigorous 2σ statistical half-width** as the error. Cost scales with the
  *surface* of the excluding union (roughly constant per tetrahedron), so it
  stays cheap on large components. Reproducible for a fixed seed.
- **Voxel occupancy grid** (its own entry point `DFNDData.occupancy_grid`, not a
  `method=` of `solvent_volume`). Rasterises the region onto a boolean grid at a
  chosen `spacing`,
  subtracting the atom union; returns both the **volume and the 3-D shape**
  (the grid + origin), which Monte Carlo cannot give. Cost scales with
  *volume / spacing³*. Use it when the shape itself is wanted.
- **Exact** (`method='exact'`, the oracle). Deterministic nested (z, y) Gauss
  quadrature with an analytic 1-D interval-union along x — no Monte Carlo, no
  3-D spherical geometry. numba-accelerated (`topomt/_private/jit.py`,
  `lazy_njit`, lazy import). No statistical error; converges with `n_quad`.
  Cost scales with *volume / tetrahedra* (O(L³)), so it is the **slowest on
  large regions** — it is a per-tetrahedron ground truth and a cross-check for
  the other two, not the production path. (Correcting an early intuition that
  "exact" might be fastest for large cavities: it is not; MC stays production.)

The validation battery (1–7 above) is met by
`tests/test_dfnd_solvent_volume_precise.py`: zero-radius and fully occupied
tetrahedra; single-sphere vs the analytic ball volume; overlapping spheres vs
the closed-form lens, where naive independent subtraction provably fails;
unequal/near-tangent radii and slivers; synthetic tetrahedra with analytic empty
volume; MC↔voxel↔exact cross-agreement within MC's error bound. Comparison
against external CASTp/VOLBL references (item 6) is deferred to the validation
program, since semantics (solvent vs molecular-surface) must be matched first.

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

## 10. Output Status Registry (canonical / experimental / provisional)

Before validation, every DFND output is classified by how stable it is, so the
team validates and reports only what is settled and does not silently forget the
parts still held together with pins.

**Source of truth:** `topomt/dfnd/output_status.py` (the `OUTPUT_STATUS`
registry). This table is the human-readable mirror; the registry is authoritative
and is kept in sync with the kernel by `tests/test_dfnd_output_status.py`, which
fails if a new family/motif is emitted unclassified or an `experimental` motif is
mislabelled.

Status meanings: `canonical` (validate & report), `provisional` (engineering use
only, precision caveat), `experimental` (shape may change, carries
`flags=['experimental']`, do not report), `diagnostic` (raw/internal, not a
public feature), `deferred` (design open).

| Output | Status | Promotion gate / blocker |
| --- | --- | --- |
| `pocket`, `void`, `channel`, `percolating`, `dry_bank` | canonical | — |
| `Mouth`, `depth_region`, `external_mouth` | canonical | — |
| `volume_topological_resident`, `center`, `mouth_area`, `R_gate_*`, `n_mouths`, `face_depth` | canonical | — |
| `volume_solvent_estimate`, `bottleneck` | provisional / experimental | precise `volume_solvent` (item-2 / L5.1) ; throat promotion (Q25) |
| `throat_candidate`, `chamber_candidate` | experimental | scoring/persistence policy + tests + toy/real + tolerance stability (Q25) |
| `surface_concavity` | diagnostic | stabilize or redefine the catch-all (L3.1) |
| `nonresident_passage`, `degenerate_subprobe` | diagnostic | deterministic synthetic fixture (item-4 / L1.1) |
| `interface` | deferred | close dry/wet ownership (item-3 / Q17) |

This registry resolves the open questions on confidence flags (Q19) and
promotion strategy (Q25): each non-canonical entry carries the explicit gate it
must clear and the consolidation item that tracks it, so "experimental" means
"tracked with a path to canonical", not "abandoned in place".
