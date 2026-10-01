# DFND and Topography audit, assessment and roadmap

Date: 2026-10-01. Audited source: `7bd47faba6179a6e02444331e442acd251572564`.
Scope: native DFND, public Topography, their contracts, current tests and owning
issues. This audit changes documentation and work tracking, not runtime code.

Subsequent implementation progress is recorded at the end of this document.
The assessment and reproductions retain their explicitly named audited source.

## Decision and precedence

The user has selected DFND and Topography as the next workstream, starting with
this audit and roadmap. Initial original-provider outputs and MolSysViewer
adoption are delivered; their broader fidelity work remains paused. Concrete
DockingMT/PharmacophoreMT adoption and additional engine integration remain
deferred. This dated scheduling decision supersedes older statements that all
DFND work must wait for complete third-party fidelity.

The [Topography conceptual contract](../topography_conceptual_contract.md) is
the public semantic direction. DFND's mathematical/input/query contracts remain
the native method references. This audit establishes current evidence and a
sequence; it does not silently choose new public classes, change method defaults,
promote experimental outputs or close implementation/scientific gates.

## Assessment

DFND has a substantial executable foundation. The next phase should preserve
its existing geometry/query/identity machinery, fix concrete ownership defects,
and establish trustworthy public support and scientific evidence. Rebuilding
the whole engine or expanding the feature vocabulary first is unwarranted.

Topography already provides useful feature access and DFND promotion. Its
accepted conceptual model is more complete than its runtime: context/snapshot
ownership, support completeness, participants, typed relations and contextual
evaluations still require adoption. The two sides must evolve together: native
records provide geometric evidence; public contracts make that evidence safe
and meaningful to consumers.

