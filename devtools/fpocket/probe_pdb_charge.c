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
