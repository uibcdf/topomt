# TopoMT API surface

Reviewed against the handoff source on 2026-11-06. This is an inventory of
implemented entry points and result boundaries, not a claim of stable production
support. Public semantic direction remains
[the Topography contract](topography_conceptual_contract.md), with incomplete
runtime adoption under #60–#63. Use [status](status.md) for evidence and
[roadmap](roadmap.md) for scheduling.

## Package entry points

The export inventory is [topomt/__init__.py](../topomt/__init__.py). The principal
workflows are:

| Entry point or object | Current role | Implementation |
| --- | --- | --- |
| `topomt.get_provider_output()` | Execute/recover an original provider and retain its own result semantics. | [dispatch](../topomt/get_provider_output.py) |
| `topomt.get_topography()` | Existing native/provider-adapter orchestration into `Topography`. | [orchestrator](../topomt/get_topography.py) |
| `topomt.Topography` | Mapping of feature IDs to features, typed lookup indexes, relations, provider runs and captured input context where adopted. | [registry](../topomt/topography/Topography.py) |
| `topomt.features` | Feature classes and the current type registry. | [feature exports](../topomt/features/__init__.py) |
| `topomt.get_delaunay_mesh()`, `DelaunayMesh`, `WeightedDelaunayMesh` | Mesh construction/substrate APIs used by native geometry. | [builder](../topomt/get_delaunay_mesh.py), [unweighted](../topomt/delaunay_mesh.py), [weighted](../topomt/weighted_delaunay_mesh.py) |
| `topomt.dfnd` | Native method, network/configuration and selection APIs. | [DFND exports](../topomt/dfnd/__init__.py) |
| `topomt.third_party`, `topomt.io`, `topomt.tools` | Provider facades, file-loading sugar and reusable geometry/feature operations. | [providers](../topomt/third_party/), [I/O](../topomt/io/), [tools](../topomt/tools/) |

The package also exports its version, `pyunitwizard`, `config`, and `demo`.
Exported names have distinct maturity and qualification scopes; module presence
alone does not certify scientific meaning or compatibility on every platform.

## Original-provider outputs

`get_provider_output(..., method=..., backend=...)` and each provider's
`get_output()` return provider-specific subclasses of
[ProviderOutput](../topomt/third_party/output.py). Method aliases include
fpocket/fpocket4, Pocketeer, AlphaSpace2, pyCASTA and CASTp/castp3/castpfold.
Defaults select the original CLI for fpocket, Python library for Python engines,
and service for CASTp. Saved-route availability and argument contracts belong to
the selected facade; do not assume every provider supports every backend.

These objects expose ordered `pockets`, source IDs, source atom indices and
membership roles, declared geometries and attributed measurements. `None`
membership means unavailable; an available empty membership is distinct. A
lining-atom set, residue mask or alpha-sphere representation does not establish
an exact closed region. Original rankings and descriptor definitions retain
their provider interpretation.

[ProviderRun](../topomt/provider_output.py) captures original inputs, outputs,
metadata and checksummed artifact bytes; its save/load operations preserve the
run's identity. Source-bound reconstruction verifies the corresponding source
context where adopted. The output and original run are separate from canonical
`Topography` semantic admission and DFND. Explicitly requesting an unavailable
original engine must not invoke a native reproduction as a substitute.

The [version-1 checkpoint](provider_pocket_output_checkpoint.md),
[provider handoff plan](provider_handoff_plan.md) and
[user engine guide](../docs/content/user/third_party_engines.md) retain contracts,
implemented routes and qualification limits. This schema remains provisional;
old archives may retain evidence without enough context for current source-bound
reconstruction.

## Topography and registered features

`get_topography()` returns the existing common registry view. `Topography`
maintains feature identity, lookup indexes and parent/child relations. Its
`molecular_system` compatibility reference may be live; `input_context` is the
historical selected input when that route captures it. Rebinding an analysed or
populated registry is rejected rather than retargeting historical results.
Public context/support and remaining mutation adoption are still partial.

The feature module exports `BaseFeature`, `Feature0D`, `Feature1D`, `Feature2D`,
`Pocket`, `Void`, `Channel`, `Mouth`, `OpenConcavity`, `Groove`, `Cleft`,
`BranchedChannel` and `Percolating`. Their registry presence does not imply every
engine promotes all of them or that provisional morphology has completed
scientific admission. `TopographyFeature` is a conceptual umbrella rather than
an implemented class. Consult the
[conceptual contract](topography_conceptual_contract.md) and
[implementation route](topography_implementation_route.md) before changing
public promotion or mutation behavior.

## DFND result model

The public native entry points are `topomt.dfnd.dfnd(...)`, a raw-first
method-development/diagnostic operation, and
`topomt.get_topography(..., method='dfnd')`, the integrated feature view.
`DelaunayFlowNetwork`, `DFNDMeshConfig`, `DFNDQuery` and the exported selectors
support explicit build/query and source/local-index contracts.

The integrated view has **one `topography.dfnd` container**, implemented by
[DFNDData](../topomt/dfnd/data.py). It holds:

- `raw`: method-specific records and parameters;
- `mesh`: the probe-independent substrate and captured atom/geometry context;
- `dfn`: query parameters, graph and typed components;
- `input_context`: captured native source/frame context where available;
- `at_probe(...)`: a new query result that reuses the mesh and rejects
  mesh-configuration overrides.

The public `Topography` top level holds promoted features. It does not expose the
retired `dfnd_records`, `dfnd_result`, `dfnd_concavity_domains`, or other
`dfnd_*` convenience attributes. The retired `*_domain` family names are not the
current contract. Native families use names such as `void`, `pocket`, `channel`
and `percolating`, with justified morphology refinements and child `Mouth`
features where applicable. See [object model](DFND/object_model.md),
[feature catalog](DFND/feature_catalog.md) and
[implementation status](DFND/implementation_status.md).

Raw dry-network/motif and matching/lineage helpers are method-development
evidence; their presence does not establish public feature or temporal identity
contracts. The notebook laboratory is paused at its recorded two-case tranche.
DFND is not a prerequisite for original-provider consumption.

## Visualization and compatibility boundaries

The TopoMT-owned [MolSysViewer addon](../molsysviewer_topomt/__init__.py) exports
`attach_provider_output`, `show_provider_pockets` and `clear_provider_pockets`
as well as existing Topography attachment/rendering operations. Provider state
is separate from canonical Topography state. See
[viewer adoption](provider_output_viewer_checkpoint.md) for the bounded display
contract; rendered points/spheres do not become exact volumetric support.

Existing provider `get_pockets()` and `get_topography()` facades keep their own
backend/default contracts. They are not interchangeable with the original-only
output dispatcher. The removed top-level `get_pockets()`/`show_pockets()` stubs
are not package exports and should not be restored from historical examples.

Use supported public owner operations and the
[integration guide](integration_with_molsyssuite.md) when extending a workflow.
Provider internals, private registry tables and experimental DFND records are
not new cross-component public APIs merely because they are importable.
