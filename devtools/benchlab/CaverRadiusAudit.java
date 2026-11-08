import chemistry.Atom;
import chemistry.PeriodicTable;
import chemistry.pdb.PdbFile;
import chemistry.pdb.PdbFileFactory;
import geometry.primitives.Point;
import java.io.File;
import java.util.Locale;

/** Read four atoms through CAVER's original public reader; implement no chemistry. */
public final class CaverRadiusAudit {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            throw new IllegalArgumentException("Expected original atom table and PDB paths");
        }
        PeriodicTable table = new PeriodicTable(new File(args[0]));
        // Same constructor/default flag as CalculationSettings.getPdbFileProcessor.
        PdbFile input = new PdbFileFactory(table).create(new File(args[1]), true);
        System.out.println("serial\tname\telement\tradius_angstrom\tx_angstrom\ty_angstrom\tz_angstrom");
        for (Atom atom : input.getAtoms().values()) {
            Point point = atom.getCenter();
            System.out.printf(Locale.ROOT, "%d\t%s\t%s\t%.17g\t%.17g\t%.17g\t%.17g%n",
                atom.getSerialNumber(), atom.getName(), atom.getElement().getSymbol(),
                atom.getRadius(), point.getX(), point.getY(), point.getZ());
        }
    }
}
