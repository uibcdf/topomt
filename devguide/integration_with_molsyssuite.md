# Integration with MolSysSuite

TopoMT contributes molecular surface topography to MolSysSuite. It composes
other members' public operations rather than maintaining another molecular,
pharmacophore or visualization subsystem. Read
[MOLSYSSUITE_GUIDE.md](../MOLSYSSUITE_GUIDE.md) and
[AGENTS.md](../AGENTS.md) for the governing development rules; this page explains
the TopoMT boundaries used by the current source and receiving work.

## Scientific ownership

| Capability | Owner and TopoMT boundary |
| --- | --- |
| Molecular representation, formats, selections, coordinates, chemistry, preparation and atom correspondence | MolSysMT. TopoMT calls public operations and preserves their source indices, frame and declared reference chemical state. |
| Molecular surface topography | TopoMT. Original detector adapters, recoverable provider evidence, source maps, pocket representations and native DFND interpretation belong here. |
| Pharmacophore recognition, feature complementation, projections, tolerances, essentiality, weights and persistence | PharmacophoreMT. TopoMT supplies attributed geometry/membership; the consumer makes and records the scientific query choices. |
| Molecular visualization and rendering | MolSysViewer. TopoMT owns its `molsysviewer_topomt` addon and topography-specific payload/interaction logic. |
| Independent CASTp numerical kernel | OpenCASTp; TopoMT owns its optional integration and Topography adapter. The transition remains tracked in #90. |

If an independently useful molecular or modeling operation is missing, report
it to that owner with a consumer use case and reproduction. A downstream local
copy is not the default way to avoid blocking work. Reuse supported owner tools;
a bounded implementation exception needs the common documented owner, rationale,
interim controls and removal condition. Shared-contract changes require the
suite coordination route rather than an undocumented consumer convention.

## Molecular source and chemistry

Use public MolSysMT loading/conversion, selection and structural operations.
Keep selected atom order, source atom maps, submitted serials, coordinate frame
and chemical state distinct. A structure index is not a chemical-state index.
Original-provider handoffs check the source evidence appropriate to their route;
they do not protonate, add hydrogens, repair bonds or infer a discarded reference
state to make a pocket calculation or consumer query succeed.

A historical source snapshot and a live compatibility reference serve different
purposes. Later caller mutation must not change captured pocket geometry or
retarget already computed Topography results. `input_context` recovery, optional
provider contexts and full public ownership/copy qualification have different
adoption scopes. See [source context](topography_input_context.md),
[Topography route](topography_implementation_route.md) and the component issues
#60/#97/#100. Do not convert those partial deliveries into a blanket ownership
claim for every route or new MolSysMT revision.

## Public PharmacophoreMT receiving

The [original-provider programme](provider_handoff_plan.md) composes a prepared
MolSysMT source, explicit original pocket output and public PharmacophoreMT
recognition/modeling. The developer recorder calls public `get_features`,
`from_receptor_projections` and native JSON persistence. It performs no second
chemical recognition or complementary-feature algorithm in TopoMT.

Keep exact provider membership and its role: residue membership, lining atoms
and arbitrary nearby atoms are different scientific selections. An empty
recognized family is not a request to expand atoms or substitute pocket geometry
for chemistry. Distances, projection directions, target orientations and matching
radii are declared consumer choices. The source pilots preserve an explicit
empty hydrophobic control alongside an independently declared polar recipe.
They do not infer affinity, binding relevance or exact closed-region support.
PharmacophoreMT remains optional for these developer integration controls.

## Quantities and application authority

Use TopoMT's configured `pyunitwizard` and the
[registered PyUnitWizard guide](../PYUNITWIZARD_GUIDE.md). Public inputs may use
different supported quantity forms. Convert to an explicit target unit before a
kernel consumes magnitudes, and return or serialize value, unit and definition
together. Internal nm/nm**3 geometry is a declared boundary contract, not a
reason to infer a unit from a bare number or descriptor name. Original values
retain their reported unit, including explicitly unspecified units where needed.

