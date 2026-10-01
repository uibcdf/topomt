# Topography conceptual-contract implementation route

Date: 2026-09-30. Status: **planned; runtime gates remain open**.
Normative decision: [topography_conceptual_contract.md](topography_conceptual_contract.md),
recorded by [#59](https://github.com/uibcdf/topomt/issues/59).
This broad route lives outside the report queues; its bounded work has owning
issues. Closing the conceptual decision does not complete these runtime gates.

Scheduling update (2026-10-01): the user has selected joint DFND/Topography
work, starting with [the audit and roadmap](DFND/audit_topography_2026_10_01.md).
The next implementation sequence is #74's bounded copy correction and #60's
ownership/context/support slice, with numerical/reference validation #75/#76.
The provider-output delivery below is historical and remains independently
usable; broader provider work is paused. No runtime gate is closed by this audit.

Scheduling update (2026-09-30): these are deferred public-model gates, not global
prerequisites for external results. The current priority is
[provider-specific pocket outputs](provider_pocket_output_checkpoint.md), #65.
Its provisional contracts reuse only the needed existing adapter evidence;
they do not claim canonical Topography admission or consolidate DFND.

## 1. Starting evidence

| Area | Implemented foundation | Remaining public contract |
| --- | --- | --- |
| Topography registry | Mapping, feature indexes, atomic add/replace/rename/remove/copy. | Context/support ownership and coherent participant/relation/evaluation references. |
| DFND geometry/query | Frozen mesh configuration/query, contextual keys, recoverable tetrahedron/face support. | Neutral public references and snapshot/invalidation obligations. |
| DFND naming | Derived topology family and catalog-based promotion; accessible atoms and interface descriptors. | Formal classification/support descriptors and explicit native-versus-provider admission. |
| Hierarchy | Dimension-restricted 0D/1D children of 2D features. | Typed relations, 2D subregion containment, interface associations and supported realizations. |
| Interfaces | Bank-based promotion and explicit-label extraction prototype. | Public molecular participant integration; localization and mixed-feature promotion where justified. |
| Provider evidence | Recoverable ProviderRun artifacts and ExternalMeasurement definitions/units. | Capability declarations and generalized native/independent evaluations. |
| Dynamics | Pairwise matching and track/event helpers in `dfnd/lineage.py`. | Public collection ownership, correspondence policy and scientific validation. |

Code evidence: `topomt/topography/Topography.py`, `topomt/features/BaseFeature.py`,
`topomt/dfnd/api.py`, `components.py`, `config.py`, `identity.py`, `lineage.py`,
and `topomt/provider_output.py`. Reading those modules establishes implementation
presence, not a passing current product matrix. Older prose saying the entire
kernel/catalog refactor or all lineage code is absent is not current evidence.

## 2. Bounded gates and dependencies

| Gate | Owner | Depends on | Closure evidence |
| --- | --- | --- | --- |
| G0: conceptual decision | [#59](https://github.com/uibcdf/topomt/issues/59) | Repository/issue review | Normative contract, adversarial scenarios, discoverable documentation and checked reporting lifecycle. |
| G1: analysis context and spatial support | [#60](https://github.com/uibcdf/topomt/issues/60) | G0 | Typed/schema decision, native and incomplete-provider examples, identity/invalidation and compatibility tests. |
| G2: participants and typed relations | [#61](https://github.com/uibcdf/topomt/issues/61) | G1 | Molecular/bank distinction, endpoint validation, overlapping incidence, honest interface association and atomic lifecycle tests. |
| G3: contextual evaluations | [#62](https://github.com/uibcdf/topomt/issues/62) | G1, G2 | Evaluation schema, atomic-distance contacts and geometric occupied-volume/fraction calculations with independent accuracy and historical-pose tests. |
| G4: provider admission and capabilities | [#63](https://github.com/uibcdf/topomt/issues/63) | G1; G2/G3 for relevant capabilities | Route-specific declarations, reported/inferred classification tests and explicit incomplete-support behavior. |

G4's inventory and admission design can proceed alongside G2/G3. Runtime use of
a relation or evaluation capability waits for its corresponding gate. The first
implementation within this deferred route is G1; no registry class zoo or blanket engine rewrite precedes
its type/schema and compatibility decision.

Every runtime slice follows test-first development. Its issue must name the
concrete pytest guard once implemented; normative design alone cannot close a
runtime gate. Each slice documents changed public behavior and schema/API
stability, passes its focused checks, and reports applicable hosted evidence.

## 3. First implementation slice

G1 must settle a small concrete schema for input context, source occurrence,
support reference and availability. Resolve snapshot/revision ownership and
local-to-source atom maps first. Keep implementation-specific primitives under
their engine namespace and expose neutral support access.

The snapshot decision must state what input evidence is retained or recoverable
and prevent a later live-input mutation from retargeting completed findings.
Define the `molecular_system` setter's behavior and the migration of direct
`features` dictionary mutation; preserving read access does not exempt writes
from registry validation. Test selected atom maps in nontrivial source order.

Distinguish geometry-input/mesh identity, probe-query identity and classification
derivation. Probe changes may reuse a compatible mesh; reporting changes and
catalog thresholds must not rewrite structural support. G1 owns the shared
minimum support/availability vocabulary used by G4, avoiding parallel schemas.
Exact tetrahedron recovery alone does not grant a physical-volume capability.

Start with one DFND concavity and its Mouth, plus an actual provider fixture
whose spatial geometry is incomplete. Test equal lining with different support,
probe/input changes, reporting-independent geometry identity, and the behavior
of an unavailable operation. Preserve existing `Topography` Mapping and imports.

This is a schema/admission migration, not an opportunity to rename every feature
class or change `get_topography()`'s default method. Compatibility projections
remain explicit. Public classes and call signatures are chosen at this gate,
not inferred from the conceptual entity names.

## 4. Interface and evaluation adoption

G2 stores molecular participants and interface associations even where the
native bank criterion misses a tight dimer. It preserves criterion provenance
and separate molecular/geometric counts. A relation can carry an unavailable or
provisional realization; it cannot claim canonical localized geometry from
whole-component membership alone.

Start with typed `part_of` containment and the current boundary/point links,
plus interface associations referencing at least two participants. Document
endpoint roles, direction, arity and evidence for these kinds before adding
general adjacency or overlap relations. Keep current connector restrictions;
validated 2D containment uses the new relation path. Declare one canonical owner
and derive the compatible parent/child views from it.

Explicit declarations and inferred associations carry different evidence states.
Test that participant registration without criterion-satisfying evidence does
not infer an interface. Preserve separate bank-based and molecular criteria,
including thresholds and negative outcomes; user labels cannot overwrite the
native bank descriptor. Shared atoms and overlapping selections remain explicit.

G2 does not close research-grade bare-interface localization or chamber/mixed
feature promotion. Before implementing either, open its own bounded scientific
issue with region definition, fixtures and acceptance tolerances. Its eventual
implementation must satisfy the conceptual contract and native catalog maturity
policy. Experimental localization does not become canonical through registration.

G3 closes only after its evaluation schema and both bounded calculations work:

1. Atomic-distance contacts between a feature's explicitly declared delimiting
   atoms and participant atoms, using an explicit length cutoff. Preserve pair
   identities and deduplicate union totals under shared participant membership.
   This quantity does not imply buried surface area or site-volume occupancy.
2. Geometric occupied volume and fraction for one DFND resident region. Define
   `T` as the union of resident tetrahedra, `A` as the union of all reference-input
   vdW balls reaching T, and `Omega = T minus A`. For participant volume
   `B = union(participant_vdw_balls)`, compute `vol(Omega intersect B)` and divide
   by `vol(Omega)` only when that denominator is positive. Record both radius
   models. The balls are not probe-expanded; this is empty-space occupancy in a
   query-selected region, not probe-center accessibility or contact-weighted
   AlphaSpace2 occupancy. Additional region models remain separate capabilities.

Both calculations initially support a single nonperiodic frame with recorded
alignment. Before implementing the volume estimator, document its method,
absolute/relative acceptance tolerances and uncertainty or convergence evidence.
Use independent analytic fixtures and test zero/partial/full occupancy and
overlapping participant unions. Numerical estimates are not relabeled exact.
A provider-formula reproduction keeps its method identity and original versus
independent values; it does not substitute for this geometric-volume gate.

A completed evaluation records its input pose. Moving B0 to B1 prevents reuse
for B1, preserves the historical B0 evaluation and unchanged reference geometry,
and requires a new evaluation or an explicit not-computed state. Moving an atom
included in the assembly's geometry input instead requires a new geometry
context. Schema-only storage, contacts alone, or placeholder occupancy values
cannot close G3.

The adversarial matrix in the conceptual contract is the shared acceptance
inventory. Select bounded cases per gate; do not claim all cases are already
validated because their native prototype tests exist.

## 5. Provider integration and existing work

[Third-party result preservation/parity](third_party_results_plan.md) remains
owned by [#19](https://github.com/uibcdf/topomt/issues/19) and its measurement
issues. G4 supplies semantic admission to that work. It does not reset its
percentage, waive original-output parity, or equate differently defined metrics.

AlphaSpace2's original wrapper now accepts an optional binder and preserves its
additional input artifact. The last sentence in issues #31–#34 describing binder
support as absent is historical. Their independent calculation, two-structure,
partial/zero-contact and zero-denominator acceptance remains open.

CASTp aggregates retain multiplicity under #51–#52; pyCASTA representative points
and ranking definitions remain under #36/#40. These are examples where an
adapter must preserve provider semantics rather than satisfy a canonical label
by inventing geometry or changing a definition.

The [native provider-method review](native_methods_plan.md) still follows the
external-result gate. DFND remains a separate native method with its own
scientific validation. Original-provider addon adoption is now owned by
[the viewer checkpoint](provider_output_viewer_checkpoint.md), #66. Broader DFND
viewer work remains separate; viewer availability does not determine these
core conceptual contracts.

## 6. Evidence and documentation maintenance

Agent-facing tests use `pytest --receptor=llm`; hosted suite tests retain their
normal selection and configured CI profile. Inspect relevant runs with
`gh run-receptor`; use its documented native fallback for missing evidence.
Keep local checks, hosted commit SHAs, design completion, provider parity and
release/matrix claims distinct.

Update the architecture entry point and contract when a gate becomes
implemented. Preserve historical checkpoints and archived decision records;
append a correction or precedence note rather than rewriting old evidence as
current success. Queued implementation reports follow `reporting_protocol.md`.
