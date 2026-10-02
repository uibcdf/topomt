# Third-party engines

TopoMT supports external engines through Python libraries, a local executable,
web services, and persisted result files. It also provides native implementations
of several algorithms. The external engines are optional: installing TopoMT does
not install them, and importing TopoMT does not import them.

## Supported routes and requirements

| Provider | Original engine route | Installation and runtime requirements | Other TopoMT routes and current limits |
|---|---|---|---|
| [fpocket](https://github.com/Discngine/fpocket) | `third_party.fpocket`, `backend='cli'` | `conda install -c conda-forge fpocket`; executable available on PATH, or supply `fpocket_cmd` | Persisted output loader; native implementation and TopoMT variant. Native equivalence is under validation. |
| [Pocketeer](https://github.com/cch1999/pocketeer) | `third_party.pocketeer`, `backend='library'` | `python -m pip install pocketeer`; upstream installs Biotite, atomview and its other requirements | Native implementation needs Biotite, but does not require Pocketeer. Native equivalence is under validation. |
| [AlphaSpace2](https://github.com/RedesignScience/AlphaSpace2) | `third_party.alphaspace2`, `backend='library'` | `python -m pip install alphaspace2`; upstream requires MDTraj, SciPy, Cython and configargparser | Native implementation; library adapter accepts a receptor and an optional ligand at a known position. Vina receptor typing is not exposed yet. Compatibility adjustments cover NumPy, the MDTraj SASA signature, and missing unbound contact arrays in PyPI 0.1.2. |
| [pyCASTA](https://github.com/giorgioluciano/pycasta) | `third_party.pycasta`, `backend='library'` | `python -m pip install pycasta biopandas colorama`; the published package omits these last two runtime requirements | Native implementation. The original runs in an isolated subprocess using its installed scripts and configuration. Optional PyMOL/FreeSASA functions have their own upstream requirements. |
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

The new entry point rejects `backend='native'`; local reproductions retain their
existing APIs and separate parity gates. Contact/volume/score definitions remain
specific to their original methods. No DFND calculation is required to use
these outputs.

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

Live service availability is not established by local unit tests. Server adapters
and persisted result loaders have separate validation; using a saved result does
not require installing or contacting its original engine.
