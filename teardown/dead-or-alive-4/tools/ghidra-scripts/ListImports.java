import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.*;
import ghidra.program.model.listing.Function;

public class ListImports extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== External/Imported Symbols ===");
        SymbolTable st = currentProgram.getSymbolTable();
        SymbolIterator ext = st.getExternalSymbols();
        int count = 0;
        while (ext.hasNext() && count < 50) {
            Symbol s = ext.next();
            println("  " + s.getName() + " @ " + s.getAddress());
            count++;
        }
        println("Total: " + count + " (showing first 50)");
    }
}
