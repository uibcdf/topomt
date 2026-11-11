# MoloVol: probe-defined regions, volumes and surfaces

[MoloVol](https://github.com/molovol/MoloVol) is an optional MIT-licensed local
program. TopoMT executes its original CLI and preserves its report, region
types and physical definitions. It offers a useful second view of how a probe
fits inside or around a structure. Align the physical definitions before
interpreting a comparison with DFND.

## Run and inspect

```python
import topomt as tmt

output = tmt.get_provider_output(
    source, method='molovol', molovol_cmd='/tools/molovol',
    elements_file='/tools/inputfile/elements.txt',
    probe_radius=1.4, grid_step=0.2, calculate_surfaces=True,
)
for cavity in output.cavities:
    print(cavity.source_id, cavity.fields['reported_type'])
    print(cavity.measurements['accessible_volume'].value)
    print(cavity.measurements['occupied_volume'].value)

total = output.measurements['molecular_volume'].value
original_report = output.report_text
decoded_report = output.original_data
```

Lengths accept angstrom scalars or compatible PyUnitWizard quantities. Returned
measurements retain original units, printed values and source fields, alongside
quantities using the application's unit policy. `output.element_radii` shows the
effective radii printed by MoloVol. Exact submitted radii and resource bytes are
retained in `output.run` because the original parameter report rounds to six
significant digits.

## Choose the physical model

The element table is part of the calculation. The reviewed original table uses
carbon radius **1.77 Å**; it does not inherit DFND's radii. To study a specified
neutral-element model, pass an explicit override:

```python
output = tmt.get_provider_output(
    source, method='molovol', molovol_cmd='/tools/molovol',
    element_radii={'C': tmt.pyunitwizard.quantity(0.17, 'nm')},
    probe_radius=1.4, grid_step=0.1,
)
```

Overrides apply to elements present in the selection. TopoMT writes a private
effective table, leaving the original resource unchanged, and saves both.
Absent or zero-radius selected elements are rejected. This initial route admits
explicit **neutral PDB element fields**, one frame and an isolated structure.
It includes both ATOM and HETATM records in that selection. It performs no
protonation, hydrogen addition or ionic-state inference. PDB decimal coordinates
are the engine's actual model; the full source context remains separately saved.

## Interpret the result

| Original quantity or row | Meaning retained by TopoMT |
| --- | --- |
| Accessible volume | Region available to probe centers (probe core). |
| Occupied volume | Original probe-occupied region, including its shell. It is a different volume from the accessible core. |
| Molecular volume | Original van der Waals plus probe-excluded void volume. |
| Molecular volume with isolated cavities | The separate original total that additionally includes isolated cavities. |
| Outside, one probe | Exterior region, with undefined occupied/core volumes. Kept in `original_data` and the report; excluded from `cavities`. |
| Isolated / Pocket / Tunnel | Original region type in `record.fields['reported_type']`. Internal rows use the common `cavities` collection; their names do not classify native DFND features. |
| Region center | Original midpoint of the region bounds. It is neither complete support nor a certified collision-free point. |

One-probe mode tests access from the original exterior. Set
`large_probe_radius=4.0` to use two probes; this radius must exceed the small
`probe_radius`. In that mode the large probe defines the exterior, and the
original Pocket/Tunnel distinction depends on entrance count. It is not DFND's
hull-relative percolation classification. Do not infer percolation from a
generic cavity count.

Volumes and surfaces are grid approximations at the recorded `grid_step` and
`octree_depth`, not exact geometric certificates. Surfaces are absent unless
`calculate_surfaces=True`. There is no atom-membership map or complete region
mesh in this first report-based route. Original OpenDX consumption, periodic
unit-cell analysis and native Topography admission are outside its scope.

## Controls and requirements

| Option | Default | Purpose |
| --- | --- | --- |
| `probe_radius`, `grid_step` | 1.4 Å, 0.2 Å | Probe size and grid resolution. |
| `large_probe_radius` | Absent | Optional two-probe mode. |
| `octree_depth` | 4 | Original optimization depth; admitted range 0–8. |
| `calculate_surfaces` | False | Request original surface measurements. |
| `elements_file` | Beside executable: `inputfile/elements.txt` | Explicit original element resource. |
| `element_radii` | No overrides | Positive per-element length overrides. |
| `workers`, `timeout` | 1, 120 seconds | Serial execution and calculation timeout. |
| `max_grid_points` | 20,000,000 | Conservative preflight cell count, including aligned grid levels. |
| `virtual_display` | Automatic | On Linux without DISPLAY, start a private Xvfb. True/False select explicitly. |
| `xvfb_cmd` | `Xvfb` | Selected virtual-display executable. |

The reviewed Linux executable reports **1.2.0**, built from original source
[`76693ae9c2b44270ae0875cefd96f8c0e9c61246`](https://github.com/molovol/MoloVol/tree/76693ae9c2b44270ae0875cefd96f8c0e9c61246).
Building needs CMake, a C++20 compiler and wxWidgets. Disabling the optional
renderer avoids VTK; the CLI still initializes wxWidgets and needs a display.
On headless Linux, install Xvfb. TopoMT allocates its own display, disables TCP,
sets DISPLAY only for the child and cleans up its own server after success or
failure. Calculation timeout excludes the bounded display startup/cleanup.
Other versions and platform/package builds need separate qualification; an
available executable alone does not establish protocol compatibility.

## Save, recover and cite

```python
output.save('molovol.zip')
restored = tmt.load_provider_output('molovol.zip', molecular_system=source)
print(tmt.cite(restored))
```

Reading verifies source/frame/chemistry, submitted PDB mapping, original query,
effective radii and saved resource fingerprints. It needs neither MoloVol,
Xvfb nor a network connection. It preserves the producing software's version
and attribution without recording another calculation. Raw historical reports
alone do not establish that source-bound provenance.

A successful run contributes the MoloVol software/article to the application's
optional Ackredit session. For the recognized original resource, it also credits
the Alvarez radii actually selected without overrides and the referenced IUPAC
atomic weights used. All-radii overrides omit the unused radii citation. Custom
tables retain their fingerprint without invented data references. Saving and
reading preserve that bibliography when the recorder is absent.

An explicit completed report with no internal rows is a valid empty result.
Missing, truncated, inconsistent, unsupported or cavity-capped reports are
failures, even if the program exits zero. A failed original execution retains
inspectable artifacts on `ProviderExecutionError.run` when within the capture
budget; it earns no MoloVol completion credit. Source conversion may have its
own completed attribution.

The source checks cover four small synthetic execution controls and direct
report agreement. They do not establish broad scientific accuracy, a DFND
advantage or a published package/platform support matrix.
