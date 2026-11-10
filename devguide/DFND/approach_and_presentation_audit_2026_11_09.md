# DFND approach and public presentation: cross-source audit

Date: **2026-11-09, America/Mexico_City**. Audited source:
`9c8fbc4b447212b5704c2b2f5df4280e01ea4ad4`.
Public entry: [DFND: Theory and Method](../../docs/content/dfnd/index.md).
New documentary follow-up: [#173](https://github.com/uibcdf/topomt/issues/173),
with an [open report](../pending_bugs/dfnd_method_book_semantics.md).

This is the requested audit, not another implementation pass. The public book,
scientific kernels, catalog rules and historical study artifacts are unchanged.
Earlier deliveries #170/#172 remain completed, dated work; their passing checks
do not establish exhaustive semantic coverage. The pre-existing human change
in `topomt/_version.py` is excluded from the audit and delivery.
Findings below describe this fixed revision. For current status use the owning
issues and maintained comparative register; this dated audit is not a separate
present-day limitation list or a paper-ready claim register.

## Assessment

The presentation has **broad topic coverage, a useful conceptual order and good
scientific restraint**. It explains much more than pocket detection: finite
decomposition, boundaries, the dry side, interfaces, hierarchy, scale, time,
measurements, provenance and validation. Its separation of mathematical reference
objects, discrete implementation and independent evidence is a major strength.

It is **not yet a fully reconstructable and internally consistent specification**
of every supported DFND policy. A statement about shared-face permeability is
false for a supported non-default branch. Several fixed/default choices and
geometric observables are underspecified. Developer documents still contain
incompatible physical interpretations that the public book correctly qualifies.

For an introductory reader, the overview-to-tetrahedron route is followable.
For someone reproducing non-default behavior or implementing DFND independently,
the account needs the targeted additions below. This is an editorial assessment;
no novice-reader usability study was performed. A new section or wholesale
rewrite is unnecessary.

| Question | Verdict |
| --- | --- |
| Are the principal topics present? | Yes, including intended extensions and their limits. |
| Does the explanation generally match the current algorithm? | Yes, with the confirmed incidence/admission exception below. |
| Can every important decision be reconstructed from the book? | Not yet; several derived policies and observable definitions are missing. |
| Is the theoretical justification complete? | No. Its outstanding physical/numerical gates are real research work, mostly acknowledged explicitly. |
| Can a reader follow the basic example? | Yes; the executable reader guards cover the tetrahedron workflow. |
| Is the account a completed biological validation or originality argument? | No, and it appropriately avoids claiming either. |

## Review boundary and sources

The review covers all **21 Markdown pages** reached from the DFND landing page,
its downloadable example, the relevant source operators and current issue state.
It uses the current contracts, original design/theory records and the existing
three-case evidence. It does not claim to re-audit every historical DFND note,
every supported provider, all protein behavior or the entire test suite.

| Boundary | Sources inspected |
| --- | --- |
| Input/carrier/query | [Configuration](../../topomt/dfnd/config.py), [network](../../topomt/dfnd/graph.py), molecular/array entry routes and immutable input context. |
| Local geometry | [Clearance solvers](../../topomt/dfnd/core/clearance.py), scalar/batch active-set construction and [volume operators](../../topomt/dfnd/core/solvent_volume.py). |
| Interpretation | [Typed components and descriptors](../../topomt/dfnd/components.py), [classifier](../../topomt/dfnd/classify.py), [public promotion](../../topomt/dfnd/api.py), [maturity declarations](../../topomt/dfnd/output_status.py). |
| Relations/time | [Interface prototype](../../topomt/dfnd/interfaces.py), [skeleton helpers](../../topomt/dfnd/centerline.py), [lineage](../../topomt/dfnd/lineage.py), [identity](../../topomt/dfnd/identity.py), [data/query views](../../topomt/dfnd/data.py). |
| Theory/design | [Core reconstruction](core_theory_review_2026_11_06.md), [mathematical definitions](Mathematical_Definitions.md), [residence/transit contract](residence_transit_contract.md), [abstract contract](abstract_contract.md), [metrics](metrics_contract.md), [numerical policy](numerical_policy.md), [justification](Justification.md), [MOLE analysis](mole_comparison_2026_11_07.md). |
| Current work/evidence | [Three-case direction](three_case_deepening.md), [boundary proposal](boundary_connectivity_contract.md), [boundary checkpoint](boundary_contract_checkpoint.md), [documentation plan](documentation_section_plan.md), [delivery/review checkpoint](documentation_checkpoint.md), frozen BenchLab records and reader/public receiving tests. |

Remote inspection fetched 21 owning/relevant issues and comments from six of
their threads, rather than inferring state from historical prose. The dated
state map is below. Raw readback/replay receipts are retained locally under
`.cache/dfnd-presentation-audit/`; the essential counterexample and reproduction
are included here so this audit does not depend on that cache surviving.

## Reconstruction of the actual approach

DFND's reference model is a union of selected atomic balls. All-atom clearance
defines admissible probe-center positions and their exterior-reachable subset.
Those continuous sets are reference objects; the implementation does not first
construct their complete geometry and then segment it.

The executed carrier is ordinary Delaunay on atomic centers within their finite
convex hull. Local residence uses four vertex balls and a center constrained to
the closed tetrahedron; local gate capacity uses three balls and a center on
the closed face. Active-set candidates are validated and positive improving
clearances retained. Their cached values are reused by probe queries.

A query thresholds residence and face capacity, applies incidence-specific
intrusion policy, and selects resident nodes plus optional nonresident connector
candidates. A finite wet edge requires **both endpoints and both incident face
admissions**. Removing OCEAN leaves finite transit components with separate
resident regions and hull contacts. Whole-face edge adjacency groups those
contacts into native exterior links.

Dry banks use the complement of finite transit nodes. Under face adjacency,
both incidences of a shared face must be nonpermeable; edge/vertex modes use
different grouping rules. This is a complementary node view, not a physical
solid/liquid partition or the graph-theoretic complement of wet edges.

The catalog first applies the zero-wall resident Percolating override, otherwise
the link/residence table. Morphology refines one-link resident concavities.
Public promotion emits supported wet families and Mouth children for the
pocket/channel compatibility families. Dry relief and fully localized molecular
interfaces are not thereby complete public feature systems. Skeletons and
matching/tracks are downstream geometric helpers, not dynamics or fluid flow.

This is a coherent architecture for explicit supports, repeated probe questions
and coupled topographic descriptions. Its physical fidelity depends on the
uncompleted gates below; the architecture alone supplies no topology-equivalence
theorem, universal performance claim or demonstrated novelty.

## Coverage of the public book

| Chapters/part | What is already explained well | Remaining audit point |
| --- | --- | --- |
| Index and overview | Full pipeline, undirected meaning of flow, two reader routes and question navigation. | Bring a compact implemented/provisional/proposed map to the opening; current scope is dispersed. |
| Geometry and probe | Ball model, signed clearance, strictness, fitting versus reaching, Delaunay/Voronoi and power-distance distinction, nonperiodic single-frame scope. | A spatial cell/face/candidate-center illustration would make the notation easier to learn. |
| Local capacities and derivation | Constrained max–min problems, active sets, positive-result clamp, local versus all-atom exclusions and numerical qualifications. | State the actual apex test and distinguish owner incidences (F1). No general solver-completeness proof is established. |
| Network and decomposition | Root removal, resident regions, connectors, reporting and a clearly abstract graph illustration. | Correct the shared-permeability statement and two-sided predicates (F1). |
| Exterior and boundaries | Native link / physical patch / public Mouth distinction, carrier areas and independently certified tetrahedron contrast. | Retain #151's open physical-refinement gate; prose is not its runtime implementation. |
| Classification | Override order, morphology, PCA, missing-value rules, confidence/marginality and name-independent support identity. | Complete the center/descriptor reference and avoid implying every field has an independent physical witness (F2/F3). |
| Dry banks and interfaces | Transit complement, relief versus bank components, participants versus geometric banks, localization and contact-only interfaces. | Explain bank incidence policy, interface contribution defaults and reporting interaction (F1/F2/F5). |
| Hierarchy and paths | Depth convention, access/funnel fit, merge prominence, actual shortest-distance skeleton objective and scope. | Disclose fixed persistence floor, branch helper, and overloaded notation (F2/F4/F7). |
| Scale and dynamics | Geometry reuse, native `at_probe` versus promotion, nested availability, nonmonotone counts, three persistence axes and matching limits. | State matching defaults or link a precise method reference (F2). |
| Measurements | Carrier/bare-empty/center/swept distinctions, local versus all-atom exclusion, MC formula and quadrature uncertainty limits. | Define the fast sampling stencil and carrier centroid (F2/F3); numerical fixes remain #75. |
| Results/provenance | Actual public/native trace, source maps, support versus occurrence, atom roles, optional attribution and unavailable versus empty. | Link a many-cell/Mouth trace and clarify that centroid placement is not a clearance certificate (F3/F6). |
| Numerics and validation | Model versus numerical changes, degeneracy, units, responsible execution, evidence ladder and honest case scope. | Good account of current limits; does not discharge #75/#76/#151 or installed qualification. |
| Notation, properties, algorithm and references | Conditional arguments, exact discrete graph meaning, pseudocode, development history and selected antecedents. | The pseudocode shares the incidence ambiguity; notation `g` changes dimension (F1/F7). |
| Worked tetrahedron | Exact downloaded inputs, three independent probe predictions, source/public correspondence, `None` descriptors and mesh reuse. | The single cell has no internal shared face and cannot guard F1 or teach a public Mouth by itself (F6). |

## Findings and recommendations

### F1 — Confirmed error: shared capacity is not shared post-policy admission

**Priority: P0, documentary correctness. Verification: reproduced. Owner: #173.**

The [network chapter](../../docs/content/dfnd/network_and_decomposition.md),
lines 30–33 at the audited revision, says the two sides use the same face
capacity/permeability decision. Only the **capacity** is necessarily shared.
The [implementation](../../topomt/dfnd/graph.py) computes:

- one `R_gate` per unique face, scattered identically to its two incidences;
- `_gate_intrusion_suspect` per `(tetrahedron, face)`, from that owner's opposite
  apex and the distance to the supporting face plane;
- per-incidence admission after the chosen intrusion policy;
- `_build_transit_edges` as the conjunction of both admissions and both finite
  transit endpoint states.

The apex test uses its **bare atomic radius**, not `radius + probe`. It tests
plane distance, not overlap of the actual free triangular patch. Degenerate
normal handling also marks suspicion. This is a plane-contact heuristic: it
does not test the disk's location on the triangle and omits probe expansion.
It is not a complete probe-expanded obstacle test or a physical certificate.

Replay of the unchanged three cases, zero extra tolerances, using their received
input/radius policies and changing only intrusion policy to `block_suspect`:

| Frozen input / probe | Internal unique faces | Unequal apex flags | Unequal post-policy states |
| --- | ---: | ---: | ---: |
| `regular_tetrahedron`, 1.2 Å | 0 | 0 | 0 |
| `closed_shell`, 0.2 Å | 312 | 110 | 75 |
| `shell_with_opening`, 1.4 Å | 282 | 101 | 27 |

For closed-shell face **6**, source atoms **[13, 23, 26]**, the two `R_gate`
values are identically **0.1198879391121351 nm**. Owner **1**, neighbor **7**,
is `permeable` without flags. Owner **7**, neighbor **1**, is `non_permeable`
with `intrusion_suspect` and `blocked_by_intrusion_policy`. **Both** report
`transit_edge=False`.

This supports a correction of the explanation. It does **not** establish a
physical crossing failure, an incorrect kernel edge rule, or a new comparative
finding. The default `flag_only` branch remains consistent with equal face
states. The pseudocode and dry-bank explanation need the same incidence scope;
dry face adjacency checks both sides for nonpermeability.

### F2 — Important choices cannot yet be reconstructed from the prose

**Priority: P1, reference completeness. Verification: inspected. Owner: #173.**

| Current choice | Source definition | Missing explanation |
| --- | --- | --- |
| Capacity-motif floor | `components._attach_capacity_motifs(..., min_persistence=0.1)`, called without an override: **0.1 nm = 1 Å**, inclusive `prominence >= floor`. | The book calls it selected without its value or the fact that no public query knob currently selects it. |
| Fast empty-volume stencil | `core.solvent_volume._simplex_lattice_weights`: four nonnegative integer weights summing to resolution 8, shifted by 0.5 and divided by 10; **165** interior points. `graph` fixes resolution 8. | Deterministic sampling is described, but not the actual stencil, default or public-control availability. |
| Bank-derived interface call | `interfaces.classify_interface_components`: at least two retained bodies with at least **3** atoms each and smallest retained-body fraction at least **0.15**. | The chapter mentions thresholds without stating them or the retained-body denominator. |
| Shared lining assignment in that prototype | `body_labels_from_dry_components` ranks banks by cell count; the first/largest bank wins a shared atom. | General overlapping atom roles are explained; this helper's exclusive intermediate labels are not. |
| Lineage matching | `match_results` and `assign_tracks`: default **min_jaccard=0.2**, exact support match preferred. | Heuristic scope is clear; the operational default is absent. |

Not every internal constant belongs in introductory prose. A compact advanced
operator/defaults table, with explicit source/version and public/private control
status, would solve this without adding chapters. A future change of a fixed
choice must update that reference; these values are not scientific calibration
recommendations.

### F3 — The public center needs an explicit geometric definition

**Priority: P1, observable meaning. Verification: inspected. Owner: #173.**

`graph._component_center` computes the volume-weighted average of complete
carrier-tetrahedron barycenters over the component's **transit node support**,
with an unweighted fallback for zero total carrier volume. Public promotion
copies this center into a quantity. It is distinct from each raw tetrahedron's
optimized residence center and from the point cloud used for morphology PCA.

The tetrahedron happens to give the same centroid in these roles. Its example
therefore hides the distinction. In general this averaging does not establish
that the point is all-atom-free, attains the component's maximum clearance,
lies on the skeleton or defines a valid ligand-placement site. This is a
consequence of the operator, not a newly measured collision on a protein.
Add its formula/support and availability meaning to measurements and results.

### F4 — Existing secondary skeletons are not discoverable in this account

**Priority: P2, implementation coverage. Verification: inspected. Owner: #173.**

The primary shortest-distance skeleton is described accurately. The existing
`centerline.channel_branch_skeletons` helper also connects extra mouths to the
primary path through shortest resident-graph routes, returning visual secondary
branches. It is absent from the chapter. Mention it beside the primary helper,
its endpoint policy and its failure/empty behavior. It still does not enumerate
every internal branch or certify physical transport.

### F5 — Developer doctrine and public explanation can teach incompatible models

**Priority: P0 for scientific reuse; verification: inspected. Existing owners below.**

| Maintained/historical text at the audited source | Conflict with the public explanation | Owner |
| --- | --- | --- |
| `Mathematical_Definitions.md` §3.4 and `residence_transit_contract.md` interpret nonresident connectors as physically passing through. | Under exact existential residence, a valid center path inside a closed cell implies local residence at that point. The public properties appendix correctly states this condition. | #76 |
| `abstract_contract.md` calls a dry node a cell where the probe cannot reside. | Current bank membership is the complement of finite transit, excluding enabled nonresident connectors. | #76, with public representation under #60 |
| `residence_transit_contract.md` and `numerical_policy.md` call tolerances physical allowances for flexibility. | The public book correctly treats them as declared decision bands without a calibrated flexibility/free-energy model. | #76 |
| `metrics_contract.md` calls the MC width rigorous and the quadrature route exact/an oracle. | The current measurement chapter correctly explains finite-sample endpoint failure and fixed-order integration error. | #75 |
| `components._attach_capacity_motifs` comments claim transit edges exclude intrusion suspects by construction; its morphometric comments identify radii with future sealing/death events. | `flag_only` retains suspect incidences; future support/contacts can change. The public book appropriately qualifies both statements. | #76; documentary reconciliation under #173 |

The older core-theory review already identified important parts of this drift;
these are not newly discovered physical failures. Some files still call
themselves definitive/current, so a reader cannot safely treat all devguide
prose as either historical or normative. Reconciliation needs explicit dated
status/precedence and a scientific decision where the contract itself changes.
Preserve history; do not silently delete or retrofit its evidence. Closing a
documentation task cannot substitute for #75/#76 acceptance.

One further **inspected contract question** belongs to #60/#61: typed interface
annotation consumes the compatibility-filtered `result['dry']['components']`,
whereas wet typed components are built from raw wet records. Changing `min_size`
can therefore change the bank inputs available to that derived annotation.
This audit has not established a physical misclassification for those changes.
Specify/test the intended filter-versus-descriptor contract before teaching that
all derived observations are reporting-independent. The raw decomposition's
independence is a narrower, already justified statement.

### F6 — The reader needs a clearer map from introductory coverage to advanced scope

**Priority: P1/P2, pedagogy. Verification: reviewer judgment. Owner: #173.**

The index has useful routes, and the answered checks improve self-study.
However, its broad opening can precede the reader's understanding that wet
public features, native dry descriptors and future relief/interface operators
have different availability. Put a small status table near the beginning with
links to precise chapters; keep software maturity separate from physical proof.

The existing [three-case public walkthrough](../../docs/content/benchlab/synthetic/public_topography.md)
can supply the many-cell/Mouth trace missing from the single-cell example.
Link directly to that evidence rather than adding a new case or duplicating
stored results. A geometric tetrahedron/face/candidate-center drawing would also
bridge the current abstract graph and scalar formulas. These are editorial
recommendations, not evidence that a novice currently fails to understand DFND.

Retain the present section structure. Put concise conclusions before lengthy
qualification, then link detailed assumptions and boundaries. The necessary
cautions should remain explicit without making the reader reconstruct the
positive algorithm from a succession of exclusions.

### F7 — One symbol changes dimension inside the hierarchy chapter

**Priority: P2, notation. Verification: inspected. Owner: #173.**

The funnel gradient is `g`, dimensionless; the joining gate is later also `g`,
with units of length in `peak - g`. The notation appendix lists only the first
meaning. Use distinct symbols, such as `g_funnel` and `R_join`, and synchronize
the sheet and formulas. This is not an error in the executed arithmetic.

## Scientific questions that prose cannot close

The book's caution is appropriate. The following boundaries should stay visible
and owned rather than being described as missing explanatory paragraphs:

- **Local optimization and paths (#76):** candidate completeness/conditioning,
  omitted obstacles, free subsets within cells, compatible face contacts and
  the interpretation of nonresident connectors.
- **Physical boundaries (#151):** complete all-atom free-patch decomposition,
  seam connectivity, region attachment and the final Mouth/Percolating decision.
  Four tetrahedron patches, one native link and zero public Mouths remain
  different observations.
- **Measurements (#75):** convergence/error evidence and boundary-safe finite-
  sample uncertainty. The compatibility name `exact` has not become an exact
  volume method through a prose correction.
- **Public adoption (#60/#61/#62/#63):** neutral recoverable support, participants,
  typed/localized relations, contextual evaluations and provider capabilities.
  Saved native context/source tracing is implemented progress, not completion
  of all these contracts.
- **Scope and delivery (#16/#18):** source examples do not qualify an installed
  Python/platform matrix or prove that this version is deployed on the website.

Selected antecedents are acknowledged responsibly. This audit does not reopen
an external-code/literature survey or decide scientific novelty. The biological
and comparative claims avoided in the book should remain avoided until their
own target-specific evidence exists.

## Issue state and action order

Remote state checked at this audit (local date 2026-11-09; UTC readback extends
into 2026-11-10). Search results were followed by individual issue fetches and
relevant comments, so an earlier open comment does not supersede later closure.

| Issues | Readback state | Audit use/disposition |
| --- | --- | --- |
| #170, #172 | Closed | Earlier method-book delivery and reader refinement; retained history, not exhaustive scientific qualification. |
| #59, #146, #147, #148, #149, #150 | Closed | Accepted conceptual decision, bounded receiving/dispatch and three independent certificate deliveries. |
| #157 | Closed | Attribution implementation is delivered in source; do not resurrect its old open comment as current absence. |
| #75, #76, #151 | Open | Existing scientific/precision/physical-boundary work. Reuse these owners. |
| #60, #61, #62, #63 | Open | Partial/public adoption and intended follow-on contracts. |
| #171 | Open | Explicit `radii_model` dispatcher warning; the worked example verifies the current default and does not fix it. |
| #93 | Open | Proposed numerical backend migration; current source has not already migrated by virtue of this issue. |
| #16, #18, #64 | Open | Qualification, deployment and pre-existing whole-site documentation diagnostics. |
| #173 | Open, created by this audit | Bounded public-book correctness/completeness follow-up F1–F4/F6/F7; no runtime fix claimed. |

Recommended order: first correct F1 and mark the competing developer accounts
through #173/#76/#75; next complete the operator/center reference F2/F3; then
add the small navigation/example/notation improvements F4/F6/F7. Scientific
development remains on the same three frozen cases under its existing owners.
Every concrete recommendation has an issue owner; this document creates no
independent hidden queue and closes no scientific limitation.

## Reproduction and evidence receipts

The incidence replay uses the existing public receiving helper, which restores
full-precision coordinates after loading dummy molecular topology, checks radii
and retains original source mapping. It does not substitute rounded PDB input.
Execution environment: Linux, Python **3.14.10**, NumPy **2.5.4**, SciPy
**1.18.1**. Face IDs refer to this received mesh; the source-atom triple is also
given so the observation is not identified only by a local integer.

```python
import runpy
from topomt import pyunitwizard as puw

receiving = runpy.run_path('tests/test_benchlab_public_topography.py')
topography, _, _ = receiving['public_result']('closed_shell', 0.2)
query = topography.dfnd.at_probe(
    puw.quantity(0.2, 'angstroms'), gate_intrusion_policy='block_suspect'
)
pair = [f for f in query.raw['faces'] if f['face_id'] == 6]
assert len(pair) == 2
assert pair[0]['R_gate'] == pair[1]['R_gate']
assert {f['permeability_state'] for f in pair} == {'permeable', 'non_permeable'}
assert not any(f['transit_edge'] for f in pair)
```

Input JSON SHA-256 values, unchanged during the audit:

| Case | SHA-256 |
| --- | --- |
| `regular_tetrahedron` | `8634f70afdaf21cb8388887f5f80ae73dc36ef4f043198a10b525a93ebde5ce3` |
| `closed_shell` | `ef19995751b2df58c8b1556011f74fa4774e924b9cd499138b8741988b650157` |
| `shell_with_opening` | `3a62da60d3812707f254d7a393f61e9f2f241fa103a9a546afa2d12d1d2b4b77` |

The three-case replay completed in **3.11 s**, peak RSS **285 MiB**. It ran
sequentially on one CPU with one numerical thread, 6 GiB address-space and 60 s
CPU limits. Preflight found about 56.5 GiB available of 60.5 GiB physical RAM,
zero memory PSI and no active swapping in the live sampled interval. Slurm
commands exist but the bounded socket check is denied in this session; no
allocation or resource reservation was claimed. No provider submission,
dependency installation, upstream checkout modification or protein analysis
was needed.

Executed checks for this delivery:

- **20 passed**, 1.93 s test time / 4.26 s process wall time, peak RSS 282.3 MiB:
  `tests/test_dfnd_documentation.py`, `tests/test_reporting_protocol.py` and
  `tests/test_comparative_findings.py`, with Pytest Receptor and one CPU/thread.
  This includes all four executable book-reader tests. It is not a full DFND or
  scientific qualification panel.
- The exact Python reproduction printed above executed successfully. All
  **32 local Markdown links** in the audit/open report resolve. Standalone MyST
  rendering of the audit, with relative links kept as ordinary hyperlinks and
  their targets checked separately, reports zero warnings.
- Fresh complete Sphinx HTML build: exit 0, **10.08 s**, peak RSS **273.9 MiB**,
  one worker. Its **21 DFND pages and 1,872 local links/assets/anchors** pass
  inspection. There are zero section warnings and eleven unchanged warnings
  elsewhere, already owned by #64. Building the book does not detect F1's
  scientific wording error.
- Report indexes and offline comparative checks pass. Live readback of the
  five finding cards, hub and linked issues also passes reconciliation: the
  tetrahedron-boundary and volume findings remain current, with #151/#75 open.
  No scientific finding state, paper claim or historical artifact was changed.

The audit's rendering/readback/reproduction receipts remain in its owned cache.
No Python product code changed, so no new lint/type or full-matrix qualification
is claimed. Existing missing physical-view targets remain pending acceptance;
no passing test is used to deny the reproduced F1 prose mismatch. The #173
correction itself remains unimplemented and open.
