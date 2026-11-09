# A complete worked reading: the regular tetrahedron

This example connects the input model, independent geometry, query states,
native records and public result. It uses the unchanged
[regular-tetrahedron BenchLab unit](../benchlab/synthetic/regular_tetrahedron/index.md),
not a newly generated molecular system.

## Exact input and query

The system has four carbon dummy atoms at regular tetrahedron vertices, edge
$a=5.3$ Å, with equal atomic radii $r=1.7$ Å. The JSON stores full-precision
quantity records; the PDB supplies dummy topology but rounds coordinates.
Restore the JSON coordinates before analysis.

Download these files into the same local directory:

- {download}`input.json <../benchlab/synthetic/regular_tetrahedron/artifacts/regular_tetrahedron_v1/input.json>`
- {download}`input.pdb <../benchlab/synthetic/regular_tetrahedron/artifacts/regular_tetrahedron_v1/input.pdb>`
- {download}`tetrahedron.py <examples/tetrahedron.py>`

The script verifies the frozen JSON SHA-256 and received radii, uses and checks
the current `vdw` radius policy, and explicitly selects probes 1.2/1.4/1.7 Å,
epsilon $10^{-6}$ Å, zero extra tolerances, connector-enabled transit,
diagnostic-only intrusion, face bank adjacency and `min_size=0`.

```bash
python tetrahedron.py tetrahedron_input
```

Here `tetrahedron_input` is the directory containing the two input files. No
provider service, downloaded protein or additional engine is required.

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
children. Their definitions explain the different counts; physical refinement
is still pending.

At 1.4 Å every hull face is covered, while the centroid remains free. At 1.7 Å
the whole finite hull is covered. These are independently justified geometric
controls, not just interpretations inferred from the returned class names.
The [certificate page](../benchlab/synthetic/regular_tetrahedron/boundary_connectivity.md)
retains witnesses, margins and verification scope.

## Execute the public analysis

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
