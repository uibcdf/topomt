# `fpocket4` Parity Matrix

## Purpose

This document records the current parity status of `topomt.third_party.fpocket._native_impl`
against the audited local source build compiled from:

- `../../repos@others/fpocket`

It is intentionally separate from the general project status so the parity
state can be updated without mixing it with broader project notes.

## Important interpretation

This matrix is about parity against the **audited local source build** of
`fpocket`, not against the system/conda-forge binary currently used by wrapper
mode.

That distinction matters because different `fpocket` binaries/builds are now
known to produce different final pocket sets on some systems.

## Current matrix

| System | Final pocket parity vs audited local source build | Current note |
|---|---|---|
| `1GG0.pdb` | Yes | Exact at pocket and `atom_indices` level |
| `1N57.pdb` | Yes | Exact |
| `3LKF.pdb` | Yes | Exact |
| `E15ALA.pdb` | Yes | Exact |
| `1ATP.pdb` | Yes | Exact |
| `1CEN.pdb` | Yes | Exact |
| `1YCR.pdb` | Yes | Exact |
| `2GI9.pdb` | Yes | Exact |
| `2H05.pdb` | Yes | Exact |
| `2HGR.pdb` | Yes | Exact in deep validation; `612` final pockets in both audited upstream and `native` |

## Summary

Final exact parity against the audited local source build has been established
for:

- `1ATP.pdb`
- `1CEN.pdb`
- `1GG0.pdb`
- `1N57.pdb`
- `1YCR.pdb`
- `2GI9.pdb`
- `2H05.pdb`
- `2HGR.pdb`
- `3LKF.pdb`
- `E15ALA.pdb`

`2HGR.pdb` should still remain outside the routine battery as a large-system
deep-validation case, because both the audited upstream build and the native
TopoMT path are expensive on this structure. In the recorded deep-validation
run:

- audited upstream final pockets: `612`
- native final pockets: `612`
- native elapsed time: `871.35 s` (`14.52 min`)

The remaining audited work is now mostly:

- keeping wrapper-binary drift clearly separated from native/source parity;
- and continuing the raw-geometry diagnostics independently of final-pocket
  parity.

## Related documents

- [native_checkpoint.md](native_checkpoint.md)
- [../pocket_algorithm_issues.md](../pocket_algorithm_issues.md)
- [corrections/README.md](corrections/README.md)
