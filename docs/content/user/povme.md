# POVME: volume inside a chosen region

[POVME](https://github.com/durrantlab/POVME) measures the free grid volume inside
regions selected by the researcher. TopoMT calls the external Python engine in
an isolated serial worker and reads its original files. It does not discover
an unknown cavity merely because an inclusion region was supplied.

```python
import topomt as tmt
from topomt import pyunitwizard as puw

output = tmt.get_provider_output(
    'receptor.pdb', method='povme',
    upstream_root='/sources/POVME-uibcdf',
    pymolecule_root='/sources/pymolecule',
    inclusion_regions=[{
        'shape': 'sphere',
        'center': puw.quantity([10, 20, 30], 'angstroms'),
        'radius': 6.0,
    }],
    grid_step=1.0, distance_cutoff=1.09,
    convex_hull_exclusion=True, contiguous_points_criteria=4,
)
region = output.regions[0]
volume = region.measurements['volume']
```

An inclusion region is required. A sphere has `shape`, a length-quantity
`center` and `radius`; a box has `shape`, `center` and length-quantity `lengths`.
Optional `exclusion_regions` remove grid points and `seed_regions` select a
connected subset using the original method. Bare radii, `grid_step` and
`distance_cutoff` are in Å; compatible quantities are accepted. The defaults
shown above retain the original hull and connectivity policy. A cutoff of zero
is allowed. An empty exclusion/seed list is allowed.

## Interpreting the volume and support

The original volume is the number of surviving grid points multiplied by the
grid spacing cubed, in Å³. It depends on the chosen region, original atomic
radii, atom-surface distance cutoff, optional hull and seed/connectivity rules.
It is distinct from a continuous closed-cavity volume or a DFND classification.

`output.regions` contains the analyzed frame's region, including an evaluated
zero volume. When the original writes its surviving points, they are exposed
as `region.geometries['retained_grid_points']` at PDB coordinate precision.
Some original early returns report a volume without writing those points:
`region.fields['point_support_status']` is then `not_written_by_original` and
the geometry is unavailable. It is not represented as an empty point set.
Original error-level frame fallbacks are rejected instead of being accepted
as valid zero-volume results.

In the captured modern-source control, exclusions covering the entire initial
region trigger an original frame error. This differs from the evaluated zero
after atom exclusion and remains under [source-specific review #195](https://github.com/uibcdf/topomt/issues/195).
TopoMT preserves that failure rather than supplying an invented successful result.

## External source and Python compatibility

The qualified source is the maintained modern rewrite reporting version 2.2.2,
distinct from the historical tag of that name. Our separate
[compatibility fork](https://github.com/uibcdf/POVME/tree/compatibility/python314-serial)
reports `2.2.2+uibcdf.1`. It changes packaging and optional Ray startup;
scientific modules and serial task methods retain original bytes. README/LICENSE
declare GPLv3-or-later; the fork corrects the conflicting Apache package metadata.

The measured serial route uses Python 3.14.10, NumPy 2.5.4, SciPy 1.18.1,
Pydantic 2.14.3, Loguru 0.7.3 and the separately pinned original `pymolecule`
source. Pydantic and Loguru retain their original minimums without unverified
upper bounds. The fork and molecular dependency remain external to TopoMT;
neither is copied into its package. Installing TopoMT does not install them.

Supply source roots, or use a separately installed matching engine and its
dependencies. `python_cmd` can select its interpreter. The selected protocol
uses `workers=1`, no Ray, `timeout=120` seconds, `max_grid_points=250000` and
`max_candidate_pairs=10000000`. Conservative preflight estimates bound all
region meshes and worst-case atom/grid neighbor storage before execution.
Ray, trajectories, every historical POVME version and a public installation
matrix are separate from these single-frame source controls.

```python
output.save('povme.zip')
restored = tmt.load_provider_output('povme.zip', molecular_system='receptor.pdb')
```

Saved reading needs no POVME, pymolecule, Pydantic, Loguru or Ray. It validates
source context, configuration, units, returned/CSV volume and reported point
counts, and preserves the original fork/version and bibliography. Fresh accepted
calculations credit POVME's requested papers and the software actually executed;
saved reading adds no calculation credit.
