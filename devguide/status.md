# TopoMT Status

## Summary

TopoMT is in an intermediate stage.

The project already contains:

- a coherent conceptual model based on `Topography` and `Feature` objects;
- a public orchestrator, `get_topography()`;
- multiple integrated engines;
- initial tests and documentation;
- ecosystem hooks for MolSysSuite packages.

However, it is not yet in a polished or stable product state.

## What is currently solid

- The central object model based on `Topography`, `Pocket`, `Void`, `Channel`,
  and `Mouth`.
- The idea of a unified API for topography detection.
- Basic interoperability with `molsysmt`.
- Initial integration of `argdigest`, `depdigest`, `pyunitwizard`, and
  `smonitor`.
- A faithful `fpocket4` integration path for the currently supported reference
  PDB systems. For the validated systems, TopoMT reproduces the direct fpocket
  binary output in terms of detected pockets, atom membership, pocket ranking,
  `Pocket Score`, and `Drug Score`.
- The AFND design and documentation package in `devguide/AFND/`.

For AFND specifically, what is solid today is mostly the design and the
documentation set, especially:

- [AFND/Overview.md](AFND/Overview.md)
- [AFND/Technical_Design.md](AFND/Technical_Design.md)
- [AFND/checkpoint.md](AFND/checkpoint.md)

## What is currently the priority

The current priority is to make TopoMT reliable inside MolSysSuite for these
engines:

- `pocketeer`
- `alphaspace2`
- `fpocket4`
- `pocket_geometry`
- `pycasta`

This includes:

- reliable atom-index mapping;
- consistent internal units;
- stable feature contracts for `Topography`;
- tests for non-AFND workflows;
- preparation for future visualization in MolSysViewer.

## What is currently in progress

- Stabilization of the non-AFND surface of the library.
- Cleanup of feature and topography internals.
- Better internal contract normalization across engines.
- Expansion of the `devguide/` to reflect the real project state.
- Extension of fpocket parity validation from the currently supported PDB set to
  additional inputs and, later, to canonical `bcif.gz` inputs.

## What is currently weak

- Public documentation is still sparse.
- Packaging metadata is still incomplete.
- The developer guide is still being built.
- Tests are unevenly distributed across engines.
- Some geometry utilities still mix stable and experimental behavior.
- Some historical PDB inputs still fail upstream parsing in `molsysmt`. At the
  moment this blocks full fpocket parity auditing for `1ATP.pdb`, `1CEN.pdb`,
  `1YCR.pdb`, and `2HGR.pdb`.

## What is postponed

AFND is postponed for now.

This does not mean AFND is unimportant. It means the project should first
consolidate the conventional engine path and the common `Topography` surface
before resuming work on the experimental alpha-flow network.

The practical reading is:

- AFND remains part of the project vision;
- AFND documentation should keep being referenced from the main guide;
- AFND implementation work should not drive current priorities.

## Working interpretation of project maturity

The practical interpretation is:

- The project is usable for development and experimentation.
- It is not yet ready to be presented as a fully stabilized library.
- The `0.1.0` milestone records the first faithful fpocket reproduction
  checkpoint on the supported reference PDB systems.
