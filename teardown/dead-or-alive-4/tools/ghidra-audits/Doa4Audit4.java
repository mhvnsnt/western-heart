import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import ghidra.app.decompiler.*;
import java.util.*;

/**
 * DOA4 AUDIT 4: disassemble around the bl->thunk call sites, decompile the
 * callers to identify the 10 externals (file I/O? alloc? crypto?).
 */
public class Doa4Audit4 extends GhidraScript {
    Memory mem;
    public void run() throws Exception {
        mem = currentProgram.getMemory();
        AddressFactory af = currentProgram.getAddressFactory();
        AddressSpace def = af.getDefaultAddressSpace();
        println("=== DOA4 AUDIT 4 ===");

        long[] callSites = {0x00b89748L, 0x00b8c790L, 0x00b8dc94L, 0x00b8ea9cL,
                            0x00d9dfd4L, 0x00d9e20cL, 0x00d9e230L};
        long[] thunks = {0x00f58764L,0x00f58774L,0x00f58794L,0x00f587a4L,0x00f587c4L,
                         0x00f58984L,0x00f58a34L,0x00f58c84L,0x00f588c4L,0x00f59154L};

        // disassemble each thunk body first
        println("--- thunk bodies ---");
        for (long t : thunks) {
            Address a = def.getAddress(t);
            for (long o = 0; o < 32; o += 4) {
                try { disassemble(a.add(o)); } catch (Exception e) {}
            }
            Instruction ins = currentProgram.getListing().getInstructionAt(a);
            StringBuilder sb = new StringBuilder();
            for (int k = 0; k < 6 && ins != null; k++) { sb.append(ins.toString()).append(" | "); ins = ins.getNext(); }
            println("thunk 0x" + Long.toHexString(t) + ": " + sb);
        }

        // disassemble + decompile each caller region
        for (long cs : callSites) {
            Address a = def.getAddress(cs);
            println("\n=== caller @ " + a + " ===");
            for (long o = -1024; o <= 512; o += 4) {
                try { disassemble(a.add(o)); } catch (Exception e) {}
            }
            // find enclosing function: walk back to a prolog-ish (stwu r1 / mflr r0)
            Address fstart = findFuncStart(a);
            println("func start guess: " + fstart);
            Function f = null;
            try { f = createFunction(fstart, null); } catch (Exception e) { println("createFunction: " + e); }
            if (f == null) f = getFunctionContaining(a);
            if (f != null) {
                println("func: " + f.getName() + " size~" + f.getBody().getNumAddresses());
                String c = decompile(f);
                if (c != null) println("--- decomp (" + c.length() + " chars) ---\n"
                    + c.substring(0, Math.min(4000, c.length())));
            } else println("(no function)");
        }
        println("=== AUDIT 4 DONE ===");
    }

    Address findFuncStart(Address a) {
        // walk back up to 512 bytes looking for stwu r1,-X(r1) (0x9421xxxx) or mflr r0 (0x7c0802a6)
        Listing L = currentProgram.getListing();
        Address cur = a;
        for (int k = 0; k < 128; k++) {
            Instruction ins = L.getInstructionAt(cur);
            if (ins != null) {
                String s = ins.toString();
                if (s.startsWith("stwu r1,") || s.equals("mflr r0")) return cur;
            }
            try { cur = cur.subtract(4); } catch (Exception e) { break; }
        }
        return a.subtract(64);
    }

    String decompile(Function f) {
        DecompInterface di = new DecompInterface();
        try {
            di.openProgram(currentProgram);
            DecompileResults dr = di.decompileFunction(f, 90, monitor);
            if (dr != null && dr.getDecompiledFunction() != null)
                return dr.getDecompiledFunction().getC();
        } catch (Exception e) { return "(decomp err " + e + ")"; }
        finally { di.dispose(); }
        return "(null)";
    }
}