Authority is explicit operation parameter, local quantity context, application
policy, then factory default. A library import is not a policy owner.
[topomt/_pyunitwizard.py](../topomt/_pyunitwizard.py) initializes the shared suite
baseline only when `has_active_policy()` is false. Registering a named converter
is not changing that baseline. Lazily importing MolSysMT, PharmacophoreMT or a
viewer must preserve the caller's active policy. Alternate-unit controls compare
physical values, source context and application policy across these boundaries.

Viewer payloads may use explicit canonical magnitudes at the receiving boundary;
this must not strip units or change physical meaning in core scientific records.
A serialized field's key is not a substitute for its declared unit/protocol.

## Argument and dependency admission

[ArgDigest](../ARGDIGEST_GUIDE.md) owns public argument normalization and
validation. The argument-name contract answers which parameters a selected
method/backend accepts; the value contract normalizes and validates each allowed
argument. A valid keyword for a native method need not be valid for an original
provider. Keep backend-specific maps and leaf contracts explicit, and reject
unknown names before optional engine or molecular work where that gateway has
adopted the contract. Molecular selection/conversion remains MolSysMT's job.

Follow the actual callable signature and registered digestion configuration.
Do not inject a universal `skip_digestion` keyword into APIs that do not declare
it. Where the accepted API supports the trusted internal bypass, its control
must be literal boolean, and prevalidated internal calls retain the source,
physical and operational checks required by their route. A bypass is not a
substitute for a missing value contract or a performance investigation. Optional
type checking is separate from this name/value admission; adding direct beartype
checks does not replace ArgDigest.

[DepDigest](../DEPDIGEST_GUIDE.md) owns optional capability availability. Keep
[topomt/_depdigest.py](../topomt/_depdigest.py), package metadata and maintained
environment declarations aligned with actual requirements and installer routes.
Guard the narrow selected original-library, executable or optional-tool route;
import its heavy dependency lazily inside that boundary. Declared availability
does not prove successful execution, a compatible ABI, scientific fidelity or
service reachability. An unavailable requested original engine must not silently
select `native` or another provider. Saved-result readers and native paths stay
independent of original engine installation where their contracts allow it.

## Diagnostics and attribution

[SMonitor](../SMONITOR_GUIDE.md) owns structured signals, diagnostics and catalog
integration. Use meaningful workflow boundaries and registered errors/warnings;
preserve absence, import, execution, conversion and malformed-result failures
rather than reporting all of them as missing packages. Instrumentation does not
own the scientific definitions of a provider's score or geometry.

[Ackredit](../ACKREDIT_GUIDE.md) supplies optional scientific attribution under
its registered client contract. Follow the supported lazy client/session pattern;
absence must not disable the scientific workflow. Retain actual method/result
provenance and original-provider credit rather than treating every imported
package as an executed scientific method. Applications own attribution sessions.
Guide adoption, installed Ackredit compatibility and executed attribution guards
are separate facts; copying a current guide establishes none of the other two.

## Visualization and validation tools

The [TopoMT addon](../molsysviewer_topomt/__init__.py) already attaches/renders
Topography and original provider outputs. Provider state, feature filters and
render groups remain distinct from canonical Topography ownership. Preserve
source atom-index spaces and explicit geometry units in viewer payloads. Display
success does not qualify exact support or scientific feature classification.
See [provider viewer adoption](provider_output_viewer_checkpoint.md) and
[the viewer ownership checkpoint](DFND/checkpoint_viewer_runtime_ownership_2026_06_14.md).

Published Pytest Receptor and GH Run Receptor are developer tools, not runtime
scientific dependencies. Use the registered
[Actions inspection guide](../GH_RUN_RECEPTOR_GUIDE.md) and
[local validation instructions](validation_and_tests.md). A focused source test,
strict installed-origin/RECORD check, hosted matrix, public artifact and support
claim have different scopes; retain exact source/dependency/artifact identities
and actual omissions for each.

## Canonical guides and receiving evidence

Root integration guides synchronized from owning repositories are read-only
consumer copies. Propose changes in the canonical owner and use the registered
synchronization/adoption route; do not patch a local copy to make these notes
agree. The guide's recorded revision and actual contracts govern its boundary.
This summary does not override them or manufacture source/public availability.
When a guide revision, API floor or dependency closure changes, review actual
consumer impact and receiving evidence before extending a qualification claim.
