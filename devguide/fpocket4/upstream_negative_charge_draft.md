Title: PDB formal-charge parsing drops trailing minus signs in 4.2.3

In fpocket 4.2.3, commit `4bb0d8447f62fee77e2c3c29f54b5fcaf5e2c066`,
`rpdb_extract_pdb_atom` copies PDB columns 79–80 to a buffer and calls `atoi`
([source, lines 372–385](https://github.com/Discngine/fpocket/blob/4bb0d8447f62fee77e2c3c29f54b5fcaf5e2c066/src/rpdb.c#L372-L385)). The valid PDB magnitude/sign field `1-` is
therefore read as positive 1; `2-` becomes positive 2.

The [official wwPDB format specification](https://www.wwpdb.org/documentation/file-format-content/format33/sect9.html#ATOM)
defines columns 79–80 as charge and explicitly gives `2+` and `1-` as examples.
The expected negative values below follow that documented magnitude/sign syntax.

An independent caller of the unchanged original parser, linked to the original
`rpdb.c`, `utils.c` and `pertable.c`, produces:

| PDB field | Expected (e) | Observed (e) |
| --- | ---: | ---: |
| `1+` | 1 | 1 |
| `1-` | -1 | 1 |
| `2-` | -2 | 2 |
| blank | 0 | 0 |

The diagnostic exits 1 because the two negative expectations fail. Compiler:
cc (Ubuntu 15.2.0-16ubuntu1) 15.2.0. It uses synthetic single-record PDB input and
does not prepare a chemical system or execute pocket detection.

The minimal caller is:

```c
/* Analytical caller of the unchanged fpocket 4.2.3 PDB parser. */
#include <stdio.h>
#include <string.h>
#include "rpdb.h"

int main(void) {
    const char *fields[] = {"1+", "1-", "2-", "  "};
    const int expected[] = {1, -1, -2, 0};
    int failures = 0;
    for (int i = 0; i < 4; ++i) {
        char line[81], type[8] = "", name[8] = "", residue[8] = "";
        char chain[8] = "", symbol[8] = "", alternate, insert;
        int serial, residue_id, charge = 999, guessed = 0;
        float x, y, z, occupancy, bfactor;
        memset(line, ' ', 80);
        line[80] = '\0';
        memcpy(line, "ATOM  ", 6);
        memcpy(line + 6, "    1", 5);
        memcpy(line + 12, " N  ", 4);
        memcpy(line + 17, "GLY", 3);
        line[21] = 'A';
        memcpy(line + 22, "   1", 4);
        memcpy(line + 30, "   0.000   0.000   0.000", 24);
        memcpy(line + 54, "  1.00  0.00", 12);
        memcpy(line + 76, " N", 2);
        memcpy(line + 78, fields[i], 2);
        rpdb_extract_pdb_atom(line, type, &serial, name, &alternate, residue,
            chain, &residue_id, &insert, &x, &y, &z, &occupancy, &bfactor,
            symbol, &charge, &guessed);
        printf("field='%s' expected_charge_e=%d parsed_charge_e=%d\n",
            fields[i], expected[i], charge);
        if (charge != expected[i]) ++failures;
    }
    return failures ? 1 : 0;
}
```

From the source root, save the caller as `probe_pdb_charge.c`, use a new scratch
directory `probe-build`, and compile without editing the original source:

```bash
mkdir probe-build
for source in rpdb utils pertable; do
  cc -ffunction-sections -fdata-sections -Iheaders -Iplugins/include \
    -Iplugins/LINUXAMD64/molfile -c "src/$source.c" \
    -o "probe-build/$source.o"
done
cc -ffunction-sections -fdata-sections -Iheaders -Iplugins/include \
  -Iplugins/LINUXAMD64/molfile probe_pdb_charge.c probe-build/rpdb.o \
  probe-build/utils.o probe-build/pertable.o -Wl,--gc-sections -lm \
  -o probe-build/charge_probe
probe-build/charge_probe
```

The observed error is in the parsed atom charge and may affect outputs exposing
that field. I have not established an effect on pocket geometry or ranking.
In particular, `descriptors.c` computes `charge_score` from the amino-acid table
through `get_charge_from_idx`, so I am not claiming this is the same quantity.
No production implementation or scientific expectations were altered for this
report. Please consider parsing the explicit trailing charge sign while
preserving declared handling of blank and malformed fields.
