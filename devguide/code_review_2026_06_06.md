# TopoMT and MolSysViewer-TopoMT Code Review

**Date:** 2026-06-06
**Scope:** `topomt/`, `molsysviewer_topomt/`, relevant tests, packaging, and CI
**Purpose:** consolidated engineering backlog for correcting confirmed defects,
clarifying contracts, and improving maintainability
**Status:** review complete; correction backlog actively tracked and partially verified

---

## 0. How to Use This Report

This document is the master technical correction backlog produced by the
2026-06-06 review. It records concrete implementation findings and organizes
them into executable work packages. It is not the authoritative definition of
the intended scientific ontology.

Use the document as follows:

1. Select the next work package according to the dependencies in section 10.
2. Add the listed regression tests before changing implementation.
3. Update each affected finding from `Open` to `In progress`, then to `Fixed`.
4. Mark a finding `Verified` only after its acceptance criteria and relevant
   complete-suite checks pass.
5. Record the correcting pull request or commit beside the finding.
6. Update affected contracts and documentation in the same work package.

Tracking states:

- **Open:** confirmed or recorded, with no correction started.
- **In progress:** regression test or implementation work has started.
- **Fixed:** implementation has changed, but complete acceptance has not yet
  been demonstrated.
- **Verified:** acceptance criteria, focused tests, and affected integration
  tests pass.
- **Decision required:** implementation must wait for an explicit scientific or
  architectural decision.

Every finding now declares evidence and tracking separately. Findings begin as
`Open`; design risks begin as `Decision required`.

The companion
[architecture review](architecture_review_2026_06_06.md) evaluates the
scientific object model and software architecture. Proposals from that document
must not be treated as approved implementation work until their contracts are
decided.

---

## 1. Executive Summary

The repository has a substantial, executable DFND implementation, a typed DFND
object layer, synthetic validation systems, and a working MolSysViewer addon.
The main scientific and architectural direction is coherent. However, several
contracts are currently implemented inconsistently across layers.

The highest-priority problems are:

1. DFND can mark a shared face as permeable while excluding the corresponding
   edge from the wet transit graph.
2. Viewer and diagnostic paths sometimes use mesh-local atom indices where
   molecular-system-global atom indices are required.
3. `Topography` mutation was not atomic and could silently corrupt derived
   indexes; this is now corrected and regression-tested.
4. Rendering a subset of features can replace the addon runtime's complete
   topography with a partial copy that no longer contains DFND data.
5. Several viewer representations cannot be rendered repeatedly because their
   tags are not cleared consistently.
6. Some public APIs have behavior that depends on import order, caller filename,
   or mocks that do not match real runtime objects.

Static DFND identity and registry integrity are now implemented and verified.
The remaining problems should be corrected before treating DFND connectivity,
dynamic lineage, or visualization as stable public contracts.

---

## 2. Review Method

The review combined:

- static reading of the TopoMT and MolSysViewer-TopoMT source;
- inspection of public and internal object contracts;
- review of the test suite and CI configuration;
- directed Ruff checks for undefined names, unsafe defaults, and closure errors;
- minimal dynamic probes that reproduce suspected defects;
- targeted pytest runs;
- a complete test-suite run using `pytest -n 12`.

The complete suite finished successfully, including its expected skips and
`xfail` cases. A passing complete suite does not invalidate the findings below:
several defects are not covered, while at least one public-surface test fails
when run in isolation because it depends on import order.

### 2.1. Review scope and confidence

Reviewed deeply:

- the public `Topography` and feature registries;
- DFND mesh, graph, component, selector, data, and promotion paths;
- the `molsysviewer_topomt` addon, renderers, runtime, and standalone helpers;
- relevant synthetic systems and tests;
- public tools reached by these workflows;
- packaging, Ruff configuration, and CI entry points.

Reviewed less deeply:

- scientific parity of every non-DFND detection engine;
- bundled or adapted third-party algorithms;
- performance on large production trajectories;
- browser behavior outside the exercised MolSysViewer workflows;
- serialization compatibility across released TopoMT versions.

Absence from this report therefore does not establish correctness in those
areas.

---

## 3. Severity and Status Conventions

Severity:

- **P0 - scientific correctness:** can change DFND classification, connectivity,
  identity, or reported scientific results.
- **P1 - data integrity / major user behavior:** can corrupt object state, render
  the wrong atoms, or break a central user workflow.
- **P2 - API correctness / reliability:** produces misleading, inconsistent, or
  fragile behavior without necessarily changing the core scientific result.
- **P3 - maintainability / quality:** increases the probability or cost of future
  defects.

Evidence:

- **Confirmed:** reproduced dynamically or directly demonstrated by the code.
- **Strong static finding:** code path is unambiguous, but no dedicated runtime
  reproducer was needed.
- **Design risk:** behavior requires an explicit contract decision before it can
  be classified as a defect.

Finding category:

- **Bug:** implementation demonstrably violates intended or documented
  behavior.
- **Contract violation:** multiple layers implement incompatible meanings for
  the same public or scientific concept.
- **Documentation drift:** documentation contradicts current implementation or
  another authoritative document.
- **Technical debt:** implementation is fragile or costly to maintain, but no
  current wrong result has been demonstrated.
- **Design decision:** several scientifically defensible behaviors exist and
  one must be chosen before implementation.

Each correction should preserve this distinction. In particular, a design
decision must not be resolved implicitly while fixing an adjacent bug.

### 3.1. Standard acceptance contract

Unless a finding defines stricter acceptance tests, verification requires all of
the following:

- a focused regression test that fails before the correction and passes after it;
- relevant integration tests selected according to the affected surface;
- the complete suite only when implementation changes have broad blast radius,
  alter shared contracts, or close a major work package;
- no new correctness-focused Ruff violations;
- affected public contracts and developer documentation updated;
- a recorded correcting commit or pull request;
- deterministic behavior across two repeated runs where ordering or identity is
  relevant.

Documentation-only edits, test-only cleanups, and warning-hygiene changes should
use focused tests plus static checks rather than rerunning the complete suite by
default.

---

## 4. P0: Scientific Correctness

### DFND-001: Face permeability and graph traversability use incompatible thresholds

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** One canonical transit-edge mask now connects two transit nodes
through every shared face classified as permeable. The duplicated strict gate
threshold was removed; physical and effective margins are reported explicitly.
See [`DFND/checkpoint_canonical_transit_edges_2026_06_12.md`](DFND/checkpoint_canonical_transit_edges_2026_06_12.md).
**Location:** `topomt/dfnd/graph.py`

