# Topography conceptual contract

Date: 2026-09-30. Status: **accepted conceptual direction; runtime adoption pending**.
Decision owner: [#59](https://github.com/uibcdf/topomt/issues/59).
Implementation gates: [topography_implementation_route.md](topography_implementation_route.md).

This is the normative public semantic direction for new Topography work. It
does not announce new Python classes, signatures, serialized schemas, or a
change to existing behavior. It supersedes conflicting public-model directions
in `architecture.md` and the June architecture review. DFND's mathematical,
numerical, input, and query contracts retain their own authority. Historical
checkpoints describe their recorded revision, not current release readiness.

Scheduling update (2026-10-01): initial provider output and viewer delivery is
complete; the user has selected [joint DFND/Topography audit and work](DFND/audit_topography_2026_10_01.md).
Runtime adoption remains pending. Broader provider fidelity stays paused.

Delivered consumer boundary: [provider-specific pocket outputs](provider_pocket_output_checkpoint.md).
Their provisional contracts preserve original semantics and shared pocket
access without waiting for DFND consolidation or the complete public runtime
gates. They are evidence for future Topography integration, not canonical
feature promotion merely because the provider calls a result a pocket.

## 1. Governing decision

**DFND is the native semantic reference; Topography is the public scientific
model.** DFND grounds the distinctions between geometry, identity, observables,
classification, accessibility, boundaries, and internal regions. A public user
can work with these concepts without knowing a Delaunay graph, wet/dry node,
component, motif, or OCEAN.

The implementation-specific substrate remains under `topography.dfnd`.
Third-party methods adapt their own results to the public model with explicit
evidence and capabilities. They need not implement DFND's substrate. A local
reimplementation of a third-party method retains that method's identity and
definition; it does not become DFND by running inside TopoMT.

The governing DFND references are the [object model](DFND/object_model.md),
[kernel/catalog decision](DFND/taxonomy_architecture_decision.md),
[feature catalog](DFND/feature_catalog.md),
[identity contract](DFND/component_identity_contract.md),
[mesh/query contract](DFND/checkpoint_query_contract_2026_06_14.md),
[interface analysis](DFND/interfaces.md), and
[metrics contract](DFND/metrics_contract.md).

## 2. Scientific entities and responsibilities

The following names identify concepts, not committed Python class names.

| Entity | Responsibility | Boundary |
| --- | --- | --- |
| Analysis context | Identifies input coordinate/topology snapshots, selections, atom maps, method/backend/version, parameters, and policies. | A live molecular-system reference alone is insufficient provenance. |
| Feature | A public topographical finding with identity, support references, classification evidence, and provenance. | Molecular selections and raw engine records are not automatically features. |
| Spatial support | Declares the geometry a finding or evaluation refers to and how it can be recovered. | A lining-atom set is not a complete spatial region. |
| Molecular participant | A named, contextual reference to selected atoms supplied by MolSysMT. | It is neither a new molecular topology nor a DFND dry bank. |
| Scientific relation | A typed connection with validated endpoints, context, definition, and supporting evidence. | An A–B edge alone does not realize an interface spatially. |
| Evaluation | A defined observation or calculation over specified features/supports/participants in a characterization context. | Its value is not an intrinsic property of every occurrence of the feature. |
| Classification | A catalog interpretation justified by observations and a versioned policy, including maturity and relevant margins. | The human name and Python subclass do not establish geometric identity. |
| Provenance | Recoverable source records and derivations, including promotion and independently calculated quantities. | Raw records are evidence, not a second editable canonical model. |

Topography owns a coherent semantic result and its feature registry. Future
participant, relation, and evaluation registries compose with it. The existing
Mapping behavior and feature access remain compatibility requirements.
Trajectories, probe sweeps, and comparisons collect contextual results; they
carry cross-result correspondences rather than making one result mutable along
those axes.

## 3. Spatial support and representation

A support declaration identifies its kind, coordinate/input context, available
primitives, recovery path, and completeness. Possible realizations include
sites, point sets, surfaces, boundary loops, and volumetric regions. Multiple
representations may derive from the same canonical support. A rendered mesh is
not automatically canonical analysis geometry.

DFND support can reference exact atom-defined tetrahedra, face clusters, or
validated subregions. Provider support can reference that provider's sites,
triangulation, region decomposition, or original record. An atom-only export
declares spatial reconstruction unavailable; it must not receive a fabricated
exact-region identity or geometry-dependent capability.

Exact identification of tetrahedral support does not imply an exact physical
volume. A volume definition also specifies resident/connectors, atomic exclusion,
radii/probe convention, and numerical accuracy. Recovery and measurement
capabilities remain distinct.

Keep these roles separate:

- **Structural support:** the primitives that define the region or boundary.
- **Delimiting atoms:** `atom_indices`, with their declared lining/tangent role.
- **Probe-accessible atoms:** the interaction surface for a particular probe.
- **Contacted atoms/sites:** the subset selected by a particular contact rule.

DFND's `accessible_atom_indices` includes the lining and past-beach atoms. This
is a probe-accessibility statement, not proof that an arbitrary ligand contacts
every listed atom. Evaluations must declare which support/atom role they use.
Do not call a loose neighborhood query geometric feature membership.

The legacy `dimensionality` indexes (0D/1D/2D) remain separate from the geometric
dimension of a particular realization. A Pocket may have a 3D region and a 2D
boundary; a Mouth may have an aperture patch and a rim. No dimension/class
migration is authorized solely by this distinction.

## 4. Identity, classification, and promotion

Distinguish four identities:

1. **Registry identity:** the human-addressable `feature_id` within Topography.
2. **Source occurrence:** the exact native result or provider run and source
   object that produced the finding.
3. **Structural support:** exact recoverable primitives on a compatible
   atom/coordinate substrate, when available.
4. **Correspondence:** evidence relating occurrences across queries, frames,
   poses, systems, or providers. It is not inferred from equal display IDs.

For DFND, `support_key` hashes the sorted collection of atom-defined tetrahedra;
the full support remains recoverable. `component_key` combines result context,
side, and support. It excludes a catalog family/name. Changing a probe changes
contextual identity even when support stays equal. Reclassification by a catalog
policy does not itself change the source geometric support.

For a provider lacking exact region support, identify its source occurrence
honestly. Neither equal atom sets nor equal pocket numbers prove equivalence to
a DFND region. Cross-system atom correspondence requires an explicit mapping;
the current same-order atom-index substrate is not universal atom identity.

Classification records preserve the reported provider label separately from
TopoMT's inferred or canonical interpretation. A native canonical catalog
assignment requires its defining observations. If an adapter cannot establish
them, it retains the reported label and declares that limitation. Existing
Pocket-like imports need an explicit compatibility view during adoption, rather
than silently acquiring DFND pocket predicates.

Native confidence/marginality is per relevant output and threshold; it is not a
universal probability that the site is biologically functional. Preserve
canonical, provisional, experimental, and diagnostic maturity where applicable.

Promotion is a recorded derivation, potentially many-to-many: a component and
its validated substructures can yield a feature subgraph; an interface can
assemble several supports. Motifs remain native objects until promotion defines
public support and invariants. Passing raw motif dictionaries through dynamic
attributes is not that promotion contract. Add feature classes only when their
invariants or behavior justify them; adjectives do not require subclasses.

## 5. Molecular participants and geometric banks

A participant refers to an input snapshot and a resolved MolSysMT selection.
Retain the selection expression, syntax, selected atom identities/order, and
mapping. A participant may be a whole molecule, chain, domain, small molecule,
or a user-defined region. Receptor and ligand are contextual roles; neither is
a universal participant type. The general vocabulary does not use `binder`;
AlphaSpace2 may retain it at its provider boundary and in compatibility calls.

Separate biological membership from geometric incidence:

- A tightly contacting dimer can form one DFND dry bank.
- One molecular participant can contribute to several geometric banks/regions.
- One bank can contain contributions from several molecular participants.
- A delimiting atom can support several features or banks simultaneously.

Preserve overlapping geometric membership and its roles. An explicit
largest-bank-wins assignment is a derived partition for a consumer that needs
one; retain the shared-membership evidence. Overlapping user selections must
also declare how counts or unions are evaluated.

Record the participant-definition policy. Geometric dry-contact counts and
molecular-participant counts remain distinct quantities. A fallback from bank
labels to molecule/chain labels cannot silently change the meaning of a count
or the criterion attached to `is_interface`.

## 6. Relations and spatial interfaces

Relations carry a kind, typed endpoints, analysis/characterization context,
definition, evidence, and provenance. Participant and feature identifiers occupy
distinct namespaces. Their endpoint arity and direction are part of the kind.

Initial semantic kinds include `part_of`, `bounded_by`/`mouth_of`, adjacency,
overlap, and derivation. These are concepts awaiting concrete schema decisions.
Containment is acyclic; geometric adjacency can be symmetric; a measurement's
target-to-participant direction is explicit. Cross-result correspondence belongs
to a comparison/collection context. Do not apply containment rules to every edge.

The existing child/parent links remain a compatibility view for their supported
boundary and point relationships. They do not already support 2D subregions or
arbitrary relations. General containment must therefore not be implemented by
passing a chamber feature to the existing dimension-restricted connector.

An **interface association** identifies two or more participants and its
criterion. An **interface realization** localizes the associated geometry:
participant-facing patches, a separating wet region when present, contact
boundaries, or another supported realization. Several realizations can belong
to one association. Whole-component multi-participant lining is useful evidence,
but is not sufficient to assert a crisp localized interface patch.

Participant registration alone does not establish an interface. Distinguish a
user-declared association from an inferred association with criterion-satisfying
evidence; neither establishes a localized realization by itself. Bank-based and
molecular criteria retain separate definitions, thresholds and outcomes.

Keep two compatible catalog uses:

- Interface status is an orthogonal descriptor of a Pocket, Void, Channel, or
  other feature. The primary geometric classification remains intact.
- A mixed Interface feature may assemble localized supports when native
  promotion and public invariants are established. It is not created merely
  because two endpoint selections exist.

Explicitly represent unlocalized associations and unavailable measurements.
Neither two facing banks nor a tight molecular contact guarantees a bounded
wet region. Buried interfaces need no mouth; bare interfaces need no promoted
cavity. Do not invent region volume for a contact-only realization.

Wet/dry wall contacts, molecular A–B contacts, and wet/wet constrictions are
different relations. Preserve DFND's shore/beach distinction and solid septum
versus empty-space constriction. The native interface thresholds and molecular
contact thresholds are named policies, not universally interchangeable rules.

## 7. Contextual contact and occupancy evaluations

Separate the geometry query from characterization of its result:

```text
geometry(A, query) -> reference feature F
characterize(F, participant B, definition, pose) -> evaluation
geometry(A union B, query) -> assembly features G
```

F and G need not have equal support, identity, or classification. A comparison
can relate them with evidence. Moving B changes a reference evaluation; it
changes the geometry substrate when B is included in the assembly input.

A completed evaluation for pose B0 remains valid for that recorded pose. Moving
to B1 prevents reuse as a current-pose result and requires a new evaluation or
an explicit not-computed state; it does not rewrite historical values or inputs.

An evaluation records target feature/support, participant(s), referenced input
frames and coordinate alignment, definition/version, algorithm, parameters,
units, value state, uncertainty/maturity, and provenance. Separate original
provider results from independent reproductions. A coordinate transform is
recorded; it must not overwrite the input snapshot. Unsupported periodic or
multi-frame conventions require a declared capability or explicit rejection.

The following quantities are distinct:

| Quantity | Required meaning |
| --- | --- |
| Atomic/site contact | A stated distance/radius or other contact predicate on declared supports. |
| Contacted-site weighted volume | Sum of site weights/volumes whose contact predicate is satisfied. |
| Geometric occupied volume | Intersection of a declared reference region with a declared participant volume model. |
| Occupied fraction | A stated numerator divided by a stated reference measure. |
| Buried/contact surface area | A stated surface model and decomposition, not a distance-based proxy. |

For geometric volume, a possible definition is
`vol(reference_region intersect union(participant_vdw_balls))`; both the region
and the volume model must be justified. Multiple participants use an explicit
union or attributed overlap decomposition. Summing individual volumes can
double-count shared occupied space.

AlphaSpace2 `occupiedSpace` sums alpha-site volumes marked by binder contact;
its occupancy divides that sum by pocket space. Reproducing that definition is
valid provider parity, not a geometric-intersection calculation. DFND's
`occupancy_grid` represents sampled empty solvent space after atom exclusion;
it is not the same occupancy quantity. An accessible-volume upper bound must
not silently become an exact occupancy denominator.

States distinguish a computed zero, unavailable capability, not computed,
undefined quantity (including a zero denominator), and failed calculation.
Normalized undefined values do not become zero; retain the untouched provider
representation as evidence. A normalized fraction declares its scale and
domain; percentages and fractions are not interchangeable without conversion.

Evaluations can target validated subregions, not only whole components. A large
connected concavity may contain several functional sites. Chamber/site promotion
must establish support and stability before generic public evaluation uses it.
Legacy scalar attributes remain compatibility projections only when their
definition and selected evaluation are unambiguous.

## 8. Provider admission, capability, and provenance

A capability declaration identifies the available operation, its support kind,
definition/model, supported inputs, and maturity. Declared availability is
separate from result value state and from evidence that a particular backend is
currently installed/reachable. Missing capability is not an empty feature set.

| Source | Public contribution | Admission obligation |
| --- | --- | --- |
| DFND | Grounded regions/boundaries, classification evidence, context and native support. | Preserve query, support, margins, and promotion provenance. |
| fpocket | Reported pockets, alpha spheres, atom mappings and descriptors. | Preserve sphere selection and provider-specific scores/surface definitions. |
| Pocketeer | Reported clustered sites and per-sphere descriptors. | Preserve filtering/order and the exact descriptor support. |
| AlphaSpace2 | Alpha/beta sites, reported pockets, contact-weighted evaluations. | Declare site-volume/contact semantics and additional participant input. |
| CASTp/CASTpFold | Reported regions and surface/mouth aggregates. | Preserve surface model and aggregate multiplicity; one row is not necessarily one Mouth. |
| pyCASTA | Reported region membership and descriptors. | Preserve atom/tetrahedron index roles and original representative-point/score definitions. |

These are semantic obligations, not claims of complete current provider parity.
Provider labels may remain reported-only; inferred classifications are separate
derivations. Do not fabricate a transit graph, individual mouths, exact region,
or canonical geometric measure when exported evidence is insufficient.

`ProviderRun` and `ExternalMeasurement` are existing building blocks. General
native and independently calculated evaluations need equally explicit
definition and provenance; do not force them into an `external_only` record.
Preserve original input/output artifacts, source identities, versions,
parameters, units, maps, checksums, and derivations. Backend execution and method
ownership remain separate axes under the existing third-party ADR.

Physical public quantities use PyUnitWizard. Engine magnitudes require explicit
unit/index-space conversion. Compare measurements only after support, probe,
radii/surface model, definition, algorithm accuracy, and inputs are compatible.
Scientific parity, adapter field preservation, and native DFND validation have
separate gates. Optional runtimes remain lazy DepDigest/SMonitor boundaries.

## 9. Ownership, invalidation, and registry integrity

Analysis data derives from identified input snapshots. A later mutation of a
live MolSysMT object cannot silently retarget a completed result. Concrete
snapshot/revision storage and serialization are implementation-gate decisions.
Canonical records are immutable or changed through validated registry operations;
raw output, derived views, and render caches cannot compete as sources of truth.

| Change | Required effect |
| --- | --- |
| Input coordinates, geometry atom population, radii or mesh policy | New geometry context and affected results. |
| DFND probe/transit/numerical query | New result context; reusable mesh where permitted. |
| Reporting filter or display label | No change to geometric support/source identity. |
| Catalog threshold/policy | New classification derivation; retain geometry provenance. |
| Participant grouping or contact/occupancy definition | New relation/evaluation context; do not rebuild unchanged reference geometry. |
| Partner pose | New reference evaluation; new substrate if the partner is part of geometry input. |

Atomic registration, replacement, rename, removal and copy cover all owned
indexes and references. Reject incompatible or dangling endpoints. A rename
updates addressable references without rewriting source artifacts. Removal
must have a declared reject/cascade policy. A detached copy must not refer back
to the original registry. Extending registries must preserve today's atomic
operations instead of attaching unvalidated parallel dictionaries.

## 10. Acceptance scenarios and ecosystem boundaries

| Scenario | Required interpretation |
| --- | --- |
| Tight A–B dimer, one dry bank | Two molecular participants remain distinguishable; a bank-only interface criterion cannot imply absence of a molecular interface. |
| Buried interface void | Interface characterization does not require a Mouth. |
| Bare contact without bounded wet space | Keep association/patch evidence; no invented cavity or cavity volume. |
| Three participants and shared lining atoms | Preserve arity and overlapping roles; declare union/count attribution. |
| Large concavity with a localized chamber/site | Evaluate the validated subregion; do not assume the entire component is one site. |
| Same lining atoms, different tetrahedral support | Different exact support remains distinguishable. |
| Feature changes catalog name across probe/frames | Preserve context and correspondence evidence; display names are not tracks. |
| Reference receptor versus occupied assembly | Distinct geometry contexts, with explicit comparison if available. |
| AlphaSpace2 partial/zero contact and zero denominator | Preserve its formula, zero versus undefined states, and original versus independent calculation. |
| CASTp row aggregates multiple openings | Preserve multiplicity; no fabricated single-mouth realization. |
| Unsupported support/capability, moved partner, copy/rename/remove | Explicit availability/invalidation and coherent owned references. |

MolSysMT owns topology, selections, molecular coordinates, generic molecular
contacts and surface observables. TopoMT owns topographical supports,
classification, feature-specific relations/evaluations, and engine conversion.
Array-only computational geometry can remain in TopoMT/shared geometry helpers.

Surface chemistry is an orthogonal annotation fed by molecular chemistry; it
does not change a feature's topology. DockingMT can consume regions/evaluations
for pose generation or docking interpretation; PharmacophoreMT can consume
geometry/chemical annotation for its own models. This decision does not move
those packages' responsibilities into Topography or require viewer work.
