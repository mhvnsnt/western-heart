import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;

public class FindFmtXrefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Finding xrefs to AFS format strings ===");
        long[] fmtAddrs = {0x00685f41L, 0x0068684bL, 0x00678485L};
        for (long av : fmtAddrs) {
            Address addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(av);
            println("\n--- Refs to " + addr + " ---");
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(addr);
            int count = 0;
            while (refs.hasNext() && count < 20) {
                Reference r = refs.next();
                Address from = r.getFromAddress();
                Function f = getFunctionContaining(from);
                String fname = (f != null) ? f.getName() + " @ " + f.getEntryPoint() : "(data)";
                println("  " + r.getReferenceType() + " from " + from + " in " + fname);
                count++;
            }
            if (count == 0) println("  (no xrefs)");
        }
    }
}
