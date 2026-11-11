# Original serial POVME evidence

Owner: uibcdf/topomt#193. The modern original source is
`durrantlab/POVME@8a9f1973c25eb52e36e0d7b20183bf896cb66729`, not the historical
v2.2.2 tag. The separately executed compatibility fork is
`uibcdf/POVME@0c55f591dea3156e1ca76a486cf1f71d56c3a192`, reporting
2.2.2+uibcdf.1. Its scientific modules and serial methods retain original bytes;
README/LICENSE grant GPLv3-or-later. Original pymolecule is
`614a95a0b792f83fbee77e4c7eed7d5ce046dee1` (0.0.1).
No engine source is distributed here.

The source is the synthetic 40-atom `../pisa/input.pdb`; it is not a protein
benchmark or native DFND characterization. Each ZIP captures its own exact
submitted PDB, source context, original configuration, engine/module identities,
stdout/stderr, diagnostics, original CSV and available point files. Each
successful branch is checked against a direct original public-API execution:

- `povme-positive.zip`: box center [0,2.5,5.5], lengths [6,7,9] angstroms,
  grid 1 angstrom, cutoff 0, hull disabled, contiguous criterion 0. Volume
  330 cubic angstroms and available retained points.
- `povme-empty.zip`: original atom filtering removes the sampled points;
  accepted evaluated zero volume with an available empty point set.
- `povme-outside.zip`: original early return outside the atoms reports volume
  without writing the retained-point PDB. Geometry remains unavailable, not
  an invented empty point set.
- `povme-failed.zip`: inclusion/exclusion spheres at zero with radii 1/4
  angstroms; grid 1, cutoff 1.09 angstrom, hull disabled, criterion 4, no seeds.
  The fully excluded initial point field triggers the original zero-size
  reduction error. TopoMT retains failure without completion credit.

The last observation remains `needs_review` under TopoMT#195 and UIBCDF/POVME#1;
it is distinct from the valid late zero. No matched DFND comparison, original
Python 3.12 or Ray execution, scientific correction or geometric inferiority
claim is established. The measured runtime is Python 3.14.10, NumPy 2.5.4,
SciPy 1.18.1, Pydantic 2.14.3 and Loguru 0.7.3, without Ray.
See `devguide/specialist_provider_checkpoint.md` and
`devguide/pending_bugs/povme_empty_initial_roi.md` for exact scope.

`protocol.json` records retained file hashes. Guards are
`tests/test_specialist_original_execution.py`, `tests/test_povme_provider.py`
and `tests/test_specialist_provider_recovery.py`. Saved producer paths remain
historical and are not reopened by readers. These are adapter/source controls,
not installed-release, general accuracy or platform qualification.
