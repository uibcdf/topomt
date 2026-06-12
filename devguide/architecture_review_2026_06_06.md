# TopoMT and MolSysViewer-TopoMT Architecture Review

**Date:** 2026-06-06  
**Scope:** scientific object model, semantic architecture, data ownership, public
API boundaries, and implementation architecture  
**Status:** proposal and decision input; approved decisions are identified by
links to their authoritative contracts

---

## 1. Purpose

This review complements
[`code_review_2026_06_06.md`](code_review_2026_06_06.md). The code review is an
executable correction backlog. This document asks a different question: whether
the current scientific concepts and software boundaries form a coherent model
that can support future TopoMT development.

The review distinguishes:

- **strengths to preserve**;
- **conceptual tensions** that need an explicit decision;
- **implementation weaknesses** that obstruct the intended model;
- **proposed target directions**, which are not approved contracts yet.

The assessment focuses most deeply on DFND and `molsysviewer_topomt`. Other
engines were considered at their integration boundaries, not scientifically
revalidated in full.

---

## 2. Executive Assessment

TopoMT has a strong scientific core. Its most important idea is the separation
between geometric substrate, probe-dependent physical interpretation, graph
decomposition, and method-agnostic semantic features. The distinction between
probe residence and probe transit is particularly valuable and should remain a
central contract.

The conceptual architecture is currently stronger than its implementation. The
main risk is not a weak scientific premise, but the gradual creation of several
partially overlapping representations of the same entity: raw dictionaries,
typed DFND objects, public features, dynamic attributes, viewer payloads, and
copied topographies.

The intended architecture can become coherent and direct if it formalizes:

1. independent semantic axes instead of overloaded class names;
2. identity across queries, probe radii, and trajectories;
3. typed relations and provenance;
4. ownership of scientific versus visual representations;
5. immutable query and result contracts;
6. one authoritative source for each piece of data.

`molsysviewer_topomt` is correctly separated as an addon, but it currently mixes
data adaptation, scientific filtering, scene lifecycle, and interaction state.
Its long-term role should be a thin application layer over stable,
viewer-independent TopoMT queries and representation payloads.

---

## 3. Current Scientific Pipeline

The real conceptual pipeline contains several legitimate layers:

```text
molecular system and atom selection
    -> geometric substrate (DelaunayMesh)
    -> probe-dependent state and traversability (DFN)
    -> decomposition (components)
    -> internal substructure (motifs and links)
    -> method-agnostic semantic objects (Topography features)
    -> visual realizations and interactions
```

This pipeline is scientifically coherent. The statement in
`DFND/object_model.md` that there are exactly two levels should therefore be
read as two **semantic namespaces**:

- private, method-specific DFND objects;
- public, method-agnostic Topography features.

It should not imply that geometry, state, decomposition, motifs, and features
are the same abstraction level.

---

## 4. Scientific Strengths to Preserve

### 4.1. Geometry is separated from probe-dependent interpretation

`DelaunayMesh` is a probe-independent substrate, while the DFN and its
components depend on a query probe. This is scientifically correct, supports
probe sweeps, and gives a clear invalidation boundary.

### 4.2. Residence and transit are different physical questions

A probe may be able to cross a face without being able to reside in every
adjacent tetrahedron. Modeling residence capacity and gate capacity separately
prevents a common conceptual error and supports channels, connectors, and dry
barriers more faithfully.

### 4.3. Components, motifs, and public features have distinct roles

The intended ladder is useful:

- a **component** is a connected DFND decomposition object;
- a **motif** is a named internal substructure;
- a **feature** is a public, method-agnostic semantic object.

Selective promotion is appropriate. Provisional or diagnostic DFND objects do
not need to become public features immediately.

### 4.4. Boundaries and interfaces are not reduced to one family label

Treating external links, mouths, wet/dry contacts, and interfaces as relations
or descriptors avoids forcing every scientifically useful property into a
single mutually exclusive taxonomy.

### 4.5. Traceability is a first-class goal

The intended trace from public feature to component or motif, then to
simplices and original atoms, is essential for scientific auditability and
visual interpretation.

### 4.6. Synthetic systems support scientific reasoning

The synthetic systems are more than tests: they provide controlled scientific
examples for residence, transit, interfaces, topology, and pathological cases.
This practice should remain central to contract development.

---

## 5. Conceptual Questions Requiring Decisions

### ARCH-001: Clarify the meaning of the two-level model

**Current tension**

