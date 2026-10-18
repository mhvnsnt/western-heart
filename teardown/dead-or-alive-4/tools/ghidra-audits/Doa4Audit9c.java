import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.util.*;

/**
 * DOA4 AUDIT 9c: proper external-symbol enumeration + the exact external
 * addresses from Audit5 (0x00f587a4/0x00f591d4/...). Print what's there.
 */
public class Doa4Audit9c extends GhidraScript {
    public void run() throws Exception {
        println("=== DOA4 AUDIT 9c: external symbols + Audit5 thunk addresses ===");
        SymbolTable st = currentProgram.getSymbolTable();
        SymbolIterator ei = st.getExternalSymbols();
        int n = 0;
        while (ei.hasNext()) {
            Symbol s = ei.next();
            n++;
            Object o = s.getObject();
            println("EXTSYM name='" + s.getName() + "' parent='"
                + (s.getParentNamespace() != null ? s.getParentNamespace().getName() : "?")
                + "' addr=" + s.getAddress() + " obj=" + (o != null ? o.getClass().getSimpleName() : "null"));
        }
        println("external symbols total: " + n);

        // the Audit5 addresses, both as-is and +0x82000000 runtime mapping
        long[] addrs = {0x00f587a4L, 0x00f591d4L, 0x00f591c4L, 0x00f587c4L, 0x00f587b4L,
                        0x00f58984L, 0x00f58974L, 0x00f589e4L, 0x00d9df70L, 0x00d9e1f0L};
        AddressFactory af = currentProgram.getAddressFactory();
        for (long v : addrs) {
            Address a = af.getDefaultAddressSpace().getAddress(v);
            MemoryBlock b = currentProgram.getMemory().getBlock(a);
            Symbol sym = st.getPrimarySymbol(a);
            Instruction ins = currentProgram.getListing().getInstructionAt(a);
            Function f = getFunctionAt(a);
            println(String.format("0x%08x block=%s sym=%s insn=[%s] func=%s",
                v,
                b != null ? b.getName() : "(none)",
                sym != null ? sym.getName() : "(none)",
                ins != null ? ins.toString() : "(none)",
                f != null ? f.getName() : "(none)"));
            // print 8 instructions at the site
            if (ins == null) {
                try { disassemble(a); } catch (Exception e) {}
                ins = currentProgram.getListing().getInstructionAt(a);
            }
            Instruction c = ins;
            for (int j = 0; j < 10 && c != null; j++) {
                println("    " + c.getAddress() + "  " + c.toString());
                c = c.getNext();
            }
        }
        println("=== AUDIT 9c DONE ===");
    }
}
