import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;

public class FindAfsCallers extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Finding functions referencing CRI AFS library ===");
        
        SymbolTable st = currentProgram.getSymbolTable();
        SymbolIterator syms = st.getAllSymbols(true);
        int count = 0;
        while (syms.hasNext() && count < 30) {
            Symbol s = syms.next();
            String name = s.getName().toLowerCase();
            if (name.contains("adxf")) {
                println("Symbol: " + s.getName() + " @ " + s.getAddress());
                ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(s.getAddress());
                int rc = 0;
                while (refs.hasNext() && rc < 10) {
                    Reference r = refs.next();
                    Function f = getFunctionContaining(r.getFromAddress());
                    if (f != null) {
                        println("  called from: " + f.getName() + " @ " + f.getEntryPoint());
                    }
                    rc++;
                }
                count++;
            }
        }
        if (count == 0) println("(no adxf symbols found)");
        println("=== Done ===");
    }
}
