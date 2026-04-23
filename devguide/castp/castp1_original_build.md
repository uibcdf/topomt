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

Local working copy used for rebuilds and instrumentation:

- `/home/diego/repos@uibcdf/topomt/sandbox/castp_alpha_4_1_src_local`

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

The cleaned audit copy was created outside the repository at:

- `/tmp/topomt_castp_radii_audit/pdb2alf_clean.c`

The essential fix was minimal and local:

```c
strncpy(temp, buffer, 4);
temp[4] = '\0';
stripout(temp2, temp);

strncpy(temp, buffer + 5, 4);
temp[4] = '\0';
stripout(temp2, temp);
```

This was applied in the parameter-table loader of `pdb2alf.c`, so the lookup
against `param.dat` works as intended.

This cleaned binary was used only as an oracle aid during the CASTp1 audit. The
native CASTp1 path does not depend on executing it.

## Rebuilding the original CASTp1 programs locally

From the local source copy:

```bash
cd /home/diego/repos@uibcdf/topomt/sandbox/castp_alpha_4_1_src_local
make delcx_new
make mkalf_new
```

This rebuilds the triangulation and alpha-shape programs through the original
Makefile structure.

Important note:

- this rebuild path does not itself fix the historical `pdb2alf.c` issue
- `delcx`, `mkalf`, and `volbl` are rebuilt from the local tree
- the cleaned `pdb2alf` used for audit was compiled separately from a patched
  temporary C file

## Clean CASTp1 oracle generation workflow

The clean oracle used during the CASTp1 parity phase was generated under:

- `/tmp/topomt_castp1_clean_oracle`

Per system, the workflow was:

1. run cleaned `pdb2alf` on the input PDB
2. run `delcx` on the weighted ASCII output
3. run `mkalf` on the resulting triangulation
4. run `volbl -s 4`
5. optionally run `mkalf -A` print commands for feature inspection

Conceptually:

```bash
pdb2alf_clean input.pdb > system_ascii
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
- the functional parity closure recorded in:
  - `devguide/castp/checkpoint_2026_04_23_castp1_functional_parity_closure.md`
