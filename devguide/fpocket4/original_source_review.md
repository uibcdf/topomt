# Original fpocket 4.2.3 source review

Date: 2026-11-05. The user supplied the read-only study checkout
`~/repos@others/fpocket`. Its clean HEAD is
`4bb0d8447f62fee77e2c3c29f54b5fcaf5e2c066`, exactly tag `4.2.3`.
The checkout was not modified or compiled in place.

The executable used by the handoff controls comes from conda-forge
`fpocket-4.2.3-h5fd1fdb_2`. Its packaged recipe selects the 4.2.3 release archive,
SHA256 `62b3da6490eeab0db488f0182150d340de2be0be23f4fd1def9d5846ce724ede`.
The recipe additionally applies a two-line `src/fparams.c` pointer/string fix
for custom-pocket argument handling. That patch does not touch the PDB parser
examined here. Source identity and package/compiler identity remain separate.
The bundled TopoMT `fpocket4.tar.gz` has a `fpocket2` root; its filename alone was
not used to identify it as this release.

## Findings in the bounded path

- `src/rpdb.c:295–389` reads serials, labels, coordinates, occupancy, B factors,
  elements and charge fields. Missing elements can be guessed from names.
- `src/rpdb.c:1038–1049` counts H atoms; `src/voronoi.c:92–130` builds a heavy-atom
  mapping and omits element `H` from its Voronoi coordinate input. Retaining H
  in the receptor does not mean it contributes a Voronoi site.
- The inspected PDB/Voronoi route constructs geometry from atom records and
  coordinates. It does not certify MolSysMT chemical connectivity. The reference
  admission/digest in TopoMT is a handoff provenance policy, not evidence that
  fpocket validates or interprets every source chemical-state property.
- `src/descriptors.c:506–511` accumulates `charge_score` through
  `get_charge_from_idx`, whose implementation in `src/aa.c:400–409` returns a
  residue-table charge. This preserves the existing TopoMT measurement definition;
  it must not be presented as a sum of submitted PDB formal charges.

## Reproduced negative-charge parser defect

`src/rpdb.c:372–385` copies the PDB two-character charge field into a buffer and
calls `atoi`. A trailing minus sign is not applied to the parsed magnitude.
The unchanged original `rpdb_extract_pdb_atom` was called from the independent
[C control](../../devtools/fpocket/probe_pdb_charge.c), linked against unchanged
`rpdb.c`, `utils.c` and `pertable.c`. The synthetic single-atom records exercise
lexical parsing, not chemical preparation or complete pocket detection.

| PDB field | Expected charge (e) | Observed charge (e) |
| --- | ---: | ---: |
| `1+` | 1 | 1 |
| `1-` | -1 | 1 |
| `2-` | -2 | 2 |
| blank | 0 | 0 |

The control intentionally exits **1** because the two negative cases fail their
independent expectations. This is not reported as a passing regression. No
fpocket or TopoMT production implementation was changed for this finding.
The source field is used in output paths such as `src/writepocket.c`; possible
downstream effects require targeted checks. The separately computed residue-table
`charge_score` is not established as affected, nor is a changed pocket ranking,
geometry, affinity or biological conclusion. The packaged executable was not
rebuilt or used to claim this isolated parser measurement.

To reproduce with a new scratch directory and a C compiler, set `FPOCKET_SOURCE`
to the pinned checkout and `FPOCKET_PROBE_DIR` to that directory:

```bash
for source in rpdb utils pertable; do
  cc -ffunction-sections -fdata-sections \
    -I"$FPOCKET_SOURCE/headers" -I"$FPOCKET_SOURCE/plugins/include" \
    -I"$FPOCKET_SOURCE/plugins/LINUXAMD64/molfile" \
    -c "$FPOCKET_SOURCE/src/$source.c" -o "$FPOCKET_PROBE_DIR/$source.o"
done
cc -ffunction-sections -fdata-sections \
  -I"$FPOCKET_SOURCE/headers" -I"$FPOCKET_SOURCE/plugins/include" \
  -I"$FPOCKET_SOURCE/plugins/LINUXAMD64/molfile" \
  devtools/fpocket/probe_pdb_charge.c "$FPOCKET_PROBE_DIR/rpdb.o" \
  "$FPOCKET_PROBE_DIR/utils.o" "$FPOCKET_PROBE_DIR/pertable.o" \
  -Wl,--gc-sections -lm -o "$FPOCKET_PROBE_DIR/charge_probe"
"$FPOCKET_PROBE_DIR/charge_probe"
```

This Linux source diagnostic is separate from the 153 passing TopoMT integration
controls. It adds no mandatory dependency, CI gate or release claim. The owning
external repository is `Discngine/fpocket`; publication of a report there needs
the common explicit external-publication authorization. No upstream issue or PR
has been created. The reviewed local issue draft is separate from the already
approved TopoMT #101 checkpoint payload.
