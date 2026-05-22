# DFND Input Policy Hardening Checkpoint

This checkpoint records the current engineering policy for molecular input into
DFND. It is not a validation of cavity-detection quality.

## Current Policy

- Molecular loading, atom selection, coordinates, and atomic radii are delegated
  to MolSysMT.
- Alternate-location resolution is not duplicated in TopoMT. MolSysMT already
  provides `solve_atoms_with_alternate_location(...)`, including the occupancy
  based policy and the `A` conformer tie-break for 0.5 occupancies.
- DFND validates the selected atom set before triangulation.
- `hydrogen_policy='exclude'` removes atoms with `atom_type == "H"` through
  MolSysMT selection masking.
- `hydrogen_policy='include'` keeps the selected atoms unchanged.

## Defensive Checks Added

DFND now raises clear `ValueError` exceptions for:

- empty molecular selections;
- selections that become empty after hydrogen exclusion;
- inconsistent coordinate/radius/atom-index array shapes;
- non-finite coordinates;
- non-finite atomic radii;
- non-positive atomic radii;
- fewer than four atoms before Delaunay triangulation.

## Tests

`tests/test_dfnd_input_policy.py` covers the input-policy failure modes above.
The tests intentionally focus on pipeline robustness and clear failure messages,
not on whether the detected cavities are scientifically correct.

`tests/test_dfnd_real_system_stability.py` also includes composition smoke tests
for `selection='all'` versus protein-only selections on small CASTpFold systems:

- `1rop`: protein plus waters;
- `2pk4`: protein plus waters and acetate.

These tests assert that `selection='all'` expands the atom set and Delaunay
substrate relative to protein-only while preserving raw-record invariants.
They do not assert that any cavity family is biologically correct.

## Pending Input Topics

- Keep alternate-location tests in MolSysMT. DFND v1 assumes MolSysMT provides
  one resolved coordinate per selected atom and does not expose `altloc_policy`.
- Add broader composition-policy tests only when they reveal input robustness
  issues; the first `selection='all'` versus protein-only smoke tests already
  cover waters and a small ligand.