Face permeability is defined inclusively and in favor of passage:

```python
face_permeable = R_gate >= R_probe - epsilon - permeability_tolerance
```

The wet graph then applies an additional, stricter test:

```python
edge_weights > probe_radius + epsilon
```

Consequently, two finite-transit tetrahedra can share a face recorded as
`permeable` but remain in different wet components.

**Observed reproduction**

At a probe radius exactly equal to a shared face's `R_gate`, the face record was
`permeable`, both tetrahedra were `resident`, but no wet component contained both
tetrahedra.

**Impact**

- artificial fragmentation of wet components;
- wrong pocket/channel/void classification near thresholds;
- inconsistent component IDs and counts;
- disagreement between face visualization and graph visualization;
- incorrect `path_capacity_min` because it repeats the stricter edge test.

**Required correction**

Create one canonical predicate or precomputed mask for shared-face
traversability. Every consumer must use it:

- face records;
- wet graph adjacency;
- connector classification;
- component extraction;
- `path_capacity_min`;
- centerline construction;
- graph visualization.

**Acceptance tests**

- For every internal face, if both incident tetrahedra are finite-transit and the
  face is `permeable`, the tetrahedra must be adjacent in the wet graph.
- Equality at `R_gate == R_probe` must follow the documented numerical policy.
- Property test across many probes: no face record and graph edge may disagree.

### DFND-002: `sea_level` was accepted and recorded but had no effect

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** `sea_level` was removed completely from DFND APIs, internal calls, effective provenance, tests, and current contracts. No compatibility shim is retained because DFND has no external users yet.
**Location:** `topomt/dfnd/graph.py`, `topomt/dfnd/api.py`, `topomt/dfnd/data.py`

Before correction, `sea_level` was exposed by public APIs, propagated through
`at_probe()`, and stored in raw parameters, but it did not participate in any
DFND calculation.

**Impact**

Users can believe they changed the decomposition while receiving an unchanged
result. The parameter is also preserved in provenance, making the output appear
to have been computed under that setting.

**Required correction**

Either implement and document its exact scientific meaning, or remove it from
public DFND APIs until an implementation exists. Do not keep an inert scientific
parameter.

### DFND-003: Physical query parameters accept invalid values

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** Negative or non-finite radii and tolerances, and non-integer or negative min_size values, are rejected before calculation.

**Location:** `topomt/dfnd/graph.py`

DFND currently accepts negative `probe_radius`, negative
`residence_tolerance`, and negative `permeability_tolerance`.

**Required correction**

Validate all scientific parameters before calculation:

- `probe_radius >= 0`;
- tolerances `>= 0`;
- `min_size` is a non-negative integer;
- enum-like policies are validated centrally;
- future physical parameters define units and valid ranges.

### DFND-004: Channel centerline clearance was not guaranteed along the path

**Evidence:** Design risk with confirmed implementation limitation
**Tracking:** Verified
**Resolution:** The API is now named `channel_skeleton`, replacing the older centerline name. It returns `path_kind='shortest_distance'`, station radii (`R_residence`), gate radii/margins for the N-1 traversed transitions, separate station and gate bottleneck indices, and `is_collision_validated=False`. Gate minima are explicitly named as shortest-path metrics, not channel capacity.
**Location:** `topomt/dfnd/centerline.py`, `tests/test_dfnd_centerline.py`

The skeleton chooses a shortest path through resident tetrahedra and connects residence centers with straight segments. A permeable shared face guarantees a feasible crossing somewhere on that face, not that the straight segment between centers is a collision-free probe trajectory. The result is therefore a visualization/geometry skeleton. Future `widest_gate_path` and validated probe-path work should live in a separate work package.

### DFND-005: Centerline mouth endpoints were order-dependent

**Evidence:** Confirmed by inspection
**Tracking:** Verified
**Resolution:** `channel_skeleton` represents the two widest mouths as virtual graph nodes connected to every incident resident tetrahedron. The shortest-distance path is computed between those virtual mouth nodes, then virtual nodes are stripped from the returned tetrahedron path. The result records `mouth_endpoint_policy='virtual_mouth_shortest_distance'`.
**Location:** `topomt/dfnd/centerline.py`, `tests/test_dfnd_centerline.py`

This removes dependence on the first tetrahedron listed for a mouth while keeping the current shortest-distance visual skeleton contract.

### DFND-013: Transit connectors belonged to both wet and dry component sets

**Evidence:** Confirmed implementation behavior
**Tracking:** Verified
**Resolution:** Dry components are now built from blocked tetrahedra only: `dry_mask = ~finite_transit`. Non-resident transit connectors remain on the wet/transit side and are excluded from dry components.
**Location:** `topomt/dfnd/graph.py`, `tests/test_dfnd_graph_contract.py`

Wet components include resident tetrahedra plus non-resident transit connectors. Dry components previously used every non-resident tetrahedron, so a connector could belong simultaneously to one wet and one dry component. The dry side now means non-resident and non-transit, which keeps wet/transit and dry membership disjoint for connector nodes.

**Closure evidence**

The connector fixture asserts that `transit_connector_tetrahedron_ids` are disjoint from all dry component tetrahedra.

### DFND-014: Dry depth was face-based while dry components can be edge/vertex-connected

**Evidence:** Strong static finding
**Tracking:** Verified
**Resolution:** The metric is now explicitly named `face_depth`. It remains face-based by design: depth propagates only through non-permeable shared faces (`dry_edges`), even when `dry_adjacency='edge'` or `'vertex'` uses looser contacts to group components.
**Location:** `topomt/dfnd/graph.py`, `tests/test_dfnd_graph_contract.py`

With `dry_adjacency="edge"` or `"vertex"`, dry components may use additional edge/vertex contacts. Stored `dry_edges`, and therefore `face_depth` propagation, contain only non-permeable shared-face contacts. A tetrahedron connected only by edge/vertex contacts can honestly retain `face_depth=None`: it is in the dry component, but not face-reachable from the dry interface.

**Closure evidence**

Raw records and public dry components expose `face_depth_*` fields, dry motifs use `face_depth`, and the raw schema was bumped to `dfnd.raw.nm.v2`.

---

## 5. P1: Data Integrity and Major User Behavior

### CORE-001: Duplicate feature IDs silently corrupt `Topography`

**Evidence:** Confirmed
**Tracking:** Verified
**Location:** `topomt/topography/Topography.py`

`add_feature()` constructs a `Warning` object for a duplicate ID but neither
emits it nor stops. The new feature overwrites `_features[feature_id]`, while the
old type, shape, and dimensionality indexes remain populated.

