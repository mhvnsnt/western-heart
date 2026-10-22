import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;
import java.util.*;

public class FindAnmReader3 extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Phase10 v3: file-table xrefs ===");
        Memory mem = currentProgram.getMemory();
        AddressSpace sp = currentProgram.getAddressFactory().getDefaultAddressSpace();
        // 1) dump printable strings in table region 0x61e000-0x61f200
        Address t0 = sp.getAddress(0x61e000L), t1 = sp.getAddress(0x61f200L);
        byte[] buf = new byte[(int)(t1.getOffset()-t0.getOffset())];
        mem.getBytes(t0, buf);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < buf.length; i++) {
            int c = buf[i] & 0xFF;
            if (c >= 0x20 && c < 0x7F) sb.append((char)c);
            else { if (sb.length() >= 4) println("TBLSTR @ " + t0.add(i - sb.length()) + " : " + sb); sb.setLength(0); }
        }
        // 2) xrefs to ANY address in 0x61e800-0x61ea20 and to anm%d.afs @0x685f3c and 0x686848
        Set<Function> fns = new TreeSet<>(Comparator.comparing(Function::getEntryPoint));
        long[][] ranges = {{0x61e800L, 0x61ea20L}, {0x685f30L, 0x685f60L}, {0x686840L, 0x686860L}, {0x61e940L, 0x61e950L}};
        for (long[] r : ranges) {
            for (long off = r[0]; off < r[1]; off++) {
                Address a = sp.getAddress(off);
                ReferenceIterator ri = currentProgram.getReferenceManager().getReferencesTo(a);
                while (ri.hasNext()) {
                    Reference ref = ri.next();
                    Function f = getFunctionContaining(ref.getFromAddress());
                    println("XREF to " + a + " from " + ref.getFromAddress() + (f != null ? " in " + f.getName() + " @ " + f.getEntryPoint() : " (no fn)"));
                    if (f != null) fns.add(f);
                }
            }
        }
        println("=== candidate functions: " + fns.size() + " ===");
        DecompInterface dec = new DecompInterface();
        dec.openProgram(currentProgram);
        int n = 0;
        for (Function f : fns) {
            if (n++ >= 6) break;
            println("----- DECOMP " + f.getName() + " @ " + f.getEntryPoint() + " -----");
            DecompileResults res = dec.decompileFunction(f, 60, monitor);
            if (res != null && res.getDecompiledFunction() != null) {
                String c = res.getDecompiledFunction().getC();
                println(c.length() > 7000 ? c.substring(0, 7000) : c);
            } else println("(decompile failed)");
        }
        println("=== Done v3 ===");
    }
}
