import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.*;
import java.util.*;

public class FindAnmReader4 extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("=== Phase10 v4: pointer-value scan to file table ===");
        Memory mem = currentProgram.getMemory();
        AddressSpace sp = currentProgram.getAddressFactory().getDefaultAddressSpace();
        long LO = 0x61e800L, HI = 0x61ea20L;
        Set<Address> ptrLocs = new TreeSet<>();
        for (MemoryBlock b : mem.getBlocks()) {
            if (!b.isInitialized()) continue;
            byte[] bytes = new byte[(int)b.getSize()];
            try { mem.getBytes(b.getStart(), bytes); } catch (Exception e) { continue; }
            for (int i = 0; i + 4 <= bytes.length; i++) {
                long be = ((bytes[i]&0xFFL)<<24)|((bytes[i+1]&0xFFL)<<16)|((bytes[i+2]&0xFFL)<<8)|(bytes[i+3]&0xFFL);
                if (be >= LO && be < HI) {
                    Address loc = b.getStart().add(i);
                    println("PTR BE @ " + loc + " -> " + sp.getAddress(be));
                    ptrLocs.add(loc);
                }
            }
        }
        println("pointer locations: " + ptrLocs.size());
        Set<Function> fns = new TreeSet<>(Comparator.comparing(Function::getEntryPoint));
        for (Address loc : ptrLocs) {
            ReferenceIterator ri = currentProgram.getReferenceManager().getReferencesTo(loc);
            while (ri.hasNext()) {
                Reference r = ri.next();
                Function f = getFunctionContaining(r.getFromAddress());
                println("XREF ptr " + loc + " from " + r.getFromAddress() + (f != null ? " in " + f.getName() + " @ " + f.getEntryPoint() : ""));
                if (f != null) fns.add(f);
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
        println("=== Done v4 ===");
    }
}