**Progress:** Corrected and covered by atomic-registry regression tests.

**Required correction**

Reject duplicates by default. If replacement is required, implement explicit
`replace_feature()` that updates every index and relation atomically.

### CORE-002: Automatic feature IDs can collide

**Evidence:** Confirmed
**Tracking:** Verified
**Location:** `topomt/topography/Topography.py`

The next ID is generated from the number of features of a type. If `POC-2`
exists while `POC-1` does not, the generated next ID is again `POC-2`.

**Progress:** Corrected and covered by atomic-registry regression tests.

**Required correction**

Use the next free suffix or a monotonic per-prefix counter.

### CORE-003: Failed `add_feature()` can partially mutate another topography

**Evidence:** Confirmed
**Tracking:** Verified
**Location:** `topomt/topography/Topography.py`

The feature is written into `_features` before checking whether it already
belongs to another `Topography`. The method then raises, leaving a partially
mutated destination registry.

**Progress:** Corrected and covered by atomic-registry regression tests.

**Required correction**

Validate the entire operation before mutation. Registry operations should be
transactional.

### CORE-004: Registered feature IDs remain mutable

**Evidence:** Confirmed
**Tracking:** Verified
**Location:** `topomt/features/BaseFeature.py`

Changing `feature.id` after registration changes the object but not the
registry's keys, indexes, or relations.

**Progress:** Corrected and covered by atomic-registry regression tests.

**Required correction**

Make IDs immutable once attached, or provide `Topography.rename_feature()` that
performs a validated atomic rename.

### CORE-005: `Topography.copy()` loses important state

**Evidence:** Confirmed
**Tracking:** Verified
**Location:** `topomt/topography/Topography.py`

Both shallow and deep copies reconstruct only a subset of state. They lose or
reset `selection`, `structure_indices`, attached `dfnd`, and arbitrary analysis
attributes.

**Progress:** Corrected and covered by atomic-registry regression tests.

**Required correction**

Define an explicit copy contract. `copy()` should preserve the full semantic
object; a separate `copy_features_only()` can create a deliberately partial
registry.

### CORE-006: `Components.add()` can silently overwrite and corrupt indexes

**Evidence:** Strong static finding
**Tracking:** Verified
**Location:** `topomt/dfnd/components.py`

The typed component registry repeats the same overwrite pattern as
`Topography`: duplicate IDs replace the primary record without removing old
side/family indexes or relations.

**Progress:** Corrected and covered by atomic-registry regression tests.

**Required correction**

Apply the same atomic registry policy to features and components.

### VIEW-001: Viewer atom-index boundaries are implicit

**Evidence:** Confirmed
**Tracking:** Verified
**Location:** `molsysviewer_topomt/render/_tetrahedra.py`,
`molsysviewer_topomt/render/_components.py`, `molsysviewer_topomt/render/_common.py`

DFND records distinguish `local_atom_indices` in the selected mesh from
`atom_indices` in the original molecular system. Both spaces are necessary:
local indices correctly index cached mesh coordinates, while global indices are
required by public records, MolSysMT, and a view loaded with the original
system. The defect was an undeclared and inconsistently converted boundary, not
the existence of local renderer geometry.

**Impact**

Wrong atoms can be rendered, described, grouped, or selected whenever DFND uses
a subset, including the normal hydrogen-exclusion path.

**Progress**

The two-space contract is implemented through centralized helpers and mandatory
labels on addon-owned payloads and metadata. Correct local geometry was
retained. The audit corrected global-to-local leaks in mouth rings, dry
scaffolds, body/contact-sheet grouping, pharmacophore chemistry, and affinity
chemistry. Partial-selection hover/click/selection tests verify that global
simplex payloads are mapped to the view only at the host boundary.

### VIEW-002: `DFNDData.info()` queries the molecular system with local indices

**Evidence:** Confirmed by inspection and shared reproducer
**Tracking:** Verified
**Location:** `topomt/dfnd/data.py`

The diagnostic card labels `local_atom_indices` as original atoms and uses them
in `molsysmt.get()` calls.

**Progress**

`DFNDData.info()` now uses `atom_indices` for molecular-system queries. A
regression test with a leading excluded hydrogen proves that mesh-local and
global indices differ and that only global indices reach MolSysMT.

### VIEW-003: Rendering selected features replaces the complete addon topography

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** The runtime and view retain the complete source topography; feature rendering uses `active_feature_ids` and a stable feature render group.
**Location:** `molsysviewer_topomt/integration.py`

`attach_features()` builds a partial `Topography` and passes it to
`attach_topography()`, which stores it as both `runtime.topography` and
`view.topography`. The partial object does not preserve DFND data.

**Progress**

`attach_features()`, `attach_pockets()`, and `new_view(feature_ids=...)` now
filter `show_topography_pockets()` directly without replacing the source.
`render_groups` manages replacement by stable `<kind>:<tag_prefix>` keys.

### VIEW-004: Re-rendering `show_dfn_graph()` causes tag collisions

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** show_dfn_graph clears every concrete tag it owns before rendering.

**Location:** `molsysviewer_topomt/render/_graph.py`

The function clears `tag_prefix` but creates node, edge, and mouth shapes with
derived tags. The second call can fail because those concrete tags remain.

**Required correction**

Centralize ownership and clearing of render groups. Every public render function
must be idempotent with respect to its `tag_prefix`.

### VIEW-005: Standalone selected-feature rendering uses the wrong keyword

**Evidence:** Confirmed by inspection
**Tracking:** Verified
**Resolution:** Standalone helpers pass the supported show keyword to new_view.

**Location:** `molsysviewer_topomt/standalone.py`

Standalone helpers call `new_view(..., render=...)`, but `new_view()` expects
`show`. The unknown keyword is swallowed by `**render_kwargs`.

**Required correction**

Use `show=feature_ids is None` and replace mock-only assertions with an
integration test that inspects emitted viewer operations.

---

## 6. P2: API Correctness and Reliability

### DFND-006: `DFNDData.at_probe()` does not preserve the full query

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** `at_probe()` replaces fields on the immutable current `DFNDQuery`, preserves reporting options, and rejects mesh-configuration overrides.
**Location:** `topomt/dfnd/data.py`, `topomt/dfnd/graph.py`

The method promises that unspecified options default to the current query, but
`dry_adjacency` and `min_size` are not preserved.

**Required correction**

Introduce one immutable DFND query/configuration object containing every
behavior-affecting parameter.