The authoritative object model says there are exactly two levels while also
describing mesh, DFN, components, motifs, and features. The intended distinction
is useful, but the wording obscures the actual analytical pipeline.

**Proposed direction**

Define two public semantic namespaces while explicitly documenting the full
pipeline of internal abstraction layers.

### ARCH-002: Separate component identity from its spatial realizations

**Current tension**

A component is described as an inseparable graph object and spatial
representation. In practice, one component can have several useful spatial
realizations: lining atoms, resident volume, alpha spheres, boundary surface,
centerline, or graph skeleton.

**Proposed direction**

Keep the component as the probe-dependent connected analytical entity. Treat
its geometries as named, derived representations with explicit provenance and
validity, rather than as one vague spatial representation.

This does not require restoring the retired word `domain`.

### ARCH-003: Model residence state and transit membership independently

**Current tension**

A non-resident connector may participate in a wet transit component while also
appearing in dry analysis. This is scientifically defensible, but a single
`side` field and one-to-one component maps imply exclusivity.

**Decision options**

- Make wet and dry decomposition memberships disjoint by definition.
- Permit overlapping analytical memberships and make every downstream mapping
  many-to-many.
- Define separate decompositions explicitly, for example residence-state
  regions and transit-network components.

**Proposed direction**

Represent residence state and transit membership as independent concepts. Do
not let the display labels `wet` and `dry` silently define incompatible
invariants.

### ARCH-004: Replace a single feature taxonomy with orthogonal axes

**Current tension**

Pocket, void, and channel are volumetric and topological entities, yet the
public hierarchy is primarily described through 0D/1D/2D feature classes and
shape labels such as concavity, convexity, boundary, and mixed.

**Proposed direction**

Describe public features through independent properties:

- support dimension: point, curve, surface, or volume;
- topographic role: concavity, convexity, boundary, interface, or neutral;
- accessibility and environment relation;
- topology: number and kind of external connections;
- morphology: pocket-like, tubular, branched, chambered, and similar labels;
- provenance and method confidence;
- dynamic state and lineage.

Stable classes should represent genuinely different contracts. Descriptors
should represent classifications that may evolve or overlap.

### ARCH-005: Introduce typed scientific relations

**Current tension**

Parent/child relations cannot directly express every relevant scientific
relationship, particularly interfaces and dynamics.

**Proposed direction**

Use typed relations such as:

- `part_of` and `contains`;
- `bounded_by` and `bounds`;
- `mouth_of`;
- `adjacent_to`;
- `overlaps`;
- `derived_from`;
- `tracks_to` or `continues_as`.

Parenthood can remain a convenient view over selected relation types, but
should not be the only relation model.

### ARCH-006: Define identity at every lifecycle scale

**Current tension**

A size-ranked component label is convenient within one result but unsuitable
as persistent identity across probe changes or trajectory frames.

**Decision status:** Resolved on 2026-06-06 by the authoritative
[`DFND/component_identity_contract.md`](DFND/component_identity_contract.md).
Static identity, contextual provenance, external-link/motif keys, and atomic
registries are implemented. Dynamic tracking remains pending.

**Approved direction**

Distinguish explicitly:

- immutable simplex identity within a mesh;
- query-local `component_index`;
- query-local display or size rank;
- human-readable `component_id`;
- public feature identity;
- cross-query or cross-frame lineage identity;
- optional structural fingerprint used for matching.

No single identifier should be expected to satisfy all these roles.

### ARCH-007: Define promotion and provenance as many-to-many

**Current tension**

The documents correctly state that one component can produce a feature
subgraph, but current promotion paths and `source_id` fields tend toward simple
one-to-one provenance.

**Proposed direction**

Represent promotion through explicit provenance records or typed relations.
One feature may derive from several components or motifs, and one component may
produce several public features.

### ARCH-008: Establish one unit boundary

**Current tension**

Public MolSysSuite conventions, numerical kernels, raw DFND records, and
viewer payloads do not consistently describe whether values are quantities or
bare floats and which units those floats use.

**Proposed direction**

Choose and document:

- the canonical public quantity contract;
- the canonical internal kernel unit;
- conversion points;
- units stored in serialized or raw records;
- unit metadata required by viewer payloads.

Bare numerical kernels are reasonable, but their unit contract must be
explicit and tested.

### ARCH-009: Generalize the external environment model

**Current tension**

A single global `OCEAN` node is a practical first model, but periodic systems,
membranes, separate compartments, and interfaces may contain distinct external
environments.

**Proposed direction**

Keep the simple default while allowing explicit environment entities or
contexts in future contracts. Components should connect to identified
environments, not depend permanently on one hard-coded global concept.

