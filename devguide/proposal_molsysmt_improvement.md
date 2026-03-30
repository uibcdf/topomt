# Proposal: MolSysMT Improvements Here

During the TopoMT reimplementation effort we are expanding the use of
`molsysmt`.

Record the requirement, the desired API shape, and why the change would benefit other
projects. That way we can
track the request, shape a PR, and keep TopoMT aligned with the central
`molsysmt` configuration.

**Proposal: Promote TopoMT Grid/Overlap Helpers to MolSysMT**

Throughout the AlphaSpace2 work we implemented `_grid_volume` and `_overlap_matrices`
inside TopoMT to characterize pockets without reusing the upstream code. These purely
numeric helpers operate on NumPy arrays and do not depend on TopoMT-internal modules,
so they would fit naturally inside `MolSysMT` (e.g., `molsysmt.analysis` or
`molsysmt.metrics`). Moving them upstream will prevent duplication when other surface
analysis tools need the same cavity descriptors and keeps the shared utility registry
centralized.

**Key functions**

- `grid_volume(points, threshold, resolution)`: voxelizes a point set, marks voxels
  within the threshold, and returns the accumulated volume.
- `overlap_matrices(groups, total_size)`: converts thereference pocket alpha indices
  into incidence vectors and returns both the intersection and union matrices for
  overlap/count statistics.

If MolSysMT accepts the proposal, TopoMT would import these helpers instead of
keeping a local copy in `topomt/methods/alphaspace2.py`. This is the right place to
record the idea so we can follow up with a PR or issue in MolSysMT when the need
arises.
