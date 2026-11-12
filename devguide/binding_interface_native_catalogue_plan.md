# Native binding-interface characterization catalogue

Revision **2**, 2026-11-12. **Cross-component proposal; no new scientific
implementation or qualified native workflow is delivered by this document.**

Revision 2 clarifies TopoMT's independent regional physicochemistry under
[#198](https://github.com/uibcdf/topomt/issues/198). The
[published first edition](https://github.com/uibcdf/topomt/blob/a13b9b2725bd8a4edd851441d1a5a53720e0f3ea/devguide/binding_interface_native_catalogue_plan.md)
and its BindingMT handoff remain intact; BindingMT's catalogue leadership is not
withdrawn and new shared acceptance is not inferred from this local refinement.

Scientific lead and implementation roadmap:
[BindingMT #112](https://github.com/uibcdf/bindingmt/issues/112).
Shared agreements:
[MolSysSuite #195](https://github.com/uibcdf/molsyssuite/issues/195).
TopoMT contribution and review:
[#197](https://github.com/uibcdf/topomt/issues/197), with its
[bounded handoff record](pending_proposals/native_interface_catalogue_handoff.md).

This is TopoMT's maintained contribution for owner review. BindingMT owns the
binding-domain catalogue and its accepted implementation decisions. Hosting this
proposal here does not transfer that ownership or establish shared acceptance.
Once decisions are received, link their authoritative owner records and retain
this proposal's dated disposition instead of maintaining competing roadmaps.

## 1. Purpose and intended user experience

Offer researchers a useful native characterization of a specified molecular
binding interface through BindingMT. Start with contacts, accessible surfaces
and burial; extend with chemical organization and qualified topographic results.
An ordinary calculation must work without PISA, its installation, server or
saved outputs. External methods remain optional providers and comparators.

The scientific goal is a coherent collection of explicitly defined observations,
binding-specific derived descriptors and meaningful comparisons. Aim to cover
useful established characterizations and demonstrate improvements where evidence
supports them. Accuracy, applicability, reproducibility, usability and resource
efficiency are separately testable objectives; no general superiority is claimed.

A routine user requests a small named set of calculations and receives a concise
summary, limitations and a saveable result. An expert can inspect definitions,
parameters, inputs, source maps, numerical controls, individual contributions and
original owner results, or compose observations already calculated elsewhere.

The first native result should remain useful without a topographic analysis.
TopoMT can subsequently explain how its footprints relate to patches, concavities,
cavities, channels or other supported spatial organization.

## 2. Relationship to the reviewed BindingInterface work

The starting design is BindingMT's
[revision 2 at 5aa21b1](https://github.com/uibcdf/bindingmt/blob/5aa21b1aaf27ee7708e5a7bb4fe58bd0300d49f0/devguide/binding_interface_design.md).
Its [reviewed implementation plan at d69315d](https://github.com/uibcdf/bindingmt/blob/d69315dfebc49ddd8c2da1999955edc078fd8893/devguide/binding_interface_implementation_plan.md)
already separates the data core, molecular correspondence, optional PISA intake,
native pharmacophoric receiving and consumer controls. Our favorable reviews of
that model stand. This proposal extends the calculation roadmap. Work-plan
revision 2's independent footprint persistence, historical/current-use controls
and aligned-map requirements are retained for the native calculation track.

Proposed decisions for BindingMT to record:

1. Lead a native characterization catalogue as a binding-domain capability.
2. Add a useful native contacts milestone, followed by surfaces/burial, alongside
   the existing data-core work. Make this the ordinary scientific route.
3. Preserve the PISA T0/T1 branch, frozen evidence and agreed controls as separately
   tracked interoperability work. Record changed priority and required scope
   explicitly; do not silently delete an earlier commitment.
4. Keep later chemistry, topography, ensembles and energetics independently
   admissible. Their unfinished profiles do not block a useful native baseline.
5. Close finite owner agreements for the operations actually selected, rather
   than require every future molecular or interface contract before development.

The existing association/realization/observation distinctions, immutable evidence,
analysis-level outcomes, scoped assurances and many-to-many site relationships
remain applicable. Initial BindingSite work under
[BindingMT #111](https://github.com/uibcdf/bindingmt/issues/111) stays independent;
optional exact site references need not require a live BindingSite instance.

## 3. Scientific ownership and dependency direction

| Concern | Owner and responsibility |
| --- | --- |
| Binding question and characterization | BindingMT: participants/grouping, relevant states/process, catalogue, binding-specific compositions, comparisons, interpretation and public workflow. |
| Molecular operations | MolSysMT: representation, chemistry, selections, coordinates, correspondence, generic contacts/interactions, radii and surface calculations. |
| Topographic organization and regional physicochemistry | TopoMT: DFND and other topographic methods, spatial supports, classifications, feature-specific physicochemical observations, relations and evaluations it produces. |
| Other specialist observations | Their scientific owners; for example PharmacophoreMT retains native hypotheses and matching semantics. |
| Shared meanings and receiving | MolSysSuite coordinates exercised contracts; each component owns its implementation and adoption evidence. |

BindingMT can implement scientifically meaningful derived descriptors and
binding-specific analysis protocols. Independently useful molecular kernels or
general decomposition tools belong in MolSysMT; specialized topographic kernels
belong in TopoMT. Compose existing public tools when they suffice. Report a
concrete missing tool to its owner before introducing a consumer implementation.

TopoMT is authoritative for its topographic associations and realizations.
BindingMT is authoritative for its binding question and characterization. A
BindingMT declaration does not register a TopoMT feature, and a topographic
descriptor does not establish biological binding. Exact references connect the
perspectives without independently editable copies of spatial records.

The native molecular baseline uses MolSysMT and must not require TopoMT or PISA.
TopoMT enrichment is selected explicitly. Neither MolSysMT nor TopoMT needs a
mandatory BindingMT import. The current PISA adapter can be reused without
relocation or duplicated parsing; any later adapter-ownership change needs its
own migration decision and consumer evidence.

TopoMT's responsibility includes the chemical character presented by a pocket,
wall, channel or spatial interface independently of a chosen ligand. MolSysMT
provides molecular chemistry; TopoMT maps it onto its actual supports and can
provide spatial distributions, appropriate area-weighted summaries and chemical
patches. BindingMT can consume these results and add association-specific
observations. These are complementary contexts, not exclusive ownership of every
chemical aggregation. The standalone TopoMT layer is tracked in
[#198's staged proposal](pending_proposals/topographic_physicochemistry.md).

## 4. Inspected starting capabilities and remaining qualification

| Starting point | Inspected fact | Limit of this evidence |
| --- | --- | --- |
| MolSysMT `ff25f120` | Public `structure.get_contacts` returns geometric contact maps or pairs under a declared threshold; relevant selection/index options exist. | Its array/pair output is not automatically a typed scientific analysis receipt. BindingMT must retain effective inputs, arguments, maps and actual checks. |
| Same MolSysMT source | Public `physchem.get_sasa` implements Shrake-Rupley sampling with a native Rust route, explicit probe, sampling and periodic controls. | Source inspection does not qualify the installed extension or the composed BindingMT calculation. |
| Same MolSysMT source | Native interaction families and analysis/query objects exist. | Chemical recognition, state, complete feature participation and each receiving route retain their own requirements. |
| Same MolSysMT source | `physchem.get_area_buried` looks up a Rose residue reference table. | This is not geometric interface burial. Similarly, tabulated `get_surface_area` is not conformational SASA. |
| BindingMT `d69315d` | The cited plan describes data, correspondence, optional provider and native consumer increments, including derived-footprint persistence and crossed historical/current-use controls. | Its proposed interface APIs and new native catalogue are not runtime qualification. |
| TopoMT `3a8ee979` | Original PISA saved receiving and source-scoped DFND evidence exist. | Complete neutral participant/support/evaluation adoption remains separate under #60/#61/#62; saved PISA records are not native Topography promotion. |

These are reproducible review baselines, not dependency floors or a claim that
all current heads are unchanged. Before execution, refresh source and native
artifact identities, import origins and eligibility for the chosen workspace.
No sibling implementation or installed environment is changed by this proposal.

## 5. Initial native calculation profile

Start with two explicit, nonempty, disjoint participant atom populations, A and B,
on one chosen Cartesian structure. The first profile uses admitted reference
chemistry, fixed coordinates and explicit radius/hydrogen policies. It excludes
inter-participant covalent links and performs no chemical completion, relaxation,
alignment, crystal expansion or periodic reconstruction implicitly.

For the first surface comparison, the evaluated environment is exactly A union B.
Solvent, cofactors, metals, ions and additional chains require explicit inclusion
and interpretation. Do not silently remove them or infer an experimental state
from a selection name. Unsupported chemistry and missing required radii fail the
affected calculation with an informative diagnosis.

Participant labels are local names. Record original occurrence/source references,
resolved selections, original/local atom and structure maps, effective chemistry,
frame/image, all effective parameters and performed checks. Matching counts or
equal numeric indices do not establish correspondence. Data-only declarations
retain unresolved references without pretending that molecular checks occurred.

This restricted calculation profile is not a universal interface definition.
Later profiles can admit overlapping groups, covalent interfaces, additional
environments, modalities or periodic systems with their own semantics and tests.

## 6. Catalogue structure and proposed families

Maintain descriptive definition identifiers independently of display order. Each
entry separates observable definition/version, algorithm/version and parameters.
Two algorithms targeting the same observable are not assumed numerically
equivalent. An intentional change of scientific meaning requires a new definition
version and an explicit compatibility decision.

Start with a maintained document and ordinary public method dispatch. Select
concrete result fields from real workflows; no universal plugin, graph, molecular
snapshot or provenance framework is required by this plan.

The identifiers below are proposed descriptive entries, not frozen API names.

| Entry | Intended observable | Initial route / maturity |
| --- | --- | --- |
| `atomic_contacts` | Inter-participant pairs, distances and counts under a named geometric predicate. | First native BindingMT calculation using MolSysMT. |
| `residue_contacts` | Explicit reduction of atom contacts to unique residue pairs and participant populations. | Native contact milestone; retain atom-level evidence and reduction policy. |
| `contact_footprints` | Unique contacted atoms/residues on each participant, with per-contact provenance. | Native contact milestone; distinct from buried-area or topographic supports. |
| `steric_overlaps` | Radius-based overlap witnesses and summaries with a stated radius model. | Subsequent geometric descriptor; no universal quality or binding decision. |
| `solvent_accessibility` | Atomic/aggregated SASA for the declared structure and occluder population. | Reuse native MolSysMT; qualify composed receiving. |
| `interface_burial` | Per-participant SASA loss, total loss, optional mean-side area and mapped contributions. | Surface milestone; close the reusable decomposition contract with MolSysMT. |
| `chemical_interactions` | Admitted H-bond, ionic, hydrophobic, aromatic and other chemical observations. | Family-specific native receiving, not a universal count from distance alone. |
| `physicochemical_partition` | Explicit polar/apolar/charge-class composition of a stated membership or surface measure. | Owner chemical classifications, BindingMT binding-domain aggregation and reuse of qualified TopoMT regional observations. |
| `buried_unsatisfied_polar_sites` | Buried polar recognition sites lacking a partner under an explicitly evaluated interaction/environment criterion. | Later candidate requiring qualified burial, complete chemistry and evaluated partner coverage; missing evidence cannot become unsatisfied-site evidence. |
| `interaction_network` | Declared residue/group network and scoped connectivity/contribution descriptors. | Later profile retaining edge definitions, multiplicity and comparison policy. |
| `topographic_organization` | Supported patches, gaps, concavities, cavities, channels and accessibility related to the binding question. | Optional qualified TopoMT results; availability is descriptor-specific. |
| `topographic_physicochemistry` | Spatial chemical characterization conditioned on a stated topographic support, including regional wall contributions and chemical patches. | Independent TopoMT capability under #198, reusable by BindingMT; generic chemical tools remain in MolSysMT. |
| `geometric_complementarity` | A stated surface-fit, orientation, separation or shape-complementarity measure on admitted geometric supports. | Later TopoMT-supported candidate with its own surface model, numerical reference and comparison eligibility. |
| `pose_comparison` | Differences in compatible contacts, surfaces or topographic findings. | Explicit observable/correspondence/coverage and normalization policy. |
| `ensemble_statistics` | Per-structure results and later contact/burial persistence summaries. | Separate sampling, correspondence and weighting qualification. |
| `energetic_observables` | A specified energy or thermodynamic endpoint from an admitted model/method. | Separate future profiles, conditions and uncertainty/convergence evidence. |
| `assembly_inference` | Probable assembly or biological-interface inference under a specified model. | Separate future decision; not implied by a descriptive interface catalogue. |

Prioritize contacts, SASA and burial. A family catalogue is not a promise that
every entry must be implemented before the first useful delivery or #112 closes.
Record the admitted initial scope and issue-backed future disposition explicitly.

## 7. Per-characterization scientific contract

Every admitted entry documents:

- The scientific question, formula/predicate, units and supported input domain.
- The molecular population measured, occluders/environment, output granularity,
  grouping, structure/state/frame and complete requested/evaluated coverage.
- Algorithm, backend, source/native versions, effective parameters, radius and
  chemistry models, numerical tolerances and convergence controls.
- Exact owner analysis/occurrence references, source/local maps, method-specific
  supports, and derivation of aggregates or footprints.
- Mandatory versus optional observations, checks actually performed, remaining
  caller preconditions and applicability at the point of use.
- Computed nonzero, computed zero, unevaluated, unavailable, undefined,
  unsupported and failed outcomes, with causes. An empty request is not a
  completed calculation; a zero denominator is not automatically zero.
- Independent reference controls, qualification scope and current owner issue.
- Offline bibliography and attribution at the meaningful completion boundary.

Known quantities use PyUnitWizard's supported conversion/interchange contracts.
Field identity and dimensionality are checked by the reader. Preserve original
owner definitions and units alongside standardized values; do not infer units
from array shape, field spelling or the current application defaults.

Do not publish a single `valid` or `quality` number as a substitute for these
facts. A failed required child operation cannot yield an apparently complete
successful characterization. An explicitly admitted partial request retains
each omission and the resulting limits on comparison or application.

## 8. Explicit computation, composition and public inspection

There are two complementary workflows:

1. **Requested native analysis:** molecular context, participants and requested
   calculations lead BindingMT to invoke public owner tools and return an
   inspectable binding characterization.
2. **Evidence composition:** supplied owner analyses/findings are related to the
   binding question without silently calculating missing observations.

The existing proposed composition operation keeps its execution boundary. The
calculation entry point's name/defaults are a BindingMT owner decision. Prefer
one concise routine call and composable expert operations over requiring users
to manually assemble the complete persistence record.

Both routes can use the same scientific result model. Summary identifies the
question, participants, requested/completed calculations, criteria, values,
coverage and limitations. Expert inspection resolves original pairs, mapped
membership, effective parameters and derivations. Site links remain optional;
a contact/burial footprint does not automatically delimit a full functional site.

Inspection, copying and core saved reading perform no scientific calculation,
foreign-asset discovery or automatic remote lookup. Explicit native recovery uses
the admitted owner reader. Preserve completed-empty analysis independently of
finding count and preserve original failures independently of current read errors.

Persist derived footprint results themselves through an admitted public save/read
route, including positive and evaluated-empty cases. Saving only their parent
characterization is insufficient. Independent core inspection must retain enough
membership, criterion, provenance and coverage without recovering optional owner
assets or repeating calculation. Preserve an original C0 match as historical
evidence; fresh read does not endorse a changed C1 context. Explicit new use checks
the admitted facts or refuses.

Preservation, molecular correspondence and current-finding applicability retain
their distinct requested guarantees. A molecular handle alone upgrades none of
them. Refuse unqualified stronger requests without returning weaker success.

## 9. Initial calculation recipes and scientific edge cases

### 9.1 Geometric contacts and footprints

Use a declared distance predicate on actual source populations, with explicit
cutoff inclusion/tolerance and periodic policy. A contact threshold, a van der
Waals overlap and a chemically interpreted interaction are different criteria.
Retain pairs and distances; derive participant footprints from their mapped
endpoints. Counts must state unique unordered pairs, directed pairs, unique
atoms or unique residue pairs rather than interchange those populations.

Repeated source selections or copied observations must not create extra atoms
or independent evidence. Retain request/delivery multiplicity separately when
it is meaningful. Reduce to residues through MolSysMT correspondence, preserving
the original atom contacts and chosen aggregation rule.

For the initial footprint profile, unique original-source membership is ascending
within its identified source axis. Local indices follow that order through the
qualified map; never sort those vectors independently. Preserve every contributing
contact/occurrence separately. An independently authored two-nonempty-group overlap
control checks union, repeated contributors and aligned nonidentity maps without
borrowing an original provider's run identity.

For two disjoint nonempty participants, completed no-contact is valid evaluated
zero with empty footprints. A required empty/unresolved participant or failed
distance calculation is a different outcome. Grouping must control the pairs
actually used; unrelated C-D contacts cannot enter an A-B characterization.

MolSysMT's current contact-map representation has a resident-memory cost even
for some pair projections. Select bounded inputs or a qualified owner neighbor
operation when appropriate; do not introduce another contact-search kernel in
BindingMT to bypass an owner representation constraint.

### 9.2 SASA and interface burial

For fixed coordinates, chemistry, radii, probe and surface policy, define:

```text
L_A = SASA_A(A) - SASA_A(A union B)
L_B = SASA_B(B) - SASA_B(A union B)
total_burial = L_A + L_B
mean_side_area = (L_A + L_B) / 2
```

The subscripts name output populations; the parentheses name full occluder
populations. Both side losses remain available. Their equality is not assumed.
The mean is an explicit reporting convention, not another recovered surface.
Atomic/residue contributions must sum to the reported totals within the stated
numerical error. Define a threshold/tolerance before promoting positive area
contributions to a buried membership; it is not a contact-distance predicate.

Isolated participant inputs retain original coordinates, radius assignments and
chemical interpretation with explicit maps. They are calculation contexts, not
relaxed unbound molecular states. Selecting A's output from A union B does not
remove B's occlusion. Use owner-supported construction of the required inputs;
do not silently cap bonds, add H, change protonation or override state labels.

If existing public operations suffice, BindingMT can compose them for this
binding question. An independently useful generic surface-decomposition helper
should be proposed/implemented in MolSysMT. Close that choice before duplicating
a reusable numerical operation or advertising a nonexistent owner API.

Record sampling resolution and convergence. Rigid rotation need only preserve a
sampled estimate within its justified numerical tolerance. Diagnose unexpected
negative losses; do not silently clamp values to hide inconsistent inputs or
numerical problems. A surface unavailable due to unknown radii is not zero area.

A later environment-aware profile can compare A+C against A+B+C. Its conditional
burial differs from the initial isolated-pair definition. Pairwise burial in a
multimolecular assembly is not generally additive, and geometric joint support
or nonadditivity does not establish thermodynamic cooperativity.

### 9.3 Chemistry and physicochemical decomposition

Receive native MolSysMT analyses with exact criterion, effective state, complete
recognition participants and original relation/occurrence correspondence.
Missing donor/acceptor information or required H is not evidence of no H bonds.
Metal/water/aromatic and other specialized profiles retain their owner limits.

Choose chemical classifications explicitly before partitioning counts or areas.
Classes may overlap; an additive partition requires an explicit disjoint policy.
State the numerator and denominator of each fraction and preserve undefined
zero-denominator cases. Chemical category, buried contribution, contacted
membership and inferred functional importance are distinct facts.

An interaction network retains its defining observations. A graph edge, a
connected network or a high contact count is not itself a binding-affinity or
biological-interface prediction. Statistical independence is not created by
repeating a feature in several analyses.

An atomic/residue contribution to area or contact count is not an energetic
hot spot. A buried-unsatisfied-site descriptor must establish evaluated chemical
partner/environment coverage; an unavailable analysis cannot supply its negative
evidence. These interpretations need their own admitted scientific profiles.

### 9.4 Topographic enrichment and comparisons

Request TopoMT observations only where a qualified profile provides their
support/context. Relate findings to participant footprints through an explicitly
defined operation. Coincident coordinates or equal atom sets do not make a
contact footprint and a cavity wall the same scientific object.

Molecular participants are not DFND dry banks. An interface needs neither a
cavity nor a bounded wet region or two banks. Bare contact and multiple
topographic patches remain expressible without inventing a positive region,
volume or primary feature classification.

Comparisons state the observable/definition, intentionally differing inputs,
correspondence, frame, chemistry, coverage and normalization. Two poses of one
pair and different candidate partners need different policies. Unavailable
observables do not become numbers. Later ensemble summaries require explicit
sampling/weights; frame frequency is not automatically a thermodynamic population.

## 10. Resources, method references and persisted evidence

Version scientific resources in their numerical owner's normal package/data
route: radii, classifications, parameter sets and relevant reference records.
Record source, meaning, units, supported chemistry, version/digest and acquisition
terms. Native baseline calculations must not obtain those resources from a PISA
installation. Do not copy competing tables into BindingMT or TopoMT to fill an
unresolved MolSysMT resource contract.

Use the existing ArgDigest, DepDigest, SMonitor, PyUnitWizard and optional
Ackredit boundaries. Record only scientific methods actually reached, including
genuinely completed child operations. A native published algorithm retains its
method reference and executed implementation; it does not claim execution of a
reference program. Studying PISA or computing a general surface quantity does
not by itself earn a PISA execution reference.

Validate bibliography offline and require real attribution tests for reached
branches, reuse, empty results, enclosing workflows, optional absence/failure
and fresh saved readers. Existing source API presence is not proof that each
owner attribution boundary already meets these requirements. Report actual
provider gaps with the native workflow evidence.

Save/read retains original producer/method versions, quantities, references,
analysis outcomes and maps. It neither recomputes SASA/contacts nor credits a
new originating calculation. Preserve unavailable external references honestly;
an internally corrupt/incomplete native archive must fail its owner reader.

## 11. Incremental delivery and dependency order

These are proposed implementation increments. The current commissioned delivery
is this document and its owner handoff, not execution of this programme.

| Increment | Scientific owner / dependency | Observable exit |
| --- | --- | --- |
| Catalogue decisions | BindingMT #112 with shared review under MolSysSuite #195. | Initial definitions, required/optional observations, defaults, resource/mapping facts and admitted assurance scopes recorded. |
| Data core | Existing BindingMT P0a/D1/D2 work. | Real declarations/analysis outcomes, useful summary, immutable identity and faithful public save/read. |
| Native contacts | BindingMT using MolSysMT; close only the molecular facts this profile needs. | A real public calculation-to-characterization round trip with independent contact expectations and PISA/TopoMT unavailable. |
| Native surfaces/burial | MolSysMT tools/any reusable gap and BindingMT binding-domain composition. | Both side losses, mapped contributions, explicit area convention, convergence and meaningful refusal/readback controls. |
| Native chemistry | Selected MolSysMT families and BindingMT aggregation. | Exact original observations, complete chemical participants, scope/unknown distinctions and public receiving for each admitted family. |
| Topographic enrichment | TopoMT's selected source profiles and existing #60/#61/#62 gates. | Actual owner result/support receiving and defined relationships to binding observations; unavailable findings remain explicit. |
| Comparison/ensemble/energy extensions | BindingMT and relevant method owners, with their own profile decisions. | Scoped methods, controls and receiving; no automatic prerequisite for the native baseline. |

Add native contacts as the first ordinary numerical milestone after the needed
data/context slice; it need not wait for SASA, chemical recognition, PISA T0/T1
or all neutral Topography work. Surface and chemistry increments can then
progress at their own actual prerequisites.

Keep existing PISA, native pharmacophoric H0/H1 and consumer P obligations
visible. The maintainer/owner records priority, accepted scope and deferred
follow-ups before closeout. This proposal does not silently cancel their tests
or make all catalogue entries new #112, BindingSite or release gates.

TopoMT's current synthetic sequence and joint review under
[#187](https://github.com/uibcdf/topomt/issues/187) remain unchanged. This plan
does not select another DFND geometry, original-provider/server run or protein
characterization phase. Small native molecular controls belong to their
specifically admitted owner calculation profiles.

## 12. Independent validation and acceptance matrix

| Control | Independently justified expectation |
| --- | --- |
| Simple geometric contacts | Hand-specified coordinates establish exact pairs and distances, including inside/on/outside the declared cutoff. Counts and exact source membership agree. |
| Participant exchange | For the admitted symmetric geometric predicate, total unique contacts are preserved and side footprints exchange through their maps. Do not generalize this to directional chemical roles. |
| Far-separated participants | No geometric contacts; no burial when the surface assumptions prove no cross-occlusion. Keep evaluated-zero evidence. |
| One isolated sphere | SASA agrees with `4*pi*(radius + probe_radius)**2` within the admitted numerical error. |
| Controlled two-sphere geometry | Analytic spherical-cap, containment and separation references test the surface recipe under stated assumptions. No PISA result defines the reference. |
| Surface aggregation | Per-atom/residue contributions sum to each side loss and the selected total/mean convention. Fixed-sample added occluders cannot increase an existing atom's accessible fraction. |
| Numerical convergence | A declared sampling sequence and independent reference bound error; no universal monotone convergence or exact rotation invariance is assumed. |
| Selection versus environment | Changing only output selection preserves the occluders; isolated-input extraction changes them intentionally with retained source maps. |
| Grouping and chemical completeness | Internal A-B and unrelated C-D observations are excluded from a requested receptor-C projection, while admitted full chemical participants remain intact. |
| Known empty / missing / failed | A completed no-contact result, unknown chemistry, unrequested measure, unsupported method and failed calculation retain different states and causes. |
| Maps and multiplicity | Reordering/extraction, original structure 2 to local 0 and repeated delivery preserve correspondence without fabricated independence. |
| Derived footprint persistence | Actual positive/empty footprint save/read preserves ordered source membership, aligned local maps, all contributors and exact parents; independent core inspection needs no optional recovery. |
| Crossed outcome/availability/use | Completed-zero with an unavailable asset, accessible failed evidence and saved C0 match with edited C1 retain distinct original outcomes and fresh-use assessments. Default read performs no discovery/reassessment. |
| Context changes | Relevant source/chemistry/frame edits reassess affected uses; unchanged footprint positions do not authenticate a complete original finding. |
| Units and persistence | Default and nondefault pm/fs policies preserve physical areas/distances, definitions, identities and reader dimensional checks. Malformed/tampered records refuse appropriately. |
| Optional dependencies | Native molecular calculation runs without PISA or TopoMT; topographic enrichment and external receiving use their explicit dependency routes. |
| Attribution | Completed branches and empty analyses credit the reached methods; failures and fresh saved readers do not invent originating executions. |

Freeze inputs, parameters, expected identities and tolerances before interpreting
outputs. Use an independent analytic or separately justified numerical reference
where available. Reusing a structure also consumed by PISA is permissible; its
expected native results must not depend on a PISA-derived answer.

Start test-first with small serial controls. Verify scheduler/allocation, CPU,
available RAM, swap and memory pressure before expensive operations, limit native
and child workers, preserve a conservative system reserve and monitor owned
work. No automatic full suite, all-core execution or scientific campaign follows
from this plan. Record interrupted and deferred evidence separately.

Source tests, real owner receiving, installed-artifact tests, platform coverage
and public delivery are different evidence. Proposed API sketches or successful
parsing do not qualify the scientific workflow.

## 13. PISA and other external methods

PISA remains a useful optional interface provider, study resource and comparator.
Its generic observables, particular numerical algorithms, empirical parameters
and assembly-inference model have different roles. Learn from published methods
and implementations with appropriate attribution; choose our definitions and
algorithms from the scientific question and evidence.

Preserve the original adapter and frozen artifacts under
[#194](https://github.com/uibcdf/topomt/issues/194). Its broader assessment and
resource/licence questions remain under
[#165](https://github.com/uibcdf/topomt/issues/165). A source-independent native
catalogue does not require removing this integration or changing historical data.

Compare eligible matched inputs, radius/chemistry/surface conventions, parameters
and supported outputs. Classify discrepancies as definition differences,
approximation/numerical effects, domain restrictions, execution issues or defects
before interpreting them. Exact reproduction of a model-specific PISA score
requires its own admitted method and validation; a new native descriptor cannot
inherit its name or predictive interpretation merely from similar units.

Any claimed improvement records the measured criterion: independently referenced
accuracy, additional supported scientific scope, clearer usable public behavior,
reproducibility or matched resource/performance results. Follow the
[comparative-finding lifecycle](comparative_findings.md), including current
limitations and their corrections. This proposal establishes no advantage card
or current third-party limitation.

## 14. Owner actions, decisions and closeout

| Action | Owning issue / next disposition |
| --- | --- |
| Admit the native catalogue, calculation/composition boundary and first milestone into the maintained roadmap. | BindingMT #112; record accepted/deferred scope, reasons and revisit conditions. |
| Agree exercised cross-component definitions, maps, quantities, attribution and receiving boundaries. | MolSysSuite #195; link each owner's concrete adoption. |
| Publish this contribution and reconcile TopoMT-specific review/follow-ups. | TopoMT #197 and its local handoff record. |
| Audit/select the exact MolSysMT tools and report a demonstrated reusable gap before implementing a workaround. | BindingMT #112 owns the finite request; open/reuse the concrete MolSysMT provider issue when its missing operation is established and link it here. |
| Deliver neutral TopoMT context/support/participant/evaluation adoption. | Existing TopoMT #60/#61/#62, with source-specific acceptance unchanged. |
| Develop physicochemical observations on topographic regions as a standalone TopoMT capability. | TopoMT #198; preserve BindingMT's binding-domain catalogue and route reusable chemical tools to MolSysMT. |
| Preserve optional PISA T0/T1 and independent H/P receiving obligations or explicitly rescope priority. | BindingMT #112 implementation plan; preserve original evidence and current status. |

The broad catalogue lives outside TopoMT's defect/proposal queues. Its bounded
local handoff has a queue record. Every selected implementation increment gets
an independently closable owner issue or an explicitly bounded part of #112;
unselected families remain catalogue candidates with an adoption trigger.

Before native runtime work, close the first profile's minimal inputs/outputs,
chemical/radius/environment rules, exact public owner calls, resource envelope,
requested guarantees and failure policy. Record actual received facts rather
than treating this proposal as owner acceptance. Existing source capability is
not proof of installed compatibility or a new shared format.

This documentation delivery is complete when its reviewed sources and navigation
are published, the exact revision is linked from BindingMT #112 and the shared
coordination issue, and independent readback verifies those handoffs. Owner review
and future adoption remain open until their explicit dispositions. Archiving the
local review later must not hide remaining scientific/implementation work.

## 15. Review baselines and primary references

- [BindingMT scientific scope at d69315d](https://github.com/uibcdf/bindingmt/blob/d69315dfebc49ddd8c2da1999955edc078fd8893/devguide/SCIENTIFIC_SCOPE.md),
  [interface design revision 2](https://github.com/uibcdf/bindingmt/blob/5aa21b1aaf27ee7708e5a7bb4fe58bd0300d49f0/devguide/binding_interface_design.md)
  and [reviewed implementation plan](https://github.com/uibcdf/bindingmt/blob/d69315dfebc49ddd8c2da1999955edc078fd8893/devguide/binding_interface_implementation_plan.md).
- MolSysMT `ff25f120243319ca9515009b4971e24a2eb0dc22`:
  [contacts](https://github.com/uibcdf/molsysmt/blob/ff25f120243319ca9515009b4971e24a2eb0dc22/molsysmt/structure/get_contacts.py),
  [SASA](https://github.com/uibcdf/molsysmt/blob/ff25f120243319ca9515009b4971e24a2eb0dc22/molsysmt/physchem/get_sasa.py),
  [tabulated buried-area descriptor](https://github.com/uibcdf/molsysmt/blob/ff25f120243319ca9515009b4971e24a2eb0dc22/molsysmt/physchem/get_area_buried.py)
  and [native interaction families](https://github.com/uibcdf/molsysmt/blob/ff25f120243319ca9515009b4971e24a2eb0dc22/molsysmt/interactions/__init__.py).
- [TopoMT conceptual contract](topography_conceptual_contract.md),
  [implementation route](topography_implementation_route.md),
  [current DFND laboratory checkpoint](DFND/notebook_laboratory_checkpoint.md)
  and [scientific attribution contract](attribution.md).
- Shrake and Rupley (1973), *Environment and exposure to solvent of protein
  atoms. Lysozyme and insulin*,
  [DOI 10.1016/0022-2836(73)90011-9](https://doi.org/10.1016/0022-2836(73)90011-9).
- Krissinel and Henrick (2007), *Inference of macromolecular assemblies from
  crystalline state*,
  [DOI 10.1016/j.jmb.2007.05.022](https://doi.org/10.1016/j.jmb.2007.05.022),
  and [original PISA description/source](https://github.com/PDBe-KB/pisa).

The primary papers identify scientific methods, not a claim that the complete
future catalogue or all internal algorithms have already been reviewed. Each
new descriptor closes its own literature, resource and implementation evidence.