### DFND-007: `min_size` has asymmetric semantics

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** `min_size` is a compatibility/reporting filter. Wet and dry retain the complete decomposition and mark `include_in_compatibility_view` symmetrically.
**Location:** `topomt/dfnd/graph.py`, `topomt/dfnd/api.py`

For wet components, `min_size` filters only compatibility feature views while
`raw['wet_components']` retains all components. For dry components, it removes
components before typed components are built.

**Required correction**

Define whether `min_size` is a decomposition parameter, reporting filter, or
feature-promotion filter. Prefer separate names for separate behaviors.

### DFND-008: Invalid component representation silently returns `None`

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** Component representations are validated at entry and unknown values raise an informative ValueError.

**Location:** `molsysviewer_topomt/render/_components.py`

Unknown representation strings fall through the dispatcher.

**Required correction**

Validate representation at entry and raise `ValueError` listing canonical
values and aliases.

### DFND-009: `probe_centers` reads parameters from the wrong object

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** probe_centers reads the canonical DFNDData.dfn.parameters and is covered with a real DFNDData regression.

**Location:** `molsysviewer_topomt/render/_components.py`

The representation reads `dfnd_data.parameters`, but real `DFNDData` stores
parameters under `dfnd_data.dfn.parameters`. Current tests use a mock that does
not match the real object layout.

### DFND-010: `WetComponent` initialization contains unreachable code

**Evidence:** Confirmed by inspection
**Tracking:** Verified
**Resolution:** WetComponent motif descriptors are initialized in __init__ instead of unreachable code.

**Location:** `topomt/dfnd/components.py`

Motif-related attributes are initialized after `return` in `__repr__` and
therefore never run for a newly constructed component.

### DFND-011: Face ID fallback depends on the filtered result

**Evidence:** Strong static finding
**Tracking:** Verified
**Resolution:** Legacy face-ID fallback now preserves the original raw face position after filtering and deduplication.

**Location:** `topomt/dfnd/selectors.py`

When a face lacks `face_id`, `select_face_ids()` uses the position in the
already-filtered output, not the original raw position.

**Required correction**

Make `face_id` a required invariant. If legacy fallback is needed, preserve the
raw positional index before filtering.

### DFND-012: Component selectors accept subtly different source shapes

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** Selectors normalize supported sources into one internal view with explicit wet/dry capabilities and reject requests unavailable from a source.
**Location:** `topomt/dfnd/selectors.py`

A complete result dictionary exposes wet and dry components. A raw dictionary
exposes only wet components because dry components live outside `raw`.

**Required correction**

Document accepted source forms and capabilities, or normalize them into one
internal selector view.

### DFND-015: Public `Mouth` promotion loses gate and provenance metrics

**Evidence:** Confirmed by inspection
**Tracking:** Verified
**Resolution:** Promoted `Mouth` features now carry the originating
`external_link_record`, source face/tetrahedron ids, local faces, flags, area as
`nm**2`, and `R_gate_min`/`R_gate_mean`/`R_gate_max` as `nm` quantities. Raw
external links now include `R_gate_mean`.
**Category:** Contract violation
**Location:** `topomt/dfnd/api.py`, `topomt/features/Mouth.py`

Promoted `Mouth` features previously received `component_id`,
`external_link_id`, and area, but gate-capacity descriptors and much of the
source `ExternalLink` provenance remained only in parent dictionaries or raw
records. Public mouth objects therefore did not carry the metrics needed to
interpret their own permeability.

**Required correction**

Define the stable public `Mouth` contract and promote available quantities and
provenance, including gate minimum, maximum, and mean; source face IDs; flags;
and an explicit link to the originating `ExternalLink`. Values with physical
dimensions must follow the public unit contract.

**Acceptance tests**

- Every promoted mouth is traceable to exactly one source external link.
- Public gate and area metrics agree with the source record after unit conversion.
- Missing optional geometry is represented explicitly, not silently dropped.

### VIEW-006: Graph representation output order is nondeterministic

**Evidence:** Strong static finding
**Tracking:** Verified
**Resolution:** Component graph nodes are emitted in sorted tetrahedron-ID order.

**Location:** `molsysviewer_topomt/render/_components.py`

Selected graph nodes are stored in a set and emitted without sorting.

### VIEW-007: Rendering return conventions are inconsistent

**Evidence:** Strong static finding
**Tracking:** Verified
**Resolution:** Primary renderers return the structurally immutable,
mapping-compatible `RenderResult`, including explicit empty results.
**Location:** `molsysviewer_topomt/render/_components.py`

Different representations return a single layer, list, dictionary, `None`, or
empty list.

**Progress**

`RenderResult` contains representation, selected IDs, actual layers, exact tags,
counts, warnings, and representation-specific details. It preserves dictionary
access and delegates layer attributes to `primary_layer` for migration.

### VIEW-008: Broad exception swallowing hides addon failures

**Evidence:** Strong static finding
**Tracking:** Open
**Location:** multiple `molsysviewer_topomt` modules

Many paths use `except Exception: pass`, including runtime resolution, panel
state, selection handling, and layer clearing.

**Required correction**

Catch expected exceptions narrowly, log unexpected exceptions, and preserve
error states in panels.

### VIEW-009: Tetrahedron click callback is a no-op

**Evidence:** Confirmed by inspection
**Tracking:** Verified
**Resolution:** Removed the no-op callback. Native shape selection and the addon active-selection hook own click synchronization.
**Location:** `molsysviewer_topomt/integration.py`

The callback is registered only to satisfy tracking/tests and performs no
action. Remove it if native selection is sufficient, or implement the required
state synchronization.

### VIEW-010: Context action is registered to a placeholder entry

**Evidence:** Strong static finding
**Tracking:** Verified
**Resolution:** `dfnd-tetrahedron-info` now points to the executable `inspect_dfnd_tetrahedra()` action, which is also reused by the lifecycle hook.
**Location:** `molsysviewer_topomt/addon.py`, `molsysviewer_topomt/context.py`

The `dfnd-tetrahedron-info` action is registered with
`focus_topography_feature`, which only returns a normalized placeholder. Actual
behavior resides in the lifecycle hook.

### VIEW-011: Feature subset views lose relations and DFND semantics

**Evidence:** Strong static finding
**Tracking:** Verified
**Resolution:** Viewer filtering no longer creates subset topographies. The explicit public `subset_topography()` utility now returns a semantic deep copy preserving retained relations and attached analysis state.
**Location:** `molsysviewer_topomt/integration.py`

`subset_topography()` copies selected features but does not preserve relations
between selected features or attached analysis substrate.

