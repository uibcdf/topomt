# A complete worked reading: the regular tetrahedron

This example connects the input model, independent geometry, query states,
native records and public result. It uses the unchanged
[regular-tetrahedron BenchLab unit](../benchlab/synthetic/regular_tetrahedron/index.md),
not a newly generated molecular system.

## The system

The system has four carbon dummy atoms at regular tetrahedron vertices, edge
$a=5.3$ Å, with equal atomic radii $r=1.7$ Å. This small system lets us predict
accommodation and entry independently of the detector.

## Predict the local capacities independently

The [regular-simplex derivation](appendices/clearance_derivations.md) gives

$$R_T=1.545573909\ \text{Å},\qquad R_f=1.359956427\ \text{Å}.$$

The single-cell Delaunay support is the quadruplet of all four source atoms.
At each query, its numerical capacities remain the same; threshold states change.

| Probe | Resident | Admitted faces | Finite transit components | Current public feature |
| --- | --- | --- | --- | --- |
| 1.2 Å | Yes | 4 | 1 | Percolating |
| 1.4 Å | Yes | 0 | 1 | Void |
| 1.7 Å | No | 0 | 0 | None |

```{figure} ../benchlab/synthetic/regular_tetrahedron/artifacts/native_study_v1/dfnd_probes.png
:alt: A probe fits at the tetrahedron center at 1.2 and 1.4 angstrom, but overlaps atomic balls at 1.7 angstrom.

Increasing the probe removes face access before it removes local residence.
The labels in this stored figure are native graph classifications: at 1.2 Å,
Percolating does not mean that the whole hull surface is free. The physical
reference below distinguishes four free patches from one native link.
```

At 1.2 Å the four hull contacts share atomic edges and cluster into one native
exterior link. There are zero native wall faces, triggering the Percolating
override. At 1.4 Å the cell is resident without an admitted contact, giving Void.
At 1.7 Å it is nonresident and has no connector contacts, so the wet result is
empty. The retained mesh/raw cell and dry-side information do not disappear.

## Compare with the physical reference

