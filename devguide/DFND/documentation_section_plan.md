# DFND scientific documentation section: proposal

Date: 2026-11-09. Owner: [#170](https://github.com/uibcdf/topomt/issues/170).
Status: **section proposal, prepared for maintainer review; public pages are not
yet authored or integrated**.
Reviewed checkout: `dc525ce63c6d30531f4924c9469511384394d9b3`.
This is a code/documentation study, not a new numerical experiment, scientific
validation, accepted API change or replacement algorithm specification.

## Recommendation and purpose

Add a first-class **DFND: Theory and Method** section at
`docs/content/dfnd/`, with its own entry in the main documentation navigation
beside the User guide and BenchLab. Use descriptive page names and a progressive
reading order. Introduce **Delaunay Flow Network Decomposition (DFND)** in full.
Explain the scientific question, the mathematical model, the
implemented algorithm and the interpretation of its results as one connected
account. DFND addresses molecular topography; pocket detection is one product.

Give each destination a distinct responsibility:

| Destination | Reader's question |
| --- | --- |
| DFND: Theory and Method | What does DFND model, how does it reason, and what do its results mean? |
| User guide | How do I perform a particular analysis? |
| API reference | What does this callable or object accept and return? |
| BenchLab | What happened on this fixed system, with what independent reference and evidence? |
| Public developer guide | How is TopoMT organized and extended? |
| Repository `devguide/` | Which contracts, decisions, investigations and development gates govern the implementation? |

The new section should contain the curated scientific explanation, with links
to practical calls and canonical study units. Keep the existing
[geometry/query guide](../../docs/content/user/dfnd_geometry.md) as the operational
reference and link it in both directions. Preserve BenchLab's system/reference,
DFND and comparison notebook separation. Do not move or copy frozen artifacts.
There is no need for another showcase or a single large theory notebook.

## What the repository study establishes

- Public DFND documentation currently explains snapshots, units, input contexts
  and probe reuse, but has no connected theory course. BenchLab supplies worked
  evidence, while public developer pages describe architecture.
- `devguide/DFND/` contains definitions, audits, catalog decisions, metric and
  identity contracts, theoretical reviews and dated checkpoints. They cannot be
  concatenated into a public specification: some describe earlier stages.
- The original proposal in
  [the CAST-inspired design](../castp/ideas_paper_1998/topomt_core_algorithm_final.md)
  uses regular triangulation, alpha complexes and directed sink/basin flow.
  Current `graph.py` uses ordinary Delaunay, local three-/four-atom clearances
  and an undirected threshold graph. Explain this evolution briefly; the word
  "final" in a historical filename does not establish current authority.
- `classify.py`, typed components and the public bridge distinguish grounded
  observations, catalog refinement and feature promotion. Raw compatibility
  family fields still exist. Neither an old access/residence table nor the
  target kernel/catalog separation alone describes every current output.
- Dry banks, wall/interface records, depth and motif descriptors exist. General
  public protrusion/ridge detection and localized molecular-interface support
  are separate, less mature work. A complete explanation must include them
  without announcing them as completed detectors.
- `lineage.py` contains both matching and track-assignment helpers. Older prose
  that calls all lineage work pending is stale, but helper availability is not
  qualification of an end-to-end molecular-dynamics workflow.
- The [theory review](core_theory_review_2026_11_06.md),
  [boundary proposal](boundary_connectivity_contract.md),
  [reference audit](../pending_proposals/dfnd_reference_validation_panel.md) and
  [volume report](../pending_bugs/dfnd_volume_precision_claims.md) qualify physical
  interpretations. Explain the actual local/discrete operators and their
  assumptions instead of importing stronger claims from older prose.
- Sphinx already supports MyST, mathematics, figures, notebooks and bibliography.
  `docs/bibliography.bib` has no DFND-specific coverage at this revision. Use the
  reviewed scientific bibliography in `topomt/_bibliography.py` and the
  [antecedent study](mole_comparison_2026_11_07.md) as inputs to a selected,
  verified public reference list; a citation ledger is not a theory chapter.

These are source-inspection conclusions at the named revision. Historical test
presence, catalog labels and passing implementation regressions are not
independent physical reference evidence.

## Reading routes and page organization

Offer two explicit routes on the landing page:

- **Understand and use the results:** overview, model, intuitive summaries of
  capacities/decomposition, classification, result interpretation, and the
  tetrahedron BenchLab unit. Later chapters remain discoverable from there.
- **Understand the complete method:** all chapters in dependency order, followed
  by formal derivations and algorithm pseudocode. Advanced readers can inspect
  implementation/API references without learning internal identifiers first.

Each chapter begins with its question and a plain-language explanation, then
introduces notation and the formal definition, describes the implemented
operation, and ends with interpretation/evidence and related API/study links.
Put long derivations in appendices, with links at the relevant definition.

Proposed sources, all **planned**, not existing public pages:

```text
docs/content/dfnd/
  index.md
  overview.md
  geometry_and_probe.md
  local_capacities.md
  network_and_decomposition.md
  exterior_and_boundaries.md
  classification.md
  dry_topography_and_interfaces.md
  hierarchy_and_paths.md
  scale_and_dynamics.md
  measurements.md
  results_and_provenance.md
  numerics_and_reproducibility.md
  validation_and_scope.md
  references.md
  appendices/
    notation.md
    clearance_derivations.md
    algorithm.md
```

## Chapter briefs

### Overview: the scientific question and the whole method

Explain characterizing regions, access, boundaries, relief and interfaces of
an atomic-ball system at a specified probe scale. Show the complete chain:
input/model → mesh → capacities → query graph → components/boundaries →
descriptors/catalog → Topography. Clarify what "flow" means here: geometric graph
connectivity, not a computed hydrodynamic flow or a solvent transport rate.
Introduce motivations and intended contributions without a novelty or
superiority claim. Link the historical/antecedent context from the references.

### Geometry and probe: define the object being studied

Introduce centers/radii, the molecular ball union, bare empty space and probe
center space. Distinguish nonpenetrating centers (`clearance >= probe`) from
strictly free centers (`clearance > probe`), the probe's swept occupied volume,
and tetrahedral carrier volume. Name tangency and numerical conventions.
Explain ordinary Delaunay, its Voronoi relationship and the finite atomic-center
convex hull. Atomic radii enter the local operators; this is not a weighted
alpha-complex construction. Include selection, hydrogen/radius policy,
single-frame input and the current nonperiodic Cartesian interpretation.

### Local capacities: residence, gates and cell states

Define a local clearance field for a specified obstacle set. State the intended
closed-cell maximum for `R_residence` over four vertex atoms and closed-face
maximum for `R_gate` over three face atoms. Explain active constraints and
interior/face/edge candidates; keep tangency candidates such as `R_apollonius4`
distinct from the adopted residence observation. Separate the formal maximum
from the solver's candidate enumeration, validation and numerical guarantees.
Derive the resident/permeable thresholds and local open/coast/sealed labels.
Explain omitted-atom intrusion and why local success is not an all-atom path.

### Network and decomposition: from local decisions to regions

Define the probe-specific finite graph, virtual OCEAN, transit edges and the
decomposition after removing the common exterior root. Show residence subsets,
optional connectors, terminal contacts and non-transit cells. State exactly
what `resident_only` and `with_connectors` implement, including tolerance and
intrusion policies. The residence/transit physical interpretation must retain
the [theory review's conditional reasoning](core_theory_review_2026_11_06.md)
and #76 ownership; do not repeat "passes through but cannot reside" as an
established physical theorem. Supply compact pseudocode and a graph drawing.

### Exterior access and boundaries: contacts, patches and mouths

Explain hull contacts, native shared-edge clustering, physical free boundary
patches, component-to-patch paths and public Mouth promotion as distinct
operations. Use the tetrahedron's four-patch reference and its one-link native
observation to make the distinction visible, with the opened/covered shells as
controls. The selected envelope is part of the observable; not every hull patch
is an intrinsic biological mouth. Explain native walls and shore/beach incidence
with explicit support and obstacle scope. Keep the #151 candidate views marked
as proposals; no example may call them as implemented API.

### Classification: measurements, names and refinement

Explain the access/residence signature, the native zero-wall Percolating
override, and morphology-based refinement to Pocket/OpenConcavity/Groove/Cleft.
Separate family, refined name, orthogonal descriptors and diagnostic labels.
Describe thresholds and per-output margins; classification confidence is not
the probability of biological functionality. Preserve identity when catalog
interpretation changes. Include a decision diagram that matches `classify.py`
and the actual promotion path; biological pore/tunnel labels require additional
evidence. Reporting suppression is a separate operation from decomposition.

### Dry topography and interfaces: the other half of the model

Distinguish local nonresidence from the bank graph's complement of finite
transit nodes; connectors make them different. Explain face/edge/vertex bank
adjacency, wet/dry incidence, depth, exposed shells and core candidates.
Present the intended grounding of protrusions, convex patches, rims, ridges,
walls and solid septa, with implemented-versus-proposed status. A dry bank is
not a molecular participant, and an entire bank is not one protrusion. Separate
native multi-bank lining from a localized molecular interface; include tight
contacts, buried interfaces and associations without a wet cavity. Chemical
characterization belongs to an orthogonal overlay, not a geometric family.

### Internal structure and paths: hierarchy inside a region

Explain topological depth, depth regions, capacity merge trees, chamber/throat
candidates and their contextual prominence/separation scales. Distinguish an
internal empty-space throat, a closed wet/wet constriction and a solid septum.
Describe the existing skeleton's actual shortest-distance objective and
resident-graph scope; it is not a widest path or a collision-validated probe
trajectory. Keep provisional motif ranking and unqualified physical transition
interpretations visible. A component hierarchy does not automatically create
public child region features or provide the full probe-sweep event history.

### Scale and dynamics: three different kinds of persistence

Separate within-query capacity hierarchy, changing probe radius on fixed
geometry, and changing coordinates across frames. Explain cached mesh reuse,
which state is recomputed, discrete nesting assumptions and why component
counts need not be monotone. Describe actual support/Jaccard matching and
track/event helpers, with ambiguity under Delaunay flips and atom-map changes.
Distinguish those helpers from a fully qualified trajectory pipeline or dynamic
biological interpretation. No new protein case is needed to author this chapter.

### Measurements: what is being measured and how accurately

For each volume/area/length, identify support, obstacle set, probe convention,
units, algorithm and accuracy statement. Separate carrier resident/transit
volumes, local barycentric bare-empty estimates, all-atom empty-volume
evaluation, probe-center volume, occupancy grids and swept volume. Explain
past-beach descriptor scope without treating it as an exact accessible set.
Distinguish full triangle area from free aperture area and a local gate radius
from a global bottleneck. Discuss Monte Carlo, deterministic quadrature and grid
error honestly: the compatibility name `method='exact'` does not establish
exact integration, and #75 remains the numerical correction owner.

### Results and provenance: connect the theory to a usable result

Walk from a public Topography finding to its context, classification, parents,
atom roles and native support. Explain `topography.dfnd.raw`, mesh, query graph
and typed components without making them prerequisites for routine use.
Separate display rank, exact support, contextual result/component identity and
cross-result correspondence. Show units, saved input/selection maps, immutable
geometry reuse, overlapping atom membership and attribution. Distinguish existing
support from the broader #60/#61 target; link complete signatures to the API.
Probe-accessible atom labels are not measured contacts of a particular ligand.

### Numerics and reproducibility: decisions at the boundary

Explain epsilon, explicit query tolerances and marginal states without treating
tolerance bands as a measured model of molecular flexibility. Cover degeneracy,
slivers, cospherical ambiguity, candidate validation, intrusion policy, units,
random seeds and reporting-versus-analysis settings. State what input/model
changes invalidate geometry or contextual identity. Explain costs in terms of
atoms, tetrahedra, faces, retained queries and selected metric work; measured
performance needs a pinned input/backend/resource profile, not a blanket speed
or complexity claim. Use bounded examples and the shared-resource policy.

### Validation and scope: how an interpretation earns support

Distinguish mathematical implications under stated assumptions, engineering
regressions, independently justified case references, matched third-party
comparisons and biological generalization. Explain what the current three
BenchLab units establish and what they leave open; older catalog names and
tests protecting observed pathologies are not independent truth. Link maintained
limitations and their owning issues rather than copying a permanent list from
historical notes. Discuss antecedents and candidate contributions separately
from demonstrated advantages; follow the comparative-finding lifecycle.

## Appendices and bibliography

- **Notation and glossary:** symbols, dimensions, obstacle sets, boundary/strict
  conventions, node states, native terms and public terms. No retired `domain`
  terminology for DFND components; distinguish support dimension from the
  legacy Feature0D/1D/2D class hierarchy.
- **Clearance derivations:** constrained optimization, active sets, unequal
  radii, admissibility and degeneracy. Separate derivations and conditional
  implications from guarantees established for the implemented solver. Include
  the regular tetrahedron as a worked calculation with its exact frozen model.
- **Algorithm:** self-contained pseudocode with input, output, policy, unit,
  filtering and failure contracts. Explain which steps are local approximations
  and which are discrete graph operations; no private Python implementation is
  copied into the reader's workflow.
- **References:** selected primary sources for geometry, probe-based molecular
  surfaces, pocket/channel antecedents and numerical methods actually discussed.
  Recheck metadata and attribution, including CAST/MOLE antecedents; identify
  unpublished project reasoning as such. Ackredit usage references complement
  this list. No fabricated DFND paper/DOI or automatic claim of priority.

## Evidence and maintenance conventions

Give readers a short scope/status note at each important inference. Distinguish
a definition, an assumption/conditional mathematical implication, implemented
behavior, an independently checked case observation, and an open scientific
question. Keep this evidence dimension separate from the existing software
output maturity (`canonical`, `provisional`, `experimental`, `diagnostic`,
`deferred`); do not create a competing output-status registry.

Use dates/revisions for scoped observations and current issue/finding links for
ongoing questions. When an algorithm, observable or promotion rule changes,
review the affected chapter, pseudocode, example and links in the same delivery.
If a limitation is corrected, reconcile the public explanation with its
maintained finding and issue; an old worked observation remains clearly dated
history. The book must not become a second unmaintained limitation inventory.
Record adopted contracts explicitly; distinguish documentary explanation from
acceptance of a proposed operator or API. These are proposed editorial criteria
for #170, not new runtime rules or an amendment of the existing scientific
contracts.

## Source and evidence map for authoring

This map identifies material to inspect and reconcile, not a declaration that
every referenced test was executed for this proposal.

| Chapter group | Main implementation / contract | Relevant guard or independent evidence |
| --- | --- | --- |
| Input/model | `graph.py` constructors, `config.py`; [input policy](input_policy.md), [units](unit_convention.md), [input context](../topography_input_context.md) | [Input policy tests](../../tests/test_dfnd_input_policy.py), [snapshot tests](../../tests/test_dfnd_geometry_snapshot.py), [context tests](../../tests/test_dfnd_input_context.py) |
| Capacities | [Clearance solvers](../../topomt/dfnd/core/clearance.py); [definitions](Mathematical_Definitions.md), [residence audit](residence_radius_audit.md), [gate audit](gate_radius_audit.md) | [Primitive tests](../../tests/test_dfnd_geometry_primitives.py), [tetrahedron reference](../../tests/test_dfnd_regular_tetrahedron_reference.py) |
| Graph/decomposition | [Graph](../../topomt/dfnd/graph.py); [query contract](checkpoint_query_contract_2026_06_14.md), [theory review](core_theory_review_2026_11_06.md) | [Graph tests](../../tests/test_dfnd_graph_contract.py), [query tests](../../tests/test_dfnd_query_contract.py); #76 independent panel |
| Exterior/boundaries | `_cluster_external_faces`, boundary helpers and bridge; [boundary proposal](boundary_connectivity_contract.md) | [Tetrahedron certificate](../../tests/test_tetrahedron_boundary_certificate.py), [opening certificate](../../tests/test_opening_connectivity_certificate.py), [shell cover](../../tests/test_closed_shell_wall_cover.py); #151 pending acceptance |
| Classification | [Catalog implementation](../../topomt/dfnd/classify.py), [bridge](../../topomt/dfnd/api.py); [catalog](feature_catalog.md), [architecture decision](taxonomy_architecture_decision.md) | [Classification tests](../../tests/test_dfnd_classify.py), [public three-case receiving](../../tests/test_benchlab_public_topography.py) |
| Dry structure/interfaces | Graph dry builders, [components](../../topomt/dfnd/components.py), [interface helpers](../../topomt/dfnd/interfaces.py); [public conceptual contract](../topography_conceptual_contract.md) | [Wet/dry adjacency](../../tests/test_dfnd_wet_dry_adjacency.py), [interface tests](../../tests/test_dfnd_interface_features.py); localized public support #60/#61 |
| Hierarchy/paths | `_attach_wet_motifs`, `_attach_capacity_motifs`, [centerline](../../topomt/dfnd/centerline.py); [motif contract](component_motifs.md) | [Hierarchy tests](../../tests/test_dfnd_hierarchy.py), [centerline tests](../../tests/test_dfnd_centerline.py); these do not certify all-atom paths |
| Scale/identity/dynamics | [Data/query views](../../topomt/dfnd/data.py), [identity](../../topomt/dfnd/identity.py), [lineage](../../topomt/dfnd/lineage.py); [identity contract](component_identity_contract.md) | [Identity tests](../../tests/test_dfnd_component_identity.py), [lineage tests](../../tests/test_dfnd_lineage.py) |
| Measurements/numerics | [Volume operators](../../topomt/dfnd/core/solvent_volume.py), data metric methods; [metrics](metrics_contract.md), [numerics](numerical_policy.md) | [Volume tests](../../tests/test_dfnd_solvent_volume.py), [on-demand volume tests](../../tests/test_dfnd_solvent_volume_precise.py); #75 accuracy gate |
| Results/qualification | [Object model](object_model.md), [output status](../../topomt/dfnd/output_status.py), [attribution](../attribution.md) | [Data tests](../../tests/test_dfnd_data.py), [registry tests](../../tests/test_dfnd_components_registry.py), [active BenchLab sequence](notebook_laboratory_checkpoint.md) |

In particular, output maturity in `output_status.py` describes the declared
software contract. It does not supersede a reproduced scientific limitation or
prove physical correctness. Resolve disagreements among old prose, current
source and accepted contracts explicitly in the owning issue before teaching a
stronger interpretation. #170 owns documentary reconciliation; algorithm or
scientific acceptance remains with its existing owners.

## Figures and worked-example plan

Use reproducible vector diagrams/plots and stored reviewed outputs; no new
rendering dependency or automatically executed public calculation is needed.

| Figure / example | Teaching purpose | Evidence boundary |
| --- | --- | --- |
| Balls, expanded balls, probe center and swept sphere | Distinguish the modeled geometric sets. | Schematic, with explicit labels; no measured molecular conclusion. |
| One tetrahedron, one gate and their candidate centers | Explain cell-center constraints, local obstacle lists and active sets. | Worked frozen tetrahedron; refer to independent analytic references. |
| Same mesh, several probe queries | Show thresholds, resident/connector/contact states and decomposition. | Reuse existing probe anchors; do not add geometries or tune thresholds. |
| Components linked to a virtual exterior root | Explain removing OCEAN and recording separate exterior contacts. | Algorithm diagram, distinct from a physical trajectory. |
| Four hull patches versus one native link | Explain boundary connectivity and the #151 gap concretely. | Link the canonical tetrahedron figure/certificate; preserve bytes. |
| Wet/dry incidence, walls and molecular participants | Separate banks, boundaries, relief and interfaces. | Labeled schematic; future protrusion segmentation stays proposed. |
| Capacity hierarchy, probe axis and time axis | Keep three meanings of persistence separate. | Schematics plus existing helper tests; no new MD qualification. |
| Public finding with source/context/support links | Make advanced inspection discoverable. | Match actual current public/native objects and availability. |

The tetrahedron is the running teaching example, not a complete demonstration
of every feature family. Reuse `closed_shell` and `shell_with_opening` for sealed
and accessible controls. Old hierarchy/interface fixtures can explain existing
code when clearly labeled; they do not become newly qualified BenchLab cases.
Select figures from the canonical study pages with attribution/context links,
not duplicate editable evidence directories. Prefer Markdown/MyST for the main
narrative; a small dedicated notebook is useful only when interaction or an
executed derivation materially helps and has its own input/output contract.

## Authoring order and completion gates

All documentary actions below belong to #170. They do not reorder the active
scientific sequence or make #170 a replacement for scientific issues.

1. Review the proposed scope, terminology and chapter dependency order. Build a
   notation sheet and a source-to-claim checklist before writing the narrative.
2. Author the overview/model/capacity/decomposition/result spine and the
   tetrahedron explanation together. Include local-versus-physical limitations
   at the relevant inference, not only in a final warnings page.
3. Add exterior/classification, dry/interface and hierarchy chapters. Reconcile
   stale developer prose in bounded edits without deleting decision history.
4. Add scale/dynamics, measurement/numerical and validation chapters, references
   and detailed appendices. Existing open scientific issues remain visible; a
   chapter can explain an unresolved question without waiting for its fix.
5. Integrate reviewed pages into `docs/index.ipynb` navigation, cross-link the
   User guide/API/BenchLab, and check the complete route for introductory and
   advanced readers. Preserve existing public addresses. Avoid publishing a
   menu of empty placeholder chapters as if the complete explanation existed.
6. Verify citations/metadata, terminology, dimensions, status/issue links,
   notation and relevant worked calculations. Run bounded example checks only
   where needed and a one-worker Sphinx build; keep notebooks execution-off in
   ordinary documentation builds. Documentation compilation does not qualify
   scientific behavior, installed packages or the support matrix (#16), and
   publication identity/deployment retains its separate #18 gate.

Before declaring the section complete, a reader should be able to reconstruct
the actual algorithm from the explanation, distinguish its mathematical target
from the implemented approximation, interpret a real current Topography result,
locate the independent evidence, and identify which intended topographic
entities remain provisional or unimplemented. The source-backed proposal is
the first deliverable under #170; authoring/integration remains open.
