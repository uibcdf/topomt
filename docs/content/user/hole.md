# HOLE: an original pore-radius profile

[HOLE](https://github.com/osmart/hole2) is an optional external executable.
TopoMT prepares its input cards and reads its original output; HOLE performs
the calculation. The qualified spherical protocol is HOLE 2.3.1, Apache-2.0.

Provide a starting point, a direction and the atomic-radius resource to use:

```python
import topomt as tmt
from topomt import pyunitwizard as puw

output = tmt.get_provider_output(
    'channel.pdb', method='hole', hole_cmd='/tools/hole',
    radii_file='/tools/hole2/rad/simple.rad',
    origin=puw.quantity([0, 0, 0], 'angstroms'), direction=[0, 0, 1],
    sample_step=0.5, end_radius=10.0, random_seed=12345,
)
path = output.channels[0]
centers = path.geometries['centerline'].coordinates
minimum = path.measurements['minimum_radius']
profile = path.fields['profile']
```

The direction is dimensionless and normalized. The origin requires a length
quantity. Bare `sample_step` and `end_radius` values mean angstroms; compatible
quantities are accepted. Defaults are 0.5 Å, 10 Å and seed 12345. The original
`rad/simple.rad` beside the selected distribution is used if `radii_file` is
omitted; supply the file explicitly when its location differs. It is an
AMBER united-atom model, not TopoMT's or DFND's radius assignment.

## Reading the result

`output.channels` contains the original sampled path. `profile['sampled']` and
`profile['midpoints']` preserve separate original evaluations. Their coordinate,
signed centerline distance and radius packets carry angstroms; the resistance
factor carries inverse angstroms. The path's minimum is HOLE's sampled-node
minimum. It is distinct from a minimum over a continuous curve or every
between-plane evaluation.

The center coordinates have the original sphere-PDB precision of 0.001 Å.
Artificial end extensions used for visualization are excluded. An identical
repeated origin record is not counted twice. Negative reported clearances stay
negative in the profile; such a path has point geometry without nonnegative
sphere radii. No path is promoted to a certified traversable channel or swept
volume. A lining-atom map is unavailable in this route.

HOLE requires steering and uses stochastic local optimization. A result does
not establish a globally widest path, transport, hydration or conductance.
The complete original report remains in `output.run` for further inspection.

## Execution and reuse

Build/acquire HOLE separately following its original documentation. A Fortran
compiler is needed to build the source. This adapter does not install or ship
HOLE. `workers=1`, `timeout=120` seconds and `max_atoms=25000` bound the selected
route; a missing command/resource and a failed original calculation have
distinct diagnostics. Exit zero alone is insufficient for success.

```python
output.save('hole.zip')
restored = tmt.load_provider_output('hole.zip', molecular_system='channel.pdb')
```

Recovery verifies the original source/frame/selection/chemistry, radius and
control fingerprints, reported query, profile and sphere data. It needs no
HOLE executable and earns no new calculation credit. Successful calculations
contribute the original HOLE citation and software identity to optional
Ackredit; the recognized original AMBER table additionally contributes its
input-data reference. Custom tables preserve their bytes without invented
citations. Source qualification uses a small frozen synthetic tube; broader
engine fidelity and installed/platform qualification remain separate.
