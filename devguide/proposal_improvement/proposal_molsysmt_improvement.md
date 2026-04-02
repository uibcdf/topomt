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

## Proposal: Fix PDB parsing failure on `1byb.pdb`

Status: resolved locally after the MolSysMT-side fix. Kept here as historical
record because it explained a temporary benchmark blocker during the expanded
`pycasta` audit.

During the expanded `pycasta` parity audit we found a separate ecosystem issue
that is not an algorithm-parity problem in `pycasta` itself.

### Symptom

The upstream public `pycasta` repository can process:

- `~/repos@others/pycasta/src/pycasta/data/bounded/1byb.pdb`

But the current TopoMT-native route fails earlier when `molsysmt` tries to
ingest the same PDB file.

Observed exception:

```python
TypeError: unsupported operand type(s) for +=: 'NoneType' and 'str'
```

The traceback points into the current PDB parsing path inside
`molsysmt.native.pdb_file_handler`, specifically while accumulating `CAVEAT`
text during `parse_format33(...)`.

### Minimal reproduction

```python
import molsysmt as msm

msm.convert(
    '/home/diego/repos@others/pycasta/src/pycasta/data/bounded/1byb.pdb',
    to_form='molsysmt.MolSys',
)
```

Current result:

- raises `TypeError: unsupported operand type(s) for +=: 'NoneType' and 'str'`

### Why this matters beyond TopoMT

- it blocks benchmark coverage for engines that rely on `molsysmt` as their
  ingestion layer;
- it is independent from the `pycasta` algorithm itself;
- and it means some PDB inputs accepted by downstream tools are still rejected
  too early by the MolSysMT parsing layer.

### Current TopoMT reading

- `1apu` is a native-versus-upstream semantic residual in `pycasta`
  (`molsysmt` molecular selection versus upstream `ATOM/HETATM` preprocessing);
- `1byb` is a different problem and should be treated as a MolSysMT ingestion
  bug, not as a `pycasta` parity residual.

### Expected fix direction

- initialize the `CAVEAT` accumulator robustly in the PDB parser before
  concatenation;
- add a regression test in MolSysMT that loads `1byb.pdb` successfully;
- and verify that the fix does not alter current behavior on already supported
  PDB inputs.

### Suggested follow-up

- open an issue or PR in MolSysMT with the minimal reproduction above;
- include `1byb.pdb` as a parser regression fixture if that repository accepts
  external benchmark files or reduced reproducer snippets.

### Draft issue text for MolSysMT

**Title**

`PDB parser fails on 1byb.pdb with TypeError while accumulating CAVEAT records`

**Body**

While expanding the TopoMT native `pycasta` parity battery we found a PDB
ingestion failure that appears to belong to MolSysMT rather than to the pocket
algorithm itself.

The file:

- `~/repos@others/pycasta/src/pycasta/data/bounded/1byb.pdb`

can be processed by the upstream public `pycasta` repository, but it currently
fails in MolSysMT during PDB ingestion.

Minimal reproduction:

```python
import molsysmt as msm

msm.convert(
    '/home/diego/repos@others/pycasta/src/pycasta/data/bounded/1byb.pdb',
    to_form='molsysmt.MolSys',
)
```

Current result:

```python
TypeError: unsupported operand type(s) for +=: 'NoneType' and 'str'
```

Current reading from the traceback:

- the failure happens inside the PDB parsing path;
- specifically while accumulating `CAVEAT` text in
  `molsysmt.native.pdb_file_handler.parse_format33(...)`.

Why this matters:

- it blocks TopoMT-native ingestion for benchmark systems that upstream tools
  can still process;
- it is independent from the `pycasta` algorithm itself;
- and it suggests MolSysMT still rejects some valid or at least practically
  relevant PDB files too early in the parsing layer.

Suggested fix direction:

- initialize the `CAVEAT` comment accumulator defensively before concatenation;
- add a regression test for `1byb.pdb` or for a reduced reproducer containing
  the relevant `CAVEAT` pattern;
- verify that existing supported PDB inputs remain unaffected.

Related context:

- this issue was found while auditing TopoMT native `pycasta`;
- it is separate from a different `pycasta` parity residual on `1apu.pdb`,
  which is about upstream `ATOM/HETATM` preprocessing semantics rather than a
  MolSysMT parser failure.