### ARCH-010: Define molecular-system ownership and cache invalidation

**Current tension**

A result retains references to a molecular system while also caching geometry,
index mappings, graph state, components, and promoted features. It is not clear
what happens if coordinates, topology, radii, selection, or structure index
change after construction.

**Proposed direction**

Treat an analysis result as derived from an explicit molecular-system snapshot
or revision. Record every input that determines validity and define which
changes invalidate mesh geometry, probe-dependent state, promotion, metrics,
and viewer payloads. Prefer immutable results or explicit recomputation over
silent mutation of cached state.

### ARCH-011: Make determinism and reproducibility contractual

**Current tension**

Component ordering, display IDs, set iteration, stochastic estimators, backend
versions, and numerical ties can change outputs without changing the underlying
scientific system. Provenance currently records only part of that context.

**Proposed direction**

Define deterministic ordering and tie-breaking for canonical records. Record
algorithm version, backend, dependency versions where relevant, query, units,
input fingerprint, and random seed. Mark stochastic metrics explicitly and
report their uncertainty.

### ARCH-012: Represent numerical uncertainty and marginal states explicitly

**Current tension**

DFND already recognizes tolerances and marginal states, but public features and
cross-engine outputs tend to present classifications and metrics as exact. Near
thresholds, small coordinate or numerical changes can alter topology.

**Proposed direction**

Keep marginality and confidence as first-class result metadata. Distinguish
exact geometric predicates, tolerance-policy outcomes, estimated metrics, and
heuristic classifications. Public promotion should preserve relevant confidence
and uncertainty instead of collapsing them into definitive labels.

### ARCH-013: Define a common capability contract across engines

**Current tension**

`get_topography()` provides one entry point, but engines expose different
objects, metrics, units, provenance depth, and confidence. A common `Feature`
class alone does not establish semantic comparability.

**Proposed direction**

Each engine adapter should declare capabilities and metric semantics. Define a
small guaranteed feature contract and named optional capabilities such as
mouths, alpha spheres, analytical volume, transit graph, dynamic tracking, and
interface descriptors. Never equate metrics from different engines solely
because they share an attribute name.

### ARCH-014: Define public API evolution and deprecation policy

**Current tension**

Legacy functions, provisional DFND records, experimental viewer calls, and
public feature attributes currently coexist without one stability policy. This
makes cleanup risky and encourages accidental reliance on implementation
details.

**Proposed direction**

Classify APIs as stable, provisional, experimental, or internal. Require
deprecation warnings, migration notes, and a removal window for stable public
APIs. Version serialized schemas independently from Python object internals.

---

## 6. Proposed TopoMT Target Architecture

The following is a direction for discussion, not an approved class design.

```text
TopographyResult
├── molecular_system reference and selection mapping
├── analyses
│   └── dfnd: DFNDResult
├── features: atomic feature registry
├── relations: typed relation registry
└── provenance: promotion and source records

DFNDResult
├── query: immutable DFNDQuery
├── mesh: immutable DelaunayMesh
├── state: probe-dependent node/face state
├── decompositions
│   ├── transit components
│   └── residence/dry analytical components
├── motifs and links
└── representation providers
```

Key properties of the target direction:

- `Topography` behaves as an analysis result and semantic catalog, not an
  arbitrary mutable bag of engine attributes.
- Every query result is explicit and reproducible.
- Raw records are immutable provenance or serialization data, not a second
  mutable source of truth.
- Typed objects expose validated views over canonical data.
- Public features reference source objects through typed provenance.
- Registries are atomic and maintain validated indexes. This is now implemented
  for `Topography` and DFND `Components`; a shared base abstraction remains
  intentionally deferred until it removes demonstrated duplication without
  obscuring their different relation models.
- Scientific representations are requested by name and generated from canonical
  data.

### 6.1. Queries and results

A typed immutable `DFNDQuery` should contain every behavior-affecting option.
A query should produce a result with a clear identity and provenance. Filters
such as minimum component size should be identified as decomposition,
reporting, promotion, or visualization filters rather than sharing one
ambiguous parameter.

### 6.2. Raw data and serialization

Raw output remains useful for audit and debugging, but should have a versioned
schema. It should not compete with typed objects as a mutable source of truth.
The project should define which fields are canonical, derived, cached, or
presentation-only.

### 6.3. Feature classes and descriptors

Avoid creating one subclass for every scientific adjective. Introduce classes
when behavior or invariant differs. Use typed descriptors for morphology,
accessibility, environment, interface status, confidence, and dynamics.

