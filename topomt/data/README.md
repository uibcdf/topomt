# Data Layout

TopoMT package data currently contains two kinds of assets:

- canonical molecular structure inputs used by demos and tests;
- reference outputs produced by external tools such as fpocket or CASTp.

## Preferred canonical format

When available, canonical structure inputs should be stored as original
`*.bcif.gz` files from the PDB archive. These retain more information than the
legacy `*.pdb` files and are therefore the preferred source format for TopoMT.

`*.pdb` files should be kept only when:

- a third-party engine requires them as input;
- there is no original `*.bcif.gz` file bundled yet;
- or they are part of a reference output produced by an external tool.

## Current policy

- `topomt.demo` now prefers `*.bcif.gz` files when they exist next to the legacy
  `*.pdb` files.
- fpocket reference fixtures remain under `topomt/data/fpocket4/`.
- CASTp reference fixtures remain under their current system-specific folders.

## Next cleanup target

The next repository cleanup should introduce a clearer separation between:

- canonical structure assets;
- engine-specific reference outputs;
- and historical sample bundles that are only kept for parser regression tests.
