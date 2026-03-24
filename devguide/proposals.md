# Pocket Detection & Characterization Proposals

## Shortlist

- **SASA integration**: add a real SASA backend (e.g., FreeSASA/MDTraj) to:
  - Pocketeer flow (burial filter)
  - PyCASTA/AlphaSpace nonpolar ratio
  - `pocket_geometry` descriptors (contact validation)
- [DONE] **Unified interface**: wrapper to run `fpocket4`, `pycasta`, `alphaspace2`, or `pocketeer` behind a single API with harmonized outputs (ids, volumes, scores, mouths, contacts). Implementation: `topomt.get_topography()`.
- **Advanced descriptors**:
  - Energy/probe grids (simple interaction maps)
  - Refined bottleneck profiling for channels
  - Lightweight pharmacophore scoring (probe scoring with atom typing)
- **Visualization**:
  - Helpers to render pockets, mouths, and axes in molsysviewer/py3Dmol
  - Export meshes (PLY/OBJ) from marching-cubes results
- **Tests/benchmarks**:
  - Unit tests for new detectors and geometry utils
  - Micro-benchmarks comparing volume/area methods (marching cubes vs voxel)
