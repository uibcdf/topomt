# CASTp1 Original Build and Clean Oracle Recipe

Date: 2026-04-23

## Purpose

This document records the reproducible local reference used during the CASTp1
native parity phase:

- original CAST alpha-shape source tree
- locally rebuildable `delcx`, `mkalf`, and `volbl`
- a cleaned `pdb2alf` used only to remove historical C string-handling breakage
- the command sequence used to regenerate the clean CASTp1 oracle

## Reference source trees

Original upstream-style source tree used for audit:

- `/home/diego/repos@uibcdf/Alphashape/castp/alpha-4.1-src`

TopoMT-maintained reproducible copy with the minimal `pdb2alf.c` cleanup:

- `/home/diego/repos@uibcdf/Alphashape/castp/topomt_version`

This `topomt_version` tree is now the preferred reproducible local reference
copy for CASTp1 rebuilds.

The top-level Makefile in the local copy already exposes the relevant targets:

- `make delcx_new`
- `make mkalf_new`
- `make tri_new`

and contains the linked subtrees for:

- `basic`
- `lia`
- `sos`
- `delcx`
- `mkalf`
- `volbl`

## Why a cleaned `pdb2alf` was needed

The original `volbl/pdb2alf.c` contains unsafe fixed-width string handling in
the parameter-table reader. In particular, it copies 4 characters with
`strncpy(...)` and then treats the destination as a C string without forcing a
terminating null byte.

This produced non-canonical historical behavior on some systems:

- parameter lookups fail spuriously
- many atoms fall back to the default heavy radius `1.80`
- after probe expansion, many ALF radii become `3.20`

That behavior is treated as a build/runtime defect of the old C converter, not
as the intended CASTp1 radii policy.

## Minimal `pdb2alf` cleanup used in the audit

The essential fix set now preserved in
`/home/diego/repos@uibcdf/Alphashape/castp/topomt_version/volbl/pdb2alf.c` is:

1. widen `resName` from `3+1` to `4+1`
2. allocate the parameter table with `calloc(...)`
3. force null termination after fixed-width `strncpy(..., 4)` reads in the
   `param.dat` loader
4. replace the fragile `bsearch(...)` lookup with an explicit stripped-label
   lookup helper
5. widen the temporary residue buffer `temp2` from `4` to `5`

The most critical string-handling part is:

```c
strncpy(temp, buffer, 4);
temp[4] = '\0';
stripout(temp2, temp);

strncpy(temp, buffer + 5, 4);
temp[4] = '\0';
stripout(temp2, temp);
```

These fixes recover the intended `param.dat` lookup behavior and avoid the
historical fallback-to-`3.20` artifact caused by broken parsing.

## Rebuilding the original CASTp1 programs locally

From the TopoMT-maintained reference copy:

```bash
bash /home/diego/repos@uibcdf/Alphashape/castp/topomt_version/build_topomt_version.sh
```

This script is stored next to the copied source tree and is the intended entry
point for rebuilding the CASTp1 reference binaries.

Important note:

- the original alpha-4.1 build system invokes `/bin/csh` directly
- therefore the host system must provide `csh`/`tcsh` at `/bin/csh`
- if `/bin/csh` is missing, the helper script exits with an explicit error
- `pdb2alf_topomt` is compiled directly from the patched `volbl/pdb2alf.c`

## Clean CASTp1 oracle generation workflow

The clean oracle used during the CASTp1 parity phase was generated under:

- `/tmp/topomt_castp1_clean_oracle`

Per system, the workflow was:

1. run `pdb2alf_topomt` on the input PDB
2. run `delcx` on the weighted ASCII output
3. run `mkalf` on the resulting triangulation
4. run `volbl -s 4`
5. optionally run `mkalf -A` print commands for feature inspection

Conceptually:

```bash
/home/diego/repos@uibcdf/Alphashape/castp/topomt_version/bin/pdb2alf_topomt input.pdb > system_ascii
delcx system_ascii
mkalf system_ascii
volbl -s 4 system_ascii
echo "print tetrahedra" | mkalf -A system_ascii
```

The audit also used explicit MKALF printouts for pockets/voids and local
diagnostics on tetrahedra.

## Native-policy conclusion from this rebuild

The correct CASTp1-native radii policy is:

- read PDB fixed fields as `pdb2alf` intended
- query `param.dat`
- use defaults only when the lookup genuinely fails
- add the solvent probe radius afterward

That policy is implemented natively through:

- `radii_model='castp1_pdb2alf'`

and matches the cleaned `pdb2alf` oracle on the local CASTp1 benchmark set.

## Freeze note

The historical compiled behavior with corrupted `3.20`-style radii on some
systems should not be used as the CASTp1 reference.

The intended CASTp1 reference for this repository is:

- cleaned-oracle CASTp1 semantics
- native `castp1_pdb2alf` radii policy
- source copy:
  - `/home/diego/repos@uibcdf/Alphashape/castp/topomt_version`
- the functional parity closure recorded in:
  - `devguide/castp/checkpoint_2026_04_23_castp1_functional_parity_closure.md`
