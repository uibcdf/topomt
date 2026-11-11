# Local cavity, channel and site providers

These routes use the original external methods through
`topomt.get_provider_output`. They extend the original-provider interface;
they do not add native reproductions or classify results through DFND.
The original engines are optional and are not installed with TopoMT.

```python
import topomt as tmt
```

| Method | Execution backend | Original records | Shared access |
| --- | --- | --- | --- |
| `pykvfinder` | `library` | Dual-probe grid cavities | `output.cavities` |
| `ghecom` | `cli` | P-mode morphological grid pockets | `output.pockets` |
| `caver` | `cli` | Tunnel paths and local free radii | `output.channels` |
| `p2rank` | `cli` | Predicted ligand-binding sites | `output.sites` |
| `mole` | `cli` | Channel profiles and original cavity/void decomposition | `output.channels`, `output.cavities` |
| `molovol` | `cli` | Original probe-defined internal regions, volumes and surfaces | `output.cavities`, `output.measurements` |

All provide `output.records`, `output.run`, `output.save(path)` and
`topomt.load_provider_output(path, molecular_system=source)`. Recovery verifies
the original source identities, frame, reference chemistry and submitted PDB
mapping without the original engine or a network connection. Keep the full
source with the bundle. No new remote submission is involved in these routes.

## Common controls

Use `selection='all'`, `structure_indices=0`, `chemical_state='reference'` and
`syntax='MolSysMT'` to select one source state. MolSysMT owns loading, selection,
PDB export and molecular preparation; these adapters perform no protonation or
chemical-state inference. Source coordinates and exact submitted PDB bytes are
retained separately. PDB's decimal precision remains a conversion limit.

`workers=1` and `timeout=300` are conservative defaults (MoloVol: 120 seconds). Timeout accepts seconds
or a time quantity. The Java routes additionally use `memory_mb=1024` as their
maximum heap and constrain the JVM's processor count. The GHECOM route is serial.
MOLE uses `memory_mb=1024` as its .NET managed heap cap and sets the .NET
processor count to `workers`. This is not a total-process RAM limit.
`max_grid_points=4000000` limits a conservative preflight bounding-grid estimate
for pyKVFinder/GHECOM. These controls are not a machine resource reservation or
a substitute for a scheduler; memory outside a Java heap also exists.

MoloVol is serial. Its `max_grid_points=20000000` preflight estimate includes
octree alignment and all allocated grid levels. It is a grid-cell admission
limit, not a process memory cap or resource reservation.

Lengths below accept scalars in the documented angstrom protocol units or
compatible PyUnitWizard quantities. Volume cutoff uses angstroms cubed.
CAVER's origin requires an explicit three-coordinate length quantity. Geometry
access always returns quantities and does not change the application's unit policy.

## MoloVol

See [the MoloVol guide](molovol.md) for its distinct volume/region definitions,
element radii, original Linux execution and headless requirements.

## MOLE