### VIEW-012: Geometry extraction and unit conversion are duplicated across renderers

**Evidence:** Strong static finding
**Tracking:** Verified
**Resolution:** Viewer-neutral payloads and final adapters now cover all active renderer geometry, including centerline tubes and rings, mouth rings, and dry-scaffold segments. Centerline stations reference tetrahedron IDs scoped by component; mouth rings reference external-link keys; scaffold edges reference canonical molecular-system atom pairs scoped by component. Cross-renderer equivalence tests cover coordinates, units, and structured identity. TopoMT final adapters now bypass MolSysViewer submanager digestion for already-normalized payloads, and the addon test suite passes with warnings promoted to errors. Direct frontend transport of arbitrary entity refs remains a MolSysViewer host proposal, not a TopoMT geometry-extraction gap.

**Category:** Technical debt with correctness risk
**Location:** `molsysviewer_topomt/render/`

Renderers independently slice coordinates, convert arrays, attach units, and
interpret atom-index spaces. This duplication has already contributed to index
and representation inconsistencies and makes new renderers easy to implement
incorrectly.

**Required correction**

Define viewer-neutral TopoMT geometry payloads with explicit units and index
spaces. Keep final MolSysViewer conversion in small shared helpers. Do not make a
viewer-side helper responsible for deciding scientific membership or semantics.

**Acceptance tests**

- Equivalent geometry sources produce identical coordinates and entity references
  across renderers.
- Payloads declare units and index spaces explicitly.
- Partial atom selections render and select the original system atoms correctly.

### TOOLS-001: `topomt.tools.features` public surface depends on import order

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** Explicit subpackage exports and isolated import coverage were added.

**Location:** `topomt/tools/features/__init__.py`,
`tests/test_tools_public_surface.py`

The public-surface test passes in the complete suite only because earlier tests
import the submodules. In isolation, `tools.features.mouths` is absent.

**Required correction**

Explicitly expose intended public subpackages and add an isolated import test in
a fresh Python process.

### TOOLS-002: Jaccard clustering fails for one feature

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** Singleton input now returns its single cluster without calling SciPy linkage.

**Location:** `topomt/tools/features/common/overlap.py`

`jaccard_overlap_clusters([[1, 2]], cutoff)` passes an empty condensed distance
matrix to SciPy linkage and raises `ValueError`.

### TOOLS-003: Channel profile geometry assumes an axis through the origin

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** Channel profile helpers now accept keyword-only `axis_point`; if
omitted, the profiling line passes through the centroid of `centers`, so
translated channels are handled consistently while existing positional calls
remain compatible.

**Location:** `topomt/tools/features/channels/profiles.py`

Radial distances were computed from the line through the origin parallel to
`axis`. A translated channel therefore received inflated radii.

### TOOLS-004: Public numerical helpers do not validate edge cases

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** Channel profiles, shortest-path indexing, Monte Carlo sphere-union
inputs, pocket ranking lengths, and mesh inputs now validate empty data, shapes,
non-finite values, sample counts, radii, and out-of-range indices with explicit
errors.

Confirmed examples were:

- empty channel profiles failed during min/max reduction;
- points exactly at the final bin edge could be omitted;
- `union_volume_monte_carlo(..., n_samples=0)` divided by zero;
- `simple_ranking()` silently truncated mismatched sequences through `zip`;
- shape and index assumptions were often left to NumPy errors.

### TOOLS-005: Generic mesh volume sums absolute per-face contributions

**Evidence:** Strong static finding
**Tracking:** Verified
**Resolution:** `_mesh_volume_area()` now computes closed-mesh volume as the
absolute value of the sum of signed tetrahedral contributions, not the sum of
per-face absolute contributions. Basic vertex/face shape, finite-value, and index
validation was added.

**Location:** `topomt/tools/geometry/meshes.py`

`_mesh_volume_area()` applied the absolute value to every triangular signed-volume contribution before summing. The standard closed-mesh formula applies the absolute value after summing signed contributions. The previous formula could overestimate volume for translated closed meshes while returning a plausible value.

### SYN-001: Synthetic builder return type depends on caller filename

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** Synthetic builders now return an explicit `SyntheticSystem` in all
caller contexts. Conversion to MolSysMT/PDB is requested through
`.to_molsysmt()` / `.to_pdb(path)`, not by caller filename.

**Location:** `topomt/dfnd/synthetic.py`

A dynamic decorator inspected the caller filename. The same function could return
`(coords, radii)` in tests or internal calls and a `MolSys` object in notebooks
or user scripts.

### SYN-002: Dynamic synthetic wrapping breaks non-builder functions

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** The module no longer wraps public callables dynamically. Builders
produce `SyntheticSystem`; numerical helpers such as `rotate()` remain plain
helpers.

**Location:** `topomt/dfnd/synthetic.py`

Every public callable was wrapped except a small exclusion list. This included
`rotate()`, whose array result was incorrectly unpacked as builder output before
the exclusion was added.

### API-001: `parse_atom_label()` raises `NameError` on invalid input

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** Invalid labels now raise the intended informative ValueError.

**Location:** `topomt/_private/atom_label.py`

The failure path references undefined variables instead of raising the intended
validation error.

### API-002: `connect_features()` does not validate argument types early

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** Both relation arguments are validated before feature lookup.

**Location:** `topomt/topography/Topography.py`

Unsupported argument types leave IDs as `None`, followed by opaque
`KeyError(None)`.

### API-003: Method error message omits supported aliases

**Evidence:** Strong static finding
**Tracking:** Verified
**Resolution:** The error message now includes the accepted fpocket4 and castp3 aliases.

**Location:** `topomt/get_topography.py`

The error message does not list every accepted method alias, including
`fpocket4` and `castp3`.

### API-004: Top-level exports are incomplete or duplicated

**Evidence:** Strong static finding
**Tracking:** Verified
**Resolution:** The v0 top-level API surface is declared in
`devguide/api_contract_v0.md` and enforced by `topomt.__all__` tests.
`get_topography` and active public modules are now listed deliberately; removed
legacy pocket stubs are not exported.

**Locations:** `topomt/__init__.py`, `molsysviewer_topomt/__init__.py`

- TopoMT imported public functions such as `get_topography` but omitted them from
  `__all__`.
- MolSysViewer-TopoMT listed `new_view` twice; that duplicate had already been
  removed.

### API-005: Public `get_pockets()` is a broken legacy stub

