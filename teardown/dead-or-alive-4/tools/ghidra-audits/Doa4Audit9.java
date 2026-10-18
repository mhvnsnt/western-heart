import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.util.*;
import java.util.*;

/**
 * DOA4 AUDIT 9 (Lead 2): dump the PE import table fully so the 10 unnamed
 * externals can be resolved against Xbox 360 XDK / CRI ADX signatures.
 * For every external symbol: name (or ordinal), owning library/DLL,
 * thunk/entry address, caller count + caller sites.
 */
public class Doa4Audit9 extends GhidraScript {
    public void run() throws Exception {
        println("=== DOA4 AUDIT 9: import table / externals dump ===");
        SymbolTable st = currentProgram.getSymbolTable();
        Namespace gns = currentProgram.getGlobalNamespace();
        SymbolIterator si = st.getSymbolIterator();
        int totalExt = 0;
        List<String> rows = new ArrayList<String>();
        while (si.hasNext()) {
            Symbol sym = si.next();
            if (sym.getSource() != SourceType.IMPORTED) continue;
            totalExt++;
            String name = sym.getName();
            SymbolType tp = sym.getSymbolType();
            Object obj = sym.getObject();
            Address thunkAddr = sym.getAddress();
            String libName = "?";
            Symbol parent = sym.getParentNamespace() instanceof Symbol
                ? (Symbol) sym.getParentNamespace() : null;
            if (parent != null) libName = parent.getName();
            // callers
            StringBuilder callers = new StringBuilder();
            int nc = 0;
            if (obj instanceof Function) {
                Function ef = (Function) obj;
                Address entry = ef.getEntryPoint();
                for (Reference r : currentProgram.getReferenceManager().getReferencesTo(entry)) {
                    if (!r.getReferenceType().isCall()) continue;
                    nc++;
                    if (nc <= 8) callers.append(" " + r.getFromAddress());
                }
            }
            rows.add("EXT name='" + name + "' lib='" + libName + "' type=" + tp
                + " thunk=" + thunkAddr + " callers=" + nc + callers);
        }
        println("imported symbols total: " + totalExt);
        for (String r : rows) println(r);

        // also dump .idata block layout (import directory visibility)
        Memory mem = currentProgram.getMemory();
        for (MemoryBlock b : mem.getBlocks()) {
            if (b.getName().toLowerCase().contains("idata") || b.getName().toLowerCase().contains("import")) {
                println("IMPORT-BLOCK " + b.getName() + " " + b.getStart() + "-" + b.getEnd() + " size=" + b.getSize());
            }
        }
        // functions that call the unnamed externals (External_XXXXXXXX)
        println("--- callers of unnamed externals ---");
        si = st.getSymbolIterator();
        while (si.hasNext()) {
            Symbol sym = si.next();
            if (sym.getSource() != SourceType.IMPORTED) continue;
            String name = sym.getName();
            if (!name.startsWith("External_") && !name.startsWith("thunk_")) continue;
            Object obj = sym.getObject();
            if (!(obj instanceof Function)) continue;
            Function ef = (Function) obj;
            Address entry = ef.getEntryPoint();
            for (Reference r : currentProgram.getReferenceManager().getReferencesTo(entry)) {
                if (!r.getReferenceType().isCall()) continue;
                Function caller = getFunctionContaining(r.getFromAddress());
                println(name + " @" + r.getFromAddress() + " caller=" + (caller != null ? caller.getName() + "@" + caller.getEntryPoint() : "(none)"));
            }
        }
        println("=== AUDIT 9 DONE ===");
    }
}
