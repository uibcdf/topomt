# Third-party engines

TopoMT supports external engines through Python libraries, a local executable,
web services, and persisted result files. It also provides native implementations
of several algorithms. The external engines are optional: installing TopoMT does
not install them, and importing TopoMT does not import them.

## Supported routes and requirements

The new [local cavity, channel and predicted-site routes](original_local_providers.md)
cover pyKVFinder, GHECOM, CAVER and P2Rank through `get_provider_output`.
That guide gives their exact protocols, access/licences, options and current
mapping limits. Their results retain distinct scientific kinds.

| Provider | Original engine route | Installation and runtime requirements | Other TopoMT routes and current limits |
|---|---|---|---|
| [fpocket](https://github.com/Discngine/fpocket) | `third_party.fpocket`, `backend='cli'` | `conda install -c conda-forge fpocket`; executable available on PATH, or supply `fpocket_cmd` | Persisted output loader; native implementation and TopoMT variant. Native equivalence is under validation. |
| [Pocketeer](https://github.com/cch1999/pocketeer) | `third_party.pocketeer`, `backend='library'` | `python -m pip install pocketeer`; upstream installs Biotite, atomview and its other requirements | Native implementation needs Biotite, but does not require Pocketeer. Native equivalence is under validation. |
| [AlphaSpace2](https://github.com/RedesignScience/AlphaSpace2) | `third_party.alphaspace2`, `backend='library'` | `python -m pip install alphaspace2`; upstream requires MDTraj, SciPy, Cython and configargparser | Saved original-output reader without AlphaSpace2/MDTraj; native implementation; library adapter accepts a receptor and optional positioned ligand. Vina receptor typing is not exposed yet. Compatibility adjustments cover NumPy, MDTraj SASA and missing unbound contact arrays in PyPI 0.1.2. |
| [pyCASTA](https://github.com/giorgioluciano/pycasta) | `third_party.pycasta`, `backend='library'` | `python -m pip install pycasta biopandas colorama`; the published package omits these last two runtime requirements | Saved original-output reader without pyCASTA; native implementation. The original runs in an isolated subprocess using its installed scripts and configuration. Optional mesh/PyMOL/FreeSASA functions have their own upstream requirements. |
| CASTp 3.0 | `third_party.castp`, `backend='server', server='castp3'` | Network access to the public server; no CASTp Python package to install | Persisted result loader. Server availability and job completion are independent of local dependencies. Local CASTp methods remain experimental. |
| CASTpFold | `third_party.castp`, `backend='server', server='castpfold'` | Network access to the public server; no CASTpFold Python package to install | Persisted result loader and experimental native CASTp routes. |

The `third_party` namespace contains provider adapters. Select `backend='library'`
explicitly for the original Python engines; those providers default to `native`.
The high-level `topomt.get_topography` API uses `implementation='wrapper'` for
Pocketeer, AlphaSpace2 and pyCASTA. A native route does not imply identical results
to the original engine; the provider comparisons and scientific audits determine
which measurements are equivalent.

The optional extras `topomt[alphaspace2]` and `topomt[pocketeer]` install auxiliary
libraries (MDTraj and Biotite), respectively. `topomt[third-party]` combines those
extras. They do not install the original engine distributions. Use the commands
in the table when choosing an original engine.

## Install and run an original engine

Run installation commands in the environment where TopoMT will execute:

```bash
conda install -c conda-forge fpocket
python -m pip install pocketeer
python -m pip install alphaspace2
python -m pip install pycasta biopandas colorama
```

Choose only the engines you need. Their upstream projects own the full dependency
and platform requirements. The following published distributions have been
checked on Linux with Python 3.13: Pocketeer 0.4.0, AlphaSpace2 0.1.2 and pyCASTA
1.0.8. Installed-engine regression tests compare their results with direct
upstream runs on the same PDB input. These checks do not certify every version,
platform, configuration, or native implementation.

The fpocket CLI route has also been checked against direct fpocket 4.2.3 runs
from conda-forge on Linux with Python 3.13. The executable must be visible in
the environment running TopoMT; installation in a different environment does
not make it available automatically.

```python
import topomt as tmt

pockets = tmt.third_party.pocketeer.get_topography(
    'protein.pdb', backend='library'
)
pockets = tmt.third_party.alphaspace2.get_topography(
    'protein.pdb', backend='library'
)
pockets = tmt.third_party.pycasta.get_topography(
    'protein.pdb', backend='library'
)
pockets = tmt.third_party.fpocket.get_topography(
    'protein.pdb', backend='cli', fpocket_cmd='fpocket'
)
```

The original Python engines are registered as soft dependencies in DepDigest.
Missing engines raise a TopoMT `LibraryNotFoundError` when their library backend
is requested. SMonitor provides the dependency diagnostic. An absent fpocket
command raises `FpocketError` with its Conda installation hint. Transitive import
failures and engine execution failures remain distinct from absence.

TopoMT requires DepDigest 0.12.0 or newer for executable availability and explicit
disabled installer routes. The shared check uses the supplied `fpocket_cmd`, so a
custom executable does not require a separate default `fpocket` on PATH. Relative
command paths are checked against the execution directory (`workdir`, or the input
PDB directory by default), matching subprocess execution. Missing
commands retain TopoMT's `FpocketError` and its Conda hint; execution failures
remain separate. Pip-only engines do not receive inferred Conda installation hints.
Publication and adoption are tracked in
[DepDigest #22](https://github.com/uibcdf/depdigest/issues/22).

TopoMT captures submitted input, engine output and execution metadata in
`Topography.provider_runs`. pyCASTA's `version_tag` is an upstream output tag,
not its PyPI distribution version. AlphaSpace2 records whether it initialized
missing unbound contact arrays; this compatibility step supplies zero ligand
contacts without changing calculated geometry or scores.

## Provider-specific pocket outputs

Use `get_provider_output` to obtain the original method's own result and shared
access to its pockets. It selects CLI for fpocket, the original Python library
for Pocketeer/AlphaSpace2/pyCASTA, and a server for CASTp. Existing
`get_topography` defaults remain unchanged.

```python
result = tmt.get_provider_output('protein.pdb', method='fpocket')
# Also available as tmt.third_party.fpocket.get_output(...).

for pocket in result.pockets:
    print(pocket.source_id, pocket.atom_indices, pocket.atom_role)
    if 'alpha_spheres' in pocket.geometries:
        spheres = pocket.geometries['alpha_spheres']
        coordinates, radii = spheres.coordinates, spheres.radii
    if 'volume' in pocket.measurements:
        reported_volume = pocket.measurements['volume']
        print(reported_volume.value, reported_volume.definition)

result.run.save('original_fpocket.zip')
```

`result` is a `FpocketOutput`, `PocketeerOutput`, `AlphaSpace2Output`,
`PyCASTAOutput` or `CASTpOutput`. These version-1 result classes are provisional;
providing the reported pockets and original evidence remains a permanent
capability. `result.records` includes auxiliary CASTp mouth aggregates, while
`result.pockets` includes all reported CASTp pocket rows, even closed cavities.

Geometry coordinates/radii have explicit length units. Available keys include
`member_atoms`, `alpha_spheres` and `beta_sites`; missing keys mean unavailable
geometry. Inspect `atom_role`: Pocketeer's mask membership comprises residue
atoms and is separate from its sphere-defined `lining_atoms` representation.
pyCASTA membership identifies tetrahedron vertices. Sites and membership alone
do not promise an exact closed region or a geometric volume.

`pocket.fields` preserves provider-specific parsed fields with their existing
conventions. Prefer `pocket.measurements` for attributed physical quantities and
`pocket.geometries` for unitized coordinates. Returned dictionaries/quantities
are independent copies. `result.input_coordinates` is a source-frame snapshot;
exact submitted structures, selections, metadata and additional AlphaSpace2
binder input remain in `result.run`. Saving that run exports original evidence,
not a serialization of the complete provisional result.

Persisted original output requires no installed engine or network:

```python
result = tmt.get_provider_output(
    'protein.pdb', method='fpocket', backend='files',
    pdb_file='protein.pdb', output_dir='protein_out',
)
result = tmt.get_provider_output(
    method='castp', backend='files', zip_file='castp_result.zip',
)
```

CASTp accepts one input route at a time: `zip_file`, `dir_path`, or explicitly
named result files. ZIP and directory imports find one result family in the
root or a subdirectory. Its result files share a directory and filename stem;
the ZIP itself can have a different name, as CASTpFold job exports commonly do.
The matching PDB supplies atom ownership. Auxiliary files, including unrelated
PDBs, remain in the original evidence. Multiple result families require an
explicit choice through the individual-file arguments.

Nested artifact paths and original bytes survive in `result.run`. An import
with only a measurement table keeps atom membership unknown. A header-only
table can describe an empty result; an absent result or a table without its
header raises an error. Empty `.poc` and `.mouth` files remain valid. Ambiguous
archives, duplicate member names, inconsistent capitalization of path components
and paths that change during extraction are rejected. This keeps artifact
identities consistent across file systems.

To associate a CASTp export with an external molecular source, supply an explicit
correspondence: one full-source atom index per row of the export's original PDB,
in that row order. MolSysMT owns correspondence and preparation; TopoMT checks
the declared map without inferring one or sorting it.

```python
output = tmt.get_provider_output(
    source, method='castp', backend='files', zip_file='original_castp.zip',
    source_atom_indices=pdb_row_to_source, selection=pdb_row_to_source,
    structure_indices=1, chemical_state='reference',
)
output.run.save('bound_castp.zip')
restored = tmt.get_provider_output(
    source, method='castp', backend='files', bundle_file='bound_castp.zip',
)
```

The bound import requires the original result PDB, one source frame and an
unambiguous existing reference chemical state. The initial binding profile
rejects alternate-location and insertion-code rows. It checks atom/residue/chain
identity and declared elements, as well as coordinates at PDB rounding precision.
Saving retains the complete source identity/frame and reference chemistry,
including atoms excluded from the provider selection. Recovery verifies that
context and preserves the exact run ID, original bytes and attributed records.
It accepts no replacement selection, frame or chemical-state settings.

Historical evidence saved without source context remains attributable, but it
cannot be reconstructed as a source-bound result by inference. Import the
original files with a known correspondence first. These checks establish a
declared correspondence; they do not establish chemical readiness or a new
server calculation.

The new entry point rejects `backend='native'`; local reproductions retain their
existing APIs and separate parity gates. Contact/volume/score definitions remain
specific to their original methods. No DFND calculation is required to use
these outputs.

TopoMT requires ArgDigest 0.17.0 or newer. `get_provider_output` validates `method`
and `backend` through ArgDigest before
importing a provider adapter. Names are case-insensitive; `fpocket4`, `castp3`
and `castpfold` retain their aliases, and `backend=None` selects the default
original route. Invalid types or incompatible routes raise a catalogued TopoMT
argument error that is also catchable as `ValueError`. Molecular inputs and
provider-specific keyword names and values remain owned by the selected adapter.

### Save and recover an original result

Keep the full molecular source alongside the original result:

```python
import topomt as tmt

result = tmt.get_provider_output(source_system, method='fpocket')
result.save('pockets.zip')

# Later, with the original molecular source restored:
recovered = tmt.load_provider_output(
    'pockets.zip', molecular_system=source_system
)
assert recovered.run == result.run
```

The same recovery call supports source-bound fpocket, Pocketeer, AlphaSpace2,
pyCASTA and CASTp results. The verified ZIP identifies its provider and original
backend. Recovery reads saved files without running the original engine or
contacting its server. It preserves the original run ID, artifacts, metadata,
pocket order, memberships and attributed measurements, including available empty
results.

`save()` delegates to `result.run.save()`; both remain supported. An existing
destination is replaced. The ZIP contains original evidence for reconstruction,
rather than the full MolSysMT source or arbitrary manually constructed record
fields. Preserve the full source with its original atom identities, frame and
reference chemistry. `load_provider_output()` verifies that source against the
saved context. Execution options, selections, frame and chemical state come
from the bundle and cannot be overridden at this boundary.

For a bound AlphaSpace2 result, also supply its original full binder source:

```python
recovered = tmt.load_provider_output(
    'bound-pockets.zip', molecular_system=receptor, binder=binder
)
```

Other providers reject `binder`. Bundles without sufficient source
context remain inspectable with `ProviderRun.load()`; the result loader reports
the missing context instead of inventing it. Existing provider-specific file
imports remain available for importing original files with explicit source maps.

For CASTp/CASTpFold, reconstruction currently supports source-bound **files**
captures. Current direct-server results retain original evidence without the
full-source reconstruction context. Saving such a result preserves that evidence
but does not make it reconstructable by `load_provider_output()`. Explicitly
binding the retained original files to the full source and known atom map creates
a separate files run, as described in the CASTp file-import examples above.

The original fpocket output API admits options declared by its CLI/files
signatures and reports unknown names through ArgDigest. The closed routes digest
selection/index shapes, single-frame requests, syntax, executable/argument types,
file paths, metadata and saved chemical-context fields before molecular preparation
or file parsing. Boolean/fractional indices, duplicate submitted atom maps and
malformed saved contexts are rejected. Index bounds, selected atom correspondence,
source coordinates and reference-state agreement are checked against the molecular
system afterward. Files recovery still permits omitted chemical options; explicit
arrays and the original submitted-row order remain supported.
Additional `provider_metadata` may annotate a run, but cannot replace the adapter's
selection, frame, syntax, atom map, chemical-context or source-binding fields.

The public fpocket `get_topography` and `get_pockets` gateways also digest their
case-insensitive `backend` through ArgDigest. They retain `cli` (default),
`wrapper`, `native` and `topomt`; `files` recovery uses `load_topography` or
`get_output(backend='files')`. The public file wrapper admits the owning loader's
option names and delegates value digestion to it. Native and variant options
remain owned by those backends; routing validation does not qualify their parity.

### Recover fpocket selections against the original source

The CLI requires a nonempty atom selection and exactly one coordinate frame.
A multi-model PDB is exported at the requested frame. Submitted atom rows follow
source order; their serials may be renumbered during PDB export.

New source-bound CLI results support `result.save()` and the shared
`tmt.load_provider_output()` call above. Their complete source snapshot is
captured without modifying the original input/output directories. Recovery
retains the original CLI backend and run ID. Raw file imports with explicit
chemical context and a submitted atom map also record this source supplement;
legacy imports with those options omitted retain their existing behavior.

CLI results retain `result.run.metadata['submitted_atom_indices']`: one source
atom index per submitted PDB atom row, in file order. Keep the full source system
and its selected frame alongside the run bundle. When importing original files
explicitly, supply their known context:

```python
recovered = tmt.get_provider_output(
    source_system, method='fpocket', backend='files',
    pdb_file=submitted_pdb, output_dir=original_output_directory,
    selection=result.run.metadata['selection'],
    structure_indices=result.run.metadata['structure_indices'],
    submitted_atom_indices=result.run.metadata['submitted_atom_indices'],
    chemical_state_context=result.run.metadata['chemical_state_context'],
)
```

The explicit map must uniquely cover the selection. Submitted serials must be
unique, and mapped source coordinates must agree with PDB coordinates within
0.00051 Å (the PDB rounding precision). Incompatible atom maps or frames raise
`ValueError`. Without an explicit map, the files route retains its legacy
serial-to-source-atom-ID behavior. A run bundle does not contain the full source
system or qualify its chemical-state context by itself.

The CLI admits an unambiguous reference chemical state. `chemical_state='reference'`
is the default; its explicit integer index is also accepted, including an index
other than zero. With the qualified MolSysMT converter, a different chosen state,
an ambiguous reference, absent chemistry or a zero-state inventory raises
`ValueError` before fpocket executes. The adapter does not change the source's
reference to make an export succeed. Unknown connectivity and a declared complete
zero-bond graph remain distinct; pocket execution does not establish readiness
for downstream chemical recognition.

New runs retain `chemical_state_context` with reference index, state ID, inventory
count and a digest of the provider's formal charges, bond table and connectivity
completeness. Pass that entry to file recovery, as above, to reject changed source
chemistry even when its coordinates agree. Keep the original full source system;
the digest does not authenticate chemistry or reconstruct a discarded state.
Files calls omitting both chemical options retain legacy behavior and do not
claim this additional state qualification. Historical bundles remain readable.

The bounded source handoff pilot is tracked in
[TopoMT #101](https://github.com/uibcdf/topomt/issues/101). Its developer command,
`python -m devtools.qualify_fpocket_handoff`, tests real execution, a nonconsecutive
selection, the second frame, source persistence and recovery, alternate units,
and independence from later source-coordinate changes. It currently requires a
compatible MolSysMT source checkout and one reference chemical state; it does
not establish general installed-package or alternative-state support.

A subsequent source integration control consumes a prepared ERalpha fragment's
original pocket through PharmacophoreMT's public `get_features` and
`from_receptor_projections` operations. It preserves membership, frame, state
and units through native model persistence. This is an explicit hydrophobic
analytical hypothesis, with caller-declared placements and matching radii.
Spatial pocket detection alone does not establish the chemical readiness needed
for native feature recognition; incomplete chemistry remains a provider error.
This optional control adds no PharmacophoreMT runtime requirement to TopoMT and
does not qualify a complete receptor model or installed integration.

### Pocketeer original inputs

Original Pocketeer options have an ArgDigest contract, including calls through
`get_provider_output`. Unknown options and invalid values are rejected before
dependency or molecular-input work. Radii, probe size and SASA threshold must be
finite positive scalars; the maximum radius must exceed the minimum. Merge
distance may be zero. `min_spheres` is a positive integer and `ignore_*` flags
are literal booleans. Scalar quantities are converted explicitly to the original
angstrom/angstrom-squared protocol; omitted options keep upstream defaults.
The original route requires one exported frame. Select its source index with
`structure_indices`; an ambiguous multiframe export is rejected before execution.
Run metadata preserves the module's `version` and adds `distribution_version`
only when the imported package matches its installed metadata origin. These
identities can differ, as in Pocketeer 0.4.0's module string `0.3.0`.
`chemical_state='reference'` (the default) records MolSysMT's unambiguous
reference state; its integer index is also accepted. Missing, empty, ambiguous
or nonreference state selections are rejected before input export and original
execution. TopoMT does not change the reference or prepare protonation, charges
or bonds. Run metadata's `chemical_state_context` retains the reference identity
and a digest of source charges, bonds and connectivity completeness, using the
same PDB-boundary tool as fpocket.

This context is provenance for the source receptor. Original Pocketeer 0.4.0
detects pockets using geometry and Biotite SASA/radius tables; it ignores hydrogen
atoms by default and does not prepare a protonation state. The context neither
establishes chemical readiness nor implies that Pocketeer uses all its fields.
Pharmacophore recognition belongs to PharmacophoreMT and requires separately
qualified source chemistry. A bounded source control now consumes a prepared
ERalpha fragment's original Pocketeer residue membership through public
PharmacophoreMT `get_features` and `from_receptor_projections`, then persists the
native model. The caller declares the selected pocket, direction, distance and
matching radius. This optional hydrophobic control preserves source/frame/state
and units; it does not add a PharmacophoreMT runtime dependency to TopoMT.
Receptor preparation and biological validation retain their separate ownership.
Qualification of an updated installed TopoMT candidate remains separate.

Save an original run and recover its parsed output with its full source:

```python
result = tmt.get_provider_output(source, method='pocketeer', structure_indices=1)
result.run.save('original.zip')
restored = tmt.get_provider_output(
    source, method='pocketeer', backend='files', bundle_file='original.zip'
)
assert restored.run.run_id == result.run.run_id
```

The `files` route uses NumPy, MolSysMT and PyUnitWizard; it does not import
Pocketeer or Biotite. `ProviderRun.load` verifies the bundle's content and identity.
Run metadata's `output_protocol` declares the original artifact's length, area,
volume and dimensionless fields; recovery verifies that exact unit contract.
Selection, frame and state come from the saved run and cannot be overridden.
Recovery checks the full atom inventory and labels, the full source frame in nm
(absolute tolerance `1e-12 nm`), chemical context and the submitted PDB row map
(`0.00051 angstroms` for three-decimal PDB coordinates). No alignment, atom
correspondence or chemical preparation is inferred. Keep the full source system
in a MolSysMT-supported persistent format; a selected exported PDB is insufficient.

Original pocket order, residue masks, sphere IDs, defining-atom maps and attributed
measurements are retained. An available empty result or membership remains empty.
Inconsistent schemas, maps, masks or nonfinite measurements are rejected. Older
runs missing the new `topomt_source_context.json` supplement remain recoverable
as `ProviderRun` artifacts, but cannot reconstruct a source-qualified
`PocketeerOutput`. The legacy `get_topography`/`get_pockets` routing is unchanged;
saved reconstruction is exposed through the original-output entry point.

## Recover original pyCASTA results

The original pyCASTA route admits argument names and values before engine
discovery. It records the submitted selection, single frame, reference chemical
state and full source context. The legacy
`get_topography(..., method='pycasta', implementation='wrapper')` also forwards
the declared selection syntax to this original adapter before preparation.

```python
result = tmt.get_provider_output(
    source, method='pycasta', structure_indices=1, chemical_state='reference'
)
result.run.save('original_pycasta.zip')
restored = tmt.get_provider_output(
    source, method='pycasta', backend='files', bundle_file='original_pycasta.zip'
)
assert restored.run.run_id == result.run.run_id
```

Keep the full source in a MolSysMT-supported persistent format, including its
reference chemistry and coordinate frames. Recovery verifies that source,
the submitted PDB rows and original ATOM/HETATM correspondence. It consumes
the tetrahedron-to-atom map verified against the original alpha NPZ during
execution; it performs no new triangulation and imports no pyCASTA scripts.
Selection, frame, state and execution options cannot override a saved run.
Historical bundles without these source and index supplements remain readable
as `ProviderRun` artifacts, but cannot reconstruct a source-qualified output.

Original ranking, tetrahedron membership, volumes, depth, representative points,
mouth measurements and reported validation outcomes retain their own meanings.
An empty result stays empty. Tagged undefined scalar measurements remain
undefined; they are never converted to zero. Nonfinite coordinates, malformed
indices, unknown schemas and incompatible sources fail explicitly.

pyCASTA's ligand mesh validation is separate from pocket detection. Its current
Trimesh path can require Rtree; upstream may catch a missing-dependency failure
and return a negative validation outcome. That outcome alone does not establish
physical exclusion. Unbound detection and saved recovery do not qualify mesh,
SASA, affinity or biological relevance. Native parity remains a separate gate.

## Show original pockets in MolSysViewer

Install the optional viewer dependencies with `python -m pip install 'topomt[viewer]'`.
The integration ships inside TopoMT as `molsysviewer_topomt`.

```python
import molsysviewer as msv
import molsysviewer_topomt as viewer_topomt
import topomt as tmt

molecular_system = 'protein.pdb'
result = tmt.get_provider_output(molecular_system, method='fpocket', structure_indices=0)
view = msv.new_view(molecular_system, structure_indices=0)
attached = viewer_topomt.attach_provider_output(view, result)
view  # Display in Jupyter; the TopoMT panels list the active run's original pockets.

if result.pockets:
    selected = [result.pockets[0].source_id]
    viewer_topomt.show_provider_pockets(view, result, pocket_ids=selected)
viewer_topomt.clear_provider_pockets(view, result)
```

The same helpers accept all five provider output classes. Original results are
retained under `view.addons.topomt.provider_outputs[result.run.run_id]`, separately
from any attached Topography. Different runs have separate layer tags; attaching
a run makes it active for the panels. The panels show all pockets or one pocket,
clear the active run's display, and disable DFND controls for provider results.

The automatic display uses available alpha spheres, beta sites or mapped member
atoms. Choose a representation explicitly, for example
`show_provider_pockets(view, result, representation='member_atoms')`.
Reported sphere radii keep their original physical meaning. Point-only evidence
uses display markers with `point_radius_nm=0.06`; this radius is not a provider
measurement or pocket boundary. No exact pocket volume or surface is inferred.
Missing geometry produces warnings in RenderResult and the panel; present empty
geometry is reported separately. Rendering and clearing preserve original data.

Load the source coordinate frame when showing its receptor alongside the output.
The helper does not align different structures or transformed coordinates.
If you choose a custom `tag_prefix`, use the same prefix for later show/clear calls.

## AlphaSpace2 contacts with a reference ligand

Original AlphaSpace2 arguments are admitted through ArgDigest before optional
dependency loading or molecular conversion. `min_vertices` is a positive integer
(booleans are rejected), and unknown option names are rejected. Receptor and
binder selections accept nonempty selection strings or flat nonnegative integer
axes. Each explicit frame axis contains one nonnegative integer; `None` and
`'all'` retain their source-dependent single-frame checks. MolSysMT owns selection
syntax, molecular-form support and conversion. Syntax names are normalized;
caller-owned index arrays and molecular inputs are forwarded without mutation.
The optional `upstream_root` remains a fallback import path, not an automatic
replacement of an installed original. The legacy native default is unchanged.

The original AlphaSpace2 adapter accepts `binder`, the upstream name for a
reference ligand whose position is already known. This engine-specific option
describes pocket geometry relative to that position. TopoMT does not search for
poses, align the inputs, calculate binding affinity, or generate pharmacophores.
For example, a pose obtained with DockingMT can be supplied as a reference input.

```python
topography = tmt.third_party.alphaspace2.get_topography(
    'receptor.pdb', backend='library', binder='ligand.pdb'
)

# Alternatively, select receptor and ligand from the same molecular complex.
topography = tmt.get_topography(
    'complex.pdb', method='alphaspace2', implementation='wrapper',
    selection='group_type=="amino acid"',
    binder='complex.pdb', binder_selection='group_name=="ACA"',
)
```

Receptor and ligand must share a coordinate frame. Each submitted selection must
contain atoms and a single structure. `binder_selection`,
`binder_structure_indices` and `binder_syntax` apply to the reference input
independently of the receptor options. Select one frame explicitly, for example
`binder_structure_indices=[1]`, when using a multi-frame input. Coordinate units
are handled by MolSysMT and the PDB/MDTraj conversion; AlphaSpace2's recorded
default contact cutoff is 1.6 angstroms.

`chemical_state='reference'` and `binder_chemical_state='reference'` refer to
each source's existing, unambiguous MolSysMT reference. You can supply that
reference's integer index, including a nonzero reference. An explicit binder
state index requires a binder. Absent, empty, ambiguous and nonreference state
requests are rejected before either input is exported. TopoMT records existing
charges, bonds and completeness as provenance without preparing chemistry or
changing either reference.

Before the original detector is imported, the adapter verifies each submitted
PDB's source map, unique serials, single frame and coordinates. The loaded
MDTraj rows must also agree in their declared nm units, allowing PDB rounding
and float32 conversion. There is no inferred atom matching or alignment.
The bundle retains separate receptor/binder full-source identities and frame
coordinates, chemical fingerprints and submitted serial maps. Snapshot fields
and settings have an explicit output-unit protocol; unspecified score units
remain unspecified. These records survive changes to the caller's sources.
Bundle persistence is available through `output.run.save(...)`; source-bound
reconstruction uses the original full sources, for example:

```python
restored = tmt.get_provider_output(
    'receptor.h5msm', method='alphaspace2', backend='files',
    binder='binder.h5msm', bundle_file='original_alphaspace2.zip',
)
```

Save the full sources through MolSysMT alongside the original bundle. Omit
`binder` for an unbound original run; supply its full source for a bound run.
This reader imports neither AlphaSpace2 nor MDTraj and retains the original
library run, artifact bytes, pocket order/IDs, memberships and attributed fields.
Selections, frames, references and `min_vertices` come from the run and cannot
be overridden. Unknown snapshot schemas, ambiguous JSON keys, missing unit
protocols or inconsistent source maps are rejected. Source coordinate agreement
uses 1e-12 nm; submitted PDB rows retain their 0.00051 angstrom tolerance.
Undefined occupancy markers remain undefined, and a recorded filter can yield
an available empty result. Recovered data are detached from the sources and
bundle path. Older runs without the required source context remain readable
as `ProviderRun` evidence but cannot reconstruct a source-bound output.

Original lining atoms need not contain the same chemical participants as a
residue-level pocket mask. Recognition and any complementary query belong to
PharmacophoreMT, using the separately prepared full source and the exact lining
indices. The prepared AlphaSpace2 pilot under
[#101](https://github.com/uibcdf/topomt/issues/101) retains an empty hydrophobic
result and a distinct explicit acceptor-to-donor control on that same membership.
Its caller-declared projection direction,
distance, donor orientation and matching radius are analytical choices; they
establish neither a binding site nor affinity. This optional integration adds no
PharmacophoreMT runtime dependency to TopoMT.

Pocket features expose `is_contact`, `alpha_contact`, `beta_contact`,
`occupied_space`, `occupied_nonpolar_space`, `occupancy` and `occupancy_nonpolar`.
Occupied quantities are sums of upstream alpha-space volumes labelled as contacts;
the fractions describe that geometric contact state, not a binding probability.
These measurements retain their original attribution and remain `external_only`.
Undefined upstream ratios are preserved as NaN in features and explicit nonfinite
records in the snapshot JSON.

Adding a ligand does not enable Vina scoring. The adapter currently submits an
untyped PDB receptor, for which AlphaSpace2 returns zero probe scores. The richer
typed-receptor scoring route remains pending.

The provider bundle retains both exact submitted inputs, their selections and
atom mappings, the full contact state, and every original export, including
`output/pdb_out/lig.pdb`. Binder input names live under `input/binder/`, so a
ligand extracted from the same complex cannot overwrite the receptor input.
Installed AlphaSpace2 0.1.2 comparisons cover the ACA ligand in bundled 2pk4,
separate files, selections from one complex, and a displaced reference frame.
They establish parity with that original engine on those inputs, not biological
validation of its contact definition.

## Source checkouts and web services

### Experimental local CASTp3 reconstruction

The local reconstruction can run without a CASTp executable or service:

```python
topography = tmt.third_party.castp3.get_topography(
    'protein.pdb', backend='native', radii_model='castp3_protor',
    pocket_definition='castp3', probe_radius=1.4
)
```

At the base alpha rank, closed voids carry independent unit-bearing
`solvent_accessible_area`, `molecular_surface_area`,
`solvent_accessible_volume` and `molecular_surface_volume` attributes. Generic
`area` and `volume` retain their polyhedral definitions. Validation currently
establishes exact lining atoms and all 900 SA/MS values within the server's
printed precision for 225 closed cavities across twenty-two bundled systems.
This includes all seven cavities of hydrogen-bearing 1CGE, corrected under
[issue #85](https://github.com/uibcdf/topomt/issues/85), and the complete
closed-void panels of 1A4J and 1CDO.

The local route offers two independently selectable pocket definitions:

| `pocket_definition` | Region rule | Interpretation |
|---|---|---|
| `'literature'` (default) | Maximum reachable depth; any route to the exterior excludes the tetrahedron. | Non-wrapping definition in the [1998 pocket-construction paper](https://doi.org/10.1016/S0166-218X(98)00067-5). |
| `'castp3'` | Lowest-rank reachable finite terminal; exterior only if no finite terminal is reachable. | Empirical compatibility inferred from archived CASTp3/CASTpFold sphere regions. |

This choice is independent of `radii_model`: either definition accepts either
radius profile. Both report component vertices as lining atoms and actual
mouth-triangle vertices as rim atoms. The old exterior-opposite atom
substitutions are no longer used, so outputs can change under the default
literature definition too. `probe_limited_depth=True` remains a diagnostic
for the literature definition and is rejected with `'castp3'`.
Each feature preserves the choices and diagnostic switches in
`feature.properties['castp3_execution']`. Select the options explicitly for
reproducible comparisons.

The compatibility definition is an inference from measurements, not a claim
to have recovered the server's source or proved a server defect. A fresh
forty-system calculation with explicit `'castp3'` and `'castp3_protor'` matches
all compared atom classes in **39/40 systems**: **533/534 pockets**, **388/388
closed voids**, **52/52 channels**, **17/17 branched channels** and **602/603
aggregate mouth records**. Complete deltas and the dated earlier baselines
remain under [issue #88](https://github.com/uibcdf/topomt/issues/88). The corrected
local numeric defect in 1CDO is tracked under
[#89](https://github.com/uibcdf/topomt/issues/89). The remaining 1HIV disagreement
is associated with modified HETATM residues absent from the server contribution
list. General protein selection retains those residues; compare identical atom
inputs before interpreting a disagreement.
Exact atom memberships do not establish individual mouth triangulation or
open-feature SA/MS metric equivalence, which remain experimental.

`castp3_protor` is an explicit empirical server profile with 1.40 Å
ASP/GLU carboxylate oxygen radii, inferred from exported sphere geometry.
Standard `protor` retains 1.42 Å for those atoms and differs from the server
in two cavities of the initial four-system panel. Both profiles require MolSysMT connectivity.
Before geometry construction, both ProtOr policies exclude explicit hydrogen
atoms through MolSysMT selection because their atomic groups already account
for attached hydrogens implicitly. This follows the
[CASTpFold computation settings](https://cfold.bme.uic.edu/castpfold/infos/allabout/computation_settings.html).
Original atom indices and requested order are retained. Explicit radius
overrides retain the selected atoms and supplied spheres.
Open pockets, mouths, altered-alpha measurements and general CASTp3 equivalence
remain experimental.

#### Published ProtOr and the CASTp server profile

ProtOr is a published reference set of empirical radii for protein atomic
groups: a heavy atom represents its attached hydrogens implicitly. It is one
established radius convention, rather than a unique universal set. The
[original paper by Tsai, Taylor, Chothia and Gerstein (1999), Table 2](https://papers.gersteinlab.org/e-print/std-vols-jmb/std-vols-jmb.pdf)
assigns 1.42 Å to type `O1H0`, which includes carboxylate oxygen, and 1.46 Å
to hydroxyl type `O2H1`. MolSysMT's ProtOr type-radius table agrees with that
published table. Assigning types to residue variants or falling back for
unrecognized atoms is a separate implementation policy.

The experimental local CASTp3 route currently assigns radius values from its
own table in TopoMT. It obtains coordinates, residue/atom labels and chemical
metadata from MolSysMT; it does not call MolSysMT's atomic-radius operation
for those values. Agreement between the tables does not establish identical
typing or fallback behavior for every input.

| Radius policy | ASP OD1/OD2 and GLU OE1/OE2 | Meaning |
|---|---:|---|
| `protor` | 1.42 Å | Published ProtOr values in the existing local assignment policy. |
| `castp3_protor` | 1.40 Å | Explicit empirical profile inferred from pinned modern-server geometry. |

The server value was inferred from exported sphere centers and radii before
checking the resulting SA/MS measures. The corrected profile reproduces the
expanded closed-void controls described above. Apart from the bounded terminal
policy below, its other assignments reuse
the local ProtOr policy; this does not certify the complete server radius
table, untested protonation states or open pockets.

An offline audit of all 89 bundled CASTpFold archives evaluates 59,080 exported
spheres without restricting the search to ASP/GLU. Observed contacts support
the current backbone, ASN/GLN amide and SER/THR/TYR hydroxyl oxygen assignments.
Presence in a PDB alone does not validate an atom's radius. Verified archived
contribution records identify which atoms were admitted. With that membership
and the revised explicit profile, all 59,080 spheres are compatible; this
does not certify full native input preparation or feature decomposition for
all 89 systems.

`castp3_protor` now assigns 1.50 Å to GLY/LEU terminal OXT atoms, independently
reconstructed from exported spheres in 1A4J and 1CDO. It excludes OXT for the
thirteen residue types observed unlisted in all contribution records: ALA,
ARG, ASN, ASP, GLN, GLU, HIS, ILE, LYS, MET, PHE, SER and VAL. The corpus
contains no OXT observations for CYS, PRO, THR, TRP or TYR, so their previous
local assignments are retained and remain unvalidated. This empirical rule
reproduces archived provider behavior; the authors' rationale is unknown.
Standard `protor` retains its historical local terminal typing. The partial
terminal coverage remains under [issue #84](https://github.com/uibcdf/topomt/issues/84);
the earlier corpus evidence is recorded in
[issue #82](https://github.com/uibcdf/topomt/issues/82).

The authors' reason for using 1.40 Å for these atoms has not been established.
Older reference sets, including Chothia's, also contain oxygen radii of
1.40 Å, but this is not evidence of the server's historical implementation
choice. Neither convention is shown to be physically more accurate by
agreement with the server alone.

The identified discrepancy concerns atomic radii, not units or probe size.
With the same 1.40 Å probe, the expanded spheres have radii of 2.82 Å under
`protor` and 2.80 Å under `castp3_protor`. This small change can affect the
area and volume of a narrow void even when its lining atoms remain identical.
Choose `protor` to retain the published radius values or `castp3_protor` to
compare with the validated modern-server panel. Selection is explicit and
does not change the default radius policy or DFND.

The evidence and its scope are recorded in
[TopoMT issue #80](https://github.com/uibcdf/topomt/issues/80).

### Original source checkouts and services

The Python adapters retain `upstream_root` for controlled source-checkout
comparisons. Supply an import root for Pocketeer or AlphaSpace2; pyCASTA accepts
the directory containing `run_analysis.py`, its package directory, or repository
root. Install the upstream runtime requirements even when using a source checkout.
For normal execution, use installed distributions in the current environment.

Web routes submit the selected structure to the external service:

```python
topography = tmt.third_party.castp.get_topography(
    'protein.pdb', backend='server', server='castpfold'
)
```

For a provider-specific result, the common original-output route is:

```python
output = tmt.get_provider_output(
    'protein.pdb', method='castp', backend='server', server='castpfold',
    probe_radius=1.4, output_zip_file='castpfold_result.zip'
)
```

The [CASTp 3.0 form](http://sts.bioe.uic.edu/castp/calculation.html) accepts PDB
files up to 5,000,000 bytes. The
[CASTpFold form](https://cfold.bme.uic.edu/castpfold/compute) accepts PDB/mmCIF
files below 2,000,000 bytes, disallows multiple-model NMR inputs and ignores
nonpolar hydrogens. TopoMT submits its selected structure as PDB. Both forms
offer a 0–10 Å probe range; the current TopoMT CASTpFold client accepts 0–5 Å.
Neither form accepts an explicit per-atom radius array. Use standard coordinate
records and atom/element names; dummy synthetic atoms need separate validation.

CASTpFold states that calculation can take minutes to hours. Exhausting the
client's polling interval does not establish that the remote job failed. Keep
the job identifier from the exception and retrieve that job before uploading
again. Retain the downloaded original ZIP for repeatable file imports.

For separate submission and retrieval, the original Fold client can reserve a
receipt before sending the PDB and retain the exact server acknowledgement:

```python
from pathlib import Path
from topomt.third_party.castp.servers.castpfold import CastpFoldClient

client = CastpFoldClient()
jobid = client.submit('protein.pdb', submission_file='submission.json')
# Run later if the calculation is still pending; reuse the accepted jobid.
payload = client.download_result_zip_bytes(jobid, wait=0, extra_wait=0, retries=0)
Path('castpfold_result.zip').write_bytes(payload)
```

An existing `submission_file` raises `FileExistsError` before another POST,
including after an interrupted or failed attempt. Read its `jobid` to resume an
accepted job. The receipt records input SHA-256, parameters, HTTP response bytes
and acknowledgement; `submitted_pending` means acceptance, not completion.
A local `failed` state does not establish whether the server created a job.
Inspect the retained response before considering another submission. This option
belongs to `CastpFoldClient.submit`; the combined high-level calls above retain
their existing interface.

Live service availability is not established by local unit tests. Server adapters
and persisted result loaders have separate validation; using a saved result does
not require installing or contacting its original engine.