**Evidence:** Confirmed by inspection
**Tracking:** Verified
**Resolution:** The broken top-level `get_pockets()` / `show_pockets()` legacy
stub was removed under the v0 API policy. Pocket-like features are exposed through
`get_topography(...)` / `Topography` or explicit provider submodules.

**Category:** Bug / public API debt
**Location:** `topomt/get_pockets.py`, `topomt/__init__.py`

The top-level `get_pockets()` ignored the requested analysis, read the relative
path `static/keys.txt`, and was exported without tests or a viable runtime
contract. Its behavior was unrelated to `get_topography()`.

### API-006: Public feature quantities use inconsistent unit conventions

**Evidence:** Confirmed by inspection
**Tracking:** Verified
**Progress:** DFND now has a settled nm-internal/raw contract, explicit raw
`schema_version`/`units` metadata, and human labels convert raw nm values before
showing angstroms. CASTp/CASTP3 public promotion now converts backend Å/Å²/Å³
records to suite-standard nm quantities. Public DFND length arguments prefer
quantities; legacy bare floats in the public compatibility facade emit
`FutureWarning` and are interpreted as angstroms before nm normalization.
**Category:** Contract violation
**Location:** DFND and third-party feature-promotion adapters

Public features were populated with quantities expressed through different unit
conventions. DFND now exposes raw values in nm/nm**2/nm**3 and promoted features
as suite-standard quantities. CASTp-family adapters now promote backend Å values
as nm quantities at the public boundary. Public DFND length-input compatibility
is explicit: quantities are the intended contract, while legacy bare floats warn
and are interpreted as angstroms in the public facade.

**Required correction**

Keep the public quantity contract, the DFND raw-unit contract, and unit metadata
explicit. Normalize every adapter at the public boundary without forcing each
numerical backend to use the same internal unit. Public length arguments should
prefer quantities; bare floats are legacy compatibility and must warn before any
future stricter rejection.

**Acceptance tests**

- Equivalent values from different engines expose the same public standard units.
- Dimensionality is validated for centers, lengths, areas, and volumes.
- Raw and serialized records state their numerical units explicitly.


---

## 7. P3: Maintainability, Packaging, and CI

### QUAL-001: Runtime dependencies are absent from Python packaging metadata

**Evidence:** Confirmed by inspection
**Tracking:** Verified
**Resolution:** `pyproject.toml` now declares the audited core runtime
dependencies and optional extras. `_depdigest.py` now tracks feature-level
optional dependencies only, and lazy optional entry points are guarded with
`depdigest`. The dependency contract is covered by focused tests.
**Publication note:** Because MolSysSuite packages remain in active joint
development, final release floors for `pyunitwizard` and `depdigest` are
publication metadata, not blockers for closing this work package. Before a
public TopoMT release, the conda recipe/environment layer should mirror this
contract and floors should be set to releases containing
`pyunitwizard.conversion_factor` and array-safe `depdigest` conditional
checks.
**Location:** `pyproject.toml`, `topomt/_depdigest.py`

`project.dependencies` now reflects imports required by the public load path.
`networkx`, `scikit-image`, `scikit-learn`, `mdtraj`, and `biotite` are
classified as extras because they are lazy, gated, or backend-specific.
`nglview` and `py3Dmol` are removed from the dependency inventory because no
active imports require them.

**Release follow-up**

Keep conda packaging aligned with this contract. Before publishing TopoMT, set
the final release floors for PyUnitWizard and DepDigest to versions that
contain `pyunitwizard.conversion_factor` and array-safe `when={...}` checks.

### QUAL-002: Ruff is declared but not enforced and reports real errors

**Evidence:** Confirmed
**Tracking:** Verified
**Resolution:** First-party `topomt` and `molsysviewer_topomt` pass the critical
`F821`, `F822`, `F823`, `F841`, `B006`, and `B023` rules. The independent
`.github/workflows/ruff.yaml` workflow enforces them on relevant pushes and
pull requests.

**Location:** repository-wide

A directed Ruff run found undefined names, unsafe mutable defaults, dead
variables, and a loop-closure warning in addition to style debt.

**Required correction**

Immediately enforce correctness rules such as `F821`, `F823`, `B006`, and
`B023`; then clean first-party source and gradually enable the broader rule set.

### QUAL-003: Documentation workflow imports the wrong package

**Evidence:** Confirmed by inspection
**Tracking:** Verified
**Resolution:** The documentation workflow now imports topomt.

**Location:** `.github/workflows/sphinx_docs_to_gh_pages.yaml`

The workflow imports `pocketmt` instead of `topomt`.

### QUAL-004: Tests overuse mocks that differ from runtime contracts

**Evidence:** Confirmed
**Tracking:** Open
**Progress:** probe_centers now has a real DFNDData regression, and the corresponding legacy mock was corrected. Broader mock replacement remains open.

**Examples:** component `probe_centers`, standalone rendering

Some tests validate mocked object layouts or incorrect keywords rather than real
behavior. Prefer real small synthetic DFND topographies, strict fakes, emitted
viewer operations, repeated rendering, and fresh-process import checks.

### QUAL-005: Known scientific failures are mixed into the normal passing suite

**Evidence:** Design risk
**Tracking:** Decision required
**Location:** `tests/test_dfnd_pathological.py`

Separate correctness tests, regressions, known limitations, and exploratory
characterization. Use strict `xfail` where a correction should become visible.

### QUAL-006: Project coding instructions and source disagree

**Evidence:** Confirmed by inspection
**Tracking:** Open

Examples include widespread `from __future__ import annotations` despite the
repository instruction forbidding it, incomplete public annotations, and mixed
style conventions.

### QUAL-008: `DelaunayFlowNetwork.get_topography()` mixes too many phases

**Evidence:** Strong static finding
**Tracking:** Open
**Category:** Technical debt with scientific-change risk
**Location:** `topomt/dfnd/graph.py`

The method combines query validation, probe-state classification, graph
construction, wet and dry decomposition, external-link extraction, compatibility
views, record construction, and result assembly in one large orchestration path.
This makes scientific changes difficult to test independently and increases the
risk of inconsistent predicates across outputs.

**Required correction**

After the relevant contracts are fixed, decompose the workflow by scientific
phase with typed intermediate results and phase-level invariant tests. Do not use
an arbitrary line-count target or extract helpers that merely move mutable local
state without clarifying ownership.

### QUAL-009: Test importability depends on the invocation command

**Evidence:** Confirmed dynamically
**Tracking:** Verified
**Resolution:** pytest.ini now defines the repository root on the test import path; direct pytest collection of the affected CASTP tests passes.

