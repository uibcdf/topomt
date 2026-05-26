# DFND Numerical Policy

This document defines the first working numerical policy for DFND.

The goal is not to hide fragile geometric decisions behind arbitrary constants.
The goal is to make every threshold, tolerance, and near-boundary state explicit
so that DFND can report what it knows and what remains uncertain.

## 1. Probe Radius and Sea Level

DFND uses a probe radius as the central physical scale.

Initial default:

- `probe_radius = 1.4 angstroms`.

The `sea_level` concept should depend on the probe radius. The first working
policy is:

- default `sea_level = probe_radius`;
- a tetrahedron can be considered exterior-reachable only through faces that
  are permeable to the same probe;
- `OCEAN` should not be understood as a CASTp alpha-rank shell, but as the
  exterior region available to the probe under DFND flow semantics;
- `OCEAN` is wet by definition, but it is not a finite tetrahedron and has no
  `R_residence`, volume, or `COAST` status.

This is a change from the older notes where `sea_level` was described as a
large curvature radius such as 10 angstroms. That older idea may still be useful
for a coarse exterior envelope, but it is not the preferred first policy for
DFND pocket accessibility.

## 2. Exterior Definition

There are two exterior signals in a finite Delaunay mesh:

- hull or boundary faces of finite tetrahedra whose neighbor index is `-1`;
- components that can reach those boundary faces through probe-permeable faces.

First working policy (Access x Residence):

1. Boundary faces are candidate exterior contacts.
2. A wet component contacts `OCEAN` only through a boundary face whose
   `R_gate >= probe_radius` under the selected tolerance policy.
3. Connected open exterior contacts are grouped into `external_links`.
4. A component is classified according to its **Access** (number of direct external links to `OCEAN`) and its **Residence** (whether it contains at least one node where `R_residence >= probe_radius`):
   - **0 external links**:
     - *Has residence*: `void` (closed cavity where the probe fits).
     - *No residence*: `degenerate_subprobe` (filter/provisional component).
   - **1 external link**:
     - *Has residence*: `pocket` (one-mouth resident concavity).
     - *No residence*: `surface_concavity` (one-mouth non-resident surface dent).
   - **>= 2 external links**:
     - *Has residence*: `multi_external_link` (multi-mouth resident channel).
     - *No residence*: `nonresident_passage` (provisional pass-through contact).

`wet_open` is used purely as a quality and accessibility descriptor, not as a classification gate.

- whether a large-box or padding construction is needed for systems with very
  sparse exterior geometry;
- whether `sea_level` should also support a larger envelope mode for coarse
  outside/bulk labeling;
- whether fragmented molecular systems should have one shared exterior root or
  one exterior context per molecular fragment.

## 3. Open, Closed, and Marginal Predicates

DFND should avoid silent hard binary decisions near thresholds.

For a quantity `x` compared against threshold `t`, use three states:

- open: `x > t + eps`;
- closed: `x < t - eps`;
- marginal: `abs(x - t) <= eps`.

Applied to DFND:

- node habitability uses `R_residence` versus `probe_radius`;
- face permeability uses `R_gate` versus `probe_radius`;
- `external_link` openness uses face permeability at the component boundary;
- dynamic gating uses threshold crossing of `R_gate(t)` around `probe_radius`.

Marginal states should be reported in raw records. The deterministic side is
**generous**: `epsilon` is applied in favour of open/permeable/resident (so the
`>=` threshold holds inclusively), and physical tolerances
(`residence_tolerance`, `permeability_tolerance`, default `0.0`,
user-controllable) widen it further for structural flexibility / coordinate
imprecision. The diagnostic must retain that the decision was near-threshold.

## 4. Tolerance Types

DFND needs more than one tolerance.

### 4.1. Length tolerance

Used for radii, distances, gate radii, and habitability radii.

Initial discussion value:

- `epsilon_length = 1e-6 angstroms` for unit-level tests and deterministic
  synthetic geometries.

Open discussion:

- whether practical molecular inputs should use a looser tolerance, for example
  tied to coordinate precision;
- whether PDB inputs with 0.001 angstrom coordinate precision should use an
  input-aware tolerance;
- whether high-precision formats should keep tighter thresholds.

### 4.2. Relative tolerance

Used when comparing quantities whose scale varies substantially.

Candidate policy:

- `epsilon_relative = 1e-8` for numerical solver residuals;
- effective tolerance `eps = max(epsilon_length, epsilon_relative * local_scale)`.

Local scale can be the maximum edge length of a tetrahedron or face.

### 4.3. Area tolerance

Used for derived mouth areas, external-link areas, and boundary face clusters.

Open discussion:

- whether tiny derived mouth area should remain a real descriptor with near-zero area;
- whether small external-link clusters should be retained but flagged;
- whether filtering tiny derived mouth descriptors or external links would hide
  physically relevant flickering in molecular dynamics.

### 4.4. Volume tolerance

Used for tiny tetrahedra, slivers, and near-zero components.

Open discussion:

- whether one-tetrahedron near-zero components should be emitted as features;
- whether volume filtering should be an optional report filter rather than core
  classification;
- whether tiny closed components should be reported as void candidates with a
  low-confidence flag.

## 5. Degenerate Geometry

DFND should not crash on degenerate or near-degenerate geometry.

Cases:

- duplicate or nearly duplicate atom coordinates;
- collinear face atoms;
- coplanar or nearly coplanar tetrahedra;
- singular clearance candidate systems;
- negative or non-physical radii;
- highly overlapping atoms.

First working policy:

- invalid local geometry should produce flagged records;
- failed `R_residence` or `R_gate` computations should not be silently treated as
  normal closed geometry without diagnostics;
- the stable classification may set the failed value to zero for graph safety,
  but raw records must preserve the failure reason.

## 6. Local Permeability Class

DFND uses wet/dry for tetrahedra and permeable/non-permeable for faces. The
local permeability class of a finite tetrahedron is derived from the
permeability pattern of its finite faces.

```text
tetrahedron_wet(T) = R_residence(T) >= R_probe
tetrahedron_dry(T) = R_residence(T) < R_probe

face_permeable(F) = R_gate(F) >= R_probe
face_non_permeable(F) = R_gate(F) < R_probe

open(T) = all finite faces of T are permeable
coast(T) = at least one finite face is permeable
           and at least one finite face is non-permeable
sealed(T) = all finite faces of T are non-permeable
```

`non-coast` is not a primary DFND label. If a broad complement is required, it
means `open or sealed`.

The combined local states to report are:

- `wet_open`;
- `wet_coast`;
- `wet_sealed`;
- `dry_open`;
- `dry_coast`;
- `dry_sealed`.

Numerical policy:

- compute and report the number of permeable, non-permeable, and marginal
  finite faces per tetrahedron;
- expose `open`, `coast`, `sealed`, and the six wet/dry combined labels in raw
  records;
- keep primary wet connectivity based on wet tetrahedra and permeable faces;
- do not let local class labels create connectivity by themselves;
- report marginal faces separately when `R_gate` is within tolerance of
  `R_probe`.

## 7. Raw Diagnostics

Every DFND run should be able to report raw numerical diagnostics:

- atom coordinates and radii model used;
- `R_residence` per tetrahedron;
- `R_gate` per face;
- open/closed/marginal state per node and face;
- failed geometry records;
- face identifiers as atom triplets;
- component labels;
- external-link face clusters;
- derived mouth descriptors when requested;
- tolerances and probe radius.

These records are essential while the method is being stabilized. Later, the
public API may hide them by default, but the implementation should keep a way to
return them.
