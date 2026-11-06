# Joining TopoMT development

TopoMT analyzes molecular surface topography and preserves the evidence behind
its geometric features. The current code serves both TopoMT's own method and
original external providers. Understanding those two paths, their ownership and
the scope of their evidence is the starting point for a useful contribution.

Read the [repository and suite instructions](index.md#first-reading), then use
[status](status.md) and [the roadmap](roadmap.md) to choose work. The current
machine-transfer task does not automatically resume the earlier implementation
programme. The accepted technical continuation remains in the
[provider handoff plan](provider_handoff_plan.md).

## The runtime models

| Model or entry point | Purpose and boundary |
| --- | --- |
| MolSysMT molecular source | Supplies molecular representation, atom selections/correspondence, coordinates and declared chemical states. Keep the full source when a later operation must verify those facts. |
| `get_provider_output()` and `ProviderOutput` | Execute or recover a selected original provider and expose its reported pockets, source indices, membership roles, available geometry and attributed measurements. Provider definitions are retained. |
| `ProviderRun` | Captures original inputs, outputs and metadata as independent artifacts. A persisted bundle preserves execution evidence; source-bound recovery additionally checks the compatible molecular source. |
| `get_topography()` and `Topography` | Supply the common feature hierarchy, registries and relationships. The accepted conceptual contract is broader than its currently implemented runtime adoption. |
| `DFNDData` | Holds the DFND-specific mesh, graph and component evidence behind native results. It complements the public hierarchy rather than replacing the original-provider result contract. |
| The TopoMT MolSysViewer addon | Displays TopoMT and provider representations while keeping their semantics separate. Showing lining atoms or spheres does not define an exact closed region. |

See [architecture](architecture.md), [API surface](api_surface.md),
[the source map](repository_map.md) and the
[accepted Topography contract](topography_conceptual_contract.md) for details.
Provider names alone do not identify the executed algorithm: select the entry
point and backend explicitly. `get_provider_output()` admits original routes;
legacy `get_topography()` routes retain their own defaults and compatibility.
An adapter result is not automatic admission to canonical DFND semantics.

## Component ownership

MolSysMT owns molecular loading, representation, selection, atom correspondence,
coordinate operations, chemistry and preparation. TopoMT owns topography
algorithms, external topography adapters, source maps, pocket records and their
evidence. PharmacophoreMT owns chemical recognition, feature complementation,
query placement, matching tolerances, essentiality, weights and model persistence.
MolSysViewer owns general visualization; TopoMT supplies its domain addon.

Use existing public operations in the owning component. Missing molecular or
pharmacophore capabilities belong in that component's issue and implementation,
with a concrete TopoMT use case. Do not copy a molecular-preparation or modeling
algorithm into TopoMT to make a downstream control pass. The
[suite responsibility map](../MOLSYSSUITE_GUIDE.md#component-responsibility-map)
and [integration guide](integration_with_molsyssuite.md) govern this boundary.

## Decisions that guide changes

**Argument admission is a priority.** Use ArgDigest for nontrivial public option
names, values and normalization. Preserve route-specific signatures and reject
invalid options before optional-engine or molecular work where the contract
allows that ordering. Runtime type checking alone does not replace value,
shape, dimensional or cross-argument constraints. Existing provider
[argument controls](fpocket4/argdigest_dispatch_checkpoint.md) and
[AlphaSpace2 contracts](alphaspace2/handoff_checkpoint.md) illustrate the work.

**Source atom indices, coordinate frames and chemical states are independent.**
A provider-local row, PDB serial and full-source atom index are different
namespaces. Persist the explicit map instead of guessing correspondence from
row order. Selecting frame 1 does not select chemical state 1. The current
reference-state adapters validate the source's existing reference; they do not
prepare another state or infer readiness from a PDB charge field.

**Quantities retain their physical meaning at every boundary.** Use
PyUnitWizard with explicit units for persistence and conversion. Existing
application policy survives lazy sibling imports. Test relevant routes under
an alternate policy such as pm/fs as well as nm/ps. Bare array agreement without
verified units is insufficient. The
[registered guide](../PYUNITWIZARD_GUIDE.md) and
[suite quantity contract](../MOLSYSSUITE_GUIDE.md#physical-quantities-and-units)
define the shared responsibilities.

**Unknown, empty and invalid results differ.** Unavailable source membership
can be `None`; an available empty membership or pocket collection is an empty
result. Malformed mapping, conflicting source context and unsupported schemas
fail explicitly. Preserve undefined original measurements rather than inventing
zeroes. A consumer cannot replace missing recognition by expanding atoms or
substituting geometric centroids without a separately declared scientific choice.

**Original providers and local reproductions retain separate contracts.**
DepDigest guards the requested optional engine at its narrow boundary. Absence
never silently selects a native implementation. Original execution, saved
recovery, native fidelity and live server access have independent acceptance
criteria. Alpha spheres, residue masks, lining atoms and reported ranks retain
their provider meanings; they establish neither affinity nor pharmacophoric
importance.

**Evidence is tied to its actual candidate and inputs.** A source control is
not an installed-package qualification. A successful local wheel install is not
public delivery or a platform matrix. Keep original artifact bytes, hashes,
versions, options, selections, frames, states, test outcomes and limitations.
A rebuilt wheel has a new identity even if its source commit is unchanged.
The [migration handoff](migration_handoff.md) distinguishes the archived
scientific outputs from old wheels that are no longer available.

## How the current architecture developed

These milestones explain decisions, not a new scheduling order. Each checkpoint
keeps the scope and date of its own stage; the latest historical “next” sentence
is not the team's current work selection.

| Period | Decision or evidence to read |
| --- | --- |
| April 2026 | CASTp source/oracle investigations separated discrete-flow geometry, numerical ordering, radii and reporting semantics. Start with the [CASTp contract](castp/contract.md), [original-build recipe](castp/castp1_original_build.md) and [functional-parity checkpoint](castp/checkpoint_2026_04_23_castp1_functional_parity_closure.md). The historical reference source tree is an external dependency. |
| June 2026 | DFND object/kernel/catalog decisions separated raw evidence, public feature classification, deterministic identity and contextual provenance. Read the [catalog decision](DFND/taxonomy_architecture_decision.md), [kernel refactor checkpoint](DFND/checkpoint_kernel_catalog_refactor.md) and [identity checkpoint](DFND/checkpoint_identity_provenance_registries_2026_06_06.md). |
| September 2026 | The [Topography conceptual contract](topography_conceptual_contract.md) established the accepted direction for spatial support, participants, contextual evaluations and provider admission. Its [implementation route](topography_implementation_route.md) remains partial; accepted semantics do not prove delivered runtime behavior. |
| October 2026 | The [joint DFND/Topography audit](DFND/audit_topography_2026_10_01.md), [snapshot checkpoint](DFND/checkpoint_geometry_snapshots_2026_10_01.md) and [CASTp membership study](castp/checkpoint_2026_10_02_corrected_pocket_membership.md) documented delivered slices and residual scientific gates. |
| November 2026 | [Original-provider receiving](provider_handoff_plan.md) added rigorous argument/source contracts, engine-independent persistence and explicit public PharmacophoreMT controls. Subsequent bounded installed checkpoints qualify exact [AlphaSpace2](alphaspace2/installed_receiving_checkpoint.md) and [pyCASTA](pycasta/installed_receiving_checkpoint.md) candidates; CASTp/CASTpFold and combined receiving retain their gates. |

The [reference catalogue](reference_catalog.md) retains the detailed studies,
drafts and earlier checkpoints. Its historical sections should be read after
the relevant current overview or contract.

## Your first development session

1. Receive the correct local branch and preserved work using the
   [migration handoff](migration_handoff.md), or verify which published branch
   your checkout actually contains.
2. Establish a compatible Python 3.14 environment through
   [packaging and environments](packaging_and_environments.md). Verify imports
   from outside the checkout and run `python -m pip check`.
3. Read the relevant current issue, contract and checkpoint. Check the
   [bug](pending_bugs/README.md) and [proposal](pending_proposals/README.md)
   queues before changing a known boundary.
4. Run the initial selection in [validation and tests](validation_and_tests.md)
   with a published Pytest Receptor and record the new host's actual baseline.
5. For executable changes, add a meaningful failing test first, implement in the
   owning component, and run applicable argument/unit/source checks. Broaden to
   the required PR or release gates when that contribution route applies.
6. Update the current overview and owning work record when the result changes
   what another developer should do. Preserve old checkpoints and use the
   [reporting protocol](reporting_protocol.md) for report lifecycle changes.

The next original-provider receiving gate is CASTp/CASTpFold. The preceding
AlphaSpace2 and pyCASTA installed checkpoints retain actual candidates,
dependency identities and executed scope; they do not credit the interrupted,
unarchived historical attempt. Use the provider plan and owning issue for the
remaining acceptance criteria and combined regression controls.
