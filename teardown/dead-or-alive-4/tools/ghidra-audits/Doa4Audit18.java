import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.util.*;

/**
 * DOA4 AUDIT 18:
 *  1. Print the program's language ID (32-bit vs 64-bit PPC?) — explains why
 *     0x00dfd4a8 (std/ld bytes) will not disassemble.
 *  2. Name import slots 40 (thunk 0x00f589e4) and 41 (thunk 0x00f589f4):
 *     find the IMPORTED symbol at/near those addresses, print name + lib.
 *  3. Full count of imported symbols (Audit9 named 10 — verify the total).
 */
public class Doa4Audit18 extends GhidraScript {
    public void run() throws Exception {
        println("=== DOA4 AUDIT 18: language check + slots 40/41 naming ===");
        println("language: " + currentProgram.getLanguage().getLanguageID()
            + " / " + currentProgram.getLanguage().getProcessor()
            + " addrSize=" + currentProgram.getAddressFactory().getDefaultAddressSpace().getPointerSize());

        AddressFactory af = currentProgram.getAddressFactory();
        long[] thunks = {0x00f589e4L, 0x00f589f4L};
        String[] slotNames = {"slot40", "slot41"};
        SymbolTable st = currentProgram.getSymbolTable();

        for (int i = 0; i < thunks.length; i++) {
            Address a = af.getDefaultAddressSpace().getAddress(thunks[i]);
            println("--- " + slotNames[i] + " thunk=0x" + Long.toHexString(thunks[i]) + " ---");
            // symbols at this address
            ghidra.program.model.symbol.Symbol[] syms = st.getSymbols(a);
            boolean found = false;
            for (ghidra.program.model.symbol.Symbol s : syms) {
                found = true;
                println("  symbol: name='" + s.getName() + "' type=" + s.getSymbolType()
                    + " source=" + s.getSource()
                    + " parent=" + s.getParentNamespace().getName());
                Object o = s.getObject();
                if (o instanceof Function) {
                    Function f = (Function) o;
                    println("    function entry=" + f.getEntryPoint()
                        + " thunked=" + f.isThunk() + " external=" + f.isExternal());
                }
            }
            // nearest imported symbols
            if (!found) println("  (no symbol at thunk address)");
            println("  nearest IMPORTED symbols:");
            SymbolIterator all = st.getSymbolIterator();
            int shown = 0;
            TreeMap<Long, String> near = new TreeMap<Long, String>();
            while (all.hasNext()) {
                Symbol s = all.next();
                if (s.getSource() != SourceType.IMPORTED) continue;
                long d = Math.abs(s.getAddress().getOffset() - thunks[i]);
                if (d < 0x1000) near.put(d, "name='" + s.getName() + "' @ " + s.getAddress()
                    + " parent=" + s.getParentNamespace().getName());
            }
            for (Map.Entry<Long, String> e : near.entrySet()) {
                if (shown++ >= 6) break;
                println("    dist=0x" + Long.toHexString(e.getKey()) + " " + e.getValue());
            }
        }

        // total imported symbols
        int total = 0;
        List<String> names = new ArrayList<String>();
        SymbolIterator si = st.getSymbolIterator();
        while (si.hasNext()) {
            Symbol s = si.next();
            if (s.getSource() != SourceType.IMPORTED) continue;
            total++;
            names.add(s.getName() + " [" + s.getParentNamespace().getName() + "]");
        }
        Collections.sort(names);
        println("imported symbols total: " + total);
        for (String n : names) println("  EXT " + n);

        println("=== AUDIT 18 DONE ===");
    }
}