**Category:** Test infrastructure bug
**Location:** `tests/methods/castp/`, `devtools/castp/`, test configuration

Direct `pytest` collection cannot import `devtools.castp` in the current
environment, while `PYTHONPATH=. python -m pytest` succeeds. The suite therefore
depends on an implicit repository-root import path that is not defined by one
canonical test contract.

**Required correction**

Choose and enforce a canonical invocation and make test-support modules
importable intentionally. Do not globally mutate `sys.path` from
`tests/conftest.py`, because that can hide installation and namespace problems.

**Acceptance tests**

- The documented canonical command collects the CASTp tests in a clean shell.
- Local and CI invocations use the same import contract.
- An isolated installed-package smoke test remains independent of repository-only
  test helpers.

### QUAL-007: Developer-guide documents contradict the authoritative object model

**Evidence:** Confirmed by inspection
**Tracking:** Open
**Category:** Documentation drift
**Locations:** `devguide/api_surface.md`, `devguide/architecture.md`,
`devguide/viewer_addon_plan.md`, `devguide/DFND/data_model_v1.md`,
`devguide/DFND/object_model.md`

The guide contains incompatible descriptions of the current architecture.
Examples include legacy `domain` and top-level `dfnd_*` vocabulary, an outdated
viewer implementation plan, inconsistent unit-boundary descriptions, and
claims of exactly two levels that obscure the real geometry-to-feature
pipeline.

**Required correction**

Declare one authoritative current contract per topic, label historical plans as
historical, and add lightweight documentation checks for retired vocabulary and
broken internal links. Resolve the conceptual questions recorded in the
companion architecture review before rewriting authoritative contracts.

---

## 8. Cross-Cutting Architectural Proposals

### 8.1. Introduce a canonical DFND query object

Create one typed immutable object containing every behavior-affecting option:
probe radius, epsilon, tolerances, transit policy, gate-intrusion policy, dry
adjacency, size/reporting policy, input policy, and radii model.

Use it in `get_topography()`, `DFNDData.at_probe()`, provenance, serialization,
visualization labels, cache keys, and tests.

### 8.2. Formalize identity and index spaces

**Progress:** The component-level contract was approved and its static identity
fields/ranking were implemented on 2026-06-06; it is authoritative in
[`DFND/component_identity_contract.md`](DFND/component_identity_contract.md).
Registry migration, contextual provenance, and external-link/motif static
identity are implemented and verified. Dynamic tracking remains pending.

Document and enforce:

- `tetrahedron_id`;
- `face_id`;
- `edge_id`;
- `component_id`;
- `component_index`;
- `size_rank`;
- `graph_label`;
- `mesh_atom_index`;
- `system_atom_index`.

Avoid using `index`, `id`, `local`, and `global` without naming the owning
space. Add construction-time invariant validation.

### 8.3. Atomic registries

**Progress:** Implemented independently for `Topography` and `Components`: unique
immutable registered IDs, validated add/replace/remove/rename, relation cleanup,
semantic copy behavior, and deterministic queries. A shared base abstraction is
deferred until it removes demonstrated duplication without obscuring their
different relation models.

### 8.4. Separate semantic data, visual selection, and render dispatch

The viewer addon should maintain one attached source topography, visual
filters/selections, deterministic render DTOs, a layer/tag registry, and
renderer-specific dispatch only at the final boundary.

### 8.5. Centralize layer and tag ownership

Every representation should register the exact tags and layers it owns.
Re-render, clear, hide, and replace operations should go through one manager.

### 8.6. Stabilize synthetic-system APIs

Replace caller-sensitive tuples with an explicit `SyntheticSystem` result:

```python
system = synthetic.hollow_sphere(...)
system.coords
system.radii
system.elements
system.to_molsysmt()
system.to_pdb(path)
```

---

## 9. Recommended Correction Sequence

### Phase 0: Freeze and characterize

- Maintain regression coverage for verified DFND-001, VIEW-001, VIEW-003,
  CORE-001, CORE-003, and the verified SYN-002 dynamic-wrapping regression.
- Add invariant checks that can run against every synthetic system.
- Record current component counts and identities before changing thresholds.

### Phase 1: Correct scientific and identity contracts

- Fix canonical face traversability.
- Validate physical query parameters.
- Formalize ID/index spaces.
- Make registry mutations atomic.
- Preserve complete query configuration in `at_probe()`.

### Phase 2: Correct viewer state and rendering

- Fix global/local index mapping.
- Keep the source topography stable in addon runtime.
- Centralize tag/layer cleanup.
- Fix `probe_centers`, graph rerendering, and standalone keyword behavior.
- Add repeat-render integration tests.

### Phase 3: Stabilize public APIs

- Replace synthetic dynamic wrapping.
- Correct isolated `topomt.tools` imports and edge cases.
- Define copy/subset semantics.
- Normalize render return objects.
- Improve errors and validation.

### Phase 4: Packaging and quality enforcement

- Declare dependencies and optional extras.
- Fix documentation CI.
- Enforce correctness-focused Ruff rules.
- Add isolated installation and fresh-process import tests.

### Phase 5: Channel skeleton scientific hardening

- The current channel result is a visualization skeleton, not a quantitative
  validated probe-center path.
- Future work: implement `widest_gate_path`, validated crossings, and channel
  profile validation against analytical synthetic systems.

---

## 9.1. Correction Campaign Progress on 2026-06-06

Completed and verified during the first correction campaign:

- WP-04 atomic feature registry;
- WP-05 atomic component registry;
- the static component-identity decision required by both packages;
- additive contextual provenance across DFND records, relations, and promoted
  features;
- exact/contextual identity for external links and motifs;
- component selectors and registry lookup by contextual/support keys.

The authoritative implementation checkpoint is
[`DFND/checkpoint_identity_provenance_registries_2026_06_06.md`](DFND/checkpoint_identity_provenance_registries_2026_06_06.md).

WP-02 query/provenance hardening is now verified. The highest-value next
engineering packages that do not require unresolved scientific decisions are the
remaining viewer and quality packages whose contracts are already explicit. Dynamic tracking is intentionally
not started until matching and lineage policy is decided.

## 10. Suggested Work Packages

Work packages are initially `Open` unless a decision gate makes them
`Decision required`. A work package is complete only when
all included findings are `Verified`, its documentation is updated, and no
listed invariant regresses on the synthetic suite.

