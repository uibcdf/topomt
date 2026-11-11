# Original MoloVol evidence

Owner: uibcdf/topomt#190. All coordinates are the public synthetic four-carbon
control, exact decimal PDB ±1.874 Å; not full-precision BenchLab JSON geometry.
Original unchanged source is `76693ae9c2b44270ae0875cefd96f8c0e9c61246`, MIT,
printed version 1.2.0. `LICENSE` and `elements.txt` are original source copies.
The latter uses carbon radius 1.77 Å. No executable is distributed here.

`protocol.json` and the plain original report preserve the initial direct
1.4 Å pilot with explicit C=1.7 Å. The four ZIPs are subsequent genuine public
API captures, each checked against another direct original execution:

| Bundle | Probe/grid in angstroms | Outcome |
| --- | --- | --- |
| isolated | 1.4 / 0.1, C=1.7, depth 4, surfaces | One Isolated internal row; original Outside retained separately. |
| empty | 6 / 0.3, C=1.7, depth 4 | Complete report, zero internal rows. |
| two_probe | 1.4 and 4 / 0.2, C=1.7, depth 4 | Five original internal rows with distinct type labels. |
| table_radii | 1.4 / 0.2, original C=1.77, depth 4 | One internal row, original radii data attribution. |

Each ZIP preserves exact submitted PDB, full original source context, source and
effective element tables, stdout/stderr/report, query/radii/resource/executable
fingerprints and separate producer attribution. Input paths/timestamps are
historical execution facts. The initial pilot and adapter serialize the same
override with different decimal text; use each capture's own exact bytes/hash.

The fixtures establish bounded adapter fidelity and recoverable original
observations. They are not exact-volume reference truth, a DFND comparison,
percolation classification or package/platform qualification. See
`devguide/molovol/overview.md` for build and evidence boundaries. Offline guards
are `tests/test_molovol_provider.py`; the explicit original execution gate is
`tests/methods/molovol/test_original_cli.py`.