The reviewed local protocol is **2.5.26.10.26**, from the maintained
[Webchemistry source](https://github.com/sb-ncbr/webchemistry/tree/fe0e84582a6bd42bc69224fd3a3022bf5c51cec3).
It uses the MIT licence. Build this source with .NET SDK 10; running this
framework-dependent build requires .NET runtime 10. The upstream README
provides `dotnet publish` instructions. Select the resulting executable with
`mole_cmd`, or place `mole2` on PATH. Availability is checked only for execution;
saved recovery needs neither executable nor runtime. The Python MOLEonline API
is a server around this engine, not a replacement for its local executable.

```python
output = tmt.get_provider_output(source, method='mole',
    mole_cmd='/path/to/mole2', probe_radius=3.0, interior_threshold=1.25)
channel = output.channels[0]
profile = channel.geometries['centerline']
coordinates, radii = profile.coordinates, profile.radii
original_json = output.original_data
```

Omitting `origin` selects original automatic origins. Supply an explicit
three-coordinate length quantity to request one point, for example
`origin=tmt.pyunitwizard.quantity([10, 20, 30], 'angstroms')`. The original
algorithm may locate an origin within `origin_radius`; retain its reported
origins rather than assuming the requested point was used exactly.

| Option | Default | Original meaning / unit |
| --- | --- | --- |
| `probe_radius` | 3.0 | Surface-detail probe, angstroms |
| `interior_threshold` | 1.25 | Original interior filtering threshold, angstroms |
| `min_depth`, `min_depth_length` | 8, 5.0 | Minimum tetrahedron depth and depth length in angstroms |
| `min_tunnel_length`, `min_pore_length` | 0.0, 0.0 | Minimum reported path lengths, angstroms |
| `surface_cover_radius` | 10.0 | Original exit-point coverage scale, angstroms |
| `origin_radius` | 5.0 | Search around an explicit origin, angstroms |
| `bottleneck_radius`, `bottleneck_tolerance` | 1.25, 0.0 | Original radius/allowed constriction-length controls, angstroms |
| `auto_origin_cover_radius` | 10.0 | Automatic-origin separation, angstroms |
| `max_auto_origins_per_cavity` | 5 | Positive maximum origin count per cavity |
| `weight_function` | `VoronoiScale` | Also `LengthAndRadius`, `Length`, `Constant` |
| `ignore_hetatoms`, `ignore_hydrogens` | `False`, `False` | Original engine atom filters |
| `compute_pores`, `compute_merged_pores` | `False`, `False` | Original automatic pore and merged-tunnel calculations |

The channel collections (`Tunnels`, `Pores`, `MergedPores`, `Paths`) retain
distinct namespaced identities and original types; shared access uses
`output.channels`. Explicit exit, arbitrary query/path and membrane-orientation
controls are outside this initial execution interface. Profiles expose original
`Radius`, `FreeRadius` and `BRadius` as `centerline`, `free_radius_centerline`
and `b_radius_centerline`. `profile_length` is the original final approximate
profile distance, rounded to 0.001 angstrom; it is not recomputed from points.

The original `Cavities` and `Voids` collections use `output.cavities`, preserving
their original type labels. **`tetrahedral_volume` sums retained Delaunay
tetrahedron volumes; it is not solvent-excluded free volume.** Inner/boundary
mesh vertices are quantity-aware geometries; `record.fields['mesh']` retains
triangle topology and declared units. These representations do not establish
an independently validated closed region. The full original surface, chemistry,
lining labels, layers, settings and origins remain accessible in the detached
`output.original_data` and raw artifacts. Its native protocol uses angstroms
and angstroms cubed. Source atom memberships remain `None` until qualified.

Execution keeps original XML/JSON/CSV, logs, input/configuration, companion-file
hashes and selected resource settings. Completion checks require the reviewed
version, the original completion marker and complete successful XML/JSON output.
An empty successful decomposition stays empty; errors do not become zero features.

## pyKVFinder

The reviewed original protocol is 0.9.6. Install it from
[the upstream project](https://github.com/LBC-LNBio/pyKVFinder) or select a
built source checkout explicitly. Upstream's NumPy range is `<2.5`; use a
compatible environment for that distribution. The separately identified
[UIBCDF compatibility branch](https://github.com/uibcdf/pyKVFinder/tree/uibcdf-compat)
0.9.6+uibcdf.2 has a bounded Linux/Python 3.14/NumPy 2.5.4 source qualification.
It keeps the scientific kernels unchanged, makes plotting optional and requires
tomlkit>=0.14 without an upper cap. Versions 0.14.0 and 0.15.2 were tested;
unreleased versions are not claimed as executed. Select the compiled source
explicitly with `upstream_root`; it does not replace the original package.
Source builds need a C/OpenMP compiler, SWIG, setuptools, wheel and NumPy;
original TOML export needs tomlkit. Plotting has separate requirements.

`topomt[pykvfinder]` installs the original 0.9.6 distribution with its upstream
constraints. The older `topomt[third-party]` extra retains its auxiliary-library
scope. For the compiled compatibility checkout, select `upstream_root` explicitly.

```python
output = tmt.get_provider_output(source, method='pykvfinder',
    step=0.6, probe_in=1.4, probe_out=4.0, removal_distance=2.4,
    volume_cutoff=5.0, include_depth=False)
cavity = output.cavities[0]
grid = cavity.geometries['grid_points'].coordinates
volume = cavity.measurements['volume'].value
```

`upstream_root` selects a built package directory containing `pyKVFinder/`;
the worker verifies that this source was not shadowed. `python_cmd` selects a
separate interpreter for the original worker if its dependency environment
differs from TopoMT's. That worker needs pyKVFinder's dependencies, not TopoMT's
full dependency stack. All detection and export operations receive the explicit
worker count. The original vdW dictionary, exported TOML/PDB and module/native
extension identities remain in the run. Reported interface residues are retained
as original labels; source atom membership is currently unavailable (`None`).

## GHECOM

The admitted CLI revision reports `LastModDate:2026/08/17`. Obtain the source
from [the author's repository](https://github.com/kawabata-takeshi/ghecom_test)
at `e1950a405323d069673fe2df445ecd3f41e8651e`; compile with one build worker
and `CFLAGS='-std=gnu99 -O2 -g -Wall'` on the reviewed Linux/GCC route.
This LGPLv3 source uses positional `P` and `-cluspock`, differing from the
older official manual. Supply `ghecom_cmd` or place the executable on PATH.

```python
output = tmt.get_provider_output(source, method='ghecom',
    ghecom_cmd='/path/to/ghecom', grid_width=0.8,
    probe_small=1.87, probe_large=6.0)
```

Only P-mode is admitted here. Original ATOM/heavy-atom filtering and built-in
radii remain provider behavior; choose an appropriate input selection and
inspect the original log. Other morphological modes need separate contracts.
Cluster identity comes from MODEL, not the grid-value residue number. Original
grid points and counts are exposed; a continuous volume is not fabricated.
The reviewed source returns 1 even on success. The adapter checks the revision,
rejects original error messages and requires complete model/count postconditions.

## CAVER

Download [CAVER 3.02 CLI](https://www.caver.cz/index.php?sid=199), the GPLv3
command-line edition, and retain its `caver.jar` and `bin/` resources together.
Set `caver_home` to that directory. CAVER Analyst is a different product with
different terms. The current source pilot uses OpenJDK 21.

```python
output = tmt.get_provider_output(source, method='caver',
    caver_home='/path/to/caver', java_cmd='/path/to/java',
    origin=tmt.pyunitwizard.quantity([17.012, 24.139, 7.790], 'angstroms'),
    probe_radius=0.6)
tunnel = output.channels[0]
centerline = tunnel.geometries['centerline'].coordinates
radii = tunnel.geometries['centerline'].radii
```

`probe_radius=0.9`, `shell_radius=3.0` and `shell_depth=4.0` use angstroms.
The original optimizer may move the requested starting point: retained origin
files and logs describe its actual choice. Ordered profile samples, available
error-bound profiles, original length, bottleneck radius, curvature and throughput
retain their definitions. A sampled profile's terminal distance is not substituted
for the original reported length. No closed volume or lining-atom map is inferred.

## P2Rank

Download [P2Rank 2.5.1](https://github.com/rdk/p2rank/releases/tag/2.5.1)
(MIT; Java 17–23) and set `p2rank_home` to its distribution directory.
The adapter invokes the original Java main class with explicit heap/processor
limits; the distributed `prank` launcher otherwise appends its own 2 GiB heap.

```python
output = tmt.get_provider_output(source, method='p2rank',
    p2rank_home='/path/to/p2rank_2.5.1', java_cmd='/path/to/java',
    model='default')
site = output.sites[0]
center = site.geometries['predicted_center'].coordinates
probability = site.measurements['probability'].value
```

`model='alphafold'` selects the original model without the B-factor feature
for appropriate predicted/NMR/cryo-EM inputs; model choice is a scientific input,
not an automatic inference. Original scores, probabilities, ranks, residues and
surface-atom labels remain accessible. Source atom indices are currently
unavailable. Predicted centers and calibrated scores do not define a closed
region, an affinity or independent evidence of biological binding.

## Recovery and failures

```python
output.save('original.zip')
restored = tmt.load_provider_output('original.zip', molecular_system=source)
assert restored.run == output.run
```

For `backend='files'`, supply only `bundle_file`; execution or source-context
overrides are rejected. Rejected original results retain an inspectable failed
receipt with `failure_stage='result_validation'`, including original process
metadata and auxiliary inputs. A successful process return code alone does not
qualify the output for recovery. Missing engines, execution failures, invalid
results and valid-empty output remain distinct. `ProviderExecutionError.run`, when available,
retains bounded partial evidence after temporary directories disappear; it can
be saved for inspection with `ProviderRun.load`. Failed runs cannot be recovered
as successful original results. Parsing a fixture alone is not execution evidence.
