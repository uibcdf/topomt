# From DFND to the public Topography object

**Current continuation:** the [support/robustness study](public_support_and_robustness.md)
and [v2 reader notebooks](index.md#download-and-run-the-current-reader-stage)
include later physical, numerical and support receiving. The original audit
below and v1 notebooks retain their original source/date.

The first three units now have an actual public receiving check through
`get_topography(method='dfnd')`. The native engine is not mocked. Coordinates
are restored from the frozen full-precision JSON, received atomic radii are
checked against its explicit array, and the opening uses the parent's source
atom IDs. All earlier scientific artifacts and notebooks retain their bytes.

| Case | Probe (Å) | Objects in `Topography` |
| --- | --- | --- |
| Regular tetrahedron | 1.2 / 1.4 / 1.7 | One `Percolating` / one `Void` / no features. |
| Closed shell | 0.05 / 1.4 / 5.0 | One `Channel` and ten `Mouth` children / one `Void` / no features. |
| Shell with opening | 1.4 / 3.0 / 5.0 | One `Pocket` and one `Mouth` child / one `Void` / no features. |

The [stronger 0.2 Å wall certificate](closed_shell/closure_at_0p2.md) additionally
supports the closed shell's public `Void` without a `Mouth` at that probe.

## What classification means here

There are three distinct stages:

1. The native graph records residence, walls and exterior-link clusters and
   assigns a family such as `void`, `pocket`, `channel` or `percolating`.
2. The native catalog may refine a one-link resident family using occlusion,
   elongation or depth. That can produce `Pocket`, `OpenConcavity`, `Groove`
   or `Cleft`; the latter refinements retain their provisional thresholds.
3. The bridge creates public objects, registers their type, shape and legacy
   dimensionality, and connects promoted `Mouth` children to their parent.

The three current examples keep the public names shown above. The receiving
checks verify the actual Python classes, catalog names, registry lookups and
relations, as well as dimensional quantities and contextual source/support keys.
`classification.confidence` describes contrast to a catalog threshold. It is
not a probability that a physical or biological interpretation is correct.

A public `Mouth` currently represents a native exterior-link cluster. Ten such
objects on the small-probe shell do not yet establish ten connected physical
openings. A percolating region has neutral shape and no promoted `Mouth`
children, even though its native graph has an exterior link.

For the opened shell at 1.4 Å, the later
[independent connectivity certificate](shell_with_opening/opening_connectivity.md)
does establish one connected free patch on the declared hull, incident to the
origin region. It matches that case's Mouth count/location; it does not qualify
the ten small-probe shell Mouths, all gate thresholds or free aperture areas.

The legacy public dimensionalities are 2 for these region objects and 1 for
their boundary objects. They are catalog conventions, not a declaration that
the recovered empty space is geometrically two-dimensional. Full neutral
support/availability adoption remains under [#60](https://github.com/uibcdf/topomt/issues/60).

## Physical contacts alongside the public catalog

The bounded source increment under #151 exposes
`topography.dfnd.dfn.boundary_connectivity` and
`feature.boundary['physical_openings']`. The five independent controls qualify
4/0/0 tetrahedron patches, zero at closed-shell 0.2 Å and one at opened-shell
1.4 Å, with supported component paths on the positive rows. Status, clipped
support, all-atom constraints and work/numerical policy remain inspectable.
Native-link Mouths and catalog classes retain their earlier meaning. Wider
small-probe shell counts and path/geometry qualification remain #76.
See the [method chapter](../../dfnd/exterior_and_boundaries.md) for exact fields
and the distinction between a global count and unresolved component attachment.

## Repeat the public receiving

Run this example from `docs/content/benchlab/synthetic/`. Change `case` to any
of the three names. It uses an existing dummy molecular topology; the PDB's
rounded coordinates and inferred chemistry do not replace the declared ball
model. A radius mismatch is an error rather than a silent input change.

```python
import json
from pathlib import Path

import molsysmt as msm
import numpy as np
from pyunitwizard import QuantityRecord

import topomt as tmt
from topomt import pyunitwizard as puw

case = 'shell_with_opening'
directory = Path(case)
protocol = json.loads(
    (directory / 'artifacts/public_topography_v1/protocol.json').read_text()
)
fixture = json.loads(
    (directory / f'artifacts/{case}_v1/input.json').read_text()
)
source_case = protocol['source_case']
source_dir = Path(source_case) / f'artifacts/{source_case}_v1'
source = json.loads((source_dir / 'input.json').read_text())

def quantity(record, field):
    return QuantityRecord.from_dict(record).to_quantity(
        field=field, unit='angstroms'
    )

system = msm.convert(str(source_dir / 'input.pdb'), to_form='molsysmt.MolSys')
coords = puw.get_value(quantity(source['coordinates'], 'coordinates'),
                       to_unit='angstroms')
msm.set(system, coordinates=puw.quantity(coords[None], 'angstroms'))
selection = protocol['selection']
received_radii = msm.physchem.get_atomic_radius(
    system, element='atom', selection=selection, definition='vdw'
)
np.testing.assert_allclose(
    puw.get_value(received_radii, to_unit='angstroms'),
    puw.get_value(quantity(fixture['atom_radii'], 'atom_radii'),
                  to_unit='angstroms'),
    rtol=0, atol=1e-14,
)
query = {
    key: quantity(value, key) if isinstance(value, dict) else value
    for key, value in protocol['query'].items()
}
query['epsilon'] = quantity(fixture['epsilon'], 'epsilon')
topography = tmt.get_topography(
    system, method='dfnd', selection=selection,
    probe_radius=puw.quantity(1.4, 'angstroms'), **query,
)
topography.info()
regions = topography.get_features(by='shape', value='concavity')
for region in regions:
    print(type(region).__name__, region.classification)
    print(topography.children_of(region.feature_id))
```

Increasing `min_size` above the raw region's total node count removes its public
projection and child mouths. It retains the raw component, geometric support
and physical result key. An empty public registry therefore needs its query
and reporting context: it is not always a physical absence. For the declared
large-probe controls, the native resident components are also genuinely absent.

## Remaining work on these same systems

The public bridge retains native dry structures under `topography.dfnd`, but
does not promote them into public convexity, buried-core or interface features.
The complete molecular-topography catalog is therefore not implemented or
validated by these three studies.

Development stays with these inputs before adding the tube. Physical mouth
connectivity, compatible continuous paths and exact-volume references retain
their own evidence requirements. The numerical contract is corrected in source `b7b5a60` under
[#75](https://github.com/uibcdf/topomt/issues/75), with [matched volume receiving](volume_measurements.md).
Wider physical/support reference progress remains [#76](https://github.com/uibcdf/topomt/issues/76).
The public receiving increment [#146](https://github.com/uibcdf/topomt/issues/146)
does not close those broader questions.

## Current executable reader stages

The independently executed [tetrahedron](regular_tetrahedron/public_topography.ipynb),
[closed shell](closed_shell/public_topography.ipynb) and
[opened shell](shell_with_opening/public_topography.ipynb) stages replay later
references and inspect actual public objects. Use the
[complete download](index.md#download-and-run-the-current-reader-stage) for
Jupyter; the retained Markdown receiving pages keep their existing addresses.
