# pathological_thin_tube

<!-- AUTO:build_synthetic_catalog -->
- **PDB:** `pathological_thin_tube.pdb`
- **Atoms:** 30 · **Probe:** 1.4 Å
- **Expected by construction:** historical alias of pathological_thin_tube_r25: identical stored coordinates, legacy PDB encoding; not an independent geometry
- **DFND families (significant):** Historical alias; no independent run
<!-- /AUTO -->

## What to observe

The 30 stored atomic coordinates and their order match
`pathological_thin_tube_r25.pdb` exactly. The historical file uses a different PDB
encoding. Its original SHA-256 is
`3b811baaf3f2704e43d45aba9b3532f47df5988b6685efd7894945cfa295dd87`.
The common generator uses length 16 Å, tube radius 2.5 Å, wall spacing 3 Å,
atomic radius 1.88 Å, jitter 0.1 Å and seed 0.

## Why

Retain the historical input and make its relationship to the radius-2.5 variant
explicit. It counts as a catalog entry, not an independent geometry or an
additional scientific reference. Catalog rebuilds preserve the original bytes.

## DFND verdict

No independent run is inferred from registration. Study probe accommodation and
continuous access with the radius-2.5 tube before interpreting any historical
fragmentation label.