### 6.4. Engine capabilities and comparable metrics

A method-agnostic `Topography` should expose a small guaranteed semantic core,
while each analysis declares optional capabilities and precise metric
definitions. Comparable names must not imply comparable scientific quantities
unless their contracts agree. Cross-engine comparison should operate through
explicit metric semantics and units.

### 6.5. Static results, collections, and trajectories

A per-frame topography, a probe-radius sweep, and a trajectory are different
objects. Collections should reference immutable instantaneous results and store
their own cross-result relations, matching evidence, lineage, events, and time
series. A query-local component ID must not become a temporal identity by
accident.

---

## 7. MolSysViewer-TopoMT Assessment

### 7.1. Strengths to preserve

- The addon is separated from TopoMT core.
- It exposes several scientifically meaningful views of the same analysis.
- Runtime state is associated with a view rather than stored globally.
- Hover, selection, and context actions aim to preserve simplex and component
  provenance.
- Renderers are already separated into representation-oriented modules.

### 7.2. Current architectural tension

The addon currently combines four responsibilities:

1. adapting and normalizing TopoMT data;
2. deciding some scientific filtering and geometry derivation;
3. managing scene objects, tags, and layer lifecycle;
4. managing interaction, selection, and panel state.

This coupling makes representation behavior inconsistent and ties the viewer to
internal DFND layouts.

### 7.3. Proposed viewer boundary

TopoMT should provide viewer-independent representation payloads or query
results. The addon should translate those payloads into MolSysViewer scene
objects and manage interaction.

```text
TopoMT analysis
    -> entity query
    -> viewer-neutral representation payload
    -> MolSysViewer renderer
    -> render group and interaction bindings
```

The boundary should ensure that the viewer does not decide scientific
classification, component membership, or index-space conversion.

### 7.4. Separate geometry source from visual style

The current word `representation` mixes scientific realization and styling.
These should be independent:

```text
geometry_source = graph | residence_spheres | alpha_spheres | accessible_volume | lining_surface
style = faces | edges | points | colors | opacity | labels
```

This makes it possible to render the same geometry consistently with different
styles and avoids duplicating scientific extraction logic across renderers.

### 7.5. Stable entity and render references

Interactions should use stable typed references, conceptually similar to:

```text
EntityRef(analysis_id, entity_kind, entity_id)
RenderGroup(render_id, source_query, tags, layers, entity_refs)
```

This would make repeated rendering, clearing, hover, context menus, and multiple
probe results deterministic.

### 7.6. Filters are not copied analyses

Selecting components or features for display should create a visual query or
filter. It should not replace the attached source topography with a partial
copy. A view should be able to hold several render groups derived from one or
more immutable analysis results.

### 7.7. Unified render result

Every public rendering function should return a common result containing:

- representation and style parameters;
- selected scientific entities;
- generated layers and tags;
- warnings and omitted entities;
- clear, update, and visibility operations.

---

## 8. Software Engineering Assessment

### 8.1. What is adequate today

The codebase is suitable for an active scientific research project and provides
substantial executable functionality. Positive engineering characteristics
include:

- extensive synthetic and regression-oriented tests;
- unusually detailed developer documentation;
- growing separation of DFND core, selectors, components, and viewer renderers;
- pragmatic use of NumPy and SciPy;
- reuse of probe-independent geometry;
- explicit attention to numerical policy and traceability.

### 8.2. What is not yet adequate for a stable scientific API

The implementation is not yet robust enough to treat DFND and its viewer
integration as stable production contracts. Principal causes are:

- registry operations that do not enforce atomic invariants;
- multiple mutable or duplicated sources of truth;
- raw dictionaries and stringly typed fields where schemas are needed;
- dynamic attributes that hide object contracts;
- scientific kernels mixed with orchestration and promotion;
- broad exception swallowing in viewer paths;
- incomplete validation and error taxonomy;
- tests that sometimes depend on import order or unrealistic mocks;
- absent package dependency declarations and incomplete CI enforcement;
- no explicit versioned serialization contract;
- documentation that describes several incompatible architectural moments;
- no explicit cache invalidation or molecular-system snapshot contract;
- no unified determinism, uncertainty, or cross-engine capability contract.

### 8.3. Implementation direction

The project does not need a wholesale rewrite. The safer route is incremental:

1. establish invariants and regression tests;
2. introduce typed immutable query and identity contracts;
3. make registries atomic;
4. define one source of truth and version raw schemas;
5. move scientific extraction behind stable queries;
6. reduce the viewer to payload translation and scene lifecycle;
7. migrate public APIs with explicit compatibility policy.