| Area | Evidence at the audited source | Assessment / remaining gate |
| --- | --- | --- |
| Delaunay and clearance | Atom-center tessellation; scalar/batched active-set residence and face-gate solvers; analytic, order and transform tests. | Strong engineering foundation for the defined local models; not global collision-free probe reachability. |
| Query and decomposition | Frozen mesh/query configurations; cached mesh re-query; one shared-face transit predicate; OCEAN, external links, resident content and dry complement. | Implemented and tested. Snapshot protection and independent connectivity validation remain. |
| Static identity | Recoverable atom-defined tetrahedron/face support, support/context keys and deterministic rankings. | Useful within compatible inputs. Mutable arrays can invalidate cached facts without changing keys (#60). |
| Classification | `classify.py` owns naming; typed family is derived; occlusion, elongation and buriedness refine names. | Basic catalog exists. Morphological thresholds are provisional; policy/version/maturity must accompany public derivations. |
| Public promotion | Concavity features and child Mouths; percolating regions; open-concavity/groove/cleft classes; source keys and units. | Already implemented, broader than older status prose. Does not implement the full public context/support model (#60). |
| Registries | Validated add/replace/rename/remove/connect, registered IDs and deep-copy tests. | Useful foundation, with a reproduced shallow-copy index corruption defect (#74); direct mutable views remain an adoption risk. |
| Metrics | Topological volume, local sampled solvent estimate, on-demand MC and quadrature, voxel grids, mouth/gate and depth measurements. | Definitions must remain separate. Numerical precision/uncertainty claims need correction (#75). |
| Dry side and interfaces | Dry components, interfaces, face depth, candidate motifs, bank-based labeling and explicit-label prototype. | Native evidence exists; dry means non-resident at the query probe, not automatically molecular material. Public participants/localized interfaces remain #61 and subsequent science. |
| Hierarchy and morphology | Capacity motifs, chamber/throat descriptors and funnel/shape measurements, with focused tests. | Provisional interpretation and thresholds; not validated public subregion promotion. |
| Dynamics | `match_results` and `assign_tracks`, including split/merge tests. | Helpers exist. Compatible atom namespaces, matching policy, confidence and public collections remain open; support keys are not tracks. |
| Channel geometry | Shortest-distance skeleton and visual branches with explicit `is_collision_validated=False`. | Visualization evidence; not widest-path capacity or a collision-validated probe route. |
| Scientific validation | Synthetic assertions, pathological behavior markers and small real-system stability checks. | Positive engineering evidence; independent reference assumptions and a frozen annotated panel are needed (#76). |
| Product readiness | Current local DFND/Topography selector passes; hosted full CI remains failed at an older source. | No complete release/matrix or biological-performance claim (#16/#58). |

Code anchors: [native API](../../topomt/dfnd/api.py),
[network](../../topomt/dfnd/graph.py), [data views](../../topomt/dfnd/data.py),
[classification](../../topomt/dfnd/classify.py),
[identity](../../topomt/dfnd/identity.py),
[Topography](../../topomt/topography/Topography.py),
[BaseFeature](../../topomt/features/BaseFeature.py),
[volume methods](../../topomt/dfnd/core/solvent_volume.py),
[lineage](../../topomt/dfnd/lineage.py),
[channel skeleton](../../topomt/dfnd/centerline.py).

## Architecture to consolidate

The implemented and target responsibilities form this sequence:

```text
MolSysMT input + identified snapshot + resolved atom map
    -> DFND cached mesh and local geometric primitives
    -> explicit probe/query -> transit/dry graphs and components
    -> grounded supports, observations and motifs
    -> versioned catalog classification + recorded promotion
    -> Topography feature registry, public support/context and relations
    -> contextual evaluations / consumers / comparison collections
```

Input topology, coordinates and selections remain MolSysMT responsibilities.
`topography.dfnd` owns the native substrate; public features reference support
and provenance without requiring a user to understand native graph objects.
Topography's current Mapping and feature imports are compatibility obligations.

Four distinctions are essential:

- Exact support recovery is separate from numerical accuracy of a measurement.
- A graph path is separate from continuous probe navigability.
- Molecular participants are separate from geometric dry banks.
- A catalog label is separate from source identity and from temporal correspondence.

Original provider outputs remain independently usable. Future admission (#63)
uses the same public support/capability vocabulary, preserves reported labels
and measurements, and never fabricates a DFND graph or region from atom-only
exports. External agreement is a descriptive validation lens, not DFND's definition.

## Reproduced integrity findings

### Shallow Topography copy corrupts the original registry

At the audited source, remove `POC-1` from a `deep=False` copy of a Topography
containing that pocket. The original still contains `POC-1`, but its type index
becomes empty. In a fresh pair, renaming in the copy makes a type lookup on the
original raise `KeyError('POC-renamed')`. `__copy__` copies dictionaries but
shares their nested sets. Existing registry-copy coverage exercises `deep=True`.

Owner: [#74](https://github.com/uibcdf/topomt/issues/74), with
[reproduction, acceptance and subsequent resolution](../archive/topography_shallow_copy_indexes.md).
Fix this bounded defect before extending registry ownership.

### Exposed native geometry can make caches and identity stale

Build a regular tetrahedron network, query it and create `DFNDData`. Changing
`data.mesh.atoms.coords[0, 0] += 0.2` changes `network.atom_coords` in nm. A new
query retains the same `substrate_key`, `result_key` and cached residence radii.
The frozen mesh configuration does not freeze those arrays. `MeshAtoms` exposes
network coordinates/radii/maps directly; raw dictionaries and feature fields
are also mutable. Topography's molecular-system setter can retarget a populated
result without an explicit historical-input policy.

Owner: [#60](https://github.com/uibcdf/topomt/issues/60); reproduced native-cache
evidence was appended there. The solution must cover native arrays, live-input
mutation, selected-source mapping and public views as one ownership contract.

### Numerical certainty is overstated at volume boundaries

For a right unit tetrahedron and an interior ball, fixed-order quadrature
approaches the analytic volume as `n_quad` increases; it is not mathematically
exact integration. MC's returned width is a normal-approximation estimate. It
can be zero for a finite sample missing a small excluded ball even though the
true empty volume is smaller. Neither behavior establishes rigorous certainty.

Owner: [#75](https://github.com/uibcdf/topomt/issues/75), with
[numeric evidence](../pending_bugs/dfnd_volume_precision_claims.md).
Keep semantic maturity, numerical uncertainty and biological validity separate.
Past-beach volume is an estimate/bracket; current local sampling does not certify
a rigorous upper bound. It must not become an exact occupancy denominator.

## Scientific reference audit

The current pathological suite preserves observable failure/sensitivity cases.
Those passing markers are useful history, but their stated ideal answers must
be checked against the actual union-of-atomic-balls model before fixing the engine.

| Historical interpretation | Required review |
| --- | --- |
| The same sphere at different atomic wall densities should keep one family. | With fixed radii, density changes the union of balls and may physically open gates. Establish whether physical accessible space actually stays equivalent. |
| Changing radii at fixed coordinates should preserve classification. | Radii are part of physical geometry. Changed topology can be expected; use an independent reference to identify an algorithm error. |
| A larger probe must find no more components. | Removing available nodes/edges can split components. Availability should be nested under a fixed compatible policy; component count need not be monotone. |
| A sampled spherical shell has continuum volume `4*pi*(R-r_atom)^3/3`. | Discrete overlapping balls do not automatically realize that continuum boundary. Separate reference-region, exclusion and integration errors. |
| Two convex bodies imply no assembly pockets. | Inter-body concavity can be legitimate. Molecular/interface context and reporting relevance are needed to decide its meaning. |
| No successful fixture proves a state impossible. | Distinguish empirical absence, a formal result under stated assumptions, and compatibility coverage. Keep the classifier total without an unsupported theorem. |

These are reasoned reference-model findings, not a claim that all fragmentation
is valid. Confirmed segmentation errors may remain after independent validation.
The local face solver handles unequal radii in its defined plane; older prose
saying mixed-radius gates are only equal-radius exact is not current solver evidence.
Planar local clearance still does not establish global three-dimensional transit.

Owner: [#76](https://github.com/uibcdf/topomt/issues/76), with
[bounded validation delivery](../pending_proposals/dfnd_reference_validation_panel.md).
Tune segmentation and morphological thresholds only after the target observables
and references are frozen. Avoid optimizing the method to preserve an invalid ideal.

## Documentation reconciliation

Historical checkpoints retain their source/date. The following wording should
not drive new implementation:

- The May DFND roadmap says Topography promotion is missing; current native
  promotion already exists, including provisional morphological classes.
- Implementation/status prose says dynamic helpers are absent; lineage helpers
  exist, while the validated public trajectory contract remains pending.
- Some input-policy prose names `dfnd_records`/`dfnd_result`; current access is
  through the single `topography.dfnd` container.
- Comments in `classify.py` say classification does not drive `feature_type`;
  the current public promotion dispatches on the classified name.
- The blanket statement that semantic copies are coherent misses #74.
- The metric status table and code differ for interfaces and hierarchy motifs;
  `output_status.py` does not itself confer biological validation.
- `volume_solvent_accessible` and some additional descriptors need a complete
  maturity/definition inventory; an additive attribute is not a public measure contract.
- Morphological threshold confidences need their own definitions: current
  classification confidence is based on occlusion, while cleft/groove proximity
  influences marginality. It is not a universal confidence probability.

This audit is the current evidence entry point. Later implementation slices must
reconcile their governing documents and affected code comments; archived measured
outcomes must not be rewritten as current certification.

## Roadmap and exit criteria

| Stage | Delivery | Owner / exit evidence |
| --- | --- | --- |
| 0. Integrity baseline | Isolate shallow-copy registry state; define ownership of cached geometry and public mutation paths. | #74 copy correction and #60 native numeric snapshots delivered. Source recovery and public mutation/context/support adoption remain partial; see the snapshot checkpoint below. |
| 1. Public context/support | Choose concrete schema/ownership, retain input/probe/atom-map/version evidence and adopt neutral support references. | #60. One DFND concavity + Mouth and one incomplete provider fixture; equal lining with different supports distinguished; probe/reporting/classification changes preserve the right identities. |
| 2. Numerical and scientific trust | Correct uncertainty/precision reporting; classify reference assumptions; freeze small independent synthetic and annotated evidence panels. | #75/#76. Defined accuracy and maturity, independent expected answers, reproducible reports and explicit unresolved cases. This can progress alongside stage 1 after the integrity baseline. |
| 3. Participants and relations | Add contextual molecular participants, typed containment/boundaries and interface associations with honest localization state. | #61 after #60. Tight dimer with fused bank, shared membership, buried/contact-only interfaces and atomic reference lifecycle tested. |
| 4. Contextual evaluations | Implement defined atomic contacts and reference-empty-region occupied volume/fraction with pose provenance. | #62 after #60/#61 and the relevant numerical contract. Independent zero/partial/full/undefined cases; moved partner creates a new evaluation, preserving historical values. |
| 5. Canonical provider admission | Adopt route-specific capabilities and reported/inferred labels without changing original-output access. | #63 after #60; relation/evaluation capabilities wait for their owners. Incomplete geometry remains explicitly unsupported; no fabricated exact region/mouth. |
| 6. Distinctive native extensions | Validate subregion promotion, dry/convex features, navigability or public dynamic collections in individually scoped work. | Future bounded scientific issues once a concrete capability is selected. Do not promote all motifs or build a speculative class hierarchy. |

The bounded **#74 correction is delivered**; the next implementation package is
**the ownership and context/support slice of #60**. Establish stage-2 references before any change
intended to fix segmentation or calibrate groove/cleft/funnel. This sequence
preserves the existing engine while making Topography a trustworthy scientific
result rather than a bag of mutable attributes.

A useful first milestone is a static DFND result with protected input/support,
recoverable provenance, explicit classification maturity and defined numerical
accuracy, consumable through the existing Mapping API. Contacts/interfaces and
dynamics follow their own gates. A complete release additionally requires #16,
#58 and applicable documentation/package checks; passing a focused selector is
insufficient. No percentage completion or delivery date is inferred here.

## Verification and limits

Current local selection:

```bash
python -m pytest --receptor=llm -p no:rerunfailures -n 4 --dist loadfile \
    tests/test_dfnd*.py tests/test_topography*.py \
    tests/test_get_topography_api.py tests/test_devguide_contract_terms.py
```

Result: **312 passed, 2 skipped, 57.49 s**, Python 3.13.14 on Linux. This includes
small real-system stability, primitives, identity/query, registry, solvent-volume,
synthetic/pathological, hierarchy/morphology and lineage checks. Skips: no known
end-to-end nonresident-passage fixture; no experimental motif in one panel.
The negative copy/cache/precision probes above supplement those existing tests.
They are reproductions, not committed runtime regressions or fixes.

Environment evidence: NumPy 2.4.6; SciPy 1.18.0; editable MolSysMT
`0.21.0+606.ga03eb4bf6`; editable PyUnitWizard `0.25.0+7.g00d756c`;
Pytest Receptor `1.2.0+7.g29516dd`. This is source-development evidence, not an
isolated installed-package or supported-Python/OS matrix certificate.

The last inspected full [CI run 36785275320](https://github.com/uibcdf/topomt/actions/runs/36785275320)
is failed at `5f2c0f43c8b0ec4b231641e0df58d1474f651785`: six test jobs failed;
GH Run Receptor identifies missing `fpocket` as one bounded cause. The run
has one success and one skip. It is older than the audited source, not a current
DFND-only failure verdict. Green lint/policy or optional-executable checks do
not supersede full scientific CI. Matrix/remediation owners remain #16/#58.

This audit does not rerun all providers, certify live CASTp, inspect browser
rendering, measure current scaling performance, validate biological detection
quality or establish exact continuous probe paths. Documentation/lifecycle
verification of this audit is reported with its publication evidence.

Publication preparation: generated queue indexes are current; reporting and
contract-term checks pass **3 tests**; full Ruff lint/format and diff checks pass.
The eleven authored/updated guide documents render with warnings treated as
errors. Including the two generated queue READMEs in a wider temporary build
also exposes their existing H1-to-H3 heading jumps; those pages are outside the
clean scoped render and remain documentation debt under #64. Public incremental
`make html` succeeds with eight existing diagnostics under #64. This does not
claim a clean full Sphinx build. Concurrent remote changes to fpocket command
availability are preserved separately; the scientific evidence above remains
at its explicitly named audited source.

## Subsequent implementation progress (2026-10-01)

The bounded registry-copy correction (#74) is implemented. Registry-owned
nested index and relation sets are independent in shallow copies, while
analysis attributes retain their existing shallow payload behavior. Its
[archived report](../archive/topography_shallow_copy_indexes.md) names the
guard and preserves the original reproduction.

Failing-first evidence: all ten combinations of five registry operations and
mutation through either original/copy failed before the correction. After the
fix, the registry module passes **23 tests**; the same joint DFND/Topography
selector above passes **324 tests with two existing skips** (63.29 s).
Reporting/contract-term checks and the copy docstring example pass **4 tests**.
These are Linux Python 3.13 development-source results, not an installed-package
or full Python/OS matrix certificate.

The next stage-0 slice remains native snapshot/cache ownership under #60,
followed by its public context/support adoption. Scientific reference review
and numerical precision remain #76/#75. No segmentation, classification,
physical geometry or provider behavior is changed by this correction.

The bounded mypy invocation still reports six pre-existing diagnostics, also
reproduced against the unchanged preceding source using `--shadow-file`.
Public annotation/narrowing and checker dependency resolution are recorded in
[#77](https://github.com/uibcdf/topomt/issues/77); this slice does not claim a
clean typing gate.

Publication preparation: generated report indexes are current; full Ruff lint
and format checks pass. The eight authored/updated guide pages render with
warnings treated as errors, and their local Markdown targets exist. Public
incremental `make html` succeeds with the same eight existing diagnostics
tracked in #64. Hosted scientific/matrix evidence remains a separate gate.

Later on 2026-10-01, #60's native numeric ownership slice is implemented and
measured in [the geometry snapshot checkpoint](checkpoint_geometry_snapshots_2026_10_01.md).
Input coordinate/radius/map edits cannot retarget cached numerical geometry;
protected mesh/input buffers are shared across probes. The expanded selector
passes 381 tests with seven existing skips. Unique retained native array bytes
are unchanged in four measured fixtures; input alias isolation and per-query
records have their explicitly documented memory costs. #60 remains partial;
the public context/support schema and mutation migration are still pending.

The final expanded selection, including restored-snapshot protection, reporting
checks and executable examples, passes 385 tests with seven existing skips.
