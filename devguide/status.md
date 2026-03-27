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
- A faithful `fpocket4` wrapper-backed integration path for the currently supported reference
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
- Separation of wrapper-backed integrations from the long-term native-method
  targets in `topomt.methods`.
- Study of `2HGR.pdb` as a large-system deep-validation case for `fpocket4`.
  Final native/source parity is now confirmed there too, but it remains outside
  the default parity battery because of cost.
- A focused diagnostic campaign on the residual raw-tetrahedrization mismatch
  between native `fpocket4` and the upstream embedded-Qhull path, especially on
  `1GG0.pdb` and `3LKF.pdb`, together with fpocket build-drift checks on
  `1GG0.pdb`, `3LKF.pdb`, and `E15ALA.pdb`.

## What is currently weak

- Public documentation is still sparse.
- Packaging metadata is still incomplete.
- The developer guide is still being built.
- Tests are unevenly distributed across engines.
- Some geometry utilities still mix stable and experimental behavior.
- Native `fpocket4` is no longer only a first experimental stage at the final
  pocket-output level. It now reaches exact final-pocket parity against the
  current audited local fpocket source build on the full audited PDB set:
  `1ATP.pdb`, `1CEN.pdb`, `1GG0.pdb`, `1N57.pdb`, `1YCR.pdb`, `2GI9.pdb`,
  `2H05.pdb`, `2HGR.pdb`, `3LKF.pdb`, and `E15ALA.pdb`.
- The remaining source-level open problem is now concentrated in the raw
  geometry layer: a small deterministic super-set of tetrahedra in local
  regions, mainly in `1GG0.pdb` and `3LKF.pdb`.
- `E15ALA.pdb` is no longer treated as a native/source residual mismatch. The
  current discrepancy there is between different fpocket binaries/builds: the
  system binary used by wrapper mode yields `9` pockets, while the locally
  instrumented build compiled from the upstream source and the current native
  path both yield `8`.
- `1GG0.pdb` and `3LKF.pdb` also show wrapper-vs-native differences against the
  current system fpocket binary, but those differences disappear when compared
  against the audited local fpocket source build. They are therefore currently
  treated as fpocket build-drift cases at the final pocket-output level.
- `2HGR.pdb` is currently treated as a large-system deep-validation case. Final
  parity is now measured there (`612` final pockets in both audited upstream
  and `native`), but it still remains outside the default parity battery
  because the run is expensive.
- `alphaspace2` has now reached parity in the current native tests for
  alpha-sphere generation and pocket/atom ownership on the audited reference
  systems, but further descriptor and scoring work is still pending.

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
  checkpoint on the supported reference PDB systems through the wrapper-backed
  integration path.