At 1.2 Å the expanded atom radius is 2.9 Å, exceeding half an edge by 0.25 Å.
All six shared edges are covered. The independent certificate verifies one
connected strict-free patch inside each face and four collision-free centroid
rays to infinity. Thus the physical hull has four patches attached to the same
free central region. Current output has one native link and zero public Mouth
children. The bounded physical record now supplies four patches and four
path-supported contacts separately. Its complete-cover controls supply zero
at 1.4 and 1.7 Å. Their definitions explain the different counts without
changing the compatibility class or promoting additional Mouth children.
See [physical support and availability](exterior_and_boundaries.md#inspect-the-physical-observation).

At 1.4 Å every hull face is covered, while the centroid remains free. At 1.7 Å
the whole finite hull is covered. These are independently justified geometric
controls, not just interpretations inferred from the returned class names.
The [certificate page](../benchlab/synthetic/regular_tetrahedron/boundary_connectivity.md)
retains witnesses, margins and verification scope.

## Measure three different volumes

The same single-cell carrier also makes volume definitions visible. Its volume
is **17.545323 Å³**. Original vertex balls are disjoint and do not reach an
opposite face, so independently subtracting four solid-angle sectors gives
**13.934035 Å³** of bare empty space. The
[volume study](../benchlab/synthetic/volume_measurements.md) checks those
hypotheses and the numerical quadrature error. Probe-expanded balls overlap;
the disjoint-sector formula cannot be reused for that different integral.

Actual public sampling gives about **0.914 Å³** of probe-center space at 1.2 Å
and **0.050 Å³** at 1.4 Å, on the same finite support. Each has its own conditional
confidence interval. The positive enclosed volume at 1.4 Å is consistent with
zero free hull patches. These measurements do not reconstruct swept or globally
exterior-accessible volume.

## Optional: reproduce and inspect the result

The JSON stores full-precision quantity records; the PDB rounds coordinates and
supplies dummy topology. The script restores the JSON coordinates before analysis.

Save the two input files inside `tetrahedron_input/`, and save the script next
to that directory:

- {download}`input.json <../benchlab/synthetic/regular_tetrahedron/artifacts/regular_tetrahedron_v1/input.json>`
- {download}`input.pdb <../benchlab/synthetic/regular_tetrahedron/artifacts/regular_tetrahedron_v1/input.pdb>`
- {download}`tetrahedron.py <examples/tetrahedron.py>`

```text
tetrahedron_study/
  tetrahedron.py
  tetrahedron_input/
    input.json
    input.pdb
```

The script verifies the frozen JSON SHA-256 and received radii, uses and checks
the current `vdw` radius policy, and explicitly selects probes 1.2/1.4/1.7 Å,
epsilon $10^{-6}$ Å, zero extra tolerances, connector-enabled transit,
diagnostic-only intrusion, face bank adjacency and `min_size=0`.

```bash
python tetrahedron.py tetrahedron_input
```

Run the command from `tetrahedron_study/`. The Python snippets below use that
same working directory, with `tetrahedron.py` available for import. No
provider service, downloaded protein or additional engine is required.

### Execute the public analysis

```{literalinclude} examples/tetrahedron.py
:language: python
:pyobject: analyze_tetrahedron
```

The downloadable file includes all imports. This function creates three
independently promoted Topography results for clarity; on this four-atom system
the repeated construction is small. It is not a recommended strategy for a
large probe sweep requiring only native records.

## Follow a public finding back to its support

```python
from pathlib import Path
from tetrahedron import analyze_tetrahedron
from topomt import pyunitwizard as puw

results = analyze_tetrahedron(Path('tetrahedron_input'))
topography = results[1.4]
feature = next(iter(topography.get_features(by='type', value='void')))
component = topography.dfnd.dfn.components[feature.component_id]
assert feature.source_id == component.component_key
assert feature.support_key == component.support_key
source_atom_indices = topography.input_context.atom_indices.tolist()
center = puw.get_value(feature.center, to_unit='angstroms')
```

The source atom map is `[0, 1, 2, 3]`. The center is the centroid, up to numerical
roundoff. The native `tetrahedra` and `faces` retain atom-defined support and
capacities in nm. Compare those values after conversion rather than treating
1.545573909 as a native nm radius.

The complete carrier volume is $a^3/(6\sqrt2)$ in Å³. It includes atom-occupied
sectors; the fast local empty estimate subtracts exclusion only approximately.
Neither value is automatically a probe-center-accessible volume.

## Read an unavailable descriptor correctly

The Void has a valid interior capacity but no native exterior link. Consequently
it has no mouth radius or occlusion ratio. Its single center also cannot define
PCA elongation or a four-level access profile:

```python
metrics = component.morphometrics
assert metrics['mouth_radius'] is None
assert metrics['occlusion'] is None
assert metrics['elongation'] is None
assert metrics['funnel'] is None
```

These `None` values are expected availability states. They do not mean a zero
mouth area, zero elongation or a failed analysis. The stored `buriedness` is 0
under the no-exterior flat-depth convention, which does not imply shallow
physical burial. [Classification](classification.md#reconstruct-the-morphology-record)
specifies the full morphology record and its fallbacks.

## Reuse the geometry without mutating the public finding

```python
larger = topography.dfnd.at_probe(puw.quantity(1.7, 'angstroms'))
assert larger.network is topography.dfnd.network
assert not larger.dfn.components.wet
assert topography.get_features(by='type', value='void')
```

The old Void remains in `topography`. `larger` is a new native DFNDData result,
not an automatically re-promoted Topography. An empty wet result here is a
completed analysis, while the uncomputed physical-patch view has no invented
zero count.

## What to carry into the next examples

The [closed shell](../benchlab/synthetic/closed_shell/index.md) and
[shell with opening](../benchlab/synthetic/shell_with_opening/index.md) add
many-cell enclosure and one-opening controls. They do not turn this tetrahedron
into evidence for every internal hierarchy, relief operator or molecular
interface. Source regression tests execute the downloadable example under nm
and pm policies, compare capacities to the independent formulas and guard its
public/native correspondence. Documentation rendering itself does not rerun it.