| Work package | Kind | Findings | Depends on | Closure evidence |
|---|---|---|---|---|
| WP-00 Documentation alignment | Documentation | QUAL-007 | Architecture decisions | authoritative contracts agree; retired vocabulary check |
| WP-01 Canonical DFND traversability **(Verified)** | Contract violation | DFND-001 | None | threshold equality and graph/face invariant tests |
| WP-02 DFND query validation and provenance **(Verified)** | Bug / contract | DFND-002, DFND-003, DFND-006, DFND-007, DFND-012 | None | typed mesh/query contract, complete reprobe preservation, reporting-independent identity, selector capability tests |
| WP-03 DFND membership and face depth **(Verified)** | Design decision / bug | DFND-013, DFND-014 | Membership decision | connector disjointness, blocked dry mask, face-depth schema v2 tests |
| WP-04 Atomic feature registry **(Verified)** | Data integrity | CORE-001 to CORE-005, API-002 | Identity decision | duplicate, failed-add, rename, relation, and copy tests |
| WP-05 Atomic component registry **(Verified)** | Data integrity | CORE-006 | WP-04, identity decision | duplicate, replace, relation, and index-integrity tests |
| WP-06 Viewer atom-index mapping **(Verified)** | Bug | VIEW-001, VIEW-002 | Index-space contract | partial-selection and excluded-hydrogen tests |
| WP-07 Viewer runtime and subset semantics **(Verified)** | Contract violation | VIEW-003, VIEW-011 | Viewer ownership decision | source remains attached after every filter operation |
| WP-08 Render lifecycle **(Verified)** | Reliability | VIEW-004, DFND-008, DFND-009, VIEW-006, VIEW-007 | Render-result decision | every representation renders twice and clears cleanly |
| WP-09 Standalone and addon actions **(Verified)** | Bug / debt | VIEW-005, VIEW-009, VIEW-010 | WP-07, WP-08 | real emitted operations and action-state tests |
| WP-10 Synthetic API stabilization **(Verified)** | API contract | SYN-001, SYN-002 | None | `SyntheticSystem` contract tests and no caller-dependent wrapping |
| WP-11 Public tools hardening **(Verified)** | Bug / reliability | TOOLS-001 to TOOLS-005 | None | fresh-process imports, translation-aware profiles, validation errors, and signed mesh-volume tests |
| WP-12 Packaging, quality, and CI **(Verified)** | Quality | QUAL-001 to QUAL-006 | Stable dependency decision | dependency contract tests, optional dependency guards, and packaging/devguide alignment |
| WP-13 Channel skeleton contract **(Verified)** | Design decision / science | DFND-004, DFND-005 | Traversability and skeleton decision | `channel_skeleton`, shortest-path gate metrics, virtual mouth endpoints, viewer caller tests |
| WP-14 Public feature metrics and units **(Verified)** | Contract / decision | DFND-015, API-006 | Unit and promotion decisions | raw-unit metadata, label conversion, public input warning, CASTp promotion tests, and DFND Mouth provenance/gate-metric tests |
| WP-15 DFND orchestration decomposition | Technical debt | QUAL-008 | WP-01, WP-02, WP-03 | phase-level invariant and regression tests |
| WP-16 Test invocation and devtools imports **(Verified)** | Test infrastructure | QUAL-009 | None | direct pytest collection of CASTP devtools tests and CI-compatible `pytest.ini` import path |
| WP-17 Legacy public API cleanup **(Verified)** | API stability | API-004, API-005 | v0 API policy | `topomt.__all__` contract tests and removal of broken pocket stubs |
| WP-18 Viewer geometry boundary **(Verified)** | Architecture / reliability | VIEW-012 | Index-space, unit, and viewer-payload decisions | cross-renderer payload equivalence tests |

### 10.1. Decision gates

The following decisions block structural work and should be recorded explicitly
before implementation:

- whether wet and dry component memberships may overlap;
- ~~the distinction among query-local index, display rank, public ID, and
  trajectory lineage identity~~ — decided in
  [`DFND/component_identity_contract.md`](DFND/component_identity_contract.md);
- whether a channel skeleton should later grow into a validated probe-center
  path;
- ~~whether visual filtering operates on queries, render groups, or copied
  topographies~~ — decided in
  [`DFND/checkpoint_viewer_runtime_ownership_2026_06_14.md`](DFND/checkpoint_viewer_runtime_ownership_2026_06_14.md);
- which object owns viewer-neutral geometric representations;
- the supported unit boundary between numerical kernels and public APIs;
- the deprecation and compatibility policy for legacy public functions.

These decisions are analyzed, but not resolved, in
[architecture_review_2026_06_06.md](architecture_review_2026_06_06.md).

---

## 11. Definition of Done

The correction campaign is complete when:

- no permeable finite-transit shared face disagrees with graph adjacency;
- every ID/index space has a documented invariant and construction-time checks;
- duplicate or failed registry mutations cannot leave partial state;
- copies and visual subsets have explicit, tested semantics;
- every viewer representation can be rendered twice and cleared without error;
- viewer selections and rendered simplices identify the correct original atoms
  under partial selections and hydrogen exclusion;
- every DFND query option is validated, preserved, and behaviorally meaningful;
- synthetic builders have stable return types;
- all public tools pass isolated edge-case tests;
- package dependencies support a clean installation;
- correctness-focused Ruff checks and documentation CI are green;
- the canonical test command works from a clean shell and matches CI;
- public feature quantities follow one documented cross-engine contract;
- public API removals or return-contract changes follow an explicit deprecation
  policy.

---

## 12. Verification Commands

```bash
pytest -n 12
pytest -q tests/test_dfnd_graph_contract.py
pytest -q tests/test_dfnd_selectors.py tests/test_dfnd_data.py
pytest -q tests/test_molsysviewer_topomt_addon.py
pytest -q tests/test_molsysviewer_topomt_addon.py -W error
pytest -q tests/test_tools_public_surface.py
ruff check topomt molsysviewer_topomt --select F821,F822,F823,F841,B006,B023
ruff format --check topomt molsysviewer_topomt tests
```

Add focused commands for each work package rather than relying only on the full
suite. Use the complete suite for broad implementation changes, shared-contract
closures, release checks, or when focused coverage cannot bound the risk.

---

## 13. Related Documents

The following documents should be updated as correction work lands:

- `devguide/DFND/component_visualization_implementation.md`;
- `devguide/DFND/numerical_policy.md`;
- `devguide/DFND/residence_transit_contract.md`;
- `devguide/DFND/known_limitations.md`;
- `devguide/DFND/pathological_systems.md`.

This report is the consolidated correction backlog. Related documents should
retain deeper domain rationale, while this report tracks whether the detected
defects have been resolved.
