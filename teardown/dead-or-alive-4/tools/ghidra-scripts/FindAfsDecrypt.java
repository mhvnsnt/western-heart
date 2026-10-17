import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;

public class FindAfsDecrypt extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Searching for AFS string references ===");
        Listing listing = currentProgram.getListing();
        // Iterate defined strings
        DataIterator strings = listing.getDefinedData(true);
        int found = 0;
        while (strings.hasNext() && found < 50) {
            Data d = strings.next();
            try {
                Object val = d.getValue();
                if (val != null) {
                    String s = val.toString();
                    if (s.contains(".afs") || s.contains("AFS")) {
                        Address addr = d.getAddress();
                        println("AFS string: '" + s + "' at " + addr);
                        // Find xrefs
                        ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(addr);
                        while (refs.hasNext()) {
                            Reference r = refs.next();
                            Address from = r.getFromAddress();
                            Function f = getFunctionContaining(from);
                            String fname = (f != null) ? f.getName() + " @ " + f.getEntryPoint() : "(no function)";
                            println("  xref from " + from + " in " + fname);
                        }
                        found++;
                    }
                }
            } catch (Exception e) { /* skip */ }
        }
        println("=== Done, found " + found + " AFS strings ===");
    }
}