---

## 9. Documentation Coherence

Several documents represent different architectural moments and currently read
as simultaneous contracts. The most important alignment work is:

- clarify the two-semantic-namespace wording in `DFND/object_model.md`;
- remove or label retired `domain` and top-level `dfnd_*` descriptions;
- align `DFND/data_model_v1.md` with the authoritative component-to-feature
  ladder;
- mark `viewer_addon_plan.md` as historical or update it to the implemented
  addon;
- define the public and internal unit boundary consistently;
- distinguish implemented behavior, intended target, and speculative proposal
  in every architecture document.

Documentation should use explicit status banners such as `authoritative`,
`implemented snapshot`, `proposal`, `historical`, or `superseded`.

---

## 10. Decisions to Record Before Structural Refactoring

The following decisions deserve individual decision records:

| Decision | Why it blocks work |
|---|---|
| Component identity and trajectory lineage | static identity, contextual provenance, and atomic registries implemented; dynamic matching and lineage policy remain pending |
| Residence state versus transit membership | determines wet/dry decomposition and coast attribution |
| Feature axes and class policy | determines public ontology and promotion |
| Typed relations and provenance | determines Topography registry architecture |
| DFND query and result ownership | determines caching, reprobe, and serialization |
| Unit boundary | determines every numerical and public data contract |
| Viewer-neutral representation API | determines TopoMT/viewer coupling |
| Render-group lifecycle | determines repeated rendering and interaction state |
| Centerline scientific meaning | determines whether reported paths are quantitative |
| Environment and OCEAN model | determines future PBC and compartment support |
| Molecular-system ownership and invalidation | determines correctness of every cached result |
| Determinism and reproducibility | determines stable records, comparisons, and auditability |
| Uncertainty and marginal-state propagation | determines scientific interpretation near thresholds |
| Cross-engine capabilities and metric semantics | determines valid method-agnostic comparisons |
| API stability and deprecation | determines safe cleanup and migration |

No decision should be hidden inside an unrelated bug fix.

---

## 11. Recommended Architecture Sequence

### Stage A: Preserve correctness while deciding contracts

- Fix isolated confirmed bugs that do not predetermine open architecture choices.
- Add invariant and characterization tests.
- Record the blocking decisions above.

### Stage B: Stabilize identity, queries, and registries

- Introduce explicit index-space and identity contracts.
- Introduce an immutable complete DFND query.
- Make feature and component registries atomic.
- Define typed relations and provenance direction.
- Define molecular-system snapshot ownership and cache invalidation.

### Stage C: Stabilize scientific data ownership

- Define canonical versus derived fields.
- Version raw and serialized records.
- Expose named scientific representations through stable queries.
- Align promotion with many-to-many provenance.
- Declare engine capabilities, metric semantics, uncertainty, and determinism.

### Stage D: Refine viewer integration

- Introduce viewer-neutral representation payloads.
- Separate source analysis, filters, render groups, and interaction state.
- Normalize render return values and lifecycle.

### Stage E: Align and publish contracts

- Update authoritative developer documentation.
- Define API stability and deprecation policy.
- Publish canonical test, reproducibility, and result-versioning contracts.
- Enforce packaging, Ruff, docs, and focused typing checks in CI.

---

## 12. Non-Goals of This Review

This review does not:

- choose the final public class hierarchy;
- approve a specific serialization format;
- decide whether overlapping wet/dry membership is canonical;
- redefine the scientific formulas for residence or gate capacity;
- establish parity of every external engine;
- require a rewrite of working code;
- treat every proposal as a defect.

Its purpose is to expose the decisions required to keep future implementation
scientifically coherent and technically maintainable.

---

## 13. Overall Verdict

TopoMT's central scientific architecture is good and worth preserving. The
geometry-to-DFN-to-component-to-feature direction is coherent, and the explicit
separation of residence and transit gives the project a strong foundation.

The architecture is not yet as direct as it should be. Static identity and
contextual provenance are now explicit, but typed relations, derived
representations, dynamic lineage, and data ownership remain partially implicit. The implementation is appropriate for research and active hardening,
but not yet adequate as a stable scientific platform without the correction
work and decisions documented here.

`molsysviewer_topomt` is a valuable functional addon, but should evolve toward a
thin rendering and interaction layer over stable TopoMT scientific queries. The
next structural changes should therefore prioritize contracts and boundaries,
not additional ad hoc representations.
