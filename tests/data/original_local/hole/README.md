# Original HOLE evidence

Owner: uibcdf/topomt#192; source/execution scope is recorded in
`devguide/specialist_provider_checkpoint.md`. Original unchanged source is
`osmart/hole2@a8eaf6121ba66625446933f4acd7d6aa336dbb47`, Apache-2.0, program 2.3.1.
No scientific source or executable is distributed in this directory.

`input.pdb` is a synthetic 77-argon tube, distinct from frozen BenchLab cases.
`radii.rad` assigns Ar=1.88 angstroms. `control.in`, `stdout.txt`, `profile.sph`
and `receipt.json` retain an initial direct original run. The source-bound ZIPs
come from subsequent genuine public-adapter executions:

- `hole.zip`: custom argon radius table, origin [0,0,0] angstroms, direction
  [0,0,1], step 0.5 angstrom, end radius 7 angstroms, seed 12345. A second direct
  original execution agrees with the adapter's profile.
- `hole-amber.zip`: same coordinates with carbon identities in
  `carbon_input.pdb`, recognized original `simple.rad` AMBER resource. This is
  a distinct radius model and exercises conditional input-data attribution.
- `hole-failed.zip`: deliberately unsuitable original radius resource; original
  execution fails. It retains attempted executable/input identity and output,
  without completed-provider attribution.

The successful custom control retains 67 sampled and 66 midpoint evaluations.
Two hundred artificial end-extension rows are excluded, and an identical
repeated origin is deduplicated. Preserve signed clearances and the original
sampled minimum; neither is a continuous/global-path or transport certificate.
Saved paths/resource names/timestamps describe the historical producer only.
`protocol.json` records exact retained file hashes. Guards are
`tests/test_specialist_original_execution.py`,
`tests/test_specialist_provider_parsers.py` and
`tests/test_specialist_provider_recovery.py`. This is adapter qualification,
not a DFND comparison, exact-geometry reference or installed/platform matrix.
