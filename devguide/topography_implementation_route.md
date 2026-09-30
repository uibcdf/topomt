# Topography conceptual-contract implementation route

Date: 2026-09-30. Status: **planned; runtime gates remain open**.
Normative decision: [topography_conceptual_contract.md](topography_conceptual_contract.md),
recorded by [#59](https://github.com/uibcdf/topomt/issues/59).
This broad route lives outside the report queues; its bounded work has owning
issues. Closing the conceptual decision does not complete these runtime gates.

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
| G3: contextual evaluations | [#62](https://github.com/uibcdf/topomt/issues/62) | G1, G2 | Definition/value-state schema and a bounded validated calculation slice with pose/support/provenance tests. |
| G4: provider admission and capabilities | [#63](https://github.com/uibcdf/topomt/issues/63) | G1; G2/G3 for relevant capabilities | Route-specific declarations, reported/inferred classification tests and explicit incomplete-support behavior. |

G4's inventory and admission design can proceed alongside G2/G3. Runtime use of
a relation or evaluation capability waits for its corresponding gate. The first
implementation is G1; no registry class zoo or blanket engine rewrite precedes
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

G2 does not close research-grade bare-interface localization or chamber/mixed
feature promotion. Before implementing either, open its own bounded scientific
issue with region definition, fixtures and acceptance tolerances. Its eventual
implementation must satisfy the conceptual contract and native catalog maturity
policy. Experimental localization does not become canonical through registration.

G3 begins with one declared support and contact/evaluation definition. Validate
its observable against independent expected evidence, not only a replay of the
implementation. Any geometric-volume slice needs a reference-region and volume
model, union handling, and an accuracy contract. A provider-formula reproduction
keeps its method identity and its original/independent value distinction.

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
scientific validation. Viewer/addon changes are deferred; viewer availability
does not determine the core conceptual contracts.

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
